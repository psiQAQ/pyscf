#!/usr/bin/env python
"""Collect reproducibility metadata for precision-test artifacts."""

import contextlib
import hashlib
import importlib
import io
import json
import os
import platform
import subprocess
import sys
import sysconfig
from importlib import metadata
from pathlib import Path


CI_KEYS = ('RUNNER_OS', 'RUNNER_ARCH', 'ImageOS', 'ImageVersion', 'OMP_NUM_THREADS',
           'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS',
           'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS', 'PYSCF_EXT_PATH')
TOOL_COMMANDS = (('cmake', '--version'), ('cc', '--version'), ('c++', '--version'),
                 ('clang', '--version'), ('gcc', '--version'), ('make', '--version'),
                 ('ldd', '--version'), ('sw_vers',), ('sysctl', '-n', 'machdep.cpu.brand_string'))


def run_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=30, check=False)
        return {'returncode': result.returncode, 'output': result.stdout}
    except (OSError, subprocess.TimeoutExpired) as err:
        return {'error': str(err)}


def capture_show_config(module):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            module.show_config()
        except Exception as err:
            return {'error': str(err)}
    return {'output': output.getvalue()}


def module_details(name):
    try:
        module = importlib.import_module(name)
        return {'version': getattr(module, '__version__', None), 'path': getattr(module, '__file__', None)}
    except Exception as err:
        return {'error': str(err)}


def optional_module(name):
    try:
        return importlib.import_module(name), None
    except Exception as err:
        return None, str(err)


def hash_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def native_libraries(pyscf_module):
    module_path = getattr(pyscf_module, '__file__', None)
    if not module_path:
        return []
    libdir = Path(module_path).resolve().parent / 'lib'
    linker = 'otool' if platform.system() == 'Darwin' else 'ldd'
    libraries = []
    for path in sorted(libdir.glob('*')):
        if path.is_file() and path.suffix.lower() in ('.dll', '.dylib', '.so'):
            details = {
                'path': str(path),
                'size': path.stat().st_size,
                'sha256': hash_file(path),
                'linkage': run_command((linker, str(path))),
            }
            libraries.append(details)
    return libraries


def package_versions():
    packages = []
    for distribution in metadata.distributions():
        name = distribution.metadata.get('Name')
        if name:
            packages.append({'name': name, 'version': distribution.version})
    return sorted(packages, key=lambda item: item['name'].lower())


def write_command_output(path, command):
    result = run_command(command)
    output = result.get('output', result.get('error', ''))
    path.write_text(output, encoding='utf-8')


def main(output_path):
    numpy, numpy_error = optional_module('numpy')
    scipy, scipy_error = optional_module('scipy')
    h5py, h5py_error = optional_module('h5py')
    pyscf, pyscf_error = optional_module('pyscf')

    result = {
        'schema_version': 1,
        'git_commit': run_command(('git', 'rev-parse', 'HEAD')),
        'python': {
            'version': sys.version,
            'executable': sys.executable,
            'implementation': platform.python_implementation(),
            'prefix': sys.prefix,
            'config': {key: sysconfig.get_config_var(key) for key in
                       ('CC', 'CXX', 'SOABI', 'EXT_SUFFIX', 'CONFIG_ARGS')},
        },
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': os.cpu_count(),
            'uname': list(platform.uname()),
        },
        'environment': {key: os.environ.get(key) for key in CI_KEYS},
        'packages': package_versions(),
        'key_modules': {name: module_details(name) for name in ('numpy', 'scipy', 'h5py', 'pyscf')},
        'numpy_config': capture_show_config(numpy) if numpy else {'error': numpy_error},
        'scipy_config': capture_show_config(scipy) if scipy else {'error': scipy_error},
        'h5py_version_info': h5py.version.info if h5py else {'error': h5py_error},
        'tools': {' '.join(command): run_command(command) for command in TOOL_COMMANDS},
        'native_libraries': native_libraries(pyscf) if pyscf else [],
    }
    if not pyscf:
        result['pyscf_import_error'] = pyscf_error
        result['libxc_version_error'] = pyscf_error
        result['xcfun_version_error'] = pyscf_error
    else:
        try:
            from pyscf.dft import libxc
            result['libxc_version'] = libxc.libxc_version()
        except Exception as err:
            result['libxc_version_error'] = str(err)
        try:
            from pyscf.dft import xcfun
            result['xcfun_version'] = xcfun.__version__
        except Exception as err:
            result['xcfun_version_error'] = str(err)
    try:
        from threadpoolctl import threadpool_info
        result['threadpools'] = threadpool_info()
    except Exception as err:
        result['threadpools_error'] = str(err)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_snapshot(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    main(output_dir / 'runtime.json')
    write_command_output(output_dir / 'pip-freeze.txt', (sys.executable, '-m', 'pip', 'freeze', '--all'))
    write_command_output(output_dir / 'pip-list.json', (sys.executable, '-m', 'pip', 'list', '--format=json'))
    write_command_output(output_dir / 'pip-check.txt', (sys.executable, '-m', 'pip', 'check'))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--snapshot-dir':
        write_snapshot(Path(sys.argv[2]))
    elif len(sys.argv) == 2:
        main(Path(sys.argv[1]))
    else:
        raise SystemExit('Usage: collect_precision_environment.py [--snapshot-dir] PATH')
