from pyscf.sgx.sgx import sgx_fit
from pyscf import gto, scf, lib
import json
import numpy
import unittest


TELEMETRY_PREFIX = 'PYSCF_SGX_HSE06_TELEMETRY_V1 '


ALL_SETTINGS = [
    [False, False, False, False, False],
    [True, False, False, False, False],
    [True, True, True, True, True],
]
ALL_PRECISIONS = [5, 6, 6]


def setUpModule():
    global mol
    mol = gto.Mole()
    mol.verbose = 5
    mol.output = '/dev/null'
    mol.atom.extend([
        ["O" , (0. , 0.     , 0.)],
        [1   , (0. , -0.757 , 0.587)],
        [1   , (0. , 0.757  , 0.587)],
    ])
    mol.basis = '6-31g'
    mol.build()


def _set_df_args(mf, dfj, fit_ovlp, optk, dm_screen, symm_fit):
    if dfj:
        mf.with_df.grids_level_f = 1
    else:
        mf.with_df.grids_level_f = 2
    if mf.xc == "HSE06" and not dfj:
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


def tearDownModule():
    global mol
    mol.stdout.close()
    del mol


def _run_with_post_kernel_snapshot(
        owner, phase, snapshots, operation, snapshotter, *args, **kwargs):
    had_shadow = 'post_kernel' in owner.__dict__
    previous_shadow = owner.__dict__.get('post_kernel')
    original = owner.post_kernel
    calls = 0

    def wrapped(envs):
        nonlocal calls
        original(envs)
        calls += 1
        if calls != 1:
            raise RuntimeError('post_kernel must be called exactly once')
        snapshots[phase] = snapshotter(envs)

    owner.post_kernel = wrapped
    try:
        result = operation(*args, **kwargs)
        if calls != 1:
            raise RuntimeError('post_kernel must be called exactly once')
        return result
    finally:
        if had_shadow:
            owner.__dict__['post_kernel'] = previous_shadow
        else:
            owner.__dict__.pop('post_kernel', None)


class PostKernelSnapshotTest(unittest.TestCase):
    class Owner:
        def __init__(self):
            self.events = []

        def post_kernel(self, envs):
            self.events.append('original')

    def test_calls_original_before_snapshot_and_restores_class_lookup(self):
        owner = self.Owner()
        snapshots = {}
        envs = {}

        def snapshotter(value):
            owner.events.append('snapshot')
            self.assertIs(value, envs)
            return {'value': 1}

        def operation():
            owner.post_kernel(envs)
            return 'result'

        result = _run_with_post_kernel_snapshot(
            owner, 'base', snapshots, operation, snapshotter)
        self.assertEqual(result, 'result')
        self.assertEqual(owner.events, ['original', 'snapshot'])
        self.assertEqual(snapshots, {'base': {'value': 1}})
        self.assertNotIn('post_kernel', owner.__dict__)

    def test_restores_after_operation_error(self):
        owner = self.Owner()
        with self.assertRaisesRegex(ValueError, 'operation'):
            _run_with_post_kernel_snapshot(
                owner, 'base', {},
                lambda: (_ for _ in ()).throw(ValueError('operation')),
                lambda envs: {})
        self.assertNotIn('post_kernel', owner.__dict__)

    def test_restores_after_snapshot_error(self):
        owner = self.Owner()

        def operation():
            owner.post_kernel({})

        with self.assertRaisesRegex(ValueError, 'snapshot'):
            _run_with_post_kernel_snapshot(
                owner, 'base', {}, operation,
                lambda envs: (_ for _ in ()).throw(ValueError('snapshot')))
        self.assertEqual(owner.events, ['original'])
        self.assertNotIn('post_kernel', owner.__dict__)

    def test_restores_existing_instance_shadow(self):
        owner = self.Owner()
        shadow = lambda envs: owner.events.append('shadow')
        owner.post_kernel = shadow

        def operation():
            owner.post_kernel({})

        _run_with_post_kernel_snapshot(
            owner, 'plus', {}, operation, lambda envs: {})
        self.assertIs(owner.__dict__['post_kernel'], shadow)
        self.assertEqual(owner.events, ['shadow'])

    def test_rejects_zero_or_multiple_post_kernel_calls(self):
        owner = self.Owner()
        with self.assertRaisesRegex(RuntimeError, 'exactly once'):
            _run_with_post_kernel_snapshot(
                owner, 'base', {}, lambda: None, lambda envs: {})
        self.assertNotIn('post_kernel', owner.__dict__)

        def twice():
            owner.post_kernel({})
            owner.post_kernel({})

        with self.assertRaisesRegex(RuntimeError, 'exactly once'):
            _run_with_post_kernel_snapshot(
                owner, 'base', {}, twice, lambda envs: {})
        self.assertNotIn('post_kernel', owner.__dict__)


class KnownValues(unittest.TestCase):

    def _check_finite_diff_grad(
            self, df_settings, order, xc, *, telemetry=False):
        mf = sgx_fit(scf.RKS(mol).set(xc=xc))
        _set_df_args(mf, *df_settings)
        phase = 'base'
        main_cycles = {}
        post = {}
        if telemetry:
            def snapshot_main_cycle(envs):
                main_cycles[phase] = {
                    'cycle': int(envs['cycle']) + 1,
                    'e_tot': float(envs['e_tot']),
                    'last_hf_e': float(envs['last_hf_e']),
                    'delta_e': float(envs['e_tot'] - envs['last_hf_e']),
                    'norm_gorb': float(envs['norm_gorb']),
                    'norm_ddm': float(envs['norm_ddm']),
                    'scf_conv': bool(envs['scf_conv']),
                    'conv_tol': float(envs['conv_tol']),
                    'conv_tol_grad': float(envs['conv_tol_grad']),
                    'conv_check': bool(envs['conv_check']),
                }
            mf.callback = snapshot_main_cycle

        g = mf.nuc_grad_method().set(
            sgx_grid_response=True, grid_response=True).kernel()
        if telemetry:
            post['base'] = (float(mf.e_tot), bool(mf.converged))
        mol1 = mol.copy()
        mf_scanner = mf.as_scanner()
        delta = 1e-4
        if telemetry:
            phase = 'plus'
        e1 = mf_scanner(mol1.set_geom_(
            f'O  0. 0. {delta:f}; 1  0. -0.757 0.587; 1  0. 0.757 0.587'
        ))
        if telemetry:
            post['plus'] = (float(e1), bool(mf_scanner.converged))
            phase = 'minus'
        e2 = mf_scanner(mol1.set_geom_(
            f'O  0. 0. -{delta:f}; 1  0. -0.757 0.587; 1  0. 0.757 0.587'
        ))
        if telemetry:
            post['minus'] = (float(e2), bool(mf_scanner.converged))
            phases = {}
            for name in ('base', 'plus', 'minus'):
                main = main_cycles[name]
                post_energy, post_converged = post[name]
                extra_executed = main['scf_conv'] and main['conv_check']
                phases[name] = {
                    'main': main,
                    'post_energy': post_energy,
                    'post_converged': post_converged,
                    'extra_executed': extra_executed,
                    'extra_shift': (
                        post_energy - main['e_tot']
                        if extra_executed else None),
                }

            analytic_gradient = float(g[0,2])
            translation_l1 = float(numpy.abs(g.sum(axis=0)).sum())
            plus_main = main_cycles['plus']['e_tot']
            minus_main = main_cycles['minus']['e_tot']
            fd_pre = (plus_main - minus_main) / (2 * delta) * lib.param.BOHR
            fd_post = (e1 - e2) / (2 * delta) * lib.param.BOHR
            error_pre = analytic_gradient - fd_pre
            error_post = analytic_gradient - fd_post
            extra_contribution = fd_post - fd_pre
            closure_residual = error_post - (
                error_pre - extra_contribution)
            translation_pass = bool(round(abs(translation_l1), 12) == 0)
            pre_pass = bool(round(abs(error_pre), 6) == 0)
            post_pass = bool(round(abs(error_post), 6) == 0)
            payload = {
                'schema_version': 1,
                'case': {
                    'settings_index': 2,
                    'settings': [True, True, True, True, True],
                    'precision': 6,
                    'xc': 'HSE06',
                    'delta': 1e-4,
                    'translation_places': 12,
                    'finite_difference_places': 6,
                },
                'units': {
                    'energy': 'Hartree',
                    'gradient': 'Hartree/Bohr',
                    'displacement': 'Angstrom',
                },
                'phases': phases,
                'result': {
                    'analytic_gradient': analytic_gradient,
                    'translation_l1': translation_l1,
                    'translation_assertion_pass': translation_pass,
                    'finite_difference_pre': fd_pre,
                    'finite_difference_post': fd_post,
                    'gradient_error_pre': error_pre,
                    'gradient_error_post': error_post,
                    'finite_difference_pre_pass': pre_pass,
                    'finite_difference_post_pass': post_pass,
                    'extra_contribution': extra_contribution,
                    'closure_residual': closure_residual,
                },
            }
            print(TELEMETRY_PREFIX + json.dumps(
                payload, sort_keys=True, separators=(',', ':'),
                allow_nan=False), flush=True)
        # Allow round-off from thread-dependent reductions while still bounding translational noise.
        self.assertAlmostEqual(numpy.abs(g.sum(axis=0)).sum(), 0, 12)
        self.assertAlmostEqual(g[0,2], (e1-e2)/(2*delta)*lib.param.BOHR, order)

    def test_finite_diff_grad_settings2_hse06_telemetry(self):
        self._check_finite_diff_grad(
            ALL_SETTINGS[2], ALL_PRECISIONS[2], 'HSE06', telemetry=True)

    def test_finite_diff_grad(self):
        self._check_finite_diff_grad(ALL_SETTINGS[0], ALL_PRECISIONS[0], "PBE0")
        self._check_finite_diff_grad(ALL_SETTINGS[0], ALL_PRECISIONS[0], "HSE06")
        self._check_finite_diff_grad(ALL_SETTINGS[0], ALL_PRECISIONS[0], "WB97X")
        self._check_finite_diff_grad(ALL_SETTINGS[1], ALL_PRECISIONS[1], "PBE0")
        self._check_finite_diff_grad(ALL_SETTINGS[1], ALL_PRECISIONS[1], "HSE06")
        self._check_finite_diff_grad(ALL_SETTINGS[1], ALL_PRECISIONS[1], "WB97X")
        self._check_finite_diff_grad(ALL_SETTINGS[2], ALL_PRECISIONS[2], "PBE0")
        self._check_finite_diff_grad(
            ALL_SETTINGS[2], ALL_PRECISIONS[2], "HSE06", telemetry=True)
        self._check_finite_diff_grad(ALL_SETTINGS[2], ALL_PRECISIONS[2], "WB97X")


if __name__ == '__main__':
    unittest.main()
