#!/usr/bin/env python
"""Focused, non-blocking diagnostics for the precision-triage workflow."""

import argparse
import copy
import csv
import json
import os
import subprocess
import sys
import time
import traceback
from collections import Counter
from pathlib import Path


REFERENCE_TESTS = (
    'pyscf/fci/test/test_dhf_slow.py::KnownValues::test_kernel',
    'pyscf/fci/test/test_dhf_slow.py::KnownValues::test_solver',
    'pyscf/mcscf/test/test_bz.py::KnownValues::test_mc1step_4o4e',
    'pyscf/mcscf/test/test_bz.py::KnownValues::test_mc1step_9o8e',
    'pyscf/mcscf/test/test_bz.py::KnownValues::test_mc2step_4o4e',
)

EOM_REFERENCE = {
    'ip': (0.4358615224789573, 0.4358615224789594, 0.5095767839056080),
    'ea': (0.1894169322207168, 0.1894169322207168, 0.2820757599337823),
}


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


class Recorder:
    def __init__(self, experiment, output):
        self.experiment = experiment
        self.output = output
        self.logs = output / 'logs'
        self.output.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(exist_ok=True)
        self.records_path = output / 'records.jsonl'
        self.handle = self.records_path.open('w', encoding='utf-8')
        self.records = []

    def log_path(self, name, attempt):
        return self.logs / f'{name}.attempt-{attempt}.log'

    def record(self, attempt, mode, status, elapsed_seconds, details):
        record = {
            'experiment': self.experiment,
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

    def finish(self):
        self.handle.close()
        grouped = Counter((record['mode'], record['status']) for record in self.records)
        with (self.output / 'summary.csv').open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(('experiment', 'mode', 'status', 'count'))
            for (mode, status), count in sorted(grouped.items()):
                writer.writerow((self.experiment, mode, status, count))

        status_counts = Counter(record['status'] for record in self.records)
        lines = [
            f'## Precision diagnostic: {self.experiment}',
            '',
            f'- Records: {len(self.records)}',
            f'- Status counts: {", ".join(f"{name}={count}" for name, count in sorted(status_counts.items())) or "none"}',
            '',
            '| Mode | Status | Count |',
            '| --- | --- | ---: |',
        ]
        lines.extend(f'| {mode} | {status} | {count} |' for (mode, status), count in sorted(grouped.items()))
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


def run_reference(args, recorder):
    for attempt, test_id in enumerate(REFERENCE_TESTS, 1):
        log_path = recorder.log_path(test_id.replace('/', '_').replace(':', '_'), attempt)
        start = time.monotonic()
        with log_path.open('w', encoding='utf-8') as handle:
            result = subprocess.run(
                (sys.executable, '-m', 'pytest', '-q', '-rA', '-s', '-c', 'pytest.ini', test_id),
                stdout=handle, stderr=subprocess.STDOUT, check=False,
            )
        text = log_path.read_text(encoding='utf-8', errors='replace')
        first_error = next((line.strip() for line in text.splitlines() if 'AssertionError:' in line), '')
        recorder.record(
            attempt, 'known_reference', 'pass' if result.returncode == 0 else 'reference_mismatch',
            time.monotonic() - start,
            {'test_id': test_id, 'exit_code': result.returncode, 'log_file': str(log_path), 'first_error': first_error},
        )


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
    from pyscf.cc import eom_gccsd
    eom = eom_gccsd.EOMIP(mycc) if kind == 'ip' else eom_gccsd.EOMEA(mycc)
    solve = eom.ipccsd if kind == 'ip' else eom.eaccsd
    star = eom.ipccsd_star_contract if kind == 'ip' else eom.eaccsd_star_contract
    right_e, right_v = solve(nroots=5)
    right_converged = copy.deepcopy(eom.converged)
    left_e, left_v = solve(nroots=5, left=True)
    left_converged = copy.deepcopy(eom.converged)
    star_e = star(left_e, right_v, left_v)
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
        'right_residuals': [residual(right_matvec, vector, energy) for energy, vector in zip(right_e, right_v)],
        'left_residuals': [residual(left_matvec, vector, energy) for energy, vector in zip(left_e, left_v)],
    }
    target = EOM_REFERENCE[kind]
    matched = all(abs(star_e[index] - target[index]) < 5e-6 for index in range(3))
    converged = all_true(right_converged) and all_true(left_converged)
    return ('pass' if matched and converged else ('not_converged' if not converged else 'reference_mismatch')), details


def run_eom(args, recorder):
    for attempt in range(1, args.repeats + 1):
        for kind in ('ip', 'ea'):
            log_path = recorder.log_path(f'eom-{kind}', attempt)
            start = time.monotonic()
            mol = None
            try:
                mol, mycc = build_eom_system(log_path)
                status, details = run_eom_kind(mycc, kind)
                details['log_file'] = str(log_path)
                recorder.record(attempt, kind, status, time.monotonic() - start, details)
            except Exception:
                recorder.record(attempt, kind, 'exception', time.monotonic() - start,
                                {'log_file': str(log_path), 'traceback': traceback.format_exc()})
            finally:
                close_mol(mol)


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
    seed_log = recorder.logs / 'ucasscf-seed.log'
    seed_mol = None
    try:
        seed_mol, seed_mc, seed_details = run_ucasscf_once(seed_log, checkpoints / 'seed.chk', 'default')
        seed_mo = copy.deepcopy(seed_mc.mo_coeff)
        seed_ci = copy.deepcopy(seed_mc.ci)
        seed_details['log_file'] = str(seed_log)
        recorder.record(0, 'seed', 'pass' if seed_mc.converged else 'not_converged', 0.0, seed_details)
    except Exception:
        recorder.record(0, 'seed', 'exception', 0.0, {'log_file': str(seed_log), 'traceback': traceback.format_exc()})
        return
    finally:
        close_mol(seed_mol)

    target = -75.7460662487894
    for attempt in range(1, args.repeats + 1):
        for mode in ('default', 'fixed'):
            log_path = recorder.log_path(f'ucasscf-{mode}', attempt)
            start = time.monotonic()
            mol = None
            try:
                mol, mc, details = run_ucasscf_once(
                    log_path, checkpoints / f'{mode}-{attempt}.chk', mode, seed_mo, seed_ci)
                details['log_file'] = str(log_path)
                matched = abs(mc.e_tot - target) < 5e-7
                status = 'pass' if matched and mc.converged else ('not_converged' if not mc.converged else 'reference_mismatch')
                recorder.record(attempt, mode, status, time.monotonic() - start, details)
            except Exception:
                recorder.record(attempt, mode, 'exception', time.monotonic() - start,
                                {'log_file': str(log_path), 'traceback': traceback.format_exc()})
            finally:
                close_mol(mol)


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
    force_ok = round(force_sum, 13) == 0
    gradient_ok = round(gradient_error, order) == 0
    return {
        'force_sum_l1': force_sum,
        'analytic_gradient_z': float(gradient[0, 2]),
        'finite_difference_z': finite_difference,
        'gradient_error': gradient_error,
        'force_assertion_pass': force_ok,
        'finite_difference_assertion_pass': gradient_ok,
    }, force_ok and gradient_ok


def run_sgx(args, recorder):
    settings_list = (
        (False, False, False, False, False),
        (True, False, False, False, False),
        (True, True, True, True, True),
    )
    precisions = (5, 6, 6)
    deltas = (1e-3, 1e-4, 1e-5, 1e-6)
    for attempt in range(1, args.repeats + 1):
        delta = deltas[(attempt - 1) % len(deltas)]
        log_path = recorder.log_path('sgx', attempt)
        mol = None
        try:
            mol = build_sgx_molecule(log_path)
            for setting_index, (settings, order) in enumerate(zip(settings_list, precisions)):
                for xc in ('PBE0', 'HSE06', 'WB97X'):
                    start = time.monotonic()
                    mode = f'settings-{setting_index}:{xc}:delta-{delta:.0e}'
                    try:
                        details, passed = run_sgx_case(mol, settings, order, xc, delta)
                        details.update({'settings': settings, 'order': order, 'xc': xc, 'delta': delta, 'log_file': str(log_path)})
                        recorder.record(attempt, mode, 'pass' if passed else 'reference_mismatch',
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
    a_full = numpy.block([[a_aa, a_ab], [a_ab.T, a_bb]])
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
        vector = numpy.hstack((flatten(x), flatten(y)))
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
        try:
            mol = gto.M(
                atom='O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587',
                basis='631g', verbose=4, output=str(log_path),
            )
            mf = dft.UKS(mol).run(xc='camb3lyp')
            td = mf.TDDFT()
            energies = td.kernel(nstates=4)[0]
            a, b = td.get_ab()
            direct_roots = direct_tddft_roots(a, b, 5)
            max_difference = float(abs(energies[:3] - direct_roots[:3]).max())
            fp = float(lib.fp(energies[:3] * 27.2114))
            converged = td.converged
            matched = max_difference < 5e-6 and abs(fp - 7.69383202636) < 5e-5
            converged = all_true(converged)
            status = 'pass' if matched and converged else ('not_converged' if not converged else 'reference_mismatch')
            recorder.record(attempt, 'camb3lyp', status, time.monotonic() - start, {
                'iterative_roots': energies,
                'direct_ab_roots': direct_roots,
                'max_direct_difference': max_difference,
                'fingerprint_ev': fp,
                'converged': converged,
                'residuals': td_residuals(td),
                'log_file': str(log_path),
            })
        except Exception:
            recorder.record(attempt, 'camb3lyp', 'exception', time.monotonic() - start,
                            {'log_file': str(log_path), 'traceback': traceback.format_exc()})
        finally:
            close_mol(mol)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment', choices=('reference', 'eom', 'ucasscf', 'sgx', 'tddft'), required=True)
    parser.add_argument('--repeats', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be positive')

    recorder = Recorder(args.experiment, args.output)
    try:
        {
            'reference': run_reference,
            'eom': run_eom,
            'ucasscf': run_ucasscf,
            'sgx': run_sgx,
            'tddft': run_tddft,
        }[args.experiment](args, recorder)
    finally:
        recorder.finish()


if __name__ == '__main__':
    main()
