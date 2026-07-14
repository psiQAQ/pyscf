import pathlib
import importlib.util
import json
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW_DIR = REPO_ROOT / '.github' / 'workflows'
WORKFLOW = WORKFLOW_DIR / 'ci-precision-check.yml'
UNIX_RUNNER = WORKFLOW_DIR / 'run_unix_precision_tests.sh'
LINUX_BUILD_SCRIPT = WORKFLOW_DIR / 'ci_linux' / 'build_pyscf.sh'
MACOS_BUILD_SCRIPT = WORKFLOW_DIR / 'ci_macos' / 'build_pyscf.sh'
WINDOWS_BUILD_SCRIPT = WORKFLOW_DIR / 'ci_windows' / 'build_wheel_ci.ps1'
LIB_CMAKE = REPO_ROOT / 'pyscf' / 'lib' / 'CMakeLists.txt'
WINDOWS_RUNNER = WORKFLOW_DIR / 'run_windows_precision_tests.ps1'
DIAGNOSTICS_WORKFLOW = WORKFLOW_DIR / 'ci-precision-diagnostics.yml'
DIAGNOSTICS_SCRIPT = WORKFLOW_DIR / 'precision_experiments.py'
WINDOWS_DIAGNOSTICS_RUNNER = WORKFLOW_DIR / 'run_windows_precision_diagnostics.ps1'
WINDOWS_BUILD_ENV_SCRIPT = WORKFLOW_DIR / 'ci_windows' / 'create_build_env.ps1'
PAIRED_DIAGNOSTICS_WORKFLOW = DIAGNOSTICS_WORKFLOW
PAIRED_DIAGNOSTICS_RUNNER = WORKFLOW_DIR / 'run_paired_precision_diagnostics.py'


class PrecisionCheckWorkflowTests(unittest.TestCase):
    def test_linux_build_dependency_download_retries_to_file(self):
        text = LINUX_BUILD_SCRIPT.read_text(encoding='utf-8')
        self.assertIn('--retry-all-errors', text)
        self.assertIn('--output "$archive"', text)
        self.assertIn('tar xzf "$archive"', text)

    def test_precision_builds_use_fixed_libxc_stability_revision(self):
        revision = 'f4439479220beff707fc071e14345a205c885521'
        for script in (LINUX_BUILD_SCRIPT, MACOS_BUILD_SCRIPT, WINDOWS_BUILD_SCRIPT):
            self.assertIn(revision, script.read_text(encoding='utf-8'))
        cmake = LIB_CMAKE.read_text(encoding='utf-8')
        self.assertIn('URL ${LIBXC_URL}', cmake)
        self.assertIn('archive/7.0.0/libxc-7.0.0.tar.gz', cmake)

    def test_linux_precision_build_accepts_explicit_libxc_revision(self):
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        script = LINUX_BUILD_SCRIPT.read_text(encoding='utf-8')
        self.assertIn('      libxc_revision:', workflow)
        self.assertIn('LIBXC_REVISION: ${{ inputs.libxc_revision }}', workflow)
        self.assertIn('revision="${LIBXC_REVISION:-', script)
        self.assertIn('${#revision}', script)
        self.assertIn('libxc-$revision.tar.gz', script)

    def test_all_diagnostics_builds_accept_explicit_libxc_revision(self):
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        macos_script = MACOS_BUILD_SCRIPT.read_text(encoding='utf-8')
        windows_script = WINDOWS_BUILD_SCRIPT.read_text(encoding='utf-8')

        self.assertEqual(workflow.count('LIBXC_REVISION: ${{ inputs.libxc_revision }}'), 3)
        self.assertIn('revision="${LIBXC_REVISION:-', macos_script)
        self.assertIn('libxc-$revision.tar.gz', macos_script)
        self.assertIn('$libxcRevision = if ($env:LIBXC_REVISION)', windows_script)
        self.assertIn('libxc-$libxcRevision.tar.gz', windows_script)

    def test_linux_diagnostics_can_replace_only_generated_wpbeh_source(self):
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        script = LINUX_BUILD_SCRIPT.read_text(encoding='utf-8')
        self.assertIn('      libxc_wpbeh_revision:', workflow)
        self.assertIn('LIBXC_WPBEH_REVISION: ${{ inputs.libxc_wpbeh_revision }}', workflow)
        self.assertIn('wpbeh_revision="${LIBXC_WPBEH_REVISION:-}"', script)
        self.assertIn('/raw/$wpbeh_revision/src/maple2c/gga_exc/gga_x_wpbeh.c', script)
        self.assertIn('libxc_url="file://$patched_archive"', script)

    def test_windows_build_environment_retries_transient_conda_failure(self):
        text = WINDOWS_BUILD_ENV_SCRIPT.read_text(encoding='utf-8')
        self.assertIn('for ($attempt = 1; $attempt -le 3; $attempt++)', text)
        self.assertIn('Start-Sleep -Seconds (10 * $attempt)', text)

    def test_spin_orbital_matrix_uses_valid_numpy_block_layout(self):
        import numpy

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        aa = numpy.eye(2).reshape(1, 2, 1, 2)
        ab = numpy.ones((1, 2, 1, 3))
        bb = numpy.eye(3).reshape(1, 3, 1, 3)
        matrix = module.spin_orbital_a((aa, ab, bb))
        self.assertEqual(matrix.shape, (5, 5))

    def test_direct_tddft_roots_uses_conjugate_a_block(self):
        import numpy

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        aa = numpy.asarray([[[[2.0]]]])
        ab = numpy.asarray([[[[1.0j]]]])
        bb = numpy.asarray([[[[3.0]]]])
        zeros = tuple(numpy.zeros_like(block) for block in (aa, ab, bb))
        actual = module.direct_tddft_roots((aa, ab, bb), zeros, 2)
        a_full = numpy.asarray([[2.0, 1.0j], [-1.0j, 3.0]])
        expected = numpy.sort(numpy.linalg.eigvalsh(a_full))
        numpy.testing.assert_allclose(actual, expected)

    def test_pbc_diagnostics_restore_atom_specific_grid_setting(self):
        from pyscf.dft import radi

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = radi.ATOM_SPECIFIC_TREUTLER_GRIDS
        with module.pbc_test_grid_settings():
            self.assertFalse(radi.ATOM_SPECIFIC_TREUTLER_GRIDS)
        self.assertIs(radi.ATOM_SPECIFIC_TREUTLER_GRIDS, original)

    def test_tda_residuals_ignore_scalar_y_amplitudes(self):
        import numpy

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        class FakeTDA:
            _scf = object()
            e = (2.0,)
            xy = (((numpy.asarray([1.0]), numpy.asarray([0.0])), (0, 0)),)

            def gen_vind(self, mf):
                def vind(vectors):
                    self.assert_vector_length = len(vectors[0])
                    return [numpy.asarray(vectors[0]) * 2]
                return vind, None

        td = FakeTDA()
        self.assertEqual(module.td_residuals(td), [0.0])
        self.assertEqual(td.assert_vector_length, 2)

    def test_pbc_tda_status_matches_original_numeric_assertion(self):
        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.pbc_tda_status(1e-11, 5e-4), 'pass')
        self.assertEqual(module.pbc_tda_status(1e-3, 5e-4), 'reference_mismatch')

    def test_tddft_status_matches_original_numeric_assertions(self):
        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.tddft_status(1e-11, 7.69383202636), 'pass')
        self.assertEqual(module.tddft_status(1e-3, 7.69383202636), 'reference_mismatch')
        self.assertEqual(module.tddft_status(1e-11, 7.7), 'reference_mismatch')

    def test_ucasscf_status_matches_original_energy_assertion(self):
        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.ucasscf_status(-75.7460662487894), 'pass')
        self.assertEqual(module.ucasscf_status(-75.746), 'reference_mismatch')

    def test_eom_diagnostic_checks_every_original_assertion(self):
        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        refs = module.EOM_ASSERTIONS['ip']
        errors = module.eom_assertion_errors(
            'ip', refs['single'], refs['right'], refs['left'], refs['star'])
        self.assertEqual(max(errors.values()), 0)
        bad_right = list(refs['right'])
        bad_right[1] += 1e-3
        errors = module.eom_assertion_errors(
            'ip', refs['single'], bad_right, refs['left'], refs['star'])
        self.assertGreater(errors['right'], 5e-6)

    def test_analyze_diagnostic_checks_original_logger_values(self):
        import numpy

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        reference = module.ANALYZE_REFERENCE
        self.assertEqual(module.analyze_output_error(reference), 0)
        changed = numpy.asarray(reference).copy()
        changed[-1] += 1e-2
        self.assertGreater(module.analyze_output_error(changed), 5e-5)

    def test_sgx_formal_shards_select_one_xc(self):
        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.sgx_xcs('sgx'), ('PBE0', 'HSE06', 'WB97X'))
        self.assertEqual(module.sgx_xcs('sgx-hse06'), ('HSE06',))
        nodeid = module.NODEIDS['sgx']
        self.assertEqual(module.nodeid_for('sgx-hse06', 'settings-0:HSE06:delta-1e-04'), nodeid)

        class Recorder:
            experiment = 'sgx-hse06'
            records = [{'nodeid': nodeid, 'attempt': 1, 'status': 'pass'}]

        recorder = Recorder()
        self.assertFalse(module.experiment_complete(recorder))
        recorder.records.append({'nodeid': nodeid, 'attempt': 2, 'status': 'reference_mismatch'})
        self.assertTrue(module.experiment_complete(recorder))
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        for experiment in ('sgx-pbe0', 'sgx-hse06', 'sgx-wb97x'):
            self.assertIn(f'          - {experiment}', workflow)

    def test_sgx_hse06_control_is_dispatchable(self):
        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('sgx-hse06-control', module.CONTROL_EXPERIMENTS)
        self.assertIn('          - split-sgx-hse06-control', workflow)

        paired_spec = importlib.util.spec_from_file_location(
            'run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        paired = importlib.util.module_from_spec(paired_spec)
        paired_spec.loader.exec_module(paired)
        experiment, profiles = paired.execution_profiles(
            'split-sgx-hse06-control', 'omp1-blas1,omp4-blas1')
        self.assertEqual(experiment, 'sgx-hse06-control')
        self.assertEqual([item[0] for item in profiles], ['omp1-blas1', 'omp4-blas1'])

    def test_sgx_hse06_control_dispatches_dedicated_runner(self):
        from types import SimpleNamespace
        from unittest import mock

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def record_once(args, recorder):
            recorder.record(1, 'rks', 'pass', 0.0, {})

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(module, 'run_sgx_hse06_control', side_effect=record_once) as runner:
                module.run_experiment(
                    'sgx-hse06-control', SimpleNamespace(repeats=1), pathlib.Path(tmp))
            runner.assert_called_once()

    def test_pbc_tdhf_replay_is_dispatchable(self):
        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('pbc-tdhf-replay', module.REPLAY_EXPERIMENTS)
        self.assertIn('pbc-tdhf-fixture-bank', module.REPLAY_EXPERIMENTS)
        self.assertIn('          - split-pbc-tdhf-replay', workflow)
        self.assertIn('          - split-pbc-tdhf-fixture-bank', workflow)

        paired_spec = importlib.util.spec_from_file_location(
            'run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        paired = importlib.util.module_from_spec(paired_spec)
        paired_spec.loader.exec_module(paired)
        experiment, profiles = paired.execution_profiles(
            'split-pbc-tdhf-replay', 'omp1-blas1,omp4-blas4')
        self.assertEqual(experiment, 'pbc-tdhf-replay')
        self.assertEqual([item[0] for item in profiles], ['omp1-blas1', 'omp4-blas4'])

    def test_pbc_tdhf_native_replay_is_dispatchable(self):
        from types import SimpleNamespace
        from unittest import mock

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        self.assertEqual(module.base_experiment('pbc-tdhf-native-replay'), 'pbc-tdhf')
        self.assertIn('          - split-pbc-tdhf-native-replay', workflow)

        def record_once(args, recorder):
            recorder.record(1, 'native-replay', 'pass', 0.0, {})

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(module, 'run_pbc_tdhf_native_replay', side_effect=record_once) as runner:
                module.run_experiment(
                    'pbc-tdhf-native-replay', SimpleNamespace(repeats=1), pathlib.Path(tmp))
            runner.assert_called_once()

    def test_pbc_tdhf_native_replay_compares_same_operator_and_marks_native_failure(self):
        import numpy
        from pyscf.data.nist import HARTREE2EV

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        a = numpy.asarray([[2.0]])
        b = numpy.zeros((1, 1))
        matrix = numpy.block([[a, b], [-b, -a]])
        x0 = numpy.asarray([[1.0, 0.0]])
        result = module.compare_pbc_tdhf_native_replay(
            lambda vectors: numpy.asarray(vectors).dot(matrix.T),
            numpy.asarray([2.1]), numpy.asarray([True]),
            a, b, x0, numpy.asarray([2.0, -2.0]),
            numpy.asarray([2.0 * HARTREE2EV]), nroots=1,
        )
        self.assertEqual(result['status'], 'reference_mismatch')
        self.assertAlmostEqual(result['operator_action_error'], 0.0)
        self.assertAlmostEqual(result['replay_reference_error_ev'], 0.0)
        self.assertAlmostEqual(result['native_replay_error_hartree'], 0.1)

    def test_pbc_tdhf_fixture_bank_creates_one_fixture_per_attempt(self):
        import numpy
        from types import SimpleNamespace
        from unittest import mock

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def create_fixture(path):
            value = float(int(path.stem.rsplit('-', 1)[1]))
            numpy.savez_compressed(
                path, a=numpy.asarray([[value]]), b=numpy.zeros((1, 1)),
                x0=numpy.asarray([[1.0, 0.0]]), hdiag=numpy.asarray([value, -value]),
                reference=numpy.asarray([value]), nroots=numpy.asarray(1))

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            recorder = module.Recorder('pbc-tdhf-fixture-bank', root / 'output')
            try:
                with mock.patch.object(module, 'create_pbc_tdhf_fixture', side_effect=create_fixture) as creator:
                    module.run_pbc_tdhf_replay(SimpleNamespace(repeats=2, fixture=None), recorder)
                self.assertEqual(creator.call_count, 2)
            finally:
                recorder.finish()
            self.assertEqual([record['attempt'] for record in recorder.records], [1, 2])
            self.assertEqual(len({record['details']['fixture_sha256'] for record in recorder.records}), 2)
            self.assertTrue((recorder.output / 'fixtures' / 'fixture-0002.npz').is_file())

    def test_pbc_tdhf_replay_dispatches_dedicated_runner(self):
        from types import SimpleNamespace
        from unittest import mock

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def record_once(args, recorder):
            recorder.record(1, 'fixed-matrix', 'pass', 0.0, {})

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    module, 'run_pbc_tdhf_replay', side_effect=record_once, create=True) as runner:
                module.run_experiment(
                    'pbc-tdhf-replay', SimpleNamespace(repeats=1, fixture=None), pathlib.Path(tmp))
            runner.assert_called_once()

    def test_pbc_tdhf_fixed_matrix_replay_solves_known_root(self):
        import numpy

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.replay_pbc_tdhf_matrix(
            numpy.asarray([[2.0]]), numpy.zeros((1, 1)),
            numpy.asarray([[1.0, 0.0]]), numpy.asarray([2.0, -2.0]),
            nroots=1, tol_residual=1e-10, max_cycle=10, verbose=0)
        self.assertEqual(result['converged'].tolist(), [True])
        numpy.testing.assert_allclose(result['iterative_roots'], [2.0], atol=1e-12)
        numpy.testing.assert_allclose(result['direct_roots'], [2.0], atol=1e-12)
        numpy.testing.assert_allclose(result['residuals'], [0.0], atol=1e-12)

    def test_pbc_tdhf_replay_reads_fixture_and_records_each_attempt(self):
        import numpy
        from types import SimpleNamespace

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            fixture = root / 'fixture.npz'
            numpy.savez_compressed(
                fixture, a=numpy.asarray([[2.0]]), b=numpy.zeros((1, 1)),
                x0=numpy.asarray([[1.0, 0.0]]), hdiag=numpy.asarray([2.0, -2.0]),
                reference=numpy.asarray([2.0]), nroots=numpy.asarray(1))
            recorder = module.Recorder('pbc-tdhf-replay', root / 'output')
            try:
                module.run_pbc_tdhf_replay(SimpleNamespace(repeats=2, fixture=fixture), recorder)
            finally:
                recorder.finish()
            self.assertEqual([record['status'] for record in recorder.records], ['pass', 'pass'])
            self.assertEqual({record['nodeid'] for record in recorder.records}, {module.NODEIDS['pbc-tdhf']})
            self.assertTrue(all(record['details']['fixture_sha256'] for record in recorder.records))

    def test_pbc_tdhf_replay_uses_original_root_assertions(self):
        import numpy
        from types import SimpleNamespace
        from unittest import mock

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = {
            'converged': numpy.asarray([True, False]),
            'iterative_roots': numpy.asarray([2.0, 3.0]),
            'direct_roots': numpy.asarray([2.0, 3.0]),
            'residuals': numpy.asarray([0.0, 1e-7]),
            'vectors': numpy.zeros((2, 4)),
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            fixture = root / 'fixture.npz'
            numpy.savez_compressed(
                fixture, a=numpy.eye(2), b=numpy.zeros((2, 2)), x0=numpy.eye(2, 4),
                hdiag=numpy.asarray([2.0, 3.0, -2.0, -3.0]), reference=numpy.asarray([2.0]),
                nroots=numpy.asarray(2))
            recorder = module.Recorder('pbc-tdhf-replay', root / 'output')
            try:
                with mock.patch.object(module, 'replay_pbc_tdhf_matrix', return_value=result):
                    module.run_pbc_tdhf_replay(SimpleNamespace(repeats=1, fixture=fixture), recorder)
            finally:
                recorder.finish()
            self.assertEqual(recorder.records[0]['status'], 'pass')

    def test_pbc_tdhf_replay_creates_fixture_for_first_profile(self):
        import numpy
        from types import SimpleNamespace
        from unittest import mock

        spec = importlib.util.spec_from_file_location('precision_experiments', DIAGNOSTICS_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def create_fixture(path):
            numpy.savez_compressed(
                path, a=numpy.asarray([[2.0]]), b=numpy.zeros((1, 1)),
                x0=numpy.asarray([[1.0, 0.0]]), hdiag=numpy.asarray([2.0, -2.0]),
                reference=numpy.asarray([2.0]), nroots=numpy.asarray(1))

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            recorder = module.Recorder('pbc-tdhf-replay', root / 'output')
            try:
                with mock.patch.object(
                        module, 'create_pbc_tdhf_fixture', side_effect=create_fixture, create=True) as creator:
                    module.run_pbc_tdhf_replay(SimpleNamespace(repeats=1, fixture=None), recorder)
                creator.assert_called_once_with(recorder.output / 'fixture.npz')
            finally:
                recorder.finish()
            self.assertEqual([record['status'] for record in recorder.records], ['pass'])

    def test_paired_runner_sets_thread_environment_and_separates_outputs(self):
        spec = importlib.util.spec_from_file_location('run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fake = '''
import argparse, json, os, pathlib
parser = argparse.ArgumentParser()
parser.add_argument('--experiment')
parser.add_argument('--repeats')
parser.add_argument('--output')
args = parser.parse_args()
output = pathlib.Path(args.output)
output.mkdir(parents=True, exist_ok=True)
keys = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')
(output / 'observed.json').write_text(json.dumps({key: os.environ.get(key) for key in keys}))
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            script = root / 'fake.py'
            script.write_text(fake, encoding='utf-8')
            code = module.main((
                '--python', sys.executable, '--script', str(script),
                '--experiment', 'fake', '--repeats', '1', '--output', str(root / 'out'),
            ))
            self.assertEqual(code, 0)
            for threads in ('1', '4'):
                observed = json.loads((root / 'out' / f't{threads}' / 'observed.json').read_text())
                self.assertEqual(set(observed.values()), {threads})
            metadata = json.loads((root / 'out' / 'paired-runs.json').read_text())
            self.assertEqual([run['threads'] for run in metadata['runs']], [1, 4])

    def test_paired_runner_propagates_child_failure(self):
        spec = importlib.util.spec_from_file_location('run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fake = 'import os, sys; sys.exit(9 if os.environ["OMP_NUM_THREADS"] == "4" else 0)'
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            script = root / 'fake.py'
            script.write_text(fake, encoding='utf-8')
            code = module.main((
                '--python', sys.executable, '--script', str(script),
                '--experiment', 'fake', '--repeats', '1', '--output', str(root / 'out'),
            ))
            self.assertEqual(code, 9)

    def test_pbc_tdhf_replay_reuses_first_profile_fixture(self):
        spec = importlib.util.spec_from_file_location('run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fake = '''
import argparse, pathlib
parser = argparse.ArgumentParser()
parser.add_argument('--experiment')
parser.add_argument('--repeats')
parser.add_argument('--output')
parser.add_argument('--fixture')
args = parser.parse_args()
output = pathlib.Path(args.output)
output.mkdir(parents=True, exist_ok=True)
bank = args.experiment == 'pbc-tdhf-fixture-bank'
fixture = pathlib.Path(args.fixture) if args.fixture else output / ('fixtures' if bank else 'fixture.npz')
if not args.fixture:
    fixture.mkdir() if bank else fixture.write_bytes(b'fixture')
(output / 'fixture-path.txt').write_text(str(fixture.resolve()), encoding='utf-8')
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            script = root / 'fake.py'
            script.write_text(fake, encoding='utf-8')
            for experiment in ('split-pbc-tdhf-replay', 'split-pbc-tdhf-fixture-bank'):
                with self.subTest(experiment=experiment):
                    output = root / experiment
                    code = module.main((
                        '--python', sys.executable, '--script', str(script), '--experiment', experiment,
                        '--profiles', 'omp1-blas1,omp4-blas4', '--repeats', '2', '--output', str(output),
                    ))
                    self.assertEqual(code, 0)
                    first = (output / 'omp1-blas1' / 'fixture-path.txt').read_text(encoding='utf-8')
                    second = (output / 'omp4-blas4' / 'fixture-path.txt').read_text(encoding='utf-8')
                    self.assertEqual(second, first)

    def test_split_runner_separates_openmp_and_blas_threads(self):
        spec = importlib.util.spec_from_file_location('run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fake = '''
import argparse, json, os, pathlib
parser = argparse.ArgumentParser()
parser.add_argument('--experiment')
parser.add_argument('--repeats')
parser.add_argument('--output')
args = parser.parse_args()
output = pathlib.Path(args.output)
output.mkdir(parents=True, exist_ok=True)
keys = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')
(output / 'observed.json').write_text(json.dumps({
    'experiment': args.experiment,
    'threads': {key: os.environ.get(key) for key in keys},
}))
'''
        expected = {
            'omp1-blas1': ('1', '1'),
            'omp4-blas1': ('4', '1'),
            'omp1-blas4': ('1', '4'),
            'omp4-blas4': ('4', '4'),
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            script = root / 'fake.py'
            script.write_text(fake, encoding='utf-8')
            code = module.main((
                '--python', sys.executable, '--script', str(script),
                '--experiment', 'split-eom', '--repeats', '1', '--output', str(root / 'out'),
            ))
            self.assertEqual(code, 0)
            for profile, (omp_threads, blas_threads) in expected.items():
                observed = json.loads((root / 'out' / profile / 'observed.json').read_text())
                self.assertEqual(observed['experiment'], 'eom')
                self.assertEqual(observed['threads']['OMP_NUM_THREADS'], omp_threads)
                self.assertEqual(set(observed['threads'][key] for key in module.BLAS_VARIABLES), {blas_threads})
            metadata = json.loads((root / 'out' / 'paired-runs.json').read_text())
            self.assertEqual([run['profile'] for run in metadata['runs']], list(expected))

    def test_split_runner_selects_requested_profiles(self):
        spec = importlib.util.spec_from_file_location('run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        experiment, profiles = module.execution_profiles(
            'split-sgx-hse06', 'omp1-blas1,omp4-blas1')

        self.assertEqual(experiment, 'sgx-hse06')
        self.assertEqual([profile[0] for profile in profiles], ['omp1-blas1', 'omp4-blas1'])

    def test_split_runner_rejects_invalid_profile_selection(self):
        spec = importlib.util.spec_from_file_location('run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        cases = (
            ('split-sgx-hse06', 'unknown'),
            ('split-sgx-hse06', 'omp1-blas1,omp1-blas1'),
            ('sgx-hse06', 'omp1-blas1'),
        )
        for experiment, profiles in cases:
            with self.subTest(experiment=experiment, profiles=profiles):
                with self.assertRaisesRegex(ValueError, 'profiles'):
                    module.execution_profiles(experiment, profiles)

    def test_split_runner_runs_only_requested_profiles(self):
        spec = importlib.util.spec_from_file_location('run_paired_precision_diagnostics', PAIRED_DIAGNOSTICS_RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fake = '''
import argparse, pathlib
parser = argparse.ArgumentParser()
parser.add_argument('--experiment')
parser.add_argument('--repeats')
parser.add_argument('--output')
args = parser.parse_args()
output = pathlib.Path(args.output)
output.mkdir(parents=True, exist_ok=True)
(output / 'experiment.txt').write_text(args.experiment)
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            script = root / 'fake.py'
            script.write_text(fake, encoding='utf-8')
            code = module.main((
                '--python', sys.executable, '--script', str(script),
                '--experiment', 'split-sgx-hse06', '--profiles', 'omp1-blas1,omp4-blas1',
                '--repeats', '1', '--output', str(root / 'out'),
            ))

            self.assertEqual(code, 0)
            self.assertEqual(
                sorted(path.name for path in (root / 'out').iterdir() if path.is_dir()),
                ['omp1-blas1', 'omp4-blas1'])
            for profile in ('omp1-blas1', 'omp4-blas1'):
                self.assertEqual((root / 'out' / profile / 'experiment.txt').read_text(), 'sgx-hse06')
            metadata = json.loads((root / 'out' / 'paired-runs.json').read_text())
            self.assertEqual(metadata['requested_profiles'], 'omp1-blas1,omp4-blas1')
            self.assertEqual([run['profile'] for run in metadata['runs']], ['omp1-blas1', 'omp4-blas1'])

    def test_paired_workflow_builds_once_for_seven_platform_pairs(self):
        text = PAIRED_DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        self.assertFalse((WORKFLOW_DIR / 'ci-precision-thread-paired.yml').exists())
        self.assertIn('workflow_dispatch:', text)
        self.assertIn('timeout-minutes: 360', text)
        self.assertIn('fail-fast: false', text)
        self.assertEqual(text.count('uses: actions/upload-artifact@v7'), 3)
        self.assertNotIn('matrix.threads', text)
        self.assertNotIn('threads: ["1", "4"]', text)
        self.assertIn('python-version: ["3.8", "3.12", "3.13"]', text)
        self.assertIn('python-version: ["3.8", "3.13"]', text)
        self.assertIn('python-version: ["3.12", "3.13"]', text)
        self.assertIn('run_paired_precision_diagnostics.py', text)
        self.assertIn('-Paired', text)
        for experiment in ('split-eom', 'split-ucasscf', 'split-sa4-newton',
                           'split-tddft', 'split-analyze', 'split-pbc-hse03', 'split-pbc-hse06',
                           'split-sgx-pbe0', 'split-sgx-wb97x'):
            self.assertIn(f'          - {experiment}', text)
        self.assertIn('${{ inputs.experiment }}/*/summary.md', text)

    def test_paired_workflow_can_shard_split_profiles(self):
        workflow = PAIRED_DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        windows_runner = WINDOWS_DIAGNOSTICS_RUNNER.read_text(encoding='utf-8')

        self.assertIn('          - split-sgx-hse06', workflow)
        self.assertIn('          - omp1-blas1,omp4-blas1', workflow)
        self.assertIn('          - omp1-blas4,omp4-blas4', workflow)
        self.assertEqual(workflow.count('--profiles "${{ inputs.profiles }}"'), 2)
        self.assertEqual(workflow.count('-Profiles "${{ inputs.profiles }}"'), 1)
        self.assertIn('[string]$Profiles = "all"', windows_runner)
        self.assertIn('--profiles $Profiles', windows_runner)

    def test_check_workflow_replaces_old_precision_workflow(self):
        self.assertTrue(WORKFLOW.exists())
        self.assertFalse((WORKFLOW_DIR / 'ci-linux-precision.yml').exists())
        self.assertTrue(UNIX_RUNNER.exists())
        self.assertFalse((WORKFLOW_DIR / 'run_linux_precision_tests.sh').exists())

    def test_check_workflow_has_approved_triggers_and_jobs(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('workflow_dispatch:', text)
        self.assertNotIn('push:', text)
        self.assertNotIn('pull_request:', text)
        self.assertIn('precision-unix:', text)
        self.assertIn('precision-windows:', text)
        self.assertIn('fail-fast: false', text)
        self.assertNotIn('continue-on-error', text)

    def test_check_workflow_has_seven_platform_version_combinations(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('os: [ubuntu-latest, macos-latest]', text)
        self.assertIn('python-version: ["3.8", "3.12", "3.13"]', text)
        self.assertIn('- os: macos-latest\n            python-version: "3.12"', text)
        self.assertIn('python-version: ["3.12", "3.13"]', text)

    def test_check_workflow_uses_isolated_platform_runners(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('run_unix_precision_tests.sh', text)
        self.assertIn('run_windows_precision_tests.ps1', text)
        self.assertNotIn('run_ci_windows.ps1', text)
        self.assertIn('PYTHONPATH="$GITHUB_WORKSPACE:${PYTHONPATH:-}"', text)

    def test_each_job_uploads_complete_result_directory(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertEqual(text.count('uses: actions/upload-artifact@v7'), 2)
        self.assertEqual(text.count('if: always()'), 4)
        self.assertGreaterEqual(text.count('tmp/precision-results'), 2)
        self.assertIn('.github/workflows/ci_windows/build-logs/**', text)

    def test_diagnostics_are_active_and_manual_only(self):
        archive = WORKFLOW_DIR / 'tmp'
        self.assertTrue(DIAGNOSTICS_WORKFLOW.exists())
        self.assertTrue(DIAGNOSTICS_SCRIPT.exists())
        self.assertTrue(WINDOWS_DIAGNOSTICS_RUNNER.exists())
        self.assertFalse((archive / 'ci-precision-diagnostics.yml').exists())
        self.assertFalse((archive / 'precision_experiments.py').exists())

        text = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('workflow_dispatch:', text)
        self.assertNotIn('push:', text)
        self.assertNotIn('pull_request:', text)
        self.assertNotIn('schedule:', text)
        self.assertIn('python .github/workflows/run_paired_precision_diagnostics.py', text)
        self.assertIn('--script .github/workflows/precision_experiments.py', text)
        self.assertIn('run_windows_precision_diagnostics.ps1', text)
        self.assertIn('paired-linux:', text)
        self.assertIn('paired-macos:', text)
        self.assertIn('paired-windows:', text)
        self.assertNotIn('matrix.family', text)
        self.assertIn('--repeats "${{ inputs.repeats }}"', text)
        self.assertIn('uses: actions/upload-artifact@v7', text)
        self.assertEqual(text.count('uses: actions/upload-artifact@v7'), 3)
        self.assertEqual(text.count('if: always()'), 8)

    def test_diagnostics_cover_retained_nodeids_and_snapshot_policy(self):
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        script = DIAGNOSTICS_SCRIPT.read_text(encoding='utf-8')
        experiments = (
            'eom', 'pbc-tdhf', 'pbc-hse06', 'pbc-hse03', 'ucasscf',
            'sa4-newton', 'sgx', 'tddft', 'analyze',
        )
        for experiment in experiments:
            self.assertIn(f'- {experiment}', workflow)
            self.assertIn(repr(experiment), script)
        for nodeid in (WORKFLOW_DIR / 'precision-selected-nodeids.txt').read_text(encoding='utf-8').splitlines():
            if nodeid.strip():
                self.assertIn(repr(nodeid), script)
        self.assertIn('save_snapshot_once', script)
        self.assertIn('array_metadata', script)
        self.assertIn("all(record['status'] == 'exception'", script)

    def test_formal_diagnostics_run_all_nodeids_with_early_stop(self):
        workflow = DIAGNOSTICS_WORKFLOW.read_text(encoding='utf-8')
        script = DIAGNOSTICS_SCRIPT.read_text(encoding='utf-8')
        self.assertIn('- all', workflow)
        self.assertIn('default: all', workflow)
        self.assertIn('default: "200"', workflow)
        self.assertNotIn('threads: ["1", "4"]', workflow)
        self.assertNotIn('matrix.threads', workflow)
        self.assertIn('run_paired_precision_diagnostics.py', workflow)
        self.assertIn("def nodeid_complete(records, nodeid):", script)
        self.assertIn("if args.experiment == 'all':", script)
        self.assertIn('nodeid_complete(recorder.records, nodeid)', script)

    def test_runners_repeat_each_selected_test_one_hundred_times(self):
        self.assertIn('repeats=100', UNIX_RUNNER.read_text(encoding='utf-8'))
        self.assertIn('"-Repeats", "100"', WINDOWS_RUNNER.read_text(encoding='utf-8'))

    def test_workflow_splits_each_platform_into_three_nodeid_shards(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertEqual(text.count('shard: [0, 1, 2]'), 2)
        self.assertIn('PRECISION_SHARD_INDEX: ${{ matrix.shard }}', text)
        self.assertIn('-ShardIndex ${{ matrix.shard }}', text)
        self.assertIn('-ShardCount 3', text)
        self.assertIn('-shard-${{ matrix.shard }}', text)

    def test_runners_write_only_the_nodeids_assigned_to_the_shard(self):
        unix = UNIX_RUNNER.read_text(encoding='utf-8')
        windows = WINDOWS_RUNNER.read_text(encoding='utf-8')
        self.assertIn('index % shard_count == shard_index', unix)
        self.assertIn('printf \'%s\\n\' "${tests[@]}" > "$results_dir/selected-nodeids.txt"', unix)
        self.assertIn('$index % $ShardCount -eq $ShardIndex', windows)
        self.assertIn('$selectedNodeIds | Set-Content -LiteralPath $NodeIdFile', windows)


if __name__ == '__main__':
    unittest.main()
