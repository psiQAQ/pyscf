#!/usr/bin/env python
"""Focused, non-blocking diagnostics for the precision-triage workflow."""

import argparse
import contextlib
import copy
import csv
import hashlib
import json
import os
import re
import shutil
import time
import traceback
from collections import Counter
from pathlib import Path


EOM_REFERENCE = {
    'ip': (0.4358615224789573, 0.4358615224789594),
    'ea': (0.1894169322207168, 0.1894169322207168, 0.2820757599337823),
}

NODEIDS = {
    'eom:ip': 'pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_ipccsd',
    'eom:ea': 'pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_eaccsd',
    'pbc-tdhf': 'pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_tdhf',
    'pbc-hse06': 'pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda',
    'pbc-hse03': 'pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_hse03_tda',
    'ucasscf': 'pyscf/mcscf/test/test_umc1step.py::KnownValues::test_ucasscf',
    'sa4-newton': 'pyscf/mcscf/test/test_h2o.py::KnownValues::test_nosymm_sa4_newton',
    'sgx': 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad',
    'tddft': 'pyscf/tdscf/test/test_tduks.py::KnownValues::test_tddft_camb3lyp',
    'analyze': 'pyscf/tdscf/test/test_tduks.py::KnownValues::test_analyze',
}


def base_experiment(experiment):
    return 'sgx' if experiment.startswith('sgx-') else experiment


def nodeid_for(experiment, mode):
    experiment = base_experiment(experiment)
    return NODEIDS.get(f'{experiment}:{mode}', NODEIDS.get(experiment))


def nodeid_complete(records, nodeid):
    statuses = {
        record['status'] for record in records
        if record['nodeid'] == nodeid and record['attempt'] > 0
    }
    return 'pass' in statuses and any(status != 'pass' for status in statuses)


def experiment_complete(recorder):
    experiment = base_experiment(recorder.experiment)
    prefix = f'{experiment}:'
    nodeids = {
        nodeid for name, nodeid in NODEIDS.items()
        if name == experiment or name.startswith(prefix)
    }
    return all(nodeid_complete(recorder.records, nodeid) for nodeid in nodeids)


def json_value(value):
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, 'tolist'):
        return json_value(value.tolist())
    if hasattr(value, 'item'):
        return json_value(value.item())
    if isinstance(value, complex):
        return {'real': value.real, 'imag': value.imag}
    return value


def flatten(value):
    if isinstance(value, (list, tuple)):
        arrays = [flatten(item) for item in value]
        return __import__('numpy').concatenate(arrays) if arrays else __import__('numpy').array(())
    return __import__('numpy').asarray(value).ravel()


def fingerprint(value):
    from pyscf import lib
    return json_value(lib.fp(__import__('numpy').asarray(value)))


def array_metadata(value):
    import numpy
    array = numpy.ascontiguousarray(value)
    finite = numpy.isfinite(array)
    return {
        'shape': array.shape,
        'dtype': str(array.dtype),
        'finite': bool(finite.all()),
        'min': json_value(array[finite].min()) if finite.any() else None,
        'max': json_value(array[finite].max()) if finite.any() else None,
        'norm': float(numpy.linalg.norm(array.ravel())),
        'fingerprint': fingerprint(array),
        'sha256': hashlib.sha256(array.tobytes()).hexdigest(),
    }


def snapshot_arrays(**values):
    import numpy
    arrays = {}
    def add(name, value):
        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                add(f'{name}_{index}', item)
        else:
            arrays[name] = numpy.asarray(value)
    for name, value in values.items():
        add(name, value)
    return arrays


def error_bucket(value):
    import math
    value = abs(float(value))
    return 'zero' if value == 0 else f'1e{math.floor(math.log10(value)):+d}'


class Recorder:
    def __init__(self, experiment, output):
        self.experiment = experiment
        self.output = output
        self.logs = output / 'logs'
        self.snapshots = output / 'snapshots'
        self.output.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(exist_ok=True)
        self.snapshots.mkdir(exist_ok=True)
        self.records_path = output / 'records.jsonl'
        self.handle = self.records_path.open('w', encoding='utf-8')
        self.records = []
        self.saved_snapshots = set()

    def log_path(self, name, attempt):
        return self.logs / f'{name}.attempt-{attempt}.log'

    def record(self, attempt, mode, status, elapsed_seconds, details):
        record = {
            'experiment': self.experiment,
            'nodeid': nodeid_for(self.experiment, mode),
            'attempt': attempt,
            'mode': mode,
            'status': status,
            'elapsed_seconds': elapsed_seconds,
            'thread_environment': {
                key: os.environ.get(key)
                for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')
            },
            'details': details,
        }
        record = json_value(record)
        self.records.append(record)
        self.handle.write(json.dumps(record, sort_keys=True) + '\n')
        self.handle.flush()

    def save_snapshot_once(self, status, signature, arrays):
        import numpy
        key = signature
        if key in self.saved_snapshots:
            return None
        self.saved_snapshots.add(key)
        safe = re.sub(r'[^A-Za-z0-9_.-]+', '-', key).strip('-') or 'snapshot'
        path = self.snapshots / f'first-{safe}.npz'
        numpy.savez_compressed(path, **arrays)
        return str(path.relative_to(self.output))

    def finish(self):
        self.handle.close()
        grouped = Counter((record['nodeid'], record['mode'], record['status']) for record in self.records)
        with (self.output / 'summary.csv').open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(('experiment', 'nodeid', 'mode', 'status', 'count'))
            for (nodeid, mode, status), count in sorted(grouped.items()):
                writer.writerow((self.experiment, nodeid, mode, status, count))

        status_counts = Counter(record['status'] for record in self.records)
        status_text = ', '.join(
            f'{name}={count}' for name, count in sorted(status_counts.items())) or 'none'
        lines = [
            f'## Precision diagnostic: {self.experiment}',
            '',
            f'- Records: {len(self.records)}',
            f'- Status counts: {status_text}',
            '',
            '| Nodeid | Mode | Status | Count |',
            '| --- | --- | --- | ---: |',
        ]
        lines.extend(
            f'| `{nodeid}` | {mode} | {status} | {count} |'
            for (nodeid, mode, status), count in sorted(grouped.items()))
        (self.output / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def close_mol(mol):
    if mol is not None and getattr(mol, 'stdout', None) is not None:
        mol.stdout.close()


def residual(matvec, vector, eigenvalue):
    import numpy
    value = matvec([vector])[0]
    norm = numpy.linalg.norm(vector)
    return float(numpy.linalg.norm(value - eigenvalue * vector) / norm) if norm else None


def all_true(value):
    return bool(__import__('numpy').asarray(value).all())


def build_eom_system(log_path):
    from pyscf import cc, gto, scf
    mol = gto.M(
        atom='O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587',
        basis='6-31g', verbose=4, output=str(log_path),
    )
    mf = scf.RHF(mol).run()
    return mol, cc.GCCSD(mf).run()


def run_eom_kind(mycc, kind):
    import numpy
    from pyscf.cc import eom_gccsd, eom_rccsd
    eom = eom_gccsd.EOMIP(mycc) if kind == 'ip' else eom_gccsd.EOMEA(mycc)
    solve = eom.ipccsd if kind == 'ip' else eom.eaccsd
    star = eom.ipccsd_star_contract if kind == 'ip' else eom.eaccsd_star_contract
    right_e, right_v = solve(nroots=3)
    right_converged = copy.deepcopy(eom.converged)
    left_e, left_v = solve(nroots=3, left=True, guess=right_v)
    left_converged = copy.deepcopy(eom.converged)
    star_input_e, star_right_v, star_left_v = eom_rccsd._sort_left_right_eigensystem(
        eom, right_converged, right_e, right_v, left_converged, left_e, left_v)
    star_e = star(star_input_e, star_right_v, star_left_v)
    right_matvec, _ = eom.gen_matvec()
    left_matvec, _ = eom.gen_matvec(left=True)
    overlaps = [[numpy.dot(left, right) for right in right_v] for left in left_v]
    details = {
        'right_eigenvalues': right_e,
        'left_eigenvalues': left_e,
        'star_eigenvalues': star_e,
        'right_converged': right_converged,
        'left_converged': left_converged,
        'left_right_overlap': overlaps,
        'matched_left_right_overlap': [
            numpy.dot(left, right) for left, right in zip(star_left_v, star_right_v)
        ],
        'right_residuals': [residual(right_matvec, vector, energy) for energy, vector in zip(right_e, right_v)],
        'left_residuals': [residual(left_matvec, vector, energy) for energy, vector in zip(left_e, left_v)],
        't1': array_metadata(mycc.t1),
        't2': array_metadata(mycc.t2),
    }
    target = EOM_REFERENCE[kind]
    errors = [abs(star_e[index] - reference) for index, reference in enumerate(target)]
    details['reference_errors'] = errors
    matched = all(error < 5e-6 for error in errors)
    converged = all_true(right_converged) and all_true(left_converged)
    status = 'pass' if matched and converged else ('not_converged' if not converged else 'reference_mismatch')
    worst_root = int(numpy.argmax(errors)) if errors else 0
    signature = (f'{kind}-pass' if status == 'pass' else
                 f'{kind}-star-root-{worst_root}-{status}-{error_bucket(errors[worst_root])}')
    arrays = snapshot_arrays(
        right_e=right_e, left_e=left_e, star_e=star_e,
        right_v=right_v, left_v=left_v, t1=mycc.t1, t2=mycc.t2,
    )
    return status, signature, details, arrays


def run_eom(args, recorder):
    for attempt in range(1, args.repeats + 1):
        for kind in ('ip', 'ea'):
            if nodeid_complete(recorder.records, nodeid_for('eom', kind)):
                continue
            log_path = recorder.log_path(f'eom-{kind}', attempt)
            start = time.monotonic()
            mol = None
            try:
                mol, mycc = build_eom_system(log_path)
                status, signature, details, arrays = run_eom_kind(mycc, kind)
                details['failure_signature'] = signature if status != 'pass' else None
                details['snapshot_file'] = recorder.save_snapshot_once(status, signature, arrays)
                details['log_file'] = str(log_path)
                recorder.record(attempt, kind, status, time.monotonic() - start, details)
            except Exception:
                recorder.record(attempt, kind, 'exception', time.monotonic() - start,
                                {'log_file': str(log_path), 'traceback': traceback.format_exc()})
            finally:
                close_mol(mol)
        if experiment_complete(recorder):
            break


def build_ucasscf_system(log_path):
    from pyscf import gto, scf
    mol = gto.M(
        atom='O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587',
        basis='631g', spin=2, verbose=4, output=str(log_path),
    )
    mf = scf.UHF(mol)
    mf.conv_tol = 1e-10
    return mol, mf.run()


def ucasscf_details(mc):
    import numpy
    from pyscf import lib
    dm1s, dm2s = mc.fcisolver.make_rdm12s(mc.ci, mc.ncas, mc.nelecas)
    occupations = [numpy.linalg.eigvalsh((dm + dm.T.conj()) * .5)[::-1] for dm in dm1s]
    eris = mc.ao2mo(mc.mo_coeff)
    rotations = tuple(numpy.eye(mo.shape[1]) for mo in mc.mo_coeff)
    orbital_gradient = mc.gen_g_hop(mc.mo_coeff, rotations, dm1s, dm2s, eris)[0]
    return {
        'e_tot': mc.e_tot,
        'e_cas': mc.e_cas,
        'converged': mc.converged,
        'gradient_norm': numpy.linalg.norm(orbital_gradient),
        'mo_fingerprint': [lib.fp(mo) for mo in mc.mo_coeff],
        'ci_fingerprint': fingerprint(mc.ci),
        'active_natural_occupations': occupations,
        'scf_density': array_metadata(mc._scf.make_rdm1()),
        'mo_coeff': [array_metadata(mo) for mo in mc.mo_coeff],
    }


def run_ucasscf_once(log_path, checkpoint, mode, seed_mo=None, seed_ci=None):
    from pyscf import mcscf
    mol, mf = build_ucasscf_system(log_path)
    try:
        mc = mcscf.UCASSCF(mf, 4, 4)
        mc.verbose = 4
        mc.chkfile = str(checkpoint)
        if mode == 'fixed':
            mc.kernel(mo_coeff=copy.deepcopy(seed_mo), ci0=copy.deepcopy(seed_ci))
        else:
            mc.kernel()
        return mol, mc, ucasscf_details(mc)
    except Exception:
        close_mol(mol)
        raise


def run_ucasscf(args, recorder):
    checkpoints = recorder.output / 'checkpoints'
    checkpoints.mkdir(exist_ok=True)
    import numpy
    guess_path = Path(__file__).resolve().parents[2] / 'pyscf' / 'mcscf' / 'test' / 'ucasscf_h2o_mo.txt'
    seed_mo = numpy.loadtxt(guess_path).reshape(2, 13, 13)
    seed_ci = None

    target = -75.7460662487894
    for attempt in range(1, args.repeats + 1):
        for mode in ('fixed',):
            log_path = recorder.log_path(f'ucasscf-{mode}', attempt)
            start = time.monotonic()
            mol = None
            try:
                mol, mc, details = run_ucasscf_once(
                    log_path, checkpoints / f'{mode}-current.chk', mode, seed_mo, seed_ci)
                details['log_file'] = str(log_path)
                matched = abs(mc.e_tot - target) < 5e-7
                status = ('pass' if matched and mc.converged else
                          ('not_converged' if not mc.converged else 'reference_mismatch'))
                signature = (f'ucasscf-{mode}-pass' if status == 'pass' else
                             f'ucasscf-{mode}-{status}-energy-{mc.e_tot:.5f}')
                details['failure_signature'] = signature if status != 'pass' else None
                snapshot_file = recorder.save_snapshot_once(
                    status, signature, snapshot_arrays(
                        mo_coeff=mc.mo_coeff, ci=mc.ci, scf_density=mc._scf.make_rdm1()))
                details['snapshot_file'] = snapshot_file
                if snapshot_file:
                    checkpoint = checkpoints / f'{mode}-current.chk'
                    saved_checkpoint = checkpoints / f'first-{signature}.chk'
                    shutil.copy2(checkpoint, saved_checkpoint)
                    details['checkpoint_file'] = str(saved_checkpoint.relative_to(recorder.output))
                recorder.record(attempt, mode, status, time.monotonic() - start, details)
            except Exception:
                recorder.record(attempt, mode, 'exception', time.monotonic() - start,
                                {'log_file': str(log_path), 'traceback': traceback.format_exc()})
            finally:
                close_mol(mol)
        if experiment_complete(recorder):
            break
    for mode in ('default', 'fixed'):
        current = checkpoints / f'{mode}-current.chk'
        if current.exists():
            current.unlink()


def build_sgx_molecule(log_path):
    from pyscf import gto
    return gto.M(
        atom='O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587',
        basis='6-31g', verbose=4, output=str(log_path),
    )


def set_sgx_options(mf, settings):
    dfj, fit_ovlp, optk, dm_screen, symm_fit = settings
    mf.with_df.grids_level_f = 1 if dfj else 2
    if mf.xc == 'HSE06' and not dfj:
        mf.with_df.debug = True
    mf.with_df.dfj = dfj
    mf.with_df.fit_ovlp = fit_ovlp
    mf.with_df.optk = optk
    if dm_screen:
        mf.with_df.sgx_tol_energy = 1e-12
    else:
        mf.with_df.sgx_tol_energy = None
        mf.with_df.sgx_tol_potential = None
    mf.with_df._symm_ovlp_fit = symm_fit
    mf.grids.level = 1
    mf.conv_tol = 1e-12


def run_sgx_case(mol, settings, order, xc, delta):
    import numpy
    from pyscf import lib, scf
    from pyscf.sgx.sgx import sgx_fit
    mf = sgx_fit(scf.RKS(mol).set(xc=xc))
    set_sgx_options(mf, settings)
    gradient = mf.nuc_grad_method().set(sgx_grid_response=True, grid_response=True).kernel()
    scanner = mf.as_scanner()
    mol1 = mol.copy()
    e_plus = scanner(mol1.set_geom_(
        f'O 0 0 {delta:f}; H 0 -0.757 0.587; H 0 0.757 0.587'))
    e_minus = scanner(mol1.set_geom_(
        f'O 0 0 {-delta:f}; H 0 -0.757 0.587; H 0 0.757 0.587'))
    force_sum = float(numpy.abs(gradient.sum(axis=0)).sum())
    finite_difference = float((e_plus - e_minus) / (2 * delta) * lib.param.BOHR)
    gradient_error = float(gradient[0, 2] - finite_difference)
    force_ok = round(force_sum, 12) == 0
    gradient_ok = round(gradient_error, order) == 0
    details = {
        'force_sum_l1': force_sum,
        'analytic_gradient_z': float(gradient[0, 2]),
        'finite_difference_z': finite_difference,
        'gradient_error': gradient_error,
        'force_assertion_pass': force_ok,
        'finite_difference_assertion_pass': gradient_ok,
        'gradient': array_metadata(gradient),
        'density': array_metadata(mf.make_rdm1()),
        'grid_coords': array_metadata(mf.grids.coords),
        'grid_weights': array_metadata(mf.grids.weights),
    }
    arrays = snapshot_arrays(
        gradient=gradient, density=mf.make_rdm1(),
        grid_coords=mf.grids.coords, grid_weights=mf.grids.weights,
        displaced_energies=(e_plus, e_minus),
    )
    return details, force_ok and gradient_ok, arrays


SGX_XCS = ('PBE0', 'HSE06', 'WB97X')
SGX_SHARDS = {
    'sgx-pbe0': ('PBE0',),
    'sgx-hse06': ('HSE06',),
    'sgx-wb97x': ('WB97X',),
}


def sgx_xcs(experiment):
    return SGX_SHARDS.get(experiment, SGX_XCS)


def run_sgx(args, recorder, xcs=SGX_XCS):
    settings_list = (
        (False, False, False, False, False),
        (True, False, False, False, False),
        (True, True, True, True, True),
    )
    precisions = (5, 6, 6)
    for attempt in range(1, args.repeats + 1):
        delta = 1e-4
        log_path = recorder.log_path('sgx', attempt)
        mol = None
        try:
            mol = build_sgx_molecule(log_path)
            for setting_index, (settings, order) in enumerate(zip(settings_list, precisions)):
                for xc in xcs:
                    start = time.monotonic()
                    mode = f'settings-{setting_index}:{xc}:delta-{delta:.0e}'
                    try:
                        details, passed, arrays = run_sgx_case(mol, settings, order, xc, delta)
                        details.update({
                            'settings': settings, 'order': order, 'xc': xc,
                            'delta': delta, 'log_file': str(log_path),
                        })
                        status = 'pass' if passed else 'reference_mismatch'
                        if status == 'pass':
                            signature = 'sgx-pass'
                        elif not details['force_assertion_pass']:
                            signature = f'sgx-{mode}-force-sum-{error_bucket(details["force_sum_l1"])}'
                        else:
                            signature = f'sgx-{mode}-finite-difference-{error_bucket(details["gradient_error"])}'
                        details['failure_signature'] = signature if status != 'pass' else None
                        details['snapshot_file'] = recorder.save_snapshot_once(status, signature, arrays)
                        recorder.record(attempt, mode, status,
                                        time.monotonic() - start, details)
                    except Exception:
                        recorder.record(attempt, mode, 'exception', time.monotonic() - start,
                                        {'settings': settings, 'xc': xc, 'delta': delta, 'log_file': str(log_path),
                                         'traceback': traceback.format_exc()})
        except Exception:
            recorder.record(attempt, 'setup', 'exception', 0.0,
                            {'log_file': str(log_path), 'traceback': traceback.format_exc()})
        finally:
            close_mol(mol)
        if experiment_complete(recorder):
            break


def direct_tddft_roots(a, b, nroots):
    import numpy
    a_aa, a_ab, a_bb = a
    b_aa, b_ab, b_bb = b
    nocc_a, nvir_a, nocc_b, nvir_b = a_ab.shape
    a_aa = a_aa.reshape(nocc_a * nvir_a, nocc_a * nvir_a)
    a_ab = a_ab.reshape(nocc_a * nvir_a, nocc_b * nvir_b)
    a_bb = a_bb.reshape(nocc_b * nvir_b, nocc_b * nvir_b)
    b_aa = b_aa.reshape(nocc_a * nvir_a, nocc_a * nvir_a)
    b_ab = b_ab.reshape(nocc_a * nvir_a, nocc_b * nvir_b)
    b_bb = b_bb.reshape(nocc_b * nvir_b, nocc_b * nvir_b)
    a_full = numpy.block([[a_aa, a_ab], [a_ab.conj().T, a_bb]])
    b_full = numpy.block([[b_aa, b_ab], [b_ab.T, b_bb]])
    abba = numpy.asarray(numpy.block([[a_full, b_full], [-b_full.conj(), -a_full.conj()]]))
    roots = numpy.linalg.eig(abba)[0]
    positive = numpy.sort(roots[roots.real > 0].real)
    return positive[positive > 1e-3][:nroots]


def td_residuals(td):
    import numpy
    vind, _ = td.gen_vind(td._scf)
    residuals = []
    for energy, xy in zip(td.e, td.xy):
        x, y = xy
        scalar_y = all(numpy.asarray(item).ndim == 0 for item in y) if isinstance(y, (list, tuple)) else (
            numpy.asarray(y).ndim == 0)
        vector = flatten(x) if scalar_y else numpy.hstack((flatten(x), flatten(y)))
        try:
            residuals.append(residual(vind, vector, energy))
        except Exception as error:
            residuals.append({'error': str(error)})
    return residuals


def run_tddft(args, recorder):
    import numpy
    from pyscf import dft, gto, lib
    for attempt in range(1, args.repeats + 1):
        log_path = recorder.log_path('tddft', attempt)
        start = time.monotonic()
        mol = None
        mf = None
        scf_history = []
        try:
            mol = gto.M(
                atom='O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587',
                basis='631g', verbose=4, output=str(log_path),
            )
            mf = dft.UKS(mol).set(xc='camb3lyp')
            mf.callback = lambda envs: scf_history.append({
                key: json_value(envs.get(key)) for key in ('cycle', 'e_tot', 'norm_ddm')
            })
            mf.kernel()
            td = mf.TDDFT()
            td.verbose = 5
            energies = td.kernel(nstates=4)[0]
            a, b = td.get_ab()
            direct_roots = direct_tddft_roots(a, b, 5)
            max_difference = float(abs(energies[:3] - direct_roots[:3]).max())
            fp = float(lib.fp(energies[:3] * 27.2114))
            converged = td.converged
            matched = max_difference < 5e-6 and abs(fp - 7.69383202636) < 5e-5
            converged = all_true(converged)
            status = 'pass' if matched and converged else ('not_converged' if not converged else 'reference_mismatch')
            signature = ('tddft-pass' if status == 'pass' else
                         f'tddft-{status}-fingerprint-{error_bucket(fp - 7.69383202636)}')
            arrays = snapshot_arrays(
                density=mf.make_rdm1(), mo_coeff=mf.mo_coeff,
                mo_energy=mf.mo_energy, a=a, b=b, xy=td.xy,
            )
            recorder.record(attempt, 'camb3lyp', status, time.monotonic() - start, {
                'iterative_roots': energies,
                'direct_ab_roots': direct_roots,
                'max_direct_difference': max_difference,
                'fingerprint_ev': fp,
                'converged': converged,
                'residuals': td_residuals(td),
                'scf_converged': mf.converged,
                'scf_energy': mf.e_tot,
                'scf_history': scf_history,
                'density': array_metadata(mf.make_rdm1()),
                'mo_energy': [array_metadata(values) for values in mf.mo_energy],
                'failure_signature': signature if status != 'pass' else None,
                'snapshot_file': recorder.save_snapshot_once(status, signature, arrays),
                'log_file': str(log_path),
            })
        except Exception as error:
            signature = f'tddft-exception-{type(error).__name__}'
            arrays = {}
            details = {'log_file': str(log_path), 'traceback': traceback.format_exc(),
                       'failure_signature': signature, 'scf_history': scf_history}
            if mf is not None and getattr(mf, 'mo_coeff', None) is not None:
                arrays = snapshot_arrays(
                    density=mf.make_rdm1(), mo_coeff=mf.mo_coeff, mo_energy=mf.mo_energy)
                details.update({
                    'scf_converged': mf.converged,
                    'scf_energy': mf.e_tot,
                    'density': array_metadata(mf.make_rdm1()),
                    'mo_energy': [array_metadata(values) for values in mf.mo_energy],
                    'snapshot_file': recorder.save_snapshot_once('exception', signature, arrays),
                })
            recorder.record(attempt, 'camb3lyp', 'exception', time.monotonic() - start,
                            details)
        finally:
            close_mol(mol)
        if experiment_complete(recorder):
            break


def build_diamond_cell(log_path, pseudo):
    from pyscf.pbc import gto
    cell = gto.Cell()
    cell.verbose = 4
    cell.output = str(log_path)
    cell.atom = 'C 0 0 0; C 0.8925000000 0.8925000000 0.8925000000'
    cell.a = '''
    1.7850000000 1.7850000000 0.0000000000
    0.0000000000 1.7850000000 1.7850000000
    1.7850000000 0.0000000000 1.7850000000
    '''
    cell.pseudo = pseudo
    cell.basis = {'C': [[0, (0.8, 1.0)], [1, (1.0, 1.0)]]}
    cell.precision = 1e-10
    return cell.build()


def scf_details(mf, history):
    return {
        'converged': mf.converged,
        'energy': mf.e_tot,
        'history': history,
        'density': array_metadata(mf.make_rdm1()),
        'mo_coeff': [array_metadata(values) for values in mf.mo_coeff]
        if isinstance(mf.mo_coeff, (list, tuple)) else array_metadata(mf.mo_coeff),
        'mo_energy': [array_metadata(values) for values in mf.mo_energy]
        if isinstance(mf.mo_energy, (list, tuple)) else array_metadata(mf.mo_energy),
    }


def pbc_snapshot(mf, td, a, b):
    return snapshot_arrays(
        density=mf.make_rdm1(), mo_coeff=mf.mo_coeff, mo_energy=mf.mo_energy,
        a=a, b=b, td_e=td.e, xy=td.xy,
    )


@contextlib.contextmanager
def pbc_test_grid_settings():
    from pyscf.dft import radi
    original = radi.ATOM_SPECIFIC_TREUTLER_GRIDS
    radi.ATOM_SPECIFIC_TREUTLER_GRIDS = False
    try:
        yield
    finally:
        radi.ATOM_SPECIFIC_TREUTLER_GRIDS = original


@pbc_test_grid_settings()
def run_pbc_tdhf(args, recorder):
    import numpy
    from pyscf.data.nist import HARTREE2EV
    from pyscf.pbc import scf
    reference = numpy.asarray((9.09165361, 11.51362009))
    for attempt in range(1, args.repeats + 1):
        log_path = recorder.log_path('pbc-tdhf', attempt)
        start = time.monotonic()
        cell = None
        try:
            cell = build_diamond_cell(log_path, 'gth-hf-rev')
            history = []
            mf = scf.UKS(cell).set(xc='m06').rs_density_fit(auxbasis='weigend')
            mf.callback = lambda envs: history.append({
                key: json_value(envs.get(key)) for key in ('cycle', 'e_tot', 'norm_ddm')
            })
            mf.kernel()
            td = mf.TDDFT().set(nstates=5, conv_tol=1e-8).run()
            a, b = td.get_ab()
            direct = direct_tddft_roots(a, b, 4)
            reference_error = float(abs(td.e[:2] * HARTREE2EV - reference).max())
            direct_error = float(abs(td.e[:4] - direct[:4]).max())
            converged = all_true(td.converged) and mf.converged
            passed = reference_error < 5e-5 and direct_error < 5e-8
            status = 'pass' if passed else ('not_converged' if not converged else 'reference_mismatch')
            if status == 'pass':
                signature = 'pbc-tdhf-pass'
            elif reference_error >= 5e-5:
                signature = f'pbc-tdhf-reference-{error_bucket(reference_error)}'
            else:
                signature = f'pbc-tdhf-direct-{error_bucket(direct_error)}'
            recorder.record(attempt, 'pbc-tdhf', status, time.monotonic() - start, {
                'scf': scf_details(mf, history),
                'iterative_roots': td.e,
                'direct_roots': direct,
                'reference_error_ev': reference_error,
                'direct_error_hartree': direct_error,
                'td_converged': td.converged,
                'td_residuals': td_residuals(td),
                'a': [array_metadata(values) for values in a],
                'b': [array_metadata(values) for values in b],
                'failure_signature': signature if status != 'pass' else None,
                'snapshot_file': recorder.save_snapshot_once(status, signature, pbc_snapshot(mf, td, a, b)),
                'log_file': str(log_path),
            })
        except Exception:
            recorder.record(attempt, 'pbc-tdhf', 'exception', time.monotonic() - start,
                            {'log_file': str(log_path), 'traceback': traceback.format_exc()})
        finally:
            close_mol(cell)
        if experiment_complete(recorder):
            break


def spin_orbital_a(a):
    import numpy
    aa, ab, bb = a
    noa, nva, nob, nvb = ab.shape
    aa = aa.reshape(noa * nva, noa * nva)
    ab = ab.reshape(noa * nva, nob * nvb)
    bb = bb.reshape(nob * nvb, nob * nvb)
    return numpy.block([[aa, ab], [ab.conj().T, bb]])


def pbc_tda_status(direct_error, tolerance):
    return 'pass' if direct_error < tolerance else 'reference_mismatch'


@pbc_test_grid_settings()
def run_pbc_tda(args, recorder, experiment, unrestricted, xc, pseudo, place):
    import numpy
    from pyscf.pbc import scf
    for attempt in range(1, args.repeats + 1):
        log_path = recorder.log_path(experiment, attempt)
        start = time.monotonic()
        cell = None
        try:
            cell = build_diamond_cell(log_path, pseudo)
            history = []
            mf = (scf.UKS(cell) if unrestricted else scf.RKS(cell)).set(xc=xc)
            mf.callback = lambda envs: history.append({
                key: json_value(envs.get(key)) for key in ('cycle', 'e_tot', 'norm_ddm')
            })
            mf.kernel()
            nstates = 3 if unrestricted else 5
            td = mf.TDA().run(nstates=nstates, conv_tol=1e-7)
            a, b = td.get_ab()
            matrix = spin_orbital_a(a) if unrestricted else a.reshape(a.shape[0] * a.shape[1], -1)
            direct = numpy.linalg.eigvalsh(matrix)
            count = 3 if unrestricted else 2
            direct_error = float(abs(td.e[:count] - direct[:count]).max())
            tolerance = .5 * 10 ** (-place)
            converged = all_true(td.converged) and mf.converged
            status = pbc_tda_status(direct_error, tolerance)
            signature = (f'{experiment}-pass' if status == 'pass' else
                         f'{experiment}-direct-{error_bucket(direct_error)}')
            a_metadata = ([array_metadata(values) for values in a]
                          if isinstance(a, (list, tuple)) else array_metadata(a))
            recorder.record(attempt, experiment, status, time.monotonic() - start, {
                'scf': scf_details(mf, history),
                'iterative_roots': td.e,
                'direct_roots': direct[:nstates],
                'direct_error_hartree': direct_error,
                'td_converged': td.converged,
                'td_residuals': td_residuals(td),
                'a': a_metadata,
                'a_hermitian_error': float(abs(matrix - matrix.conj().T).max()),
                'failure_signature': signature if status != 'pass' else None,
                'snapshot_file': recorder.save_snapshot_once(status, signature, pbc_snapshot(mf, td, a, b)),
                'log_file': str(log_path),
            })
        except Exception:
            recorder.record(attempt, experiment, 'exception', time.monotonic() - start,
                            {'log_file': str(log_path), 'traceback': traceback.format_exc()})
        finally:
            close_mol(cell)
        if experiment_complete(recorder):
            break


def run_pbc_hse06(args, recorder):
    run_pbc_tda(args, recorder, 'pbc-hse06', False, 'hse06', 'gth-pbe', 3)


def run_pbc_hse03(args, recorder):
    run_pbc_tda(args, recorder, 'pbc-hse03', True, 'hse03', 'gth-hf-rev', 6)


def casscf_gradient(mc):
    try:
        return array_metadata(mc.get_grad())
    except Exception as error:
        return {'error': str(error)}


def add_ci_snapshots(arrays, prefix, ci):
    import numpy
    values = ci if isinstance(ci, (list, tuple)) else (ci,)
    for index, value in enumerate(values):
        arrays[f'{prefix}_{index}'] = numpy.asarray(value)


def run_sa4_newton(args, recorder):
    from pyscf import gto, mcscf, scf
    checkpoints = recorder.output / 'checkpoints'
    checkpoints.mkdir(exist_ok=True)
    for attempt in range(1, args.repeats + 1):
        log_path = recorder.log_path('sa4-newton', attempt)
        start = time.monotonic()
        mol = None
        try:
            mol = gto.M(
                atom='O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587',
                basis='631g', verbose=4, output=str(log_path))
            mf = scf.RHF(mol).set(conv_tol=1e-10).run()
            ref = mcscf.CASSCF(mf, 4, 4).state_average_([.25] * 4)
            ref.chkfile = str(checkpoints / 'sa4-reference-current.chk')
            mo_ref = ref.sort_mo([4, 5, 6, 10], base=1)
            ref.kernel(mo_ref)
            newton = mcscf.CASSCF(mf, 4, 4).state_average_([.25] * 4).newton()
            newton.verbose = 5
            newton.chkfile = str(checkpoints / 'sa4-newton-current.chk')
            mo_newton = newton.sort_mo([4, 5, 6, 10], base=1)
            newton.kernel(mo_newton)
            energy_error = float(abs(newton.e_tot - ref.e_tot))
            state_errors = abs(__import__('numpy').asarray(newton.e_states) - ref.e_states)
            passed = energy_error < 5e-9 and float(state_errors.max()) < 5e-5
            status = 'pass' if passed else 'reference_mismatch'
            signature = ('sa4-newton-pass' if status == 'pass' else
                         f'sa4-newton-energy-{error_bucket(energy_error)}')
            arrays = snapshot_arrays(
                scf_density=mf.make_rdm1(), ref_mo=ref.mo_coeff,
                newton_mo=newton.mo_coeff, ref_states=ref.e_states,
                newton_states=newton.e_states)
            add_ci_snapshots(arrays, 'ref_ci', ref.ci)
            add_ci_snapshots(arrays, 'newton_ci', newton.ci)
            snapshot_file = recorder.save_snapshot_once(status, signature, arrays)
            details = {
                'scf': scf_details(mf, []),
                'reference_energy': ref.e_tot,
                'newton_energy': newton.e_tot,
                'energy_error': energy_error,
                'reference_states': ref.e_states,
                'newton_states': newton.e_states,
                'state_errors': state_errors,
                'reference_gradient': casscf_gradient(ref),
                'newton_gradient': casscf_gradient(newton),
                'reference_mo': array_metadata(ref.mo_coeff),
                'newton_mo': array_metadata(newton.mo_coeff),
                'failure_signature': signature if status != 'pass' else None,
                'snapshot_file': snapshot_file,
                'log_file': str(log_path),
            }
            if snapshot_file:
                saved_checkpoints = []
                for name in ('sa4-reference', 'sa4-newton'):
                    current = checkpoints / f'{name}-current.chk'
                    saved = checkpoints / f'first-{signature}-{name}.chk'
                    shutil.copy2(current, saved)
                    saved_checkpoints.append(str(saved.relative_to(recorder.output)))
                details['checkpoint_files'] = saved_checkpoints
            recorder.record(attempt, 'sa4-newton', status, time.monotonic() - start, details)
        except Exception:
            recorder.record(attempt, 'sa4-newton', 'exception', time.monotonic() - start,
                            {'log_file': str(log_path), 'traceback': traceback.format_exc()})
        finally:
            close_mol(mol)
        if experiment_complete(recorder):
            break
    for name in ('sa4-reference', 'sa4-newton'):
        current = checkpoints / f'{name}-current.chk'
        if current.exists():
            current.unlink()


def optional_array_call(obj, name, *args, **kwargs):
    method = getattr(obj, name, None)
    if method is None:
        return None
    try:
        return method(*args, **kwargs)
    except Exception as error:
        return {'error': str(error)}


def run_analyze(args, recorder):
    import numpy
    from pyscf import gto, lib, scf, tdscf
    length_reference = .16147450863004867
    velocity_reference = .19750347627735745
    for attempt in range(1, args.repeats + 1):
        log_path = recorder.log_path('analyze', attempt)
        start = time.monotonic()
        mol = None
        try:
            mol = gto.M(
                atom='O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587',
                basis='631g', spin=2, verbose=4, output=str(log_path))
            mf = scf.UHF(mol).run()
            td = tdscf.TDHF(mf).set(verbose=5).run(conv_tol=1e-6)
            length = td.oscillator_strength(gauge='length')
            velocity = td.oscillator_strength(gauge='velocity', order=2)
            length_error = float(abs(lib.fp(length) - length_reference))
            velocity_error = float(abs(lib.fp(velocity) - velocity_reference))
            converged = all_true(td.converged) and mf.converged
            passed = converged and length_error < 5e-6 and velocity_error < 5e-6
            status = 'pass' if passed else ('not_converged' if not converged else 'reference_mismatch')
            if status == 'pass':
                signature = 'analyze-pass'
            elif length_error >= 5e-6:
                signature = f'analyze-length-{error_bucket(length_error)}'
            else:
                signature = f'analyze-velocity-{error_bucket(velocity_error)}'
            arrays = snapshot_arrays(
                density=mf.make_rdm1(), mo_coeff=mf.mo_coeff, mo_energy=mf.mo_energy,
                td_e=td.e, xy=td.xy, length=length, velocity=velocity)
            recorder.record(attempt, 'analyze', status, time.monotonic() - start, {
                'scf': scf_details(mf, []),
                'td_e': td.e,
                'td_converged': td.converged,
                'td_residuals': td_residuals(td),
                'length': array_metadata(length),
                'velocity_order_2': array_metadata(velocity),
                'length_error': length_error,
                'velocity_error': velocity_error,
                'transition_dipole': json_value(optional_array_call(td, 'transition_dipole')),
                'transition_velocity_dipole': json_value(optional_array_call(td, 'transition_velocity_dipole')),
                'failure_signature': signature if status != 'pass' else None,
                'snapshot_file': recorder.save_snapshot_once(status, signature, arrays),
                'log_file': str(log_path),
            })
        except Exception:
            recorder.record(attempt, 'analyze', 'exception', time.monotonic() - start,
                            {'log_file': str(log_path), 'traceback': traceback.format_exc()})
        finally:
            close_mol(mol)
        if experiment_complete(recorder):
            break


EXPERIMENTS = (
    'eom', 'pbc-tdhf', 'pbc-hse06', 'pbc-hse03', 'ucasscf',
    'sa4-newton', 'sgx', 'tddft', 'analyze',
)


def run_experiment(experiment, args, output):
    recorder = Recorder(experiment, output)
    try:
        if experiment == 'sgx' or experiment in SGX_SHARDS:
            run_sgx(args, recorder, sgx_xcs(experiment))
        else:
            {
                'eom': run_eom,
                'pbc-tdhf': run_pbc_tdhf,
                'pbc-hse06': run_pbc_hse06,
                'pbc-hse03': run_pbc_hse03,
                'ucasscf': run_ucasscf,
                'sa4-newton': run_sa4_newton,
                'tddft': run_tddft,
                'analyze': run_analyze,
            }[experiment](args, recorder)
    finally:
        recorder.finish()
    if not recorder.records or all(record['status'] == 'exception' for record in recorder.records):
        raise SystemExit(f'{experiment} produced no usable records; inspect logs and artifact output.')
    return recorder


def write_all_summary(output, recorders):
    records = [record for recorder in recorders for record in recorder.records]
    with (output / 'records.jsonl').open('w', encoding='utf-8') as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + '\n')
    summaries = [(recorder.output / 'summary.md').read_text(encoding='utf-8') for recorder in recorders]
    (output / 'summary.md').write_text('\n'.join(summaries), encoding='utf-8')
    with (output / 'summary.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(('experiment', 'nodeid', 'mode', 'status', 'count'))
        for recorder in recorders:
            grouped = Counter((record['nodeid'], record['mode'], record['status']) for record in recorder.records)
            for (nodeid, mode, status), count in sorted(grouped.items()):
                writer.writerow((recorder.experiment, nodeid, mode, status, count))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment', choices=('all',) + EXPERIMENTS + tuple(SGX_SHARDS), required=True)
    parser.add_argument('--repeats', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be positive')

    if args.experiment == 'all':
        args.output.mkdir(parents=True, exist_ok=True)
        recorders = [run_experiment(experiment, args, args.output / experiment) for experiment in EXPERIMENTS]
        write_all_summary(args.output, recorders)
    else:
        run_experiment(args.experiment, args, args.output)


if __name__ == '__main__':
    main()
