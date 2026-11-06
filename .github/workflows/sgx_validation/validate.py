"""SGX validation driver. No numerical functions or density context are patched."""
import argparse
import ctypes
import datetime
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import unittest


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str) + '\n', encoding='utf-8')


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def thread_queries():
    if os.name == 'nt':
        import psutil
        paths = {item.path for item in psutil.Process().memory_maps()}
    else:
        paths = {line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines()
                 if '/' in line}
    result = []
    for path in sorted(paths):
        if not any(name in path.lower() for name in ['openblas', 'libblas', 'libgomp', 'mkl_rt']):
            continue
        library = ctypes.CDLL(path)
        row = {'path': path, 'sha256': digest(path), 'getters': {}}
        for symbol in ['openblas_get_num_threads', 'scipy_openblas_get_num_threads',
                       'scipy_openblas_get_num_threads64_', 'openblas_get_num_threads64_',
                       'omp_get_max_threads', 'MKL_Get_Max_Threads']:
            try:
                getter = getattr(library, symbol)
            except AttributeError:
                continue
            getter.argtypes = []
            getter.restype = ctypes.c_int
            row['getters'][symbol] = getter()
        result.append(row)
    return result


def run_one(args):
    import numpy
    dll_handle = None
    if args.source:
        sys.path.insert(0, str(args.source))
    if args.native_lib:
        dll_handle = os.add_dll_directory(str(args.native_lib))
        load_library = numpy.ctypeslib.load_library
        source_lib = (args.source / 'pyscf/lib').resolve()

        def native_loader(name, path):
            if Path(path).resolve() == source_lib and (args.native_lib / (name + '.dll')).is_file():
                path = str(args.native_lib)
            return load_library(name, path)

        numpy.ctypeslib.load_library = native_loader
    import scipy
    import scipy.linalg
    import pyscf
    from pyscf import lib, dft
    from pyscf.sgx import sgx, sgx_jk
    from pyscf.scf import hf

    package = Path(pyscf.__file__).resolve().parent
    if args.source:
        assert package == args.source / 'pyscf', package
    else:
        assert not package.is_relative_to(args.test_root), package
        assert 'site-packages' in str(package), package
        assert not any(Path(p or '.').resolve() == args.test_root for p in sys.path)
    source_files = ['pyscf/sgx/sgx.py', 'pyscf/sgx/sgx_jk.py', 'pyscf/scf/hf.py',
                    'pyscf/sgx/grad/rks.py', 'pyscf/sgx/grad/uks.py']
    equivalence = []
    for name in source_files:
        imported_file = package.parent / name
        expected_file = args.test_root / name
        row = {'file': name, 'imported_path': str(imported_file),
               'imported_sha256': digest(imported_file), 'candidate_sha256': digest(expected_file)}
        assert row['imported_sha256'] == row['candidate_sha256'], row
        equivalence.append(row)

    report = {'pid': os.getpid(), 'started_at_utc': now(), 'python': sys.version,
              'executable': sys.executable, 'platform': platform.platform(),
              'source_sha': args.source_sha, 'tool_sha256': digest(__file__),
              'suite': args.suite, 'production_equivalence': equivalence,
              'packages': {dist.metadata['Name']: dist.version for dist in importlib.metadata.distributions()},
              'pyscf_import': str(package), 'pyscf_version': pyscf.__version__,
              'libxc_version': dft.libxc.libxc_version(), 'openmp_threads': lib.num_threads(),
              'thread_queries': thread_queries(),
              'thread_environment': {key: os.environ.get(key) for key in
                  ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                   'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS']},
              'native_library_adapter': str(args.native_lib) if args.native_lib else None,
              'numerical_wrappers': False, 'gradient_cases': [], 'test_sources': []}
    paths = {
        'lifecycle': ['pyscf/sgx/test/test_rsh.py'],
        'forwarding': ['pyscf/sgx/test/test_rsh_forwarding.py'],
        'rks': ['pyscf/sgx/grad/test/test_rks.py'],
        'uks': ['pyscf/sgx/grad/test/test_uks.py'],
        'sgx': ['pyscf/sgx/test/test_sgx.py', 'pyscf/sgx/test/test_sgx_jk.py'],
    }[args.suite]
    suite = unittest.TestSuite()
    observed_codes = set()
    for i, path in enumerate(paths):
        test_path = args.test_root / path
        report['test_sources'].append({'path': path, 'sha256': digest(test_path)})
        spec = importlib.util.spec_from_file_location('_sgx_validation_' + str(i), test_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        if args.suite in ['rks', 'uks']:
            suite.addTest(module.KnownValues('test_finite_diff_grad_high_cost'))
            observed_codes.add(module.KnownValues._check_finite_diff_grad.__code__)
        elif args.suite == 'sgx':
            names = [name for name in unittest.defaultTestLoader.getTestCaseNames(module.KnownValues)
                     if not name.endswith('_high_cost')]
            suite.addTests(module.KnownValues(name) for name in names)
        else:
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    report['selected_tests'] = [str(test) for group in suite for test in
                                (group if isinstance(group, unittest.TestSuite) else [group])]
    expected_count = suite.countTestCases()
    assert expected_count > 0

    def observe(frame, event, arg):
        if event == 'return' and frame.f_code in observed_codes:
            local = frame.f_locals
            row = {'xc': local['xc'], 'settings': list(local['df_settings']),
                   'decimals': local['order']}
            if all(key in local for key in ['g', 'e1', 'e2', 'delta']):
                gradient = float(local['g'][0, 2])
                finite_diff = float((local['e1'] - local['e2']) / (2 * local['delta']) * lib.param.BOHR)
                row.update(gradient=gradient, finite_diff=finite_diff,
                           error=abs(gradient - finite_diff), delta_angstrom=local['delta'],
                           e_plus=local['e1'], e_minus=local['e2'])
            report['gradient_cases'].append(row)

    started = time.monotonic()
    if observed_codes:
        sys.setprofile(observe)
    try:
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        sys.setprofile(None)
    report.update(tests_run=result.testsRun, expected_tests=expected_count,
                  skipped=result.skipped, failures=[(str(t), tb) for t, tb in result.failures],
                  errors=[(str(t), tb) for t, tb in result.errors],
                  seconds=time.monotonic() - started, finished_at_utc=now())
    executed = result.testsRun == expected_count and not result.skipped
    if observed_codes:
        cases = report['gradient_cases']
        executed = executed and len(cases) == 9 and [r['xc'] for r in cases] == ['PBE0', 'HSE06', 'WB97X'] * 3
        executed = executed and all('error' in row for row in cases)
    report['result'] = 'Passed' if result.wasSuccessful() and executed else 'Failed'
    write_json(args.output / 'result.json', report)
    return 0 if report['result'] == 'Passed' else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-root', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--native-lib', type=Path)
    parser.add_argument('--source-sha', required=True)
    parser.add_argument('--suite', choices=['lifecycle', 'forwarding', 'rks', 'uks', 'sgx'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--attempts', type=int, default=1)
    parser.add_argument('--one', action='store_true')
    args = parser.parse_args()
    for name in ['test_root', 'source', 'native_lib', 'output']:
        value = getattr(args, name)
        if value:
            setattr(args, name, value.resolve())
    if args.one:
        try:
            return run_one(args)
        except Exception:
            write_json(args.output / 'result.json', {'result': 'Error', 'pid': os.getpid(),
                       'exception': traceback.format_exc(), 'finished_at_utc': now()})
            traceback.print_exc()
            return 2
    if not 1 <= args.attempts <= 200:
        parser.error('attempts must be between 1 and 200')
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'validate-source.py').write_bytes(Path(__file__).read_bytes())
    config = args.output / 'empty_config.py'
    config.write_text('# No user configuration.\n', encoding='utf-8')
    ext_paths = args.output / 'empty_ext_paths.txt'
    ext_paths.write_text('', encoding='utf-8')
    env = os.environ.copy()
    env.update({key: '1' for key in ['OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS',
                                  'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS']})
    env.update(OMP_NUM_THREADS='4', PYSCF_CONFIG_FILE=str(config), PYSCF_EXT_PATH=str(ext_paths),
               PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    report = {'pid': os.getpid(), 'source_sha': args.source_sha, 'suite': args.suite,
              'requested_attempts': args.attempts, 'tool_sha256': digest(__file__),
              'started_at_utc': now(), 'attempts': []}
    for number in range(1, args.attempts + 1):
        out = args.output / ('attempt-%04d' % number)
        out.mkdir()
        command = [sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--one',
                   '--test-root', str(args.test_root), '--source-sha', args.source_sha,
                   '--suite', args.suite, '--output', str(out)]
        for name in ['source', 'native_lib']:
            if getattr(args, name):
                command.extend(['--' + name.replace('_', '-'), str(getattr(args, name))])
        with (out / 'stdout.log').open('wb') as stdout, (out / 'stderr.log').open('wb') as stderr:
            proc = subprocess.Popen(command, cwd=out, env=env, stdout=stdout, stderr=stderr)
            row = {'attempt': number, 'pid': proc.pid, 'command': command, 'started_at_utc': now()}
            write_json(out / 'process.json', row)
            code = proc.wait()
        detail = json.loads((out / 'result.json').read_text()) if (out / 'result.json').exists() else {'result': 'Missing'}
        row.update(exit_code=code, result=detail['result'], finished_at_utc=now())
        report['attempts'].append(row)
        report['result'] = 'Passed' if not code and number == args.attempts else ('Failed' if code else 'Running')
        report['finished_at_utc'] = now()
        write_json(args.output / 'summary.json', report)
        print(json.dumps({key: row[key] for key in ['attempt', 'pid', 'exit_code', 'result']}), flush=True)
        if code:
            return code
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
