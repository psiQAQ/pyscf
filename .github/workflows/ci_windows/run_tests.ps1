param(
    [ValidateSet("pr", "full")]
    [string]$Mode = "pr",
    [string]$TestEnvName = "pyscf-win313-test",
    [string]$RuntimeDllDir = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$VerifyScript = Join-Path $RepoRoot "tools/windows/verify-installed-wheel.ps1"

$PrPytestNodeIds = @(
    "pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_ipccsd",
    "pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_tdhf",
    "pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda",
    "pyscf/tdscf/test/test_tduks.py::KnownValues::test_analyze",
    "pyscf/tdscf/test/test_tduks.py::KnownValues::test_tddft_camb3lyp"
)

$FullExcludePytestNodeIds = @(
    "pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_ipccsd",
    "pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_eaccsd",
    "pyscf/fci/test/test_dhf_slow.py::KnownValues::test_kernel",
    "pyscf/fci/test/test_dhf_slow.py::KnownValues::test_solver",
    "pyscf/mcscf/test/test_bz.py::KnownValues::test_mc1step_4o4e",
    "pyscf/mcscf/test/test_bz.py::KnownValues::test_mc1step_9o8e",
    "pyscf/mcscf/test/test_bz.py::KnownValues::test_mc2step_4o4e"
)

$VerifyArgs = @(
    "--no-capture-output",
    "-n", $TestEnvName,
    "powershell",
    "-ExecutionPolicy", "Bypass",
    "-File", $VerifyScript,
    "-SkipBuild"
)
if ($RuntimeDllDir) {
    $VerifyArgs += @("-RuntimeDllDir", $RuntimeDllDir)
}
if ($Mode -eq "pr") {
    $VerifyArgs += @("-PytestNodeIds", ($PrPytestNodeIds -join ","))
}
else {
    $VerifyArgs += @("-ExcludePytestNodeIds", ($FullExcludePytestNodeIds -join ","))
}

conda run @VerifyArgs
if ($LASTEXITCODE -ne 0) {
    throw "Windows $Mode verification failed"
}
