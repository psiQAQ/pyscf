param(
    [string]$EnvironmentFile = "tools/windows/environment.yml"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$EnvironmentPath = Join-Path $RepoRoot $EnvironmentFile

conda env create --file $EnvironmentPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create Windows build environment from $EnvironmentFile"
}
