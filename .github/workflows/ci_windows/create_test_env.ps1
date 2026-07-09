param(
    [string]$TestEnvName = "pyscf-win313-test",
    [string]$EnvironmentFile = ".github/workflows/ci_windows/environment-test.yml",
    [string]$RequirementsFile = ".github/workflows/ci_windows/requirements-test.txt"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$EnvironmentPath = Join-Path $RepoRoot $EnvironmentFile
$RequirementsPath = Join-Path $RepoRoot $RequirementsFile

conda env create --file $EnvironmentPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create Windows test environment from $EnvironmentFile"
}

conda run --no-capture-output -n $TestEnvName python -m pip install -r $RequirementsPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install Windows test-only dependencies from $RequirementsFile"
}
