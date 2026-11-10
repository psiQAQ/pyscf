"""Run the unchanged DiamondPBE0 tests and record TD roots for diagnosis."""
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import sys
import unittest

import numpy as np
import pyscf
from pyscf.pbc.tdscf.test import test_uks


def emit(td, method, reference, failure=None):
    record = {
        'sample': os.environ['DIAGNOSTIC_SAMPLE'],
        'source': os.environ['DIAGNOSTIC_SOURCE'],
        'method': method,
        'reference_ev': np.asarray(reference).tolist(),
        'failure': failure,
        'pid': os.getpid(),
    }
    if td is not None:
        record.update(
            energies_ev=(td.e * test_uks.unitev).tolist(),
            converged=np.asarray(td.converged).tolist(),
            nstates=td.nstates,
            conv_tol=td.conv_tol,
            max_cycle=td.max_cycle,
            scf_converged=bool(td._scf.converged),
            scf_energy=float(td._scf.e_tot),
        )
        if failure and method == 'TDDFT':
            try:
                a, b = td.get_ab()
                record['dense_roots_ev'] = (
                    test_uks.diagonalize(a, b, nroots=8) * test_uks.unitev
                ).tolist()
            except Exception as error:
                record['dense_diagnostic_error'] = repr(error)
    print('UKS_DIAGNOSTIC ' + json.dumps(record), flush=True)


original_kernel = test_uks.DiamondPBE0.kernel


def recorded_kernel(self, method, reference, **kwargs):
    try:
        td = original_kernel(self, method, reference, **kwargs)
    except Exception as error:
        traceback = error.__traceback__
        td = None
        while traceback is not None:
            if traceback.tb_frame.f_code is original_kernel.__code__:
                td = traceback.tb_frame.f_locals.get('td')
            traceback = traceback.tb_next
        emit(td, method, reference, repr(error))
        raise
    emit(td, method, reference)
    return td


source = Path.cwd().resolve()
assert Path(pyscf.__file__).resolve().is_relative_to(source / 'pyscf')
print('UKS_ENVIRONMENT ' + json.dumps({
    'python': sys.version,
    'source': os.environ['DIAGNOSTIC_SOURCE'],
    'packages': {name: metadata.version(name) for name in
                 ('numpy', 'scipy', 'h5py', 'pytest', 'pytest-xdist')},
    'threads': {name: os.environ.get(name) for name in
                ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                 'BLIS_NUM_THREADS', 'OMP_WAIT_POLICY', 'OPENBLAS_THREAD_TIMEOUT')},
}), flush=True)
test_uks.DiamondPBE0.kernel = recorded_kernel
suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_uks.DiamondPBE0)
result = unittest.TextTestRunner(verbosity=2).run(suite)
print('UKS_RESULT ' + json.dumps({
    'sample': os.environ['DIAGNOSTIC_SAMPLE'],
    'tests': result.testsRun,
    'failures': len(result.failures),
    'errors': len(result.errors),
}), flush=True)
sys.exit(0 if result.wasSuccessful() else 1)
