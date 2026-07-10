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


def hash_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def native_libraries(root):
    libdir = root / 'pyscf' / 'lib'
    linker = 'otool' if platform.system() == 'Darwin' else 'ldd'
    libraries = []
    for path in sorted(libdir.glob('*')):
        if path.is_file() and path.suffix.lower() in ('.dll', '.dylib', '.so'):
            details = {
                'path': str(path.relative_to(root)),
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


def main(output_path):
    root = Path.cwd()
    import h5py
    import numpy
    import pyscf
    import scipy

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
        'numpy_config': capture_show_config(numpy),
        'scipy_config': capture_show_config(scipy),
        'h5py_version_info': h5py.version.info,
        'tools': {' '.join(command): run_command(command) for command in TOOL_COMMANDS},
        'native_libraries': native_libraries(root),
    }
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


if __name__ == '__main__':
    main(Path(sys.argv[1]))
