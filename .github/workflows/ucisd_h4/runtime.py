"""Record the actual H4 process environment after its test call has finished."""
import pytest


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if call.when != 'call' or not item.nodeid.endswith('test_ucisd.py::KnownValues::test_h4'):
        return report
    import ctypes
    import importlib.metadata
    import json
    import os
    from pathlib import Path
    import sys

    import psutil
    import pyscf
    from pyscf import lib

    libraries = sorted({m.path for m in psutil.Process().memory_maps()
                        if m.path.lower().endswith(('.dll', '.pyd', '.so'))
                        or '.so.' in m.path})
    blas = []
    for path in libraries:
        if 'openblas' not in path.lower():
            continue
        library = ctypes.CDLL(path)
        for prefix in ('openblas_', 'scipy_openblas_'):
            for suffix in ('', '64_', '_64_'):
                symbol = prefix + 'get_num_threads' + suffix
                if hasattr(library, symbol):
                    fn = getattr(library, symbol)
                    fn.restype, fn.argtypes = ctypes.c_int, []
                    blas.append({'path': path, 'symbol': symbol, 'threads': fn()})
    result = {'nodeid': item.nodeid, 'outcome': report.outcome,
              'recorded_after_test_call': True, 'pid': os.getpid(),
              'python': sys.version, 'executable': sys.executable,
              'pyscf': str(Path(pyscf.__file__).resolve()),
              'openmp_threads': lib.num_threads(), 'blas': blas, 'libraries': libraries,
              'versions': {n: importlib.metadata.version(n) for n in
                           ('numpy', 'scipy', 'h5py', 'pytest', 'pytest-xdist')},
              'environment': {n: os.environ.get(n) for n in
                              ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'RUNNER_TEMP',
                               'TMP', 'TEMP', 'PYSCF_TMPDIR')}}
    out = Path(os.environ['UCISD_REPORT']) / 'runtime'
    out.mkdir(exist_ok=True)
    (out / (os.environ.get('PYTEST_XDIST_WORKER', 'serial') + '.json')).write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return report
