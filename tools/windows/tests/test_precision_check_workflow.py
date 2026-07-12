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
WINDOWS_RUNNER = WORKFLOW_DIR / 'run_windows_precision_tests.ps1'
DIAGNOSTICS_WORKFLOW = WORKFLOW_DIR / 'ci-precision-diagnostics.yml'
DIAGNOSTICS_SCRIPT = WORKFLOW_DIR / 'precision_experiments.py'
WINDOWS_DIAGNOSTICS_RUNNER = WORKFLOW_DIR / 'run_windows_precision_diagnostics.ps1'
PAIRED_DIAGNOSTICS_WORKFLOW = DIAGNOSTICS_WORKFLOW
PAIRED_DIAGNOSTICS_RUNNER = WORKFLOW_DIR / 'run_paired_precision_diagnostics.py'


class PrecisionCheckWorkflowTests(unittest.TestCase):
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
