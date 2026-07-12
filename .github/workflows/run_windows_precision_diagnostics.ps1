param(
    [Parameter(Mandatory)][string]$BuildEnvName,
    [Parameter(Mandatory)][string]$TestEnvName,
    [Parameter(Mandatory)][ValidatePattern("^\d+\.\d+$")][string]$PythonVersion,
    [Parameter(Mandatory)][string]$Experiment,
    [Parameter(Mandatory)][ValidateRange(1, 1000)][int]$Repeats,
    [string]$RuntimeDllDir = "",
    [switch]$Paired
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$WindowsWorkflowDir = Join-Path $PSScriptRoot "ci_windows"
$OutputDir = if ($Paired) {
    Join-Path $RepoRoot "tmp\precision-thread-paired\$Experiment"
} else {
    Join-Path $RepoRoot "tmp\precision-diagnostics\$Experiment"
}
$Script = Join-Path $PSScriptRoot "precision_experiments.py"
$PairedRunner = Join-Path $PSScriptRoot "run_paired_precision_diagnostics.py"
$Collector = Join-Path $PSScriptRoot "collect_precision_environment.py"

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
& (Join-Path $WindowsWorkflowDir "create_build_env.ps1") `
    -BuildEnvName $BuildEnvName `
    -PythonVersion $PythonVersion

$buildArgs = @(
    "--no-capture-output", "-n", $BuildEnvName,
    "powershell", "-ExecutionPolicy", "Bypass", "-File",
    (Join-Path $WindowsWorkflowDir "build_pyscf.ps1"),
    "-BuildEnvName", $BuildEnvName
)
if ($RuntimeDllDir) {
    $buildArgs += @("-RuntimeDllDir", $RuntimeDllDir)
}
conda run @buildArgs
if ($LASTEXITCODE -ne 0) { throw "Windows diagnostic wheel build failed" }

& (Join-Path $WindowsWorkflowDir "create_test_env.ps1") `
    -TestEnvName $TestEnvName `
    -PythonVersion $PythonVersion

$wheel = Get-ChildItem -LiteralPath (Join-Path $RepoRoot "dist") -Filter "pyscf-*.whl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $wheel) { throw "No diagnostic wheel was found under dist/." }

conda run --no-capture-output -n $TestEnvName python -m pip install --force-reinstall --no-deps $wheel.FullName
if ($LASTEXITCODE -ne 0) { throw "Failed to install diagnostic wheel" }

$savedPythonPath = $env:PYTHONPATH
$diagnosticExit = 0
try {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    if ($Paired) {
        conda run --no-capture-output -n $TestEnvName python $PairedRunner `
            --script $Script `
            --experiment $Experiment `
            --repeats $Repeats `
            --output $OutputDir
    } else {
        conda run --no-capture-output -n $TestEnvName python $Script `
            --experiment $Experiment `
            --repeats $Repeats `
            --output $OutputDir
    }
    $diagnosticExit = $LASTEXITCODE

    conda run --no-capture-output -n $TestEnvName python $Collector `
        --snapshot-dir (Join-Path $OutputDir "environment\runtime")
    if ($LASTEXITCODE -ne 0) { throw "Failed to collect diagnostic environment" }
}
finally {
    if ($null -ne $savedPythonPath) { $env:PYTHONPATH = $savedPythonPath }
    else { Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue }
}

if ($diagnosticExit -ne 0) { throw "Precision diagnostics failed" }
