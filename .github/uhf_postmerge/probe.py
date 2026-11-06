"""Read loaded native-library state without changing thread limits or SCF hooks."""

import ctypes
import hashlib
import importlib.metadata
import os
import platform
import sys
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def loaded_libraries():
    if os.name == 'nt':
        import psutil  # Existing Windows runtime dependency.
        paths = {m.path for m in psutil.Process().memory_maps()}
    else:
        paths = {line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines()
                 if '/' in line}
    return sorted(p for p in paths if Path(p).is_file())


def native_threads():
    pools = []
    for path in loaded_libraries():
        name = Path(path).name.lower()
        if not ('openblas' in name or name.startswith(
                ('libblas.', 'libgomp', 'libomp', 'libiomp', 'mkl_rt', 'libmkl_rt'))):
            continue
        dll = ctypes.CDLL(path)
        entry = {'path': path, 'sha256': sha256(path)}
        if 'openblas' in name:
            for prefix in ('', 'scipy_'):
                for suffix in ('', '64_', '_64_'):
                    symbol = prefix + 'openblas_get_num_threads' + suffix
                    if hasattr(dll, symbol):
                        fn = getattr(dll, symbol)
                        fn.restype = ctypes.c_int
                        entry.update(api='openblas', symbol=symbol, num_threads=fn())
                        for key, restype in (('get_config', ctypes.c_char_p),
                                             ('get_corename', ctypes.c_char_p),
                                             ('get_parallel', ctypes.c_int)):
                            extra = getattr(dll, prefix + 'openblas_' + key + suffix, None)
                            if extra is not None:
                                extra.restype = restype
                                value = extra()
                                entry[key] = value.decode() if isinstance(value, bytes) else value
                        break
                if 'num_threads' in entry:
                    break
        elif hasattr(dll, 'omp_get_max_threads'):
            fn = dll.omp_get_max_threads
            fn.restype = ctypes.c_int
            entry.update(api='openmp', symbol='omp_get_max_threads', num_threads=fn())
        elif hasattr(dll, 'MKL_Get_Max_Threads'):
            fn = dll.MKL_Get_Max_Threads
            fn.restype = ctypes.c_int
            entry.update(api='mkl', symbol='MKL_Get_Max_Threads', num_threads=fn())
        elif name.startswith(('libblas.so', 'liblapack.so')):
            # Ubuntu's reference BLAS has no threading API. Its actual resolved
            # path identifies the serial implementation; OpenBLAS is handled above.
            if '/blas/' in path or '/lapack/' in path:
                entry.update(api='reference-blas', num_threads=1,
                             evidence='resolved reference BLAS path; serial implementation')
        if 'num_threads' not in entry:
            raise RuntimeError('Cannot identify actual thread count: ' + path)
        pools.append(entry)
    if not pools or not any(p['api'] == 'openmp' for p in pools):
        raise RuntimeError('Native OpenMP/BLAS thread metadata is incomplete')
    return pools


def environment():
    import numpy
    import scipy
    import h5py
    import pyscf
    from pyscf import lib
    from pyscf.dft import libxc, xcfun

    keys = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS',
            'RUNNER_OS', 'RUNNER_ARCH', 'RUNNER_NAME', 'ImageOS', 'ImageVersion',
            'RUNNER_TEMP', 'TMP', 'TEMP', 'PYSCF_TMPDIR', 'GITHUB_RUN_ID',
            'GITHUB_RUN_ATTEMPT', 'GITHUB_SHA')
    return {
        'python': sys.version, 'executable': sys.executable, 'prefix': sys.prefix,
        'platform': platform.platform(), 'machine': platform.machine(),
        'cpu_count': os.cpu_count(), 'pid': os.getpid(), 'cwd': os.getcwd(),
        'sys_path': sys.path, 'environment': {k: os.environ.get(k) for k in keys},
        'modules': {m.__name__: {'version': m.__version__, 'path': m.__file__}
                    for m in (numpy, scipy, h5py, pyscf)},
        'packages': sorted((d.metadata['Name'], d.version)
                           for d in importlib.metadata.distributions()),
        'libxc_version': libxc.libxc_version(), 'xcfun_version': xcfun.__version__,
        'pyscf_openmp_threads': lib.num_threads(), 'native_pools': native_threads(),
    }
