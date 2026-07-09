param(
    [ValidateSet("full", "check")]
    [string]$Mode = "full",
    [string]$BuildEnvName = "pyscf-win313",
    [string]$TestEnvName = "pyscf-win313-test",
    [string]$RuntimeDllDir = ""
)

$ErrorActionPreference = "Stop"
$WindowsWorkflowDir = Join-Path $PSScriptRoot "ci_windows"

& (Join-Path $WindowsWorkflowDir "create_build_env.ps1")
$BuildArgs = @(
    "--no-capture-output",
    "-n", $BuildEnvName,
    "powershell",
    "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $WindowsWorkflowDir "build_wheel_ci.ps1")
)
if ($RuntimeDllDir) {
    $BuildArgs += @("-RuntimeDllDir", $RuntimeDllDir)
}
conda run @BuildArgs
if ($LASTEXITCODE -ne 0) {
    throw "Failed to build the Windows wheel"
}
& (Join-Path $WindowsWorkflowDir "create_test_env.ps1") `
    -TestEnvName $TestEnvName
& (Join-Path $WindowsWorkflowDir "run_tests.ps1") `
    -Mode $Mode `
    -TestEnvName $TestEnvName
