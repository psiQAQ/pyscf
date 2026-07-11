param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$BuildEnvName,
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$TestEnvName,
    [Parameter(Mandatory)]
    [ValidatePattern("^\d+\.\d+$")]
    [string]$PythonVersion,
    [string]$RuntimeDllDir = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$WindowsWorkflowDir = Join-Path $PSScriptRoot "ci_windows"
$ResultsDir = Join-Path $RepoRoot "tmp\precision-results"
$BuildEnvironmentDir = Join-Path $ResultsDir "environment\build"
$TestEnvironmentDir = Join-Path $ResultsDir "environment\test"
$NodeIdSource = Join-Path $PSScriptRoot "precision-selected-nodeids.txt"
$NodeIdFile = Join-Path $ResultsDir "selected-nodeids.txt"
$VerifyScript = Join-Path $WindowsWorkflowDir "verify_installed_wheel_ci.ps1"
$CollectorScript = Join-Path $PSScriptRoot "collect_precision_environment.py"

if (-not (Test-Path -LiteralPath $NodeIdSource -PathType Leaf)) {
    throw "Precision node-ID file was not found: $NodeIdSource"
}

Remove-Item -LiteralPath $ResultsDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $BuildEnvironmentDir, $TestEnvironmentDir -Force | Out-Null
Copy-Item -LiteralPath $NodeIdSource -Destination $NodeIdFile -Force

& (Join-Path $WindowsWorkflowDir "create_build_env.ps1") `
    -BuildEnvName $BuildEnvName `
    -PythonVersion $PythonVersion

$buildArgs = @(
    "--no-capture-output",
    "-n", $BuildEnvName,
    "powershell",
    "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $WindowsWorkflowDir "build_pyscf.ps1"),
    "-BuildEnvName", $BuildEnvName
)
if ($RuntimeDllDir) {
    $buildArgs += @("-RuntimeDllDir", $RuntimeDllDir)
}
conda run @buildArgs
if ($LASTEXITCODE -ne 0) {
    throw "Windows precision wheel build failed"
}

conda run --no-capture-output -n $BuildEnvName python $CollectorScript --snapshot-dir $BuildEnvironmentDir
if ($LASTEXITCODE -ne 0) {
    throw "Failed to collect the Windows precision build environment"
}
$buildCondaList = conda list -n $BuildEnvName --json
if ($LASTEXITCODE -ne 0) {
    throw "Failed to list the Windows precision build environment"
}
$buildCondaList | Set-Content -LiteralPath (Join-Path $BuildEnvironmentDir "conda-list.json") -Encoding utf8
@(
    "phase=build",
    "python_version=$PythonVersion",
    "build_environment=$BuildEnvName",
    "test_environment=$TestEnvName",
    "repeat_count=1",
    "OMP_NUM_THREADS=$env:OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS=$env:OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS=$env:MKL_NUM_THREADS"
) | Set-Content -LiteralPath (Join-Path $BuildEnvironmentDir "runner-config.txt") -Encoding utf8

$wheel = Get-ChildItem -LiteralPath (Join-Path $RepoRoot "dist") -Filter "pyscf-*.whl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $wheel) {
    throw "Windows precision wheel metadata could not find a wheel under dist/."
}
[pscustomobject]@{
    file_name = $wheel.Name
    size_bytes = $wheel.Length
    sha256 = (Get-FileHash -LiteralPath $wheel.FullName -Algorithm SHA256).Hash
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $ResultsDir "wheel-metadata.json") -Encoding utf8

& (Join-Path $WindowsWorkflowDir "create_test_env.ps1") `
    -TestEnvName $TestEnvName `
    -PythonVersion $PythonVersion

$savedPythonPath = $env:PYTHONPATH
$verificationExit = 0
try {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    $verifyArgs = @(
        "--no-capture-output",
        "-n", $TestEnvName,
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", $VerifyScript,
        "-Mode", "check",
        "-Repeats", "1",
        "-ReportDir", $ResultsDir,
        "-SelectedPytestNodeIdsFile", $NodeIdFile
    )
    conda run @verifyArgs
    $verificationExit = $LASTEXITCODE

    conda run --no-capture-output -n $TestEnvName python $CollectorScript --snapshot-dir $TestEnvironmentDir
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to collect the Windows precision test environment"
    }
    $testCondaList = conda list -n $TestEnvName --json
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to list the Windows precision test environment"
    }
    $testCondaList | Set-Content -LiteralPath (Join-Path $TestEnvironmentDir "conda-list.json") -Encoding utf8
    @(
        "phase=test",
        "python_version=$PythonVersion",
        "build_environment=$BuildEnvName",
        "test_environment=$TestEnvName",
        "repeat_count=1",
        "verification_exit_code=$verificationExit",
        "OMP_NUM_THREADS=$env:OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS=$env:OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS=$env:MKL_NUM_THREADS"
    ) | Set-Content -LiteralPath (Join-Path $TestEnvironmentDir "runner-config.txt") -Encoding utf8
}
finally {
    if ($null -ne $savedPythonPath) {
        $env:PYTHONPATH = $savedPythonPath
    }
    else {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    }
}

if ($verificationExit -ne 0) {
    throw "Windows precision verification found failing attempts; see $ResultsDir"
}
