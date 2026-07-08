import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "windows-ci.yml"


class WindowsCIWorkflowTests(unittest.TestCase):
    def test_windows_ci_workflow_exists(self):
        self.assertTrue(WORKFLOW.exists())

    def test_workflow_defines_pr_and_full_jobs(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: Windows CI", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("windows-wheel-pr:", text)
        self.assertIn("windows-wheel-full:", text)
        self.assertIn("runs-on: windows-latest", text)
        self.assertIn("timeout-minutes: 90", text)
        self.assertIn("timeout-minutes: 180", text)
        self.assertIn("github.event_name == 'push' || github.event_name == 'pull_request'", text)
        self.assertIn("github.event_name == 'workflow_dispatch'", text)

    def test_workflow_reuses_existing_windows_entrypoints(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("conda-incubator/setup-miniconda@v4", text)
        self.assertIn("msys2/setup-msys2@v2", text)
        self.assertIn("tools/windows/environment.yml", text)
        self.assertIn("tools/windows/environment-test.yml", text)
        self.assertIn("tools/windows/build-wheel.ps1", text)
        self.assertIn("tools/windows/verify-installed-wheel.ps1", text)
        self.assertIn("-SkipBuild", text)
        self.assertIn("Verify installed wheel subset", text)
        self.assertIn("Verify installed wheel full sweep", text)
        self.assertIn("-TestRoots 'pyscf\\gto\\test','pyscf\\scf\\test'", text)

    def test_workflow_uploads_windows_artifacts(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertIn("windows-ci-pr-artifacts", text)
        self.assertIn("windows-ci-full-artifacts", text)
        self.assertIn("dist/*.whl", text)
        self.assertIn("tools/windows/build-logs/**", text)
        self.assertIn("tools/windows/reports/**", text)


if __name__ == "__main__":
    unittest.main()
