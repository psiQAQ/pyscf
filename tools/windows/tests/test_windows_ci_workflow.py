import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci-windows.yml"
RUN_CI_WINDOWS = REPO_ROOT / ".github" / "workflows" / "run_ci_windows.ps1"
RUN_TESTS = REPO_ROOT / ".github" / "workflows" / "ci_windows" / "run_tests.ps1"
VERIFY = REPO_ROOT / ".github" / "workflows" / "ci_windows" / "verify_installed_wheel_ci.ps1"


class WindowsCIWorkflowTests(unittest.TestCase):
    def test_windows_ci_workflow_exists(self):
        self.assertTrue(WORKFLOW.exists())
        self.assertTrue(RUN_CI_WINDOWS.exists())
        self.assertTrue(RUN_TESTS.exists())
        self.assertTrue(VERIFY.exists())

    def test_workflow_defines_build_and_check_jobs(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: Windows CI", text)
        self.assertIn("https://docs.github.com/en/actions/language-and-framework-guides/using-python-with-github-actions", text)
        self.assertIn("psiQAQ", text)
        self.assertIn("jeanwsr", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("windows-build:", text)
        self.assertIn("windows-build-check:", text)
        self.assertIn("runs-on: windows-latest", text)
        self.assertIn("timeout-minutes: 180", text)
        self.assertIn("timeout-minutes: 90", text)
        self.assertIn("github.event_name == 'push' || github.event_name == 'pull_request'", text)
        self.assertIn("github.event_name == 'workflow_dispatch'", text)

    def test_workflow_runs_full_on_pr_and_check_on_dispatch(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("conda-incubator/setup-miniconda@v4", text)
        self.assertIn("msys2/setup-msys2@v2", text)
        self.assertIn(".github\\workflows\\run_ci_windows.ps1", text)
        self.assertIn("-Mode full", text)
        self.assertIn("-Mode check", text)

    def test_windows_ci_helpers_use_ci_local_entrypoints(self):
        wrapper = RUN_CI_WINDOWS.read_text(encoding="utf-8")
        helper = RUN_TESTS.read_text(encoding="utf-8")
        self.assertIn("ci_windows", wrapper)
        self.assertIn("create_build_env.ps1", wrapper)
        self.assertIn("create_test_env.ps1", wrapper)
        self.assertIn("build_wheel_ci.ps1", wrapper)
        self.assertIn("run_tests.ps1", wrapper)
        self.assertIn("verify_installed_wheel_ci.ps1", helper)
        self.assertNotIn("tools/windows/verify-installed-wheel.ps1", helper)
        self.assertNotIn("-PytestNodeIds", helper)
        self.assertNotIn("-ExcludePytestNodeIds", helper)
        verify_text = VERIFY.read_text(encoding="utf-8")
        self.assertIn('if ($Mode -eq "full")', verify_text)
        self.assertIn('if ($Mode -eq "check")', verify_text)

    def test_workflow_uploads_windows_artifacts(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertIn("windows-build-artifacts", text)
        self.assertIn("windows-build-check-artifacts", text)
        self.assertIn("dist/*.whl", text)
        self.assertIn(".github/workflows/ci_windows/build-logs/**", text)
        self.assertIn(".github/workflows/ci_windows/reports/**", text)


if __name__ == "__main__":
    unittest.main()
