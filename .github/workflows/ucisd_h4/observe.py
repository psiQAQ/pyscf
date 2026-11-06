"""Read-only observations of the original UCISD H4 test; investigation only."""
import ctypes
import functools
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys

import pytest


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    if not item.nodeid.endswith('test_ucisd.py::KnownValues::test_h4'):
        return (yield)
    import numpy as np
    import scipy.linalg
    import pyscf
    from pyscf import ci, lib
    from pyscf.ci import ucisd

    out = Path(os.environ['UCISD_REPORT']) / 'trace' / os.environ.get('PYTEST_XDIST_WORKER', 'serial')
    out.mkdir(parents=True, exist_ok=False)
    if sys.platform == 'win32':
        import psutil
        libraries = sorted({m.path for m in psutil.Process().memory_maps()
                            if m.path.lower().endswith(('.dll', '.pyd'))})
    else:
        libraries = sorted({line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines()
                            if '.so' in line and '/' in line})
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
                    fn.restype = ctypes.c_int
                    fn.argtypes = []
                    blas.append({'path': path, 'symbol': symbol, 'threads': fn()})
    package = Path(pyscf.__file__).resolve().parent
    env = {'pid': os.getpid(), 'nodeid': item.nodeid, 'python': sys.version,
           'executable': sys.executable, 'pyscf': pyscf.__file__,
           'openmp_threads': lib.num_threads(), 'blas': blas, 'libraries': libraries,
           'einsum_backend': lib.numpy_helper.EINSUM_BACKEND,
           'versions': {n: importlib.metadata.version(n) for n in
                        ('numpy', 'scipy', 'h5py', 'pytest', 'pytest-xdist')},
           'environment': {n: os.environ.get(n) for n in
                           ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'RUNNER_TEMP',
                            'TMP', 'TEMP', 'PYSCF_TMPDIR')},
           'source_sha256': {n: hashlib.sha256((package / n).read_bytes()).hexdigest()
                             for n in ('ci/ucisd.py', 'ci/cisd.py', 'ci/test/test_ucisd.py',
                                       'cc/uccsd.py', 'scf/hf.py', 'lib/linalg_helper.py')}}
    (out / 'environment.json').write_text(json.dumps(env, indent=2) + '\n', encoding='utf-8')
    sequence = 0

    def record(stage, **values):
        nonlocal sequence
        sequence += 1
        arrays, summaries = {}, {}

        def inspect(name, value):
            if value is None or isinstance(value, (str, bool, int)):
                summaries[name] = value
            elif isinstance(value, (tuple, list)):
                for i, v in enumerate(value):
                    inspect(f'{name}.{i}', v)
            elif isinstance(value, np.ndarray) or np.isscalar(value):
                a = np.asarray(value)
                if a.dtype.kind in 'biufc':
                    arrays[name] = a
                    finite = bool(np.isfinite(a).all())
                    summaries[name] = {'shape': a.shape, 'dtype': str(a.dtype), 'finite': finite,
                                       'norm': float(np.linalg.norm(a)) if finite else None}
            elif hasattr(value, '__dict__'):
                for key, v in vars(value).items():
                    if isinstance(v, (np.ndarray, tuple, list, float, complex)):
                        inspect(f'{name}.{key}', v)

        for name, value in values.items():
            inspect(name, value)
        np.savez(out / f'{sequence:04d}-{stage}.npz', **arrays)
        with (out / 'trace.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'sequence': sequence, 'stage': stage, 'values': summaries}) + '\n')

    with pytest.MonkeyPatch.context() as patch:
        factory = ci.CISD

        @functools.wraps(factory)
        def traced_factory(mf, *a, **kw):
            record('scf', cls=type(mf).__name__, converged=mf.converged, energy=mf.e_tot,
                   mo_coeff=mf.mo_coeff, mo_energy=mf.mo_energy, mo_occ=mf.mo_occ,
                   nelec=mf.mol.nelec)
            result = factory(mf, *a, **kw)
            record('converted', cls=type(result._scf).__name__, mo_coeff=result.mo_coeff,
                   mo_energy=result._scf.mo_energy, mo_occ=result.mo_occ)
            return result

        patch.setattr(ci, 'CISD', traced_factory)

        def wrap_method(name):
            original = getattr(ucisd.UCISD, name)

            @functools.wraps(original)
            def wrapped(self, *a, **kw):
                if name == 'contract':
                    record('contract-input', vector=a[0])
                result = original(self, *a, **kw)
                record(name, result=result)
                return result

            patch.setattr(ucisd.UCISD, name, wrapped)

        for name in ('ao2mo', 'make_diagonal', 'get_init_guess', 'contract'):
            wrap_method(name)
        original_eigh = scipy.linalg.eigh

        @functools.wraps(original_eigh)
        def traced_eigh(a, *rest, **kw):
            if sys._getframe(1).f_code.co_name == 'davidson1':
                record('davidson-heff', heff=a)
            return original_eigh(a, *rest, **kw)

        patch.setattr(scipy.linalg, 'eigh', traced_eigh)
        return (yield)
