param(
    [string]$BuildEnvName = "pyscf-win313",
    [string]$RuntimeDllDir = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$BuildScript = Join-Path $RepoRoot ".github\workflows\ci_windows\build_wheel_ci.ps1"

$BuildArgs = @(
    "--no-capture-output",
    "-n", $BuildEnvName,
    "powershell",
    "-ExecutionPolicy", "Bypass",
    "-File", $BuildScript,
    "-Clean"
)
if ($RuntimeDllDir) {
    $BuildArgs += @("-RuntimeDllDir", $RuntimeDllDir)
}

conda run @BuildArgs
if ($LASTEXITCODE -ne 0) {
    throw "Failed to build the Windows wheel"
}
