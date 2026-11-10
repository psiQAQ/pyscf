"""Observe the original H2 test without changing its numerical parameters."""
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np
import pytest

TARGET = 'test_h2_cms3ftlda22_631g'


def json_default(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return str(value)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    if item.name != TARGET:
        yield
        return
    import pyscf
    from pyscf import gto, scf, lib
    from pyscf.mcpdft import mspdft
    from pyscf.dft import libxc
    from threadpoolctl import threadpool_info

    dest = Path(os.environ['CMS_CASE_DIR'])
    tag = f'{os.environ.get("PYTEST_XDIST_WORKER", "main")}-{os.getpid()}'
    output = dest / f'trace-{tag}.json'
    record = dict(pid=os.getpid(), worker=tag, nodeid=item.nodeid,
                  source=pyscf.__file__, python=sys.version,
                  pools_before=threadpool_info(), omp_threads=lib.num_threads(),
                  libxc_version=libxc.__version__, rhf_iterations=[], casscf_iterations=[], cms_iterations=[])
    arrays = {}
    handles = []

    def save():
        output.write_text(json.dumps(record, indent=2, default=json_default))
        np.savez_compressed(dest / f'arrays-{tag}.npz', **arrays)

    def snapshot(prefix, **values):
        for key, value in values.items():
            if value is not None:
                arrays[prefix + '_' + key] = np.array(value, copy=True)
        save()

    original_m = gto.M
    original_scf = scf.hf.SCF.kernel
    original_opt = mspdft._MSPDFT.optimize_mcscf_
    original_dia = mspdft._MSPDFT.diabatize
    original_kernel = mspdft._MSPDFT.kernel

    def molecule(*args, **kwargs):
        kwargs.update(verbose=5, output=str(dest / f'iterations-{tag}.log'))
        mol = original_m(*args, **kwargs)
        handles.append(mol.stdout)
        record['molecule'] = dict(atom=mol.atom, basis=mol.basis, unit=mol.unit,
                                  charge=mol.charge, spin=mol.spin)
        save()
        return mol

    def rhf(self, *args, **kwargs):
        callback = self.callback
        def observe(e):
            record['rhf_iterations'].append({k: e[k] for k in
                ('cycle', 'e_tot', 'norm_gorb', 'norm_ddm') if k in e})
            if len(record['rhf_iterations']) == 1:
                snapshot('rhf_first', **{k: e[k] for k in ('dm', 'mo_coeff', 'mo_energy') if k in e})
            if callable(callback):
                callback(e)
        self.callback = observe
        try:
            ret = original_scf(self, *args, **kwargs)
            record['rhf'] = dict(converged=bool(self.converged), energy=self.e_tot)
            snapshot('rhf_final', mo=self.mo_coeff, energies=self.mo_energy, occupations=self.mo_occ)
            return ret
        finally:
            self.callback = callback

    def optimize(self, *args, **kwargs):
        record['tolerances'] = {k: getattr(self, k, None) for k in
            ('conv_tol', 'conv_tol_sarot', 'conv_tol_diabatize', 'nudge_tol_diabatize', 'max_cyc_diabatize')}
        snapshot('casscf_initial', mo=self.mo_coeff, ci=kwargs.get('ci0'))
        callback = self.callback
        def observe(e):
            record['casscf_iterations'].append({k: e[k] for k in
                ('imacro', 'imicro', 'e_tot', 'de', 'norm_gorb', 'norm_gorb0', 'norm_gci') if k in e})
            save()
            if callable(callback):
                callback(e)
        self.callback = observe
        try:
            ret = original_opt(self, *args, **kwargs)
            record['casscf'] = dict(converged=bool(self.converged), energies=self.e_mcscf)
            snapshot('casscf_final', mo=self.mo_coeff, ci=self.ci)
            return ret
        finally:
            self.callback = callback

    def diabatize(self, *args, **kwargs):
        snapshot('cms_initial', ci=kwargs.get('ci', self.ci))
        objective = self.diabatizer
        def observe_objective(*a, **kw):
            f, g, h, update = objective(*a, **kw)
            record['cms_iterations'].append(dict(objective=f, gradient=np.array(g), hessian=np.array(h)))
            save()
            def observe_update(u):
                values = update(u)
                record['cms_iterations'].append(dict(objective=values[0], gradient=np.array(values[1]),
                                                     hessian=np.array(values[2]), rotation=np.array(u)))
                save()
                return values
            return f, g, h, observe_update
        with patch.object(self, 'diabatizer', observe_objective):
            conv, ci = original_dia(self, *args, **kwargs)
        record['cms'] = dict(converged=bool(conv))
        snapshot('cms_final', ci=ci)
        return conv, ci

    def kernel(self, *args, **kwargs):
        ret = original_kernel(self, *args, **kwargs)
        errors = np.asarray(self.e_states) - [-1.08553117, -0.69136123, -0.49602992]
        record['final'] = dict(energies=np.array(self.e_states), errors=errors,
                               converged=bool(self.converged))
        snapshot('final', mo=self.mo_coeff, ci=self.ci, heff_mcscf=self.heff_mcscf,
                 hdiag_pdft=self.hdiag_pdft, si_pdft=self.si_pdft)
        if (dest.name == 'isolated-000' or not self.converged
                or any(round(float(e), 4) != 0 for e in errors)):
            np.savez_compressed(dest / f'grid-{tag}.npz', coords=self.grids.coords, weights=self.grids.weights)
        return ret

    save()
    with patch.object(gto, 'M', molecule), patch.object(scf.hf.SCF, 'kernel', rhf), \
         patch.object(mspdft._MSPDFT, 'optimize_mcscf_', optimize), \
         patch.object(mspdft._MSPDFT, 'diabatize', diabatize), \
         patch.object(mspdft._MSPDFT, 'kernel', kernel):
        outcome = yield
    record['pytest_exception'] = str(outcome.excinfo) if outcome.excinfo else None
    record['pools_after'] = threadpool_info()
    record['libraries'] = sorted({line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines()
                                  if '.so' in line and '/' in line})
    save()
    for handle in handles:
        handle.flush()
        handle.close()
