import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "windows-ci.yml"
RUN_CI_WINDOWS = REPO_ROOT / ".github" / "workflows" / "run_ci_windows.ps1"
RUN_TESTS = REPO_ROOT / ".github" / "workflows" / "ci_windows" / "run_tests.ps1"


class WindowsCIWorkflowTests(unittest.TestCase):
    def test_windows_ci_workflow_exists(self):
        self.assertTrue(WORKFLOW.exists())
        self.assertTrue(RUN_CI_WINDOWS.exists())
        self.assertTrue(RUN_TESTS.exists())

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
        self.assertIn(".github\\workflows\\run_ci_windows.ps1", text)
        self.assertIn("-Mode pr", text)
        self.assertIn("-Mode full", text)

    def test_windows_ci_helpers_reuse_existing_windows_entrypoints(self):
        wrapper = RUN_CI_WINDOWS.read_text(encoding="utf-8")
        helper = RUN_TESTS.read_text(encoding="utf-8")
        self.assertIn("ci_windows", wrapper)
        self.assertIn("create_build_env.ps1", wrapper)
        self.assertIn("create_test_env.ps1", wrapper)
        self.assertIn("build_pyscf.ps1", wrapper)
        self.assertIn("run_tests.ps1", wrapper)
        self.assertIn("tools/windows/verify-installed-wheel.ps1", helper)
        self.assertIn("-PytestNodeIds", helper)
        self.assertIn("-ExcludePytestNodeIds", helper)
        self.assertIn("test_eom_gccsd.py::KnownValues::test_ipccsd", helper)
        self.assertIn("test_eom_gccsd.py::KnownValues::test_eaccsd", helper)
        self.assertIn("test_dhf_slow.py::KnownValues::test_kernel", helper)
        self.assertIn("test_bz.py::KnownValues::test_mc1step_4o4e", helper)
        self.assertIn("test_rks.py::Diamond::test_hse06_tda", helper)
        self.assertIn("test_tduks.py::KnownValues::test_tddft_camb3lyp", helper)

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
