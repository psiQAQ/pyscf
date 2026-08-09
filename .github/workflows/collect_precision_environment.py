#!/usr/bin/env python
"""Collect reproducibility metadata for precision-test artifacts."""

import argparse
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


CI_KEYS = (
    'RUNNER_OS', 'RUNNER_ARCH', 'ImageOS', 'ImageVersion', 'OMP_NUM_THREADS',
    'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS',
    'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS', 'PYSCF_EXT_PATH',
    'PRECISION_TESTED_SHA',
)
TOOL_COMMANDS = (
    ('cmake', '--version'), ('cc', '--version'), ('c++', '--version'),
    ('clang', '--version'), ('gcc', '--version'), ('make', '--version'),
    ('ldd', '--version'), ('sw_vers',),
)
ENVIRONMENT_MODES = ('source-tree', 'installed-wheel')


def run_command(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
            check=False,
        )
        return {'returncode': result.returncode, 'output': result.stdout}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'error': str(error)}


def capture_show_config(module):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            module.show_config()
        except Exception as error:
            return {'error': str(error)}
    return {'output': output.getvalue()}


def optional_module(name):
    try:
        return importlib.import_module(name), None
    except Exception as error:
        return None, str(error)


def module_details(name):
    module, error = optional_module(name)
    if module is None:
        return {'error': error}
    return {
        'version': getattr(module, '__version__', None),
        'path': getattr(module, '__file__', None),
    }


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
            libraries.append({
                'path': str(path),
                'size': path.stat().st_size,
                'sha256': hash_file(path),
                'linkage': run_command((linker, str(path))),
            })
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
    path.write_text(result.get('output', result.get('error', '')), encoding='utf-8')


def collect(output_path, pip_check=None):
    numpy, numpy_error = optional_module('numpy')
    scipy, scipy_error = optional_module('scipy')
    h5py, h5py_error = optional_module('h5py')
    pyscf, pyscf_error = optional_module('pyscf')
    result = {
        'schema_version': 2 if pip_check is not None else 1,
        'git_commit': run_command(('git', 'rev-parse', 'HEAD')),
        'python': {
            'version': sys.version,
            'executable': sys.executable,
            'implementation': platform.python_implementation(),
            'prefix': sys.prefix,
            'config': {
                key: sysconfig.get_config_var(key)
                for key in ('CC', 'CXX', 'SOABI', 'EXT_SUFFIX', 'CONFIG_ARGS')
            },
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
        'key_modules': {
            name: module_details(name) for name in ('numpy', 'scipy', 'h5py', 'pyscf')
        },
        'numpy_config': capture_show_config(numpy) if numpy else {'error': numpy_error},
        'scipy_config': capture_show_config(scipy) if scipy else {'error': scipy_error},
        'h5py_version_info': h5py.version.info if h5py else {'error': h5py_error},
        'tools': {' '.join(command): run_command(command) for command in TOOL_COMMANDS},
        'native_libraries': native_libraries(pyscf) if pyscf else [],
    }
    if pip_check is not None:
        result['pip_check'] = pip_check
    if not pyscf:
        result['pyscf_import_error'] = pyscf_error
    else:
        for name in ('libxc', 'xcfun'):
            try:
                module = importlib.import_module(f'pyscf.dft.{name}')
                value = module.libxc_version() if name == 'libxc' else module.__version__
                result[f'{name}_version'] = value
            except Exception as error:
                result[f'{name}_version_error'] = str(error)
    try:
        from threadpoolctl import threadpool_info
        result['threadpools'] = threadpool_info()
    except Exception as error:
        result['threadpools_error'] = str(error)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )


def write_snapshot(output_dir, mode):
    output_dir.mkdir(parents=True, exist_ok=True)
    pip_check_command = (sys.executable, '-m', 'pip', 'check')
    pip_check_result = run_command(pip_check_command)
    (output_dir / 'pip-check.txt').write_text(
        pip_check_result.get('output', pip_check_result.get('error', '')),
        encoding='utf-8',
    )
    collect(output_dir / 'runtime.json', pip_check={
        'mode': mode,
        'command': list(pip_check_command),
        'returncode': pip_check_result.get('returncode'),
        'error': pip_check_result.get('error'),
        'output_file': 'pip-check.txt',
    })
    write_command_output(
        output_dir / 'pip-freeze.txt',
        (sys.executable, '-m', 'pip', 'freeze', '--all'),
    )
    write_command_output(
        output_dir / 'pip-list.json',
        (sys.executable, '-m', 'pip', 'list', '--format=json'),
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot-dir', action='store_true')
    parser.add_argument('--mode', choices=ENVIRONMENT_MODES)
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    if args.snapshot_dir and args.mode is None:
        parser.error('--mode is required with --snapshot-dir')
    if not args.snapshot_dir and args.mode is not None:
        parser.error('--mode requires --snapshot-dir')
    return args


if __name__ == '__main__':
    args = parse_args()
    if args.snapshot_dir:
        write_snapshot(args.path, args.mode)
    else:
        collect(args.path)
