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
$EnvironmentDir = Join-Path $ResultsDir "environment"
$VerifyScript = Join-Path $WindowsWorkflowDir "verify_installed_wheel_ci.ps1"
$CollectorScript = Join-Path $PSScriptRoot "collect_precision_environment.py"

[string[]]$SelectedPytestNodeIds = @(
    "pyscf/adc/test/test_radc/test_ee_df_N2.py::KnownValues::test_ee_adc2",
    "pyscf/gw/test/test_gw.py::KnownValues::test_gwac_pade_frozen",
    "pyscf/grad/test/test_mcpdft.py::KnownValues::test_scanner",
    "pyscf/grad/test/test_mcpdft.py::KnownValues::test_gradients",
    "pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_ipccsd",
    "pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_eaccsd",
    "pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_casci_multistate",
    "pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_decomposition_hybrid_sa",
    "pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_decomposition_sa",
    "pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_energy_tot",
    "pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_kernel_steps_casscf",
    "pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_state_average",
    "pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_tpbe0",
    "pyscf/grad/test/test_pdft_diatomic_gradients.py::KnownValues::test_grad_h2_cms3ftlda22_sto3g_slow",
    "pyscf/mcpdft/test/test_diatomic_energies.py::KnownValues::test_h2_cms3ftlda22_sto3g",
    "pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_tdhf",
    "pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda",
    "pyscf/tdscf/test/test_tduks.py::KnownValues::test_analyze",
    "pyscf/tdscf/test/test_tduks.py::KnownValues::test_tddft_camb3lyp",
    "pyscf/mcscf/test/test_umc1step.py::KnownValues::test_ucasscf",
    "pyscf/mcscf/test/test_h2o.py::KnownValues::test_nosymm_sa4_newton",
    "pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad",
    "pyscf/fci/test/test_spin_op.py::KnownValues::test_contract_ss",
    "pyscf/dft/test/test_gks.py::KnownValues::test_collinear_gks_lda",
    "pyscf/adc/test/test_uadc/test_ip_cvs_P.py::KnownValues::test_ip_adc2x",
    "pyscf/mcscf/test/test_casci.py::KnownValues::test_with_x2c_scanner",
    "pyscf/tdscf/test/test_tdrks_vv10.py::KnownValues::test_wb97xv_tda_triplet",
    "pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_hse03_tda",
    "pyscf/cc/test/test_uccsdt_highm.py::KnownValues::test_zero_beta_electrons"
)

Remove-Item -LiteralPath $ResultsDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $EnvironmentDir -Force | Out-Null
$NodeIdFile = Join-Path $ResultsDir "selected-nodeids.txt"
$SelectedPytestNodeIds | Set-Content -LiteralPath $NodeIdFile -Encoding utf8

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
        "-Repeats", "10",
        "-ReportDir", $ResultsDir,
        "-SelectedPytestNodeIdsFile", $NodeIdFile
    )
    conda run @verifyArgs
    $verificationExit = $LASTEXITCODE

    conda run --no-capture-output -n $TestEnvName python -m pip freeze --all | Set-Content -LiteralPath (Join-Path $EnvironmentDir "pip-freeze.txt") -Encoding utf8
    conda run --no-capture-output -n $TestEnvName python -m pip list --format=json | Set-Content -LiteralPath (Join-Path $EnvironmentDir "pip-list.json") -Encoding utf8
    conda run --no-capture-output -n $TestEnvName python -m pip check | Set-Content -LiteralPath (Join-Path $EnvironmentDir "pip-check.txt") -Encoding utf8
    conda list -n $TestEnvName --json | Set-Content -LiteralPath (Join-Path $EnvironmentDir "conda-list.json") -Encoding utf8
    conda run --no-capture-output -n $TestEnvName python $CollectorScript (Join-Path $EnvironmentDir "runtime.json")
    Get-FileHash -LiteralPath (Get-ChildItem -LiteralPath (Join-Path $RepoRoot "dist") -Filter "pyscf-*.whl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Algorithm SHA256 |
        Select-Object Path, Algorithm, Hash |
        ConvertTo-Json |
        Set-Content -LiteralPath (Join-Path $EnvironmentDir "wheel-hash.json") -Encoding utf8
    @(
        "python_version=$PythonVersion",
        "build_environment=$BuildEnvName",
        "test_environment=$TestEnvName",
        "repeat_count=10",
        "verification_exit_code=$verificationExit",
        "OMP_NUM_THREADS=$env:OMP_NUM_THREADS"
    ) | Set-Content -LiteralPath (Join-Path $EnvironmentDir "runner-config.txt") -Encoding utf8
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
