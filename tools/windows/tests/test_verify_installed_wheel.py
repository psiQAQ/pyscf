import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
VERIFY_WHEEL = REPO_ROOT / ".github" / "workflows" / "ci_windows" / "verify_installed_wheel_ci.ps1"


class VerifyInstalledWheelScriptTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("powershell") or shutil.which("pwsh"), "PowerShell is required")
    def test_staging_recreates_the_target_directory(self):
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        command = r'''
$scriptPath = $env:STAGE_TEST_SCRIPT
$source = $env:STAGE_TEST_SOURCE
$runRoot = $env:STAGE_TEST_RUN_ROOT
$repoRoot = $env:STAGE_TEST_REPO_ROOT
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $scriptPath, [ref]$tokens, [ref]$errors)
foreach ($name in @('Get-RelativePath', 'Sanitize-Name', 'Stage-TestDirectory')) {
    $node = $ast.FindAll({
        param($item)
        $item -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $item.Name -eq $name
    }, $true)[0]
    Invoke-Expression $node.Extent.Text
}
$first = Stage-TestDirectory -SourceDirectory $source -RunRoot $runRoot -RepoRoot $repoRoot
$sentinel = Join-Path $first.staged_directory 'sentinel.txt'
Set-Content -LiteralPath $sentinel -Value 'stale'
$null = Stage-TestDirectory -SourceDirectory $source -RunRoot $runRoot -RepoRoot $repoRoot
if (Test-Path -LiteralPath $sentinel) { throw 'stale staged file survived' }
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            source = root / "repo" / "pyscf" / "demo" / "test"
            source.mkdir(parents=True)
            (source / "test_demo.py").write_text("pass\n", encoding="utf-8")
            env = os.environ.copy()
            env.update({
                "STAGE_TEST_SCRIPT": str(VERIFY_WHEEL),
                "STAGE_TEST_SOURCE": str(source),
                "STAGE_TEST_RUN_ROOT": str(root / "run"),
                "STAGE_TEST_REPO_ROOT": str(root / "repo"),
            })
            result = subprocess.run(
                [powershell, "-NoProfile", "-Command", command],
                capture_output=True, text=True, check=False, env=env,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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
        self.assertIn("PYTEST_DISABLE_PLUGIN_AUTOLOAD", text)
        self.assertIn('Join-Path $RepoRoot "pytest.ini"', text)
        self.assertIn("pytest.ini was not found at the repository root", text)

    def test_script_discovers_installed_test_directories(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        self.assertIn("function Stage-TestDirectory", text)
        self.assertIn("Get-ChildItem -Directory -Recurse (Join-Path $RepoRoot \"pyscf\")", text)
        self.assertIn("Where-Object { $_.Name -eq 'test' }", text)
        self.assertIn("Sort-Object -Unique", text)
        self.assertIn("function Get-RelativePath", text)
        self.assertNotIn("[System.IO.Path]::GetRelativePath", text)
        self.assertNotIn(".Replace($RepoRoot", text)
        self.assertNotIn("function Get-LogicalPath", text)
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
        self.assertIn('Copy-Item -LiteralPath $sourcePytestIni -Destination $pytestIni -Force', text)
        self.assertIn("function Write-TestProgress", text)
        self.assertIn("function Write-FailureSummary", text)
        self.assertIn('Write-Host ("[{0}/{1}] {2} completed: {3}. Log: {4}"', text)
        self.assertIn('Write-Host ("Failed verification targets: {0}" -f $failed.Count)', text)
        self.assertIn('Write-Host ("- {0} | Log: {1}" -f $result.logical_target, $resolvedLogPath)', text)
        self.assertIn("Resolve-Path $LogPath", text)
        self.assertIn("Write-TestProgress -CompletedCount $completedCount", text)
        self.assertIn("Write-FailureSummary -Results $results", text)
        self.assertIn("$result = Invoke-ExternalCommandCapture -FilePath $PythonExe -ArgumentList $argumentList", text)
        self.assertIn("$result.AllOutput | Set-Content -Path $LogPath -Encoding UTF8", text)
        self.assertNotIn("& $PythonExe @argumentList 2>&1", text)
        self.assertIn("-CompletedCount $completedCount", text)
        self.assertIn("-TotalCount $totalTests", text)
        self.assertIn('throw "One or more verification targets failed. See installed-wheel-report.md for details."', text)

    def test_script_supports_full_and_check_modes(self):
        text = VERIFY_WHEEL.read_text(encoding="utf-8")
        selected_nodeids = (REPO_ROOT / ".github" / "workflows" / "precision-selected-nodeids.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn('[ValidateSet("full", "check")]', text)
        self.assertIn("[string[]]$SelectedPytestNodeIds", text)
        self.assertIn('if ($Mode -eq "check")', text)
        self.assertIn('if ($Mode -eq "full")', text)
        self.assertIn("precision-selected-nodeids.txt", text)
        self.assertIn("test_eom_gccsd.py::KnownValues::test_ipccsd", selected_nodeids)
        self.assertIn("test_rks.py::Diamond::test_hse06_tda", selected_nodeids)
        self.assertIn("test_tduks.py::KnownValues::test_analyze", selected_nodeids)
        self.assertIn("test_uks.py::DiamondM06::test_tdhf", selected_nodeids)
        self.assertNotIn("FullExcludedPytestNodeIds", text)
        self.assertNotIn("--deselect", text)


if __name__ == "__main__":
    unittest.main()
