param(
    [Parameter(Mandatory = $true)]
    [string]$NodeIdsFile,
    [Parameter(Mandatory = $true)]
    [int]$Repeats,
    [Parameter(Mandatory = $true)]
    [string]$Profile,
    [Parameter(Mandatory = $true)]
    [string]$RuntimeDllDir,
    [string]$RepoRoot = '',
    [string]$ReportDirectory = 'tmp/precision-results'
)

$ErrorActionPreference = 'Stop'

if (-not $RepoRoot) {
    $RepoRoot = Join-Path $PSScriptRoot '..\..'
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$nodeidsPath = (Resolve-Path -LiteralPath $NodeIdsFile).Path
$runner = Join-Path $RepoRoot '.github\workflows\run_precision_tests.py'
$testedSha = if ($env:GITHUB_SHA) {
    $env:GITHUB_SHA
}
else {
    (& git -C $RepoRoot rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to determine tested SHA'
    }
}

# Validate the user-controlled selection before the expensive wheel build.
& python $runner `
    --nodeids-file $nodeidsPath `
    --repeats $Repeats `
    --profile $Profile `
    --tested-sha $testedSha `
    --working-directory $RepoRoot `
    --rootdir $RepoRoot `
    --pytest-config (Join-Path $RepoRoot 'pytest.ini') `
    --validate-only
if ($LASTEXITCODE -ne 0) {
    throw 'Precision input validation failed'
}

& (Join-Path $RepoRoot '.github\workflows\ci_windows\build_wheel.ps1') `
    -RepoRoot $RepoRoot `
    -RuntimeDllDir $RuntimeDllDir `
    -ReportDirectory $ReportDirectory
if ($LASTEXITCODE -ne 0) {
    throw 'Precision wheel build failed'
}

& (Join-Path $RepoRoot '.github\workflows\ci_windows\verify_installed_wheel.ps1') `
    -RepoRoot $RepoRoot `
    -ReportDirectory $ReportDirectory `
    -PrecisionNodeIdsFile $nodeidsPath `
    -PrecisionRepeats $Repeats `
    -PrecisionProfile $Profile `
    -TestedSha $testedSha
if ($LASTEXITCODE -ne 0) {
    throw 'Installed-wheel precision verification failed'
}
