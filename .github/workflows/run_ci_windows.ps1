param(
    [ValidateSet("pr", "full")]
    [string]$Mode = "pr",
    [string]$BuildEnvName = "pyscf-win313",
    [string]$TestEnvName = "pyscf-win313-test",
    [string]$RuntimeDllDir = ""
)

$ErrorActionPreference = "Stop"
$WindowsWorkflowDir = Join-Path $PSScriptRoot "ci_windows"

& (Join-Path $WindowsWorkflowDir "create_build_env.ps1")
& (Join-Path $WindowsWorkflowDir "build_pyscf.ps1") `
    -BuildEnvName $BuildEnvName `
    -RuntimeDllDir $RuntimeDllDir
& (Join-Path $WindowsWorkflowDir "create_test_env.ps1") `
    -TestEnvName $TestEnvName
& (Join-Path $WindowsWorkflowDir "run_tests.ps1") `
    -Mode $Mode `
    -TestEnvName $TestEnvName `
    -RuntimeDllDir $RuntimeDllDir
