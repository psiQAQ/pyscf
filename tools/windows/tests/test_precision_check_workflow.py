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

    def test_check_workflow_has_exact_seven_matrix_combinations(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        combinations = (
            ('ubuntu-latest', '3.8'),
            ('ubuntu-latest', '3.12'),
            ('ubuntu-latest', '3.13'),
            ('macos-latest', '3.8'),
            ('macos-latest', '3.13'),
            ('windows-latest', '3.12'),
            ('windows-latest', '3.13'),
        )
        for os_name, python_version in combinations:
            entry = f'- os: {os_name}\n            python-version: "{python_version}"'
            self.assertEqual(text.count(entry), 1, entry)
        self.assertNotIn('- os: macos-latest\n            python-version: "3.12"', text)
        self.assertNotIn('- os: windows-latest\n            python-version: "3.8"', text)

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


if __name__ == '__main__':
    unittest.main()
