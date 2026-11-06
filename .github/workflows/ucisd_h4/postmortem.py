"""Save the original H4 exception's live arrays after calculation has failed."""
import pytest


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # unittest's report hook first transfers its exception into call.excinfo.
    report = yield
    if (call.when == 'call' and report.failed and call.excinfo is not None
            and item.nodeid.endswith('test_ucisd.py::KnownValues::test_h4')):
        import os
        from pathlib import Path
        import traceback

        out = Path(os.environ['UCISD_FAILURE_DIR'])
        try:
            save_failure(call.excinfo, out, item.nodeid)
        except Exception:
            # Keep the original test failure and separately expose capture errors.
            out.mkdir(parents=True, exist_ok=True)
            error = traceback.format_exc()
            (out / 'capture-error.txt').write_text(error, encoding='utf-8')
            print(error)
    return report


def save_failure(excinfo, out, nodeid):
    # Imports, array reads and allocations below occur only after an exception.
    import ctypes
    import importlib.metadata
    import json
    import os
    from pathlib import Path
    import sys
    import traceback

    import numpy as np
    import psutil
    import pyscf
    from pyscf import lib

    out.mkdir(parents=True, exist_ok=False)
    (out / 'exception.txt').write_text(
        ''.join(traceback.format_exception(excinfo.type, excinfo.value, excinfo.tb)),
        encoding='utf-8')
    arrays, values, frames = {}, {}, []

    def save(name, value, depth=0):
        if isinstance(value, (np.ndarray, np.generic, float, complex)):
            a = np.asarray(value)
            if a.dtype.kind in 'biufc':
                arrays[name] = a.copy()
                finite = np.isfinite(a)
                values[name] = {'shape': list(a.shape), 'dtype': str(a.dtype),
                                'finite': bool(finite.all()),
                                'nonfinite_count': int(a.size - finite.sum()),
                                'norm': float(np.linalg.norm(a)) if finite.all() else None}
        elif value is None or isinstance(value, (bool, int)):
            values[name] = value
        elif isinstance(value, (tuple, list)):
            for i, child in enumerate(value):
                save(f'{name}.{i}', child, depth)
        elif depth < 2 and type(value).__module__.startswith('pyscf.'):
            values[name] = {'object_type': type(value).__module__ + '.' + type(value).__qualname__}
            for key, child in vars(value).items():
                if key == '_scf' or isinstance(child, (np.ndarray, np.generic, float,
                                                      complex, bool, int, tuple, list)):
                    save(f'{name}.{key}', child, depth + 1)

    selected = {
        'test_h4': ('mf', 'myci', 'eris', 'ci0', 'ecisd'),
        'cisd': ('self', 'eris', 'ci0'),
        'kernel': ('myci', 'eris', 'ci0', 'diag', 'ehf'),
        'davidson1': ('xs', 'ax', 'x0', 'xt', 'axt', 'icyc', 'space', 'head', 'rnow'),
        'eigh': ('a',),
        '_asarray_validated': ('a',),
        'asarray_chkfinite': ('a',),
    }
    tb = excinfo.tb
    while tb is not None:
        frame = tb.tb_frame
        function = frame.f_code.co_name
        prefix = f'{len(frames):02d}-{function}'
        frames.append({'prefix': prefix, 'function': function,
                       'file': frame.f_code.co_filename, 'line': tb.tb_lineno})
        for key in selected.get(function, ()):
            if key in frame.f_locals:
                save(f'{prefix}.{key}', frame.f_locals[key])
        if function == 'davidson1' and frame.f_locals.get('heff') is not None:
            # Unused storage in the larger allocation is not a numerical result.
            space = frame.f_locals['space']
            save(f'{prefix}.heff_active', frame.f_locals['heff'][:space, :space])
        tb = tb.tb_next
    np.savez(out / 'arrays.npz', **arrays)
    (out / 'frames.json').write_text(json.dumps({'nodeid': nodeid,
        'exception': {'type': excinfo.typename, 'message': str(excinfo.value)},
        'frames': frames, 'values': values}, indent=2) + '\n', encoding='utf-8')

    libraries = sorted({m.path for m in psutil.Process().memory_maps()
                        if m.path.lower().endswith(('.dll', '.pyd'))})
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
    environment = {'pid': os.getpid(), 'python': sys.version,
        'executable': sys.executable, 'pyscf': str(Path(pyscf.__file__).resolve()),
        'openmp_threads': lib.num_threads(), 'blas': blas, 'libraries': libraries,
        'versions': {n: importlib.metadata.version(n) for n in
                     ('numpy', 'scipy', 'h5py', 'pytest', 'pytest-xdist')},
        'environment': {n: os.environ.get(n) for n in ('OMP_NUM_THREADS',
            'OPENBLAS_NUM_THREADS', 'RUNNER_TEMP', 'TMP', 'TEMP', 'PYSCF_TMPDIR')}}
    (out / 'environment.json').write_text(json.dumps(environment, indent=2) + '\n',
                                         encoding='utf-8')
