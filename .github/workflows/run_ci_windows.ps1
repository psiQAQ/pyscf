param(
    [ValidateSet("full", "check")]
    [string]$Mode = "full",
    [string]$BuildEnvName = "pyscf-win313",
    [string]$TestEnvName = "pyscf-win313-test",
    [string]$RuntimeDllDir = "",
    [ValidateRange(1, 1000)]
    [int]$Repeats = 1,
    [string]$SelectedPytestNodeIdsFile = ".github/workflows/precision-selected-nodeids.txt",
    [string]$ResultsDir = "tmp/precision-results"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$WindowsWorkflowDir = Join-Path $PSScriptRoot "ci_windows"
$CollectorScript = Join-Path $PSScriptRoot "collect_precision_environment.py"
if (-not [System.IO.Path]::IsPathRooted($ResultsDir)) {
    $ResultsDir = Join-Path $RepoRoot $ResultsDir
}
if (-not [System.IO.Path]::IsPathRooted($SelectedPytestNodeIdsFile)) {
    $SelectedPytestNodeIdsFile = Join-Path $RepoRoot $SelectedPytestNodeIdsFile
}
if (-not (Test-Path -LiteralPath $SelectedPytestNodeIdsFile -PathType Leaf)) {
    throw "Selected pytest node-ID file was not found: $SelectedPytestNodeIdsFile"
}

$BuildEnvironmentDir = Join-Path $ResultsDir "environment\build"
Remove-Item -LiteralPath $ResultsDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $BuildEnvironmentDir -Force | Out-Null
Copy-Item -LiteralPath $SelectedPytestNodeIdsFile -Destination (Join-Path $ResultsDir "selected-nodeids.txt") -Force

& (Join-Path $WindowsWorkflowDir "create_build_env.ps1") -BuildEnvName $BuildEnvName
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

conda run --no-capture-output -n $BuildEnvName python $CollectorScript --snapshot-dir $BuildEnvironmentDir
if ($LASTEXITCODE -ne 0) {
    throw "Failed to collect the Windows build environment"
}
$buildCondaList = conda list -n $BuildEnvName --json
if ($LASTEXITCODE -ne 0) {
    throw "Failed to list the Windows build environment"
}
$buildCondaList | Set-Content -LiteralPath (Join-Path $BuildEnvironmentDir "conda-list.json") -Encoding utf8
@(
    "phase=build",
    "mode=$Mode",
    "repeat_count=$Repeats",
    "build_environment=$BuildEnvName",
    "test_environment=$TestEnvName",
    "OMP_NUM_THREADS=$env:OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS=$env:OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS=$env:MKL_NUM_THREADS"
) | Set-Content -LiteralPath (Join-Path $BuildEnvironmentDir "runner-config.txt") -Encoding utf8

& (Join-Path $WindowsWorkflowDir "create_test_env.ps1") -TestEnvName $TestEnvName
& (Join-Path $WindowsWorkflowDir "run_tests.ps1") `
    -Mode $Mode `
    -TestEnvName $TestEnvName `
    -Repeats $Repeats `
    -ReportDir $ResultsDir `
    -SelectedPytestNodeIdsFile (Join-Path $ResultsDir "selected-nodeids.txt")
