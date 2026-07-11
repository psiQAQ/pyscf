param(
    [ValidateSet("full", "check")]
    [string]$Mode = "full",
    [string]$TestEnvName = "pyscf-win313-test",
    [ValidateRange(1, 1000)]
    [int]$Repeats = 1,
    [string]$ReportDir = "",
    [string]$SelectedPytestNodeIdsFile = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$VerifyScript = Join-Path $RepoRoot ".github\workflows\ci_windows\verify_installed_wheel_ci.ps1"
$CollectorScript = Join-Path $RepoRoot ".github\workflows\collect_precision_environment.py"
if (-not $ReportDir) {
    $ReportDir = Join-Path $RepoRoot "tmp\precision-results"
}
if (-not [System.IO.Path]::IsPathRooted($ReportDir)) {
    $ReportDir = Join-Path $RepoRoot $ReportDir
}

$VerifyArgs = @(
    "--no-capture-output",
    "-n", $TestEnvName,
    "powershell",
    "-ExecutionPolicy", "Bypass",
    "-File", $VerifyScript,
    "-Mode", $Mode,
    "-Repeats", $Repeats,
    "-ReportDir", $ReportDir
)
if ($SelectedPytestNodeIdsFile) {
    $VerifyArgs += @("-SelectedPytestNodeIdsFile", $SelectedPytestNodeIdsFile)
}

conda run @VerifyArgs
$verificationExit = $LASTEXITCODE

$TestEnvironmentDir = Join-Path $ReportDir "environment\test"
conda run --no-capture-output -n $TestEnvName python $CollectorScript --snapshot-dir $TestEnvironmentDir
if ($LASTEXITCODE -ne 0) {
    throw "Failed to collect the Windows test environment"
}
$testCondaList = conda list -n $TestEnvName --json
if ($LASTEXITCODE -ne 0) {
    throw "Failed to list the Windows test environment"
}
$testCondaList | Set-Content -LiteralPath (Join-Path $TestEnvironmentDir "conda-list.json") -Encoding utf8
@(
    "phase=test",
    "mode=$Mode",
    "repeat_count=$Repeats",
    "test_environment=$TestEnvName",
    "verification_exit_code=$verificationExit",
    "OMP_NUM_THREADS=$env:OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS=$env:OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS=$env:MKL_NUM_THREADS"
) | Set-Content -LiteralPath (Join-Path $TestEnvironmentDir "runner-config.txt") -Encoding utf8

if ($verificationExit -ne 0) {
    throw "Windows $Mode verification failed"
}
