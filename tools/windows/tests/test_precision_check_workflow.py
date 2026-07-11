import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW_DIR = REPO_ROOT / '.github' / 'workflows'
WORKFLOW = WORKFLOW_DIR / 'ci-precision-check.yml'
UNIX_RUNNER = WORKFLOW_DIR / 'run_unix_precision_tests.sh'
WINDOWS_RUNNER = WORKFLOW_DIR / 'run_windows_precision_tests.ps1'


class PrecisionCheckWorkflowTests(unittest.TestCase):
    def test_check_workflow_replaces_old_precision_workflow(self):
        self.assertTrue(WORKFLOW.exists())
        self.assertFalse((WORKFLOW_DIR / 'ci-linux-precision.yml').exists())
        self.assertTrue(UNIX_RUNNER.exists())
        self.assertFalse((WORKFLOW_DIR / 'run_linux_precision_tests.sh').exists())

    def test_check_workflow_has_approved_triggers_and_jobs(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        for trigger in ('push:', 'pull_request:', 'workflow_dispatch:'):
            self.assertIn(trigger, text)
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

    def test_diagnostics_are_archived_together(self):
        archive = WORKFLOW_DIR / 'tmp'
        self.assertTrue((archive / 'ci-precision-diagnostics.yml').exists())
        self.assertTrue((archive / 'precision_experiments.py').exists())
        self.assertFalse((WORKFLOW_DIR / 'ci-precision-diagnostics.yml').exists())
        self.assertFalse((WORKFLOW_DIR / 'precision_experiments.py').exists())

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
