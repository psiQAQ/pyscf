import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
VERIFY_WHEEL = REPO_ROOT / ".github" / "workflows" / "ci_windows" / "verify_installed_wheel_ci.ps1"


class VerifyInstalledWheelScriptTests(unittest.TestCase):
    def test_script_exists_and_reuses_ci_build_entrypoint(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        self.assertIn("param(", text)
        self.assertIn('[ValidateSet("full", "check")]', text)

    def test_script_checks_pytest_before_running_suite(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        self.assertIn('"pytest"', text)
        self.assertIn('"--version"', text)
        self.assertIn("pytest is not available", text)
        self.assertIn("function Invoke-ExternalCommandCapture", text)

    def test_script_prefers_active_conda_python_when_available(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        self.assertIn('$env:CONDA_PREFIX', text)
        self.assertIn('Join-Path $env:CONDA_PREFIX "python.exe"', text)
        self.assertIn('Test-Path $condaPython', text)
        self.assertIn("PythonExe resolved to a directory", text)
        self.assertIn('Test-Path $resolved -PathType Container', text)

    def test_script_runs_from_temp_root_and_clears_pythonpath(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        self.assertIn("Remove-Item Env:PYTHONPATH", text)
        self.assertIn("Join-Path $env:TEMP", text)
        self.assertIn("Push-Location $RunRoot", text)
        self.assertIn("function Invoke-PythonSnippetCapture", text)
        self.assertIn("UTF8Encoding($false)", text)
        self.assertIn("PYTEST_DISABLE_PLUGIN_AUTOLOAD", text)
        self.assertIn("function Write-PytestConfig", text)

    def test_script_discovers_installed_test_directories(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        self.assertIn("function Stage-TestDirectory", text)
        self.assertIn("Get-ChildItem -Directory -Recurse (Join-Path $RepoRoot \"pyscf\")", text)
        self.assertIn("Where-Object { $_.Name -eq 'test' }", text)
        self.assertIn("Sort-Object -Unique", text)
        self.assertIn("function Get-RelativePath", text)
        self.assertNotIn("[System.IO.Path]::GetRelativePath", text)
        self.assertNotIn(".Replace($RepoRoot", text)
        self.assertIn("Copy-Item -Path (Join-Path $SourceDirectory '*')", text)
        self.assertIn("Join-Path $RunRoot \"tests\"", text)
        self.assertIn("[string[]]$SelectedPytestNodeIds", text)
        self.assertIn("function Split-PytestNodeId", text)
        self.assertIn("function Get-PytestNodeGroups", text)
        self.assertIn('IndexOf("::"', text)
        self.assertNotIn('.Split("::", 2', text)
        self.assertIn('Join-Path $staged.staged_directory $nodeid.relative_file', text)
        self.assertNotIn("PYSCF_DESELECT_NODEIDS", text)

    def test_script_installs_latest_wheel_and_writes_ci_reports(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        self.assertIn("Get-ChildItem (Join-Path $RepoRoot \"dist\\pyscf-*.whl\")", text)
        self.assertIn('"pip"', text)
        self.assertIn('"install"', text)
        self.assertIn('"--force-reinstall"', text)
        self.assertIn("--no-deps", text)
        self.assertIn("installed-wheel-report.md", text)
        self.assertIn("installed-wheel-report.json", text)
        self.assertIn("installed-wheel-report-$reportStamp.md", text)
        self.assertIn("installed-wheel-report-$reportStamp.json", text)
        self.assertIn('.github\\workflows\\ci_windows\\reports', text)
        self.assertIn("pytest_summary", text)
        self.assertIn("Get-RelativePath -BasePath $RepoRoot -TargetPath $resolvedLog", text)
        self.assertNotIn('-PytestIni (Join-Path $RepoRoot "pytest.ini")', text)
        self.assertIn("function Write-TestProgress", text)
        self.assertIn("function Write-FailureSummary", text)
        self.assertIn('Write-Host ("[{0}/{1}] {2} completed: {3}. Log: {4}"', text)
        self.assertIn('Write-Host ("Failed verification targets: {0}" -f $failed.Count)', text)
        self.assertIn('Write-Host ("- {0} | Log: {1}" -f $result.logical_target, $resolvedLogPath)', text)
        self.assertIn("Resolve-Path $LogPath", text)
        self.assertIn("Write-TestProgress -CompletedCount $completedCount", text)
        self.assertIn("Write-FailureSummary -Results $results", text)
        self.assertIn("-CompletedCount $completedCount", text)
        self.assertIn("-TotalCount $totalTests", text)
        self.assertIn('throw "One or more verification targets failed. See installed-wheel-report.md for details."', text)

    def test_script_supports_full_and_check_modes(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        self.assertIn('[ValidateSet("full", "check")]', text)
        self.assertIn("[string[]]$SelectedPytestNodeIds", text)
        self.assertIn('if ($Mode -eq "check")', text)
        self.assertIn('if ($Mode -eq "full")', text)
        self.assertIn("test_eom_gccsd.py::KnownValues::test_ipccsd", text)
        self.assertIn("test_rks.py::Diamond::test_hse06_tda", text)
        self.assertIn("test_tduks.py::KnownValues::test_analyze", text)
        self.assertIn("test_uks.py::DiamondM06::test_tdhf", text)


if __name__ == "__main__":
    unittest.main()
