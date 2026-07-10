param(
    [string]$TestEnvName = "pyscf-win313-test",
    [ValidatePattern("^\d+\.\d+$")]
    [string]$PythonVersion = "3.13",
    [string]$EnvironmentFile = ".github/workflows/ci_windows/environment-test.yml",
    [string]$RequirementsFile = ".github/workflows/ci_windows/requirements-test.txt"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$EnvironmentPath = Join-Path $RepoRoot $EnvironmentFile
$RequirementsPath = Join-Path $RepoRoot $RequirementsFile

if (-not (Test-Path $EnvironmentPath -PathType Leaf)) {
    throw "Windows test environment template was not found: $EnvironmentPath"
}

$TemporaryEnvironmentPath = [System.IO.Path]::GetTempFileName()
try {
    $contents = Get-Content -LiteralPath $EnvironmentPath -Raw
    $contents = $contents -replace '(?m)^name:\s*.*$', "name: $TestEnvName"
    $contents = $contents -replace '(?m)^  - python=.*$', "  - python=$PythonVersion"
    [System.IO.File]::WriteAllText($TemporaryEnvironmentPath, $contents, (New-Object System.Text.UTF8Encoding($false)))

    conda env create --file $TemporaryEnvironmentPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create Windows test environment $TestEnvName for Python $PythonVersion"
    }
}
finally {
    Remove-Item -LiteralPath $TemporaryEnvironmentPath -Force -ErrorAction SilentlyContinue
}

conda run --no-capture-output -n $TestEnvName python -m pip install -r $RequirementsPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install Windows test-only dependencies from $RequirementsFile"
}
