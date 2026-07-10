#
# Windows installed-wheel verification flow:
# 1. Resolve the repo root and target Python interpreter, then locate the newest built wheel under dist/.
# 2. Force-reinstall that wheel into the active verification environment so tests exercise the packaged artifact.
# 3. Create an isolated temporary run root with a local PySCF config and temp directory for this CI run only.
# 4. Copy the shared repo pytest.ini into the run root and scrub host-side pytest/PYTHONPATH overrides.
# 5. Stage each test directory into the temporary run root so pytest cannot accidentally import from the source tree.
# 6. Run either the selected PR check nodeids or the full per-directory sweep and save per-target logs.
# 7. Record per-target logs and summary reports, then count leftover temp files inside the disposable run root.
# 8. Fail the job when any verification target fails or when temporary files are left behind after the run.
#
param(
    [ValidateSet("full", "check")]
    [string]$Mode = "full",
    [string]$PythonExe = "",
    [string]$RepoRoot = "",
    [string]$ReportDir = ""
)

$ErrorActionPreference = "Stop"
$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

[string[]]$SelectedPytestNodeIds = @(
    "pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_ipccsd",
    "pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_tdhf",
    "pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda",
    "pyscf/tdscf/test/test_tduks.py::KnownValues::test_analyze"
)

function Resolve-RepoRoot {
    param([string]$ConfiguredValue)
    if ($ConfiguredValue) {
        return (Resolve-Path $ConfiguredValue).Path
    }
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
}

function Resolve-PythonExe {
    param([string]$ConfiguredValue)
    if ($ConfiguredValue) {
        $resolved = (Resolve-Path $ConfiguredValue).Path
        if (Test-Path $resolved -PathType Container) {
            throw "PythonExe resolved to a directory: $resolved"
        }
        return $resolved
    }
    # On Windows CI, PATH can still point at a host interpreter after conda activation.
    # Prefer CONDA_PREFIX explicitly so build/verify always target the intended environment.
    if ($env:CONDA_PREFIX) {
        $condaPython = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path $condaPython) {
            return (Resolve-Path $condaPython).Path
        }
    }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Python was not found on PATH. Activate the target conda environment or pass -PythonExe explicitly."
    }
    return $cmd.Source
}

function Invoke-ExternalCommandCapture {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList
    )
    # Start-Process + redirected temp files avoids PowerShell stream formatting differences and
    # gives stable stdout/stderr capture for Windows subprocesses that do not behave well in pipelines.
    $stdoutPath = [System.IO.Path]::GetTempFileName()
    $stderrPath = [System.IO.Path]::GetTempFileName()
    try {
        $process = Start-Process `
            -FilePath $FilePath `
            -ArgumentList $ArgumentList `
            -NoNewWindow `
            -PassThru `
            -Wait `
            -RedirectStandardOutput $stdoutPath `
            -RedirectStandardError $stderrPath
        $stdout = @()
        $stderr = @()
        if (Test-Path $stdoutPath) {
            $stdout = @(Get-Content $stdoutPath -ErrorAction SilentlyContinue)
        }
        if (Test-Path $stderrPath) {
            $stderr = @(Get-Content $stderrPath -ErrorAction SilentlyContinue)
        }
        return [pscustomobject]@{
            ExitCode = $process.ExitCode
            StdOut = $stdout
            StdErr = $stderr
            AllOutput = @($stdout + $stderr)
        }
    }
    finally {
        Remove-Item $stdoutPath -Force -ErrorAction SilentlyContinue
        Remove-Item $stderrPath -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-PythonSnippetCapture {
    param(
        [string]$PythonExe,
        [string]$Code
    )
    $snippetPath = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), ".py")
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    try {
        [System.IO.File]::WriteAllText($snippetPath, $Code, $utf8NoBom)
        return Invoke-ExternalCommandCapture -FilePath $PythonExe -ArgumentList @($snippetPath)
    }
    finally {
        Remove-Item $snippetPath -Force -ErrorAction SilentlyContinue
    }
}

function Ensure-Pytest {
    param([string]$PythonExe)
    $result = Invoke-ExternalCommandCapture -FilePath $PythonExe -ArgumentList @(
        "-m",
        "pytest",
        "--version"
    )
    if ($result.ExitCode -ne 0) {
        throw "pytest is not available in the target environment. Install pytest into that environment before running verify_installed_wheel_ci.ps1. Output: $($result.AllOutput -join ' ')"
    }
    return ($result.AllOutput | Select-Object -Last 1).ToString().Trim()
}

function Get-RelativePath {
    param(
        [string]$BasePath,
        [string]$TargetPath
    )
    $baseFull = [System.IO.Path]::GetFullPath($BasePath)
    $targetFull = [System.IO.Path]::GetFullPath($TargetPath)
    if (-not $baseFull.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $baseFull += [System.IO.Path]::DirectorySeparatorChar
    }
    $baseUri = [System.Uri]$baseFull
    $targetUri = [System.Uri]$targetFull
    $relativeUri = $baseUri.MakeRelativeUri($targetUri)
    $relative = [System.Uri]::UnescapeDataString($relativeUri.ToString())
    return $relative -replace '/', [System.IO.Path]::DirectorySeparatorChar
}

function Stage-TestDirectory {
    param(
        [string]$SourceDirectory,
        [string]$RunRoot,
        [string]$RepoRoot
    )
    $relative = Get-RelativePath -BasePath $RepoRoot -TargetPath $SourceDirectory
    $stageRoot = Join-Path $RunRoot "tests"
    # Run tests from a staged copy so installed-wheel verification cannot import helpers or packages
    # from the source tree by accident, which is easier to trip over on Windows than on Linux/macOS.
    $stagedDirectory = Join-Path $stageRoot (Sanitize-Name $relative)
    New-Item -ItemType Directory -Path $stagedDirectory -Force | Out-Null
    Copy-Item -Path (Join-Path $SourceDirectory '*') -Destination $stagedDirectory -Recurse -Force
    return [pscustomobject]@{
        staged_directory = $stagedDirectory
        logical_directory = $relative
    }
}

function Get-TestDirectories {
    param([string]$RepoRoot)
    return Get-ChildItem -Directory -Recurse (Join-Path $RepoRoot "pyscf") |
        Where-Object { $_.Name -eq 'test' } |
        Select-Object -ExpandProperty FullName |
        Sort-Object -Unique
}

function Split-PytestNodeId {
    param([string]$NodeId)
    $separatorIndex = $NodeId.IndexOf("::", [System.StringComparison]::Ordinal)
    if ($separatorIndex -lt 0) {
        return [pscustomobject]@{
            path_part = $NodeId
            suffix = ""
        }
    }
    return [pscustomobject]@{
        path_part = $NodeId.Substring(0, $separatorIndex)
        suffix = $NodeId.Substring($separatorIndex)
    }
}

function Get-PytestNodeGroups {
    param(
        [string]$RepoRoot,
        [string[]]$ConfiguredNodeIds
    )
    $groupTable = @{}
    foreach ($configuredNodeId in $ConfiguredNodeIds) {
        $parsed = Split-PytestNodeId -NodeId $configuredNodeId
        $sourcePath = (Resolve-Path (Join-Path $RepoRoot $parsed.path_part)).Path
        $sourceDirectory = Split-Path $sourcePath -Parent
        if ((Split-Path $sourceDirectory -Leaf) -ne "test") {
            throw "PytestNodeId must point to a file inside a test directory: $configuredNodeId"
        }
        if (-not $groupTable.ContainsKey($sourceDirectory)) {
            $groupTable[$sourceDirectory] = New-Object System.Collections.Generic.List[object]
        }
        $logicalPath = Get-RelativePath -BasePath $RepoRoot -TargetPath $sourcePath
        $relativeFile = Get-RelativePath -BasePath $sourceDirectory -TargetPath $sourcePath
        $groupTable[$sourceDirectory].Add([pscustomobject]@{
            logical_nodeid = $logicalPath + $parsed.suffix
            relative_file = $relativeFile
            suffix = $parsed.suffix
        })
    }
    return $groupTable.GetEnumerator() |
        Sort-Object Name |
        ForEach-Object {
            [pscustomobject]@{
                source_directory = $_.Key
                nodeids = @($_.Value)
            }
        }
}

function Get-LatestWheel {
    param([string]$RepoRoot)
    $wheel = Get-ChildItem (Join-Path $RepoRoot "dist\pyscf-*.whl") |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $wheel) {
        throw "No wheel was found under dist/. Build the wheel first."
    }
    return $wheel
}

function Install-Wheel {
    param(
        [string]$PythonExe,
        [string]$WheelPath
    )
    $result = Invoke-ExternalCommandCapture -FilePath $PythonExe -ArgumentList @(
        "-m",
        "pip",
        "install",
        "--force-reinstall",
        "--no-deps",
        $WheelPath
    )
    foreach ($line in $result.AllOutput) {
        Write-Host $line
    }
    if ($result.ExitCode -ne 0) {
        throw "Wheel installation failed: $WheelPath`n$($result.AllOutput -join [Environment]::NewLine)"
    }
}

function New-RunRoot {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $RunRoot = Join-Path $env:TEMP "pyscf-installed-wheel-$stamp"
    New-Item -ItemType Directory -Path $RunRoot -Force | Out-Null
    return $RunRoot
}

function Initialize-RunRoot {
    param([string]$RunRoot)
    $tmpDir = Join-Path $RunRoot "pyscftmpdir"
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
    $configPath = Join-Path $RunRoot ".pyscf_conf.py"
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($configPath, @(
        'pbc_tools_pbc_fft_engine = "NUMPY+BLAS"',
        'scf_hf_SCF_mute_chkfile = True',
        # Keep PySCF temp files inside the disposable run root so Windows file locking does not
        # leak leftovers into the checkout and so leftover-file checks stay local to this run.
        'TMPDIR = "./pyscftmpdir"'
    ), $utf8NoBom)
}

function Sanitize-Name {
    param([string]$Value)
    return ($Value -replace '[\\/:*?"<>| ]', '__')
}

function Get-PytestSummary {
    param([string[]]$OutputLines)
    $summaryLine = $null
    $reversedOutput = @($OutputLines)
    [array]::Reverse($reversedOutput)
    foreach ($line in $reversedOutput) {
        if ($line -match '\bin\b' -and $line -match '(subtests passed|subtests failed|passed|failed|error|errors|skipped|warning|warnings|xfailed|xpassed)') {
            $summaryLine = $line.Trim()
            break
        }
    }
    return $summaryLine
}

function Invoke-PytestTargets {
    param(
        [string]$PythonExe,
        [string[]]$Targets,
        [string]$PytestIni,
        [string]$LogPath
    )
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $argumentList = @(
        "-m",
        "pytest",
        "-s",
        "-c",
        $PytestIni
    )
    $argumentList += $Targets
    $result = Invoke-ExternalCommandCapture -FilePath $PythonExe -ArgumentList $argumentList
    $timer.Stop()
    $result.AllOutput | Set-Content -Path $LogPath -Encoding UTF8
    foreach ($line in $result.AllOutput) {
        Write-Host $line
    }
    $allOutput = @($result.AllOutput)
    return [pscustomobject]@{
        exit_code = $result.ExitCode
        duration_seconds = [math]::Round($timer.Elapsed.TotalSeconds, 3)
        log_path = $LogPath
        status = if ($result.ExitCode -eq 0) { "passed" } else { "failed" }
        pytest_summary = Get-PytestSummary -OutputLines $allOutput
    }
}

function Write-TestProgress {
    param(
        [int]$CompletedCount,
        [int]$TotalCount,
        [string]$LogicalDirectory,
        [string]$Status,
        [string]$LogPath
    )
    $statusLabel = if ($Status -eq "passed") { "pass" } else { "fail" }
    $resolvedLogPath = if (Test-Path $LogPath) {
        (Resolve-Path $LogPath).Path
    }
    else {
        [System.IO.Path]::GetFullPath($LogPath)
    }
    Write-Host ("[{0}/{1}] {2} completed: {3}. Log: {4}" -f $CompletedCount, $TotalCount, $LogicalDirectory, $statusLabel, $resolvedLogPath)
}

function Write-FailureSummary {
    param([psobject[]]$Results)
    $failed = @($Results | Where-Object status -eq "failed")
    if ($failed.Count -eq 0) {
        return
    }
    Write-Host ""
    Write-Host ("Failed verification targets: {0}" -f $failed.Count)
    foreach ($result in $failed) {
        $resolvedLogPath = if (Test-Path $result.log_path) {
            (Resolve-Path $result.log_path).Path
        }
        else {
            [System.IO.Path]::GetFullPath($result.log_path)
        }
        Write-Host ("- {0} | Log: {1}" -f $result.logical_target, $resolvedLogPath)
    }
}

function Write-Reports {
    param(
        [string]$RepoRoot,
        [string]$ReportDir,
        [psobject[]]$Results,
        [string]$WheelPath,
        [string]$PythonExe,
        [string]$RunRoot,
        [string]$PytestVersion,
        [psobject]$ImportInfo,
        [int]$TmpFileCount
    )
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
    $reportStamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $jsonPath = Join-Path $ReportDir "installed-wheel-report.json"
    $mdPath = Join-Path $ReportDir "installed-wheel-report.md"
    $datedJsonPath = Join-Path $ReportDir "installed-wheel-report-$reportStamp.json"
    $datedMdPath = Join-Path $ReportDir "installed-wheel-report-$reportStamp.md"
    $wheelRelativePath = Get-RelativePath -BasePath $RepoRoot -TargetPath $WheelPath
    $runRootLabel = [System.IO.Path]::GetFileName($RunRoot)

    $summary = [pscustomobject]@{
        generated_at = (Get-Date).ToString("s")
        mode = $Mode
        wheel = $WheelPath
        python = $PythonExe
        pytest = $PytestVersion
        run_root = $RunRoot
        environment_name = $ImportInfo.env_name
        tmpfile_count = $TmpFileCount
        passed = @($Results | Where-Object status -eq "passed").Count
        failed = @($Results | Where-Object status -eq "failed").Count
        total = @($Results).Count
        results = @(
            foreach ($result in $Results) {
                $resolvedLog = (Resolve-Path $result.log_path).Path
                [pscustomobject]@{
                    logical_target = $result.logical_target
                    status = $result.status
                    duration_seconds = $result.duration_seconds
                    pytest_summary = $result.pytest_summary
                    relative_log_path = Get-RelativePath -BasePath $RepoRoot -TargetPath $resolvedLog
                }
            }
        )
    }

    $summaryJson = $summary | ConvertTo-Json -Depth 5
    $summaryJson | Set-Content -Path $jsonPath -Encoding UTF8
    $summaryJson | Set-Content -Path $datedJsonPath -Encoding UTF8

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# Installed Wheel Verification Report")
    $lines.Add("")
    $lines.Add("- Mode: $Mode")
    $lines.Add("- Generated at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')")
    $lines.Add("- Conda environment: $($ImportInfo.env_name)")
    $lines.Add("- pytest: $PytestVersion")
    $lines.Add("- Wheel: $wheelRelativePath")
    $lines.Add("- Run root: $runRootLabel")
    $lines.Add("- Leftover temporary files: $TmpFileCount")
    $lines.Add("- Summary: passed $($summary.passed) / total $($summary.total), failed $($summary.failed)")
    $lines.Add("")
    $lines.Add("| Target | Status | Seconds | Pytest Summary | Log |")
    $lines.Add("| --- | --- | ---: | --- | --- |")
    foreach ($result in $summary.results) {
        $pytestSummary = if ($result.pytest_summary) { $result.pytest_summary } else { "(no pytest summary captured)" }
        $lines.Add("| $($result.logical_target) | $($result.status) | $($result.duration_seconds) | $pytestSummary | $($result.relative_log_path) |")
    }
    $lines | Set-Content -Path $mdPath -Encoding UTF8
    $lines | Set-Content -Path $datedMdPath -Encoding UTF8
}

try {
    $RepoRoot = Resolve-RepoRoot $RepoRoot
    $PythonExe = Resolve-PythonExe $PythonExe
    if (-not $ReportDir) {
        $ReportDir = Join-Path $RepoRoot ".github\workflows\ci_windows\reports"
    }

    $wheel = Get-LatestWheel -RepoRoot $RepoRoot
    Install-Wheel -PythonExe $PythonExe -WheelPath $wheel.FullName
    $pytestVersion = Ensure-Pytest -PythonExe $PythonExe

    if ($Mode -eq "check") {
        $runItems = @(Get-PytestNodeGroups -RepoRoot $RepoRoot -ConfiguredNodeIds $SelectedPytestNodeIds)
    }
    if ($Mode -eq "full") {
        $runItems = @(
            foreach ($testDir in (Get-TestDirectories -RepoRoot $RepoRoot)) {
                [pscustomobject]@{
                    source_directory = $testDir
                    nodeids = @()
                }
            }
        )
    }

    $RunRoot = New-RunRoot
    $logsDir = Join-Path $ReportDir "logs"
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Initialize-RunRoot -RunRoot $RunRoot
    $sourcePytestIni = Join-Path $RepoRoot "pytest.ini"
    if (-not (Test-Path $sourcePytestIni -PathType Leaf)) {
        throw "pytest.ini was not found at the repository root: $sourcePytestIni"
    }
    $pytestIni = Join-Path $RunRoot "pytest.ini"
    # Copy the repo config into the staged run root so pytest still uses the shared policy file
    # while the actual test execution stays isolated from the checkout.
    Copy-Item -LiteralPath $sourcePytestIni -Destination $pytestIni -Force

    $env:OMP_NUM_THREADS = "4"
    $savedPythonPath = $env:PYTHONPATH
    $savedPytestAddopts = $env:PYTEST_ADDOPTS
    $savedPytestDisablePluginAutoload = $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD
    # Source-tree PYTHONPATH and host-side pytest plugins are common false positives on Windows CI.
    # Clear both so this run exercises the installed wheel with only the local staged tests.
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    Remove-Item Env:PYTEST_ADDOPTS -ErrorAction SilentlyContinue
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

    $results = @()
    $importInfo = $null
    Push-Location $RunRoot
    try {
        $importResult = Invoke-PythonSnippetCapture -PythonExe $PythonExe -Code @'
import json
import importlib.metadata as metadata
import pathlib
import sys
import pyscf
import pyscf.lib
packages = {}
for name in ["pyscf", "numpy", "scipy", "h5py", "pytest", "pytest-cov", "pytest-timer", "geometric", "spglib", "pyberny"]:
    try:
        packages[name] = metadata.version(name)
    except metadata.PackageNotFoundError:
        pass
env_name = pathlib.Path(sys.executable).parent.name
print(json.dumps({"env_name": env_name, "packages": packages}, ensure_ascii=False))
'@
        if ($importResult.ExitCode -ne 0) {
            throw "Installed wheel import check failed: $($importResult.AllOutput -join ' ')"
        }
        $importInfo = ($importResult.AllOutput | Select-Object -Last 1 | ConvertFrom-Json)

        $totalTests = $runItems.Count
        $completedCount = 0
        foreach ($runItem in $runItems) {
            $staged = Stage-TestDirectory -SourceDirectory $runItem.source_directory -RunRoot $RunRoot -RepoRoot $RepoRoot
            $logicalTarget = $staged.logical_directory
            $pytestTargets = @($staged.staged_directory)
            $logLabel = $staged.logical_directory

            if ($runItem.nodeids.Count -gt 0) {
                $pytestTargets = @(
                    foreach ($nodeid in $runItem.nodeids) {
                        (Join-Path $staged.staged_directory $nodeid.relative_file) + $nodeid.suffix
                    }
                )
                if ($runItem.nodeids.Count -eq 1) {
                    $logicalTarget = $runItem.nodeids[0].logical_nodeid
                    $logLabel = $logicalTarget
                }
                else {
                    $logicalTarget = "{0} ({1} nodeids)" -f $staged.logical_directory, $runItem.nodeids.Count
                    $logLabel = $logicalTarget
                }
            }

            $logName = (Sanitize-Name $logLabel) + ".log"
            $logPath = Join-Path $logsDir $logName
            $pytestResult = Invoke-PytestTargets -PythonExe $PythonExe -Targets $pytestTargets -PytestIni $pytestIni -LogPath $logPath
            $results += [pscustomobject]@{
                logical_target = $logicalTarget
                duration_seconds = $pytestResult.duration_seconds
                log_path = $pytestResult.log_path
                status = $pytestResult.status
                pytest_summary = $pytestResult.pytest_summary
            }
            $completedCount += 1
            Write-TestProgress -CompletedCount $completedCount -TotalCount $totalTests -LogicalDirectory $logicalTarget -Status $pytestResult.status -LogPath $pytestResult.log_path
        }

        $tmpDir = Join-Path $RunRoot "pyscftmpdir"
        $tmpFileCount = if (Test-Path $tmpDir) { @(Get-ChildItem -Force $tmpDir).Count } else { 0 }
        Write-Host "There are $tmpFileCount leftover temporary files"

        Write-Reports -RepoRoot $RepoRoot -ReportDir $ReportDir -Results $results -WheelPath $wheel.FullName -PythonExe $PythonExe -RunRoot $RunRoot -PytestVersion $pytestVersion -ImportInfo $importInfo -TmpFileCount $tmpFileCount
        Write-FailureSummary -Results $results

        $failedCount = @($results | Where-Object status -eq "failed").Count
        if ($failedCount -gt 0 -or $tmpFileCount -gt 0) {
            throw "One or more verification targets failed. See installed-wheel-report.md for details."
        }
    }
    finally {
        Pop-Location
        if ($null -ne $savedPythonPath) {
            $env:PYTHONPATH = $savedPythonPath
        }
        else {
            Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
        }
        if ($null -ne $savedPytestAddopts) {
            $env:PYTEST_ADDOPTS = $savedPytestAddopts
        }
        else {
            Remove-Item Env:PYTEST_ADDOPTS -ErrorAction SilentlyContinue
        }
        if ($null -ne $savedPytestDisablePluginAutoload) {
            $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = $savedPytestDisablePluginAutoload
        }
        else {
            Remove-Item Env:PYTEST_DISABLE_PLUGIN_AUTOLOAD -ErrorAction SilentlyContinue
        }
        if (Test-Path $RunRoot) {
            Remove-Item $RunRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}
finally {
    $Stopwatch.Stop()
    Write-Host ("Total verification time: {0:hh\:mm\:ss} ({1:N1} s)" -f $Stopwatch.Elapsed, $Stopwatch.Elapsed.TotalSeconds)
}
