import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / '.github' / 'workflows' / 'ci-windows.yml'
RUN_CI_WINDOWS = REPO_ROOT / '.github' / 'workflows' / 'run_ci_windows.ps1'
RUN_TESTS = REPO_ROOT / '.github' / 'workflows' / 'ci_windows' / 'run_tests.ps1'
VERIFY = REPO_ROOT / '.github' / 'workflows' / 'ci_windows' / 'verify_installed_wheel_ci.ps1'


class WindowsCIWorkflowTests(unittest.TestCase):
    def test_windows_ci_workflow_exists(self):
        self.assertTrue(WORKFLOW.exists())
        self.assertTrue(RUN_CI_WINDOWS.exists())
        self.assertTrue(RUN_TESTS.exists())
        self.assertTrue(VERIFY.exists())

    def test_workflow_defines_manual_full_validation_only(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('name: Windows CI', text)
        self.assertIn('workflow_dispatch:', text)
        self.assertIn('windows-build-full:', text)
        self.assertNotIn('windows-build-check:', text)
        self.assertNotIn('push:', text)
        self.assertNotIn('pull_request:', text)
        self.assertNotIn('schedule:', text)
        self.assertNotIn('if: ${{ false }}', text)
        self.assertIn('runs-on: windows-latest', text)
        self.assertIn('timeout-minutes: 180', text)

    def test_workflow_runs_full_through_existing_entrypoint(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('conda-incubator/setup-miniconda@v4', text)
        self.assertIn('msys2/setup-msys2@v2', text)
        self.assertIn('.github\\workflows\\run_ci_windows.ps1', text)
        self.assertIn('-Mode full', text)

    def test_windows_ci_helpers_keep_check_and_full_entrypoints(self):
        wrapper = RUN_CI_WINDOWS.read_text(encoding='utf-8')
        helper = RUN_TESTS.read_text(encoding='utf-8')
        self.assertIn('ci_windows', wrapper)
        self.assertIn('create_build_env.ps1', wrapper)
        self.assertIn('create_test_env.ps1', wrapper)
        self.assertIn('build_wheel_ci.ps1', wrapper)
        self.assertIn('run_tests.ps1', wrapper)
        self.assertIn('verify_installed_wheel_ci.ps1', helper)
        verify_text = VERIFY.read_text(encoding='utf-8')
        self.assertIn('if ($Mode -eq "full")', verify_text)
        self.assertIn('if ($Mode -eq "check")', verify_text)

    def test_workflow_uploads_windows_artifacts(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('actions/upload-artifact@v7', text)
        self.assertIn('windows-build-artifacts', text)
        self.assertIn('if: always()', text)
        self.assertIn('tmp/precision-results/**', text)
        self.assertIn('.github/workflows/ci_windows/build-logs/**', text)
        self.assertIn('dist/*.whl', text)
        self.assertIn('include-hidden-files: true', text)

    def test_runner_records_source_revision_before_build(self):
        text = RUN_CI_WINDOWS.read_text(encoding='utf-8')
        revision = 'git -C $RepoRoot rev-parse HEAD'
        self.assertIn(revision, text)
        self.assertIn('source-revision.txt', text)
        self.assertLess(text.index(revision), text.index('create_build_env.ps1'))
        self.assertLess(
            text.index('source-revision.txt'), text.index('create_build_env.ps1'))


if __name__ == '__main__':
    unittest.main()
