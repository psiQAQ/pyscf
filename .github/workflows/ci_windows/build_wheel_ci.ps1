#
# Windows wheel build flow:
# 1. Resolve the repo root, Python interpreter, MSYS2 runtime directory, and toolchain executables.
# 2. Start a transcript so the full Windows build session is preserved in a standalone log file.
# 3. Prepend the conda/MSYS2 toolchain paths so CMake, Ninja, gcc, and runtime DLL lookup stay deterministic.
# 4. Optionally clean previous build/dist outputs when the caller requests a fresh rebuild.
# 5. Configure the Windows build environment variables used by setuptools/CMake/Ninja.
# 6. Copy the required MSYS2 runtime DLLs into pyscf/lib so the wheel can import on a clean machine.
# 7. Retry support-DLL collection after an initial bootstrap build when Windows dependencies are generated lazily.
# 8. Run the final wheel build and leave both the wheel artifact and the transcript log for later inspection.
#
param(
    [string]$PythonExe = "",
    [string]$RuntimeDllDir = "",
    [string]$RepoRoot = "",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$TranscriptStarted = $false
$LogPath = $null

$RuntimeDlls = @(
    # Windows wheels do not get the MSYS2 UCRT/OpenBLAS runtime "for free".
    # These DLLs must be bundled next to pyscf/lib binaries for import-time loading.
    "libgcc_s_seh-1.dll",
    "libgomp-1.dll",
    "libgfortran-5.dll",
    "libopenblas.dll",
    "libquadmath-0.dll",
    "libstdc++-6.dll",
    "libwinpthread-1.dll"
)

$SupportDlls = @(
    @("libcint.dll"),
    @("libxc.dll"),
    # xcfun shows up under either name depending on how the Windows dependency build exported it.
    @("xcfun.dll", "libxcfun.dll")
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
        return (Resolve-Path $ConfiguredValue).Path
    }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Python was not found on PATH. Activate the target conda environment or pass -PythonExe explicitly."
    }
    return $cmd.Source
}

function Require-Command {
    param(
        [string]$Name,
        [string]$Hint = ""
    )
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        if ($Hint) {
            throw "Missing required command: $Name. $Hint"
        }
        throw "Missing required command: $Name"
    }
    return $cmd.Source
}

function Resolve-NinjaExe {
    param(
        [string]$LibraryBin,
        [string]$ScriptsDir
    )
    $candidates = @(
        (Join-Path $LibraryBin "ninja.exe"),
        (Join-Path $ScriptsDir "ninja.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }
    throw "Missing required command: ninja. Install Ninja into the target conda environment."
}

function Resolve-RuntimeDllDir {
    param([string]$ConfiguredValue)
    if ($ConfiguredValue) {
        return (Resolve-Path $ConfiguredValue).Path
    }

    # Prefer the active gcc location first; hosted Windows runners often have more than one MSYS2 install.
    $gccCmd = Get-Command gcc -ErrorAction SilentlyContinue
    if ($gccCmd) {
        return (Split-Path $gccCmd.Source -Parent)
    }

    $candidates = @(
        "D:\msys64\ucrt64\bin",
        "C:\msys64\ucrt64\bin"
    )
    foreach ($candidate in $candidates) {
        if ((Test-Path (Join-Path $candidate "gcc.exe")) -and
            (Test-Path (Join-Path $candidate "libgcc_s_seh-1.dll"))) {
            return (Resolve-Path $candidate).Path
        }
    }

    throw "Unable to locate the MSYS2 UCRT64 runtime directory. Pass -RuntimeDllDir explicitly or install MSYS2 UCRT64 at D:\msys64\ucrt64\bin or C:\msys64\ucrt64\bin."
}

function Copy-RequiredDlls {
    param(
        [string]$RuntimeDllDir,
        [string]$LibDir
    )
    foreach ($name in $RuntimeDlls) {
        $source = Join-Path $RuntimeDllDir $name
        if (-not (Test-Path $source)) {
            throw "Missing runtime DLL: $source"
        }
        Copy-Item -LiteralPath (Join-Path $RuntimeDllDir $name) -Destination (Join-Path $LibDir $name) -Force
    }
}

function Copy-SupportDlls {
    param(
        [string]$DepsBinDir,
        [string]$LibDir,
        [switch]$AllowMissing
    )
    $missing = @()
    foreach ($candidates in $SupportDlls) {
        $source = $null
        $name = $null
        foreach ($candidate in $candidates) {
            $candidatePath = Join-Path $DepsBinDir $candidate
            if (Test-Path $candidatePath) {
                $source = $candidatePath
                $name = $candidate
                break
            }
        }
        if (-not $source) {
            if ($AllowMissing) {
                $missing += ,($candidates -join ', ')
                continue
            }
            throw "Missing support DLL. Checked: $($candidates -join ', ') under $DepsBinDir"
        }
        Copy-Item -LiteralPath $source -Destination (Join-Path $LibDir $name) -Force
    }
    return $missing
}

function Invoke-WheelBuild {
    param(
        [string]$PythonExe,
        [string]$RepoRoot
    )
    Push-Location $RepoRoot
    try {
        & $PythonExe -m build -x --wheel --no-isolation --outdir dist .
        if ($LASTEXITCODE -ne 0) {
            throw "Wheel build failed"
        }
    }
    finally {
        Pop-Location
    }
}

try {
    $RepoRoot = Resolve-RepoRoot $RepoRoot
    $BuildLogsDir = Join-Path $RepoRoot ".github\workflows\ci_windows\build-logs"
    New-Item -ItemType Directory -Path $BuildLogsDir -Force | Out-Null
    $LogPath = Join-Path $BuildLogsDir ("build-wheel-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
    Start-Transcript -Path $LogPath -Force | Out-Null
    $TranscriptStarted = $true
    Write-Host "Build log: $LogPath"

    $PythonExe = Resolve-PythonExe $PythonExe
    $PythonDir = Split-Path $PythonExe -Parent
    if ((Split-Path $PythonDir -Leaf) -ieq "Scripts") {
        $EnvRoot = Split-Path $PythonDir -Parent
    }
    else {
        $EnvRoot = $PythonDir
    }

    $LibraryBin = Join-Path $EnvRoot "Library\\bin"
    $ScriptsDir = Join-Path $EnvRoot "Scripts"
    $LibDir = Join-Path $RepoRoot 'pyscf\lib'
    $DepsBinDir = Join-Path $RepoRoot 'pyscf\lib\deps\bin'
    $RuntimeDllDir = Resolve-RuntimeDllDir -ConfiguredValue $RuntimeDllDir

    $BootstrapPaths = @(
        $RuntimeDllDir,
        $LibraryBin,
        $ScriptsDir,
        $PythonDir,
        $env:PATH
    ) | Where-Object { $_ } | Select-Object -Unique
    # Front-load the conda/MSYS2 toolchain so CMake, Ninja, gcc, and dependent DLL discovery resolve
    # against the intended Windows build environment instead of a host-global installation.
    $env:PATH = $BootstrapPaths -join ';'

    Require-Command "cmake" | Out-Null
    $NinjaExe = Resolve-NinjaExe -LibraryBin $LibraryBin -ScriptsDir $ScriptsDir
    Require-Command "gcc" | Out-Null
    Require-Command "g++" | Out-Null

    if ($Clean) {
        Remove-Item (Join-Path $RepoRoot "build") -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $RepoRoot "dist") -Recurse -Force -ErrorAction SilentlyContinue
    }

    $env:CC = "gcc"
    $env:CXX = "g++"
    $env:CMAKE_BUILD_PARALLEL_LEVEL = "8"
    # OpenBLAS is consumed through the MSYS2 import library on Windows; the .dll.a keeps CMake/Ninja
    # linking consistent with the runtime DLLs that are later copied into the wheel payload.
    $env:CMAKE_CONFIGURE_ARGS = "-G Ninja -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DBLAS_LIBRARIES=$RuntimeDllDir\\..\\lib\\libopenblas.dll.a -DENABLE_XCFUN=ON -DBUILD_XCFUN=ON"

    Copy-RequiredDlls -RuntimeDllDir $RuntimeDllDir -LibDir $LibDir
    $missingSupportDlls = @(Copy-SupportDlls -DepsBinDir $DepsBinDir -LibDir $LibDir -AllowMissing)
    if ($missingSupportDlls.Count -gt 0) {
        # Some support DLLs are generated only after the first dependency build pass on Windows.
        # Bootstrap once, then copy the freshly produced DLLs before the final wheel build.
        Write-Host "Missing support DLLs will be retried after the first wheel build pass."
        Invoke-WheelBuild -PythonExe $PythonExe -RepoRoot $RepoRoot
    }
    Copy-SupportDlls -DepsBinDir $DepsBinDir -LibDir $LibDir | Out-Null
    Invoke-WheelBuild -PythonExe $PythonExe -RepoRoot $RepoRoot
}
finally {
    if ($TranscriptStarted) {
        Stop-Transcript | Out-Null
        if ($LogPath) {
            Write-Host "Build log saved to: $LogPath"
        }
    }
    $Stopwatch.Stop()
    Write-Host ("Total build time: {0:hh\:mm\:ss} ({1:N1} s)" -f $Stopwatch.Elapsed, $Stopwatch.Elapsed.TotalSeconds)
}
