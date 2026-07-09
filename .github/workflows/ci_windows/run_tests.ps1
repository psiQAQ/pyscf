param(
    [ValidateSet("full", "check")]
    [string]$Mode = "full",
    [string]$TestEnvName = "pyscf-win313-test"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$VerifyScript = Join-Path $RepoRoot ".github\workflows\ci_windows\verify_installed_wheel_ci.ps1"

$VerifyArgs = @(
    "--no-capture-output",
    "-n", $TestEnvName,
    "powershell",
    "-ExecutionPolicy", "Bypass",
    "-File", $VerifyScript,
    "-Mode", $Mode
)

conda run @VerifyArgs
if ($LASTEXITCODE -ne 0) {
    throw "Windows $Mode verification failed"
}
