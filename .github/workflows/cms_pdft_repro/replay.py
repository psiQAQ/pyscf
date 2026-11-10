"""Replay observed CMS inputs, comparing current and intended nudge defaults."""
import importlib.util
import json
import os
from pathlib import Path
import sys

import numpy as np
from pyscf import gto, scf, mcpdft
from threadpoolctl import threadpool_info

source = Path(os.environ['CMS_SOURCE'])
out = Path(os.environ['CMS_OUT'])
prior = source.parent / 'prior-evidence'
out.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('original_test', source / 'pyscf/mcpdft/test/test_diatomic_energies.py')
original_test = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original_test)
rows = json.loads((prior / 'summary.json').read_text())
selected = [r for r in rows if r['label'] == 'isolated-000'
            or (r['label'].startswith('isolated-') and not r['passed'])]
result = dict(pid=os.getpid(), source=str(source), python=sys.version,
              pools=threadpool_info(), cases=[])
for row in selected:
    case = prior / row['label']
    trace = json.loads(next(case.glob('trace-*.json')).read_text())
    with np.load(next(case.glob('arrays-*.npz'))) as data:
        mo = data['casscf_final_mo'].copy()
        initial_ci = data['cms_initial_ci'].copy()
    for nudge in ((None,) if os.environ.get('CMS_REPLAY_FIXED') == '1' else (None, 1e-3)):
        label = f"{row['label']}-{'default' if nudge is None else 'nudge-1e-3'}"
        mol = gto.M(atom='H 0 0 0; H 1.3 0 0', basis='6-31G',
                    verbose=5, output=str(out / (label + '.log')))
        mf = scf.RHF(mol)
        # RHF caches these integrals in the original test. Preserve the same
        # in-core AO2MO route rather than recomputing through the Mole route.
        mf._eri = mol.intor('int2e', aosym='s8')
        mc = mcpdft.CASSCF(mf, 'ftLDA,VWN3', 2, 2, grids_attr=original_test.my_grids)
        mc = mc.multi_state([1/3] * 3, 'cms')
        mc.fix_spin_(ss=0, shift=1)
        mc.mo_coeff = mo.copy()
        mc.ci = list(initial_ci.copy())
        f0, g0, h0 = mc.diabatizer()[:3]
        kwargs = {} if nudge is None else dict(nudge_tol=nudge)
        converged, mc.ci = mc.diabatize(ci=mc.ci, **kwargs)
        f1, g1, h1 = mc.diabatizer()[:3]
        mc.heff_mcscf = mc.make_heff_mcscf()
        mc.hdiag_pdft = mc.compute_pdft_energy_(dump_chk=False)[-1]
        energies = mc._eig_si(mc.get_heff_pdft())[0]
        entry = dict(label=label, nudge=mc.nudge_tol_diabatize if nudge is None else nudge,
                     converged=bool(converged), initial_objective=f0, final_objective=f1,
                     initial_objective_error=f0-trace['cms_iterations'][0]['objective'],
                     initial_gradient_error=float(np.max(np.abs(g0-trace['cms_iterations'][0]['gradient']))),
                     initial_hessian_error=float(np.max(np.abs(h0-trace['cms_iterations'][0]['hessian']))),
                     gradient_norm=float(np.linalg.norm(g1)),
                     hessian_eigenvalues=np.linalg.eigvalsh(h1).tolist(),
                     energies=energies.tolist(),
                     errors=(energies-[-1.08553117, -.69136123, -.49602992]).tolist())
        result['cases'].append(entry)
        result['pools'] = threadpool_info()
        (out / 'replay.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(entry), flush=True)
        mol.stdout.close()
if os.environ.get('CMS_REPLAY_FIXED') == '1':
    assert len(result['cases']) == len(selected)
    assert all(c['converged'] and all(round(e, 4) == 0 for e in c['errors'])
               for c in result['cases']), 'Fixed-source replay did not satisfy original criteria'
