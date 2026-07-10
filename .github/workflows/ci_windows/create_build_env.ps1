param(
    [string]$BuildEnvName = "pyscf-win313",
    [ValidatePattern("^\d+\.\d+$")]
    [string]$PythonVersion = "3.13",
    [string]$EnvironmentFile = ".github/workflows/ci_windows/environment-build.yml"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$EnvironmentPath = Join-Path $RepoRoot $EnvironmentFile

if (-not (Test-Path $EnvironmentPath -PathType Leaf)) {
    throw "Windows build environment template was not found: $EnvironmentPath"
}

$TemporaryEnvironmentPath = [System.IO.Path]::GetTempFileName()
try {
    $contents = Get-Content -LiteralPath $EnvironmentPath -Raw
    $contents = $contents -replace '(?m)^name:\s*.*$', "name: $BuildEnvName"
    $contents = $contents -replace '(?m)^  - python=.*$', "  - python=$PythonVersion"
    [System.IO.File]::WriteAllText($TemporaryEnvironmentPath, $contents, (New-Object System.Text.UTF8Encoding($false)))

    conda env create --file $TemporaryEnvironmentPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create Windows build environment $BuildEnvName for Python $PythonVersion"
    }
}
finally {
    Remove-Item -LiteralPath $TemporaryEnvironmentPath -Force -ErrorAction SilentlyContinue
}
