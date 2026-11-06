"""Task-only post-merge verification; never rewrites production code or tests."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

from probe import environment, sha256

BASE = 'ab749b4fd00f95a08ad00997356c9f6f77fc8674'
TARGET = 'pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing'
REGRESSIONS = [
    'pyscf/scf/test/test_addons.py::KnownValues::' + name
    for name in ('test_rohf_smearing1', 'test_rhf_smearing_nelec', 'test_smearing_mu0')
] + [
    'pyscf/pbc/scf/test/test_addons.py::KnownValues::' + name
    for name in ('test_krhf_smearing', 'test_kuhf_smearing', 'test_kuhf_smearing1',
                 'test_rhf_smearing', 'test_uhf_smearing', 'test_smearing_for_custom_H')
]


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def run(command, **kwargs):
    subprocess.run([str(x) for x in command], check=True, **kwargs)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def bundle(args):
    repo, dest = args.repo.resolve(), args.root.resolve() / 'bundle'
    dest.mkdir(parents=True, exist_ok=False)
    if git(repo, 'diff', BASE, '--', 'pyscf', 'setup.py', 'pyproject.toml', 'MANIFEST.in'):
        raise RuntimeError('Scientific/build sources differ from baseline B')
    wheel, = (repo / 'dist').glob('pyscf-*.whl')
    shutil.copy2(wheel, dest / wheel.name)
    source_hashes = {}
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith('pyscf/') and name.endswith('.py'):
                source = repo / name
                if not source.is_file() or archive.read(name) != source.read_bytes():
                    raise RuntimeError('Wheel/source mismatch: ' + name)
                source_hashes[name] = sha256(source)
    tests = sorted({node.split('::')[0] for node in [TARGET] + REGRESSIONS})
    for name in tests:
        target = dest / 'tests' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / name, target)
    shutil.copy2(repo / 'pytest.ini', dest / 'pytest.ini')
    manifest = {
        'source_sha': BASE, 'tool_sha': git(repo, 'rev-parse', 'HEAD'),
        'source_tree': git(repo, 'rev-parse', BASE + ':pyscf'),
        'wheel': wheel.name, 'wheel_sha256': sha256(wheel),
        'wheel_bytes': wheel.stat().st_size, 'python_sources': source_hashes,
        'tests': {name: sha256(repo / name) for name in tests},
        'target': TARGET, 'regressions': REGRESSIONS,
        'tool_files': {p.name: sha256(p) for p in Path(__file__).parent.glob('*.py')},
        'build_python': sys.version,
    }
    write_json(dest / 'manifest.json', manifest)


def install(args):
    root = args.root.resolve()
    manifest = json.loads((root / 'bundle/manifest.json').read_text())
    wheel = root / 'bundle' / manifest['wheel']
    assert sha256(wheel) == manifest['wheel_sha256']
    venv = root / 'venv'
    run([sys.executable, '-B', '-m', 'venv', venv])
    python = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    command = [python, '-B', '-m', 'pip', 'install', wheel, 'pytest<9']
    constraints = root / 'bundle/environment-lock.txt'
    if constraints.exists():
        command += ['-c', constraints]
    run(command)
    run([python, '-B', '-m', 'pip', 'check'])
    # Reuse each platform's preflight dependency versions in every formal shard.
    freeze = subprocess.check_output([str(python), '-m', 'pip', 'freeze'], text=True)
    if not constraints.exists():
        constraints.write_text(''.join(line + '\n' for line in freeze.splitlines()
                                       if not line.lower().startswith('pyscf')),
                               encoding='utf-8')
    site = Path(subprocess.check_output(
        [str(python), '-c', 'import sysconfig; print(sysconfig.get_path("purelib"))'],
        text=True).strip())
    for relative, digest in manifest['python_sources'].items():
        assert sha256(site / relative) == digest, relative
    for relative, digest in manifest['tests'].items():
        source = root / 'bundle/tests' / relative
        assert sha256(source) == digest
        target = site / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        (target.parent / '__init__.py').touch()
    write_json(root / 'installation.json', {
        'python': str(python), 'site': str(site), 'pip_freeze': freeze,
        'production_files_verified': len(manifest['python_sources']),
        'manifest': manifest,
    })


class EvidencePlugin:
    def __init__(self):
        self.collected = []
        self.reports = []
        self.deselected = []

    def pytest_collection_finish(self, session):
        self.collected = [item.nodeid for item in session.items]

    def pytest_deselected(self, items):
        self.deselected.extend(item.nodeid for item in items)

    def pytest_runtest_logreport(self, report):
        self.reports.append({'nodeid': report.nodeid, 'when': report.when,
                             'outcome': report.outcome, 'duration': report.duration,
                             'longrepr': str(report.longrepr) if report.longrepr else None})


def child(args):
    import pytest
    import pyscf
    from pyscf.scf import hf
    from pyscf.scf.smearing import _SmearingSCF

    root = args.root.resolve()
    installation = json.loads((root / 'installation.json').read_text())
    manifest = installation['manifest']
    site = Path(installation['site'])
    assert Path(pyscf.__file__).resolve().parent == site / 'pyscf'
    assert Path.cwd().resolve() == site
    for relative, digest in manifest['tests'].items():
        assert sha256(site / relative) == digest
    # This profiler observes return values and frame locals. It never replaces a
    # scientific method, sets a callback, or changes an SCF input/return value.
    checks, stages, objects = [], [], {}
    check_code = _SmearingSCF.check_convergence.__code__
    kernel_code = hf.kernel.__code__

    def profile(frame, event, value):
        if event != 'return':
            return
        if frame.f_code is check_code:
            self = frame.f_locals['self']
            envs = frame.f_locals['envs']
            stage = objects.setdefault(id(self), len(objects) + 1)
            checks.append({
                'stage': stage, 'cycle': int(envs['cycle']) + 1,
                'extra': bool(envs.get('scf_conv')),
                'dF_or_fallback_dE': float(frame.f_locals['dF']),
                'dE': float(envs['e_tot'] - envs['last_hf_e']),
                'norm_gorb': float(envs['norm_gorb']),
                'e_tot': float(envs['e_tot']), 'e_free': self.e_free,
                'entropy': self.entropy, 'conv_tol': float(envs['conv_tol']),
                'conv_tol_grad': float(envs['conv_tol_grad']),
                'returned_converged': bool(value), 'sigma': self.sigma,
                'fix_spin': bool(self.fix_spin),
            })
        elif frame.f_code is kernel_code:
            mf = frame.f_locals['mf']
            if isinstance(mf, _SmearingSCF) and value is not None:
                stages.append({
                    'stage': objects.setdefault(id(mf), len(objects) + 1),
                    'e_tot': float(value[1]), 'e_free': mf.e_free,
                    'entropy': mf.entropy, 'converged': bool(value[0]),
                    'sigma': mf.sigma, 'fix_spin': bool(mf.fix_spin),
                    'conv_tol': mf.conv_tol, 'cycles': mf.cycles,
                })

    plugin = EvidencePlugin()
    nodes = REGRESSIONS if args.regressions else [TARGET]
    before = environment()
    sys.setprofile(profile)
    try:
        code = pytest.main(nodes + ['-s', '-v', '-c', str(root / 'bundle/pytest.ini'),
                           '-o', 'addopts=', '--rootdir=.', '--import-mode=prepend',
                           '-p', 'no:cacheprovider', '--tb=long',
                           '--junitxml=' + str(args.output.with_suffix('.xml'))],
                           plugins=[plugin])
    finally:
        sys.setprofile(None)
    after = environment()
    calls = [r for r in plugin.reports if r['when'] == 'call']
    valid = (code == 0 and sorted(plugin.collected) == sorted(nodes)
             and not plugin.deselected and len(calls) == len(nodes)
             and all(r['outcome'] == 'passed' for r in plugin.reports))
    if not args.regressions:
        valid = valid and len(stages) == 2 and len(objects) == 2
        valid = valid and [s['sigma'] for s in stages] == [.01, .1]
        valid = valid and [s['fix_spin'] for s in stages] == [True, False]
        valid = valid and stages[-1]['conv_tol'] == 1e-9
    result = {
        'status': 'Passed' if valid else 'Failed', 'pytest_exit_code': int(code),
        'source_sha': manifest['source_sha'], 'tool_sha': manifest['tool_sha'],
        'wheel_sha256': manifest['wheel_sha256'], 'requested_nodes': nodes,
        'collected': plugin.collected, 'deselected': plugin.deselected,
        'reports': plugin.reports, 'checks': checks, 'stages': stages,
        'environment_before': before, 'environment_after': after,
    }
    write_json(args.output, result)
    return 0 if valid else 1


def sweep(args):
    root = args.root.resolve()
    installation = json.loads((root / 'installation.json').read_text())
    manifest = installation['manifest']
    output = root / 'evidence' / args.label
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(root / 'installation.json', output / 'installation.json')
    records = []
    for attempt in range(1, args.repeats + 1):
        attempt_dir = output / f'{attempt:04d}'
        attempt_dir.mkdir()
        scratch = root / 'scratch' / args.label / f'{attempt:04d}'
        scratch.mkdir(parents=True)
        env = os.environ.copy()
        env.update({key: '4' for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                    'MKL_NUM_THREADS', 'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS',
                    'NUMEXPR_NUM_THREADS')})
        env.update({key: str(scratch) for key in ('TMP', 'TEMP', 'TMPDIR',
                                                'RUNNER_TEMP', 'PYSCF_TMPDIR')})
        env.update(PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1',
                   PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
        for key in ('PYTHONPATH', 'PYSCF_EXT_PATH', 'PYSCF_CONFIG_FILE', 'PYTEST_ADDOPTS'):
            env.pop(key, None)
        command = [installation['python'], '-B', str(Path(__file__).resolve()),
                   'child', '--root', str(root), '--output', str(attempt_dir / 'result.json')]
        if args.regressions:
            command.append('--regressions')
        started = time.time()
        with (attempt_dir / 'pytest.log').open('w', encoding='utf-8') as log:
            process = subprocess.Popen(command, cwd=installation['site'], env=env,
                                       stdout=log, stderr=subprocess.STDOUT)
            write_json(attempt_dir / 'process.json', {
                'pid': process.pid, 'started_unix': started, 'command': command,
                'cwd': installation['site'], 'scratch': str(scratch),
            })
            rc = process.wait()
        result_path = attempt_dir / 'result.json'
        result = json.loads(result_path.read_text()) if result_path.exists() else {}
        record = {'attempt': attempt, 'returncode': rc, 'pid': process.pid,
                  'seconds': time.time() - started,
                  'status': result.get('status', 'Failed') if rc == 0 else 'Failed',
                  'result': str(result_path.relative_to(output)),
                  'log': str((attempt_dir / 'pytest.log').relative_to(output)),
                  'source_sha': manifest['source_sha'], 'tool_sha': manifest['tool_sha'],
                  'wheel_sha256': manifest['wheel_sha256']}
        records.append(record)
        with (output / 'records.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(record) + '\n')
        write_json(output / 'summary.json', {
            'planned': args.repeats, 'executed': len(records),
            'passed': sum(r['status'] == 'Passed' for r in records),
            'failed': sum(r['status'] != 'Passed' for r in records),
            'first_failure': next((r for r in records if r['status'] != 'Passed'), None),
            'source_sha': manifest['source_sha'], 'tool_sha': manifest['tool_sha'],
            'wheel_sha256': manifest['wheel_sha256'], 'label': args.label,
        })
        print(json.dumps(record), flush=True)
        if args.stop_on_failure and record['status'] != 'Passed':
            break
    return 0 if len(records) == args.repeats and all(
        r['status'] == 'Passed' for r in records) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('bundle', 'install', 'child', 'sweep'))
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path)
    parser.add_argument('--label', default='preflight')
    parser.add_argument('--repeats', type=int, default=1)
    parser.add_argument('--regressions', action='store_true')
    parser.add_argument('--stop-on-failure', action='store_true')
    args = parser.parse_args()
    return globals()[args.command](args) or 0


if __name__ == '__main__':
    raise SystemExit(main())
