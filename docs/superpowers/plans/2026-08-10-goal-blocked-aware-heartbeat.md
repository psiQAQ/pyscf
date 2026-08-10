# Goal Blocked-Aware Heartbeat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unstable Stage 2 waiting monitor with one local runtime copy that can restore the exact blocked Goal to active after the exact CI run reaches a wake condition.

**Architecture:** Preserve the reviewed GoalBridge byte-for-byte and create one ignored runtime copy. Add one pure `blocked -> set` decision plus its self-test, then swap the single exact process by PID and record separate runtime provenance; scientific code, CI identity, validator, and the frozen helper remain unchanged.

**Tech Stack:** Windows PowerShell 5.1, Codex App Server Goal API through the existing script, GitHub CLI read-only polling, local `.agents/` state.

## Global Constraints

- Frozen helper remains `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1` with SHA-256 `4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639`.
- Runtime copy is `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1`; it is local ignored state and is never staged or pushed.
- Exact CI identity is run `31404086927`, head `2133114d93af1c7cb18f1acdc5693e871d8632db`, interval `1800`, wake threshold `300`.
- Stop processes only by captured PID after exact executable, script, run, head, interval, wake-threshold, and start-time checks.
- At all times there is at most one heartbeat. No dispatch, rerun, cancel, dependency change, scientific edit, selector change, assertion change, or artifact-gate change is allowed.
- The Goal thread ID remains `019f64bd-77a5-7573-88e9-fd80b1882e70`; objective text must remain unchanged.

---

### Task 1: TDD the isolated blocked-aware runtime copy

**Files:**
- Source only: `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1`
- Create: `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1`
- Record: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`

**Interfaces:**
- Consumes: `Get-TerminalActivationAction -Goal $Goal -ActivationUncertain $ActivationUncertain`, where `$Goal.status` is a string and `$ActivationUncertain` is a Boolean, from the frozen helper.
- Produces: the same function, with `status='blocked'` returning the existing action string `'set'`; all parameters and other return values remain unchanged.

- [ ] **Step 1: Freeze the source and create a byte-identical local copy**

Run in Windows PowerShell 5.1:

```powershell
$ErrorActionPreference = 'Stop'
$Source = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$Runtime = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1'
$ExpectedSourceSha = '4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
if ((Get-FileHash -Algorithm SHA256 $Source).Hash.ToLowerInvariant() -cne $ExpectedSourceSha) { throw 'Frozen source drift' }
if (Test-Path -LiteralPath $Runtime) { throw 'Blocked-aware runtime copy already exists' }
Copy-Item -LiteralPath $Source -Destination $Runtime
if ((Get-FileHash -Algorithm SHA256 $Runtime).Hash.ToLowerInvariant() -cne $ExpectedSourceSha) { throw 'Initial runtime copy is not byte-identical' }
```

- [ ] **Step 2: Add the failing pure self-test**

Use `apply_patch` on the runtime copy only. Immediately after the existing paused/active activation-action tests, add:

```powershell
$blockedAction = Get-TerminalActivationAction `
    -Goal ([pscustomobject]@{ status = 'blocked' }) `
    -ActivationUncertain $false
if ($blockedAction -ne 'set') {
    throw "blocked goal returned '$blockedAction'; expected 'set'"
}
```

Do not add the production branch yet.

- [ ] **Step 3: Run the RED test and prove the intended failure**

```powershell
$Runtime = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1'
$Raw = @(& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoProfile -ExecutionPolicy Bypass -File $Runtime -SelfTest 2>&1)
$Exit = $LASTEXITCODE
if ($Exit -eq 0) { throw 'Blocked self-test unexpectedly passed before implementation' }
$Text = ($Raw | ForEach-Object { [string]$_ }) -join "`n"
if ($Text -notmatch 'Goal status blocked is invalid during initial check') { throw "Wrong RED signature: $Text" }
```

Expected: exit nonzero with `Goal status blocked is invalid during initial check`.

- [ ] **Step 4: Add the minimum production branch and update the test count**

Use `apply_patch` on the runtime copy only. In `Get-TerminalActivationAction`, immediately after the existing paused branch, add:

```powershell
if ($Goal.status -eq 'blocked') {
    return 'set'
}
```

Change only the final self-test success text from `18 cases` to `19 cases`.

- [ ] **Step 5: Run GREEN, AST, encoding, and scope checks**

```powershell
$ErrorActionPreference = 'Stop'
$Source = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$Runtime = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1'
$Raw = @(& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoProfile -ExecutionPolicy Bypass -File $Runtime -SelfTest 2>&1)
if ($LASTEXITCODE -ne 0 -or (($Raw | ForEach-Object { [string]$_ }) -join "`n") -notmatch 'Heartbeat self-test passed \(19 cases\)') { throw 'Blocked-aware GREEN failed' }
$Tokens = $null; $Errors = $null
[void][Management.Automation.Language.Parser]::ParseFile($Runtime, [ref]$Tokens, [ref]$Errors)
if ($Errors.Count -ne 0) { throw 'Runtime AST invalid' }
$Bytes = [IO.File]::ReadAllBytes($Runtime)
if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) { throw 'Runtime has UTF-8 BOM' }
if (@($Bytes | Where-Object { $_ -eq 13 }).Count -ne 0) { throw 'Runtime is not LF-only' }
$SourceText = [IO.File]::ReadAllText($Source, (New-Object Text.UTF8Encoding($false)))
$RuntimeText = [IO.File]::ReadAllText($Runtime, (New-Object Text.UTF8Encoding($false)))
$BlockedBranch = "    if (`$Goal.status -eq 'blocked') {`n        return 'set'`n    }`n"
$BlockedTest = @'
$blockedAction = Get-TerminalActivationAction `
    -Goal ([pscustomobject]@{ status = 'blocked' }) `
    -ActivationUncertain $false
if ($blockedAction -ne 'set') {
    throw "blocked goal returned '$blockedAction'; expected 'set'"
}
'@
$BlockedTestText = $BlockedTest.Trim() + "`n"
if ([regex]::Matches($RuntimeText, [regex]::Escape($BlockedBranch)).Count -ne 1) { throw 'Blocked production branch count is not one' }
if ([regex]::Matches($RuntimeText, [regex]::Escape($BlockedTestText)).Count -ne 1) { throw 'Blocked self-test count is not one' }
if ([regex]::Matches($RuntimeText, [regex]::Escape("Heartbeat self-test passed (19 cases).")).Count -ne 1) { throw 'Updated self-test count marker is not one' }
$Normalized = $RuntimeText.Replace($BlockedBranch, '').Replace($BlockedTestText, '').Replace(
    "Heartbeat self-test passed (19 cases).",
    "Heartbeat self-test passed (18 cases).")
if ($Normalized -cne $SourceText) { throw 'Runtime copy has changes outside the blocked branch, blocked self-test, and test-count text' }
$RuntimeSha = (Get-FileHash -Algorithm SHA256 $Runtime).Hash.ToLowerInvariant()
Write-Output "BLOCKED_AWARE_RUNTIME_SHA256=$RuntimeSha"
```

- [ ] **Step 6: Mutation-check the new self-test without altering the final runtime**

```powershell
$ErrorActionPreference = 'Stop'
$Runtime = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1'
$Mutation = Join-Path $env:TEMP 'libxc-712-ci-heartbeat-blocked-aware-mutation.ps1'
$Utf8 = New-Object Text.UTF8Encoding($false)
$Text = [IO.File]::ReadAllText($Runtime, $Utf8)
$Branch = "    if (`$Goal.status -eq 'blocked') {`n        return 'set'`n    }`n"
if ($Text.IndexOf($Branch, [StringComparison]::Ordinal) -lt 0) { throw 'Mutation target missing' }
[IO.File]::WriteAllText($Mutation, $Text.Replace($Branch, ''), $Utf8)
try {
    $Raw = @(& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoProfile -ExecutionPolicy Bypass -File $Mutation -SelfTest 2>&1)
    if ($LASTEXITCODE -eq 0) { throw 'Removing blocked branch did not fail self-test' }
    if ((($Raw | ForEach-Object { [string]$_ }) -join "`n") -notmatch 'Goal status blocked is invalid during initial check') { throw 'Mutation failed for wrong reason' }
}
finally {
    Remove-Item -LiteralPath $Mutation -Force -ErrorAction SilentlyContinue
}
```

Expected: mutation exits nonzero for the blocked activation decision; final runtime file hash is unchanged.

---

### Task 2: Replace the exact monitor and enter the recoverable blocked state

**Files:**
- Execute: `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1`
- Modify: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Preserve: `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1`

**Interfaces:**
- Consumes: runtime-copy SHA from Task 1; exact old PID `24620`; run `31404086927`; head `2133114d93af1c7cb18f1acdc5693e871d8632db`.
- Produces: one new exact monitor PID and command line; exact Goal status `blocked`; active-document recovery evidence.

- [ ] **Step 1: Verify the old monitor and capture its immutable identity**

```powershell
$ErrorActionPreference = 'Stop'
$OldPid = 24620
$PowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$OldScript = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$RunId = '31404086927'; $Head = '2133114d93af1c7cb18f1acdc5693e871d8632db'
$Old = Get-CimInstance Win32_Process -Filter "ProcessId=$OldPid" -ErrorAction Stop
$Required = @($OldScript, $RunId, $Head, '-IntervalSeconds 1800', '-WakeAfterMinutes 300')
$Exact = $Old.ExecutablePath -ceq $PowerShell
foreach ($Token in $Required) { $Exact = $Exact -and ([string]$Old.CommandLine -like "*$Token*") }
if (-not $Exact) { throw 'Old monitor identity mismatch; refuse handoff' }
$OldProcess = Get-Process -Id $OldPid -ErrorAction Stop
$OldStartUtc = $OldProcess.StartTime.ToUniversalTime()
```

- [ ] **Step 2: Stop only the exact old PID and verify it is gone**

```powershell
$Process = Get-Process -Id $OldPid -ErrorAction Stop
if ($Process.StartTime.ToUniversalTime() -ne $OldStartUtc) { throw 'Old PID start-time mismatch' }
$Process.Kill()
if (-not $Process.WaitForExit(10000)) { throw 'Old monitor did not exit within 10 seconds' }
if ($null -ne (Get-CimInstance Win32_Process -Filter "ProcessId=$OldPid" -ErrorAction SilentlyContinue)) { throw 'Old monitor still exists' }
```

- [ ] **Step 3: Launch and verify one runtime-copy monitor**

```powershell
$Runtime = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1'
$Args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$Runtime,'-TargetRunIds',$RunId,'-TargetHeadSha',$Head,'-IntervalSeconds','1800','-WakeAfterMinutes','300')
$New = Start-Process -FilePath $PowerShell -ArgumentList $Args -WindowStyle Hidden -PassThru
try {
    $NewPid = $New.Id; $NewStartUtc = $New.StartTime.ToUniversalTime()
    Start-Sleep -Seconds 2
    if ($New.HasExited) { throw "New monitor exited early: $($New.ExitCode)" }
    $Cim = Get-CimInstance Win32_Process -Filter "ProcessId=$NewPid" -ErrorAction Stop
    $Required = @($Runtime, $RunId, $Head, '-IntervalSeconds 1800', '-WakeAfterMinutes 300')
    $Exact = $Cim.ExecutablePath -ceq $PowerShell
    foreach ($Token in $Required) { $Exact = $Exact -and ([string]$Cim.CommandLine -like "*$Token*") }
    if (-not $Exact) { throw 'New monitor identity mismatch' }
    $All = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
        $_.ProcessId -ne $PID -and $_.ExecutablePath -ceq $PowerShell -and
        ([string]$_.CommandLine).IndexOf('libxc-712-ci-heartbeat', [StringComparison]::OrdinalIgnoreCase) -ge 0
    })
    if ($All.Count -ne 1 -or $All[0].ProcessId -ne $NewPid) { throw 'Heartbeat handoff did not leave exactly one monitor' }
}
catch {
    $Primary = $_.Exception
    try { $New.Refresh(); if (-not $New.HasExited) { $New.Kill(); [void]$New.WaitForExit(10000) } } catch {}
    throw [InvalidOperationException]::new("New monitor launch failed: $($Primary.Message)", $Primary)
}
Write-Output "BLOCKED_AWARE_MONITOR_PID=$NewPid"
Write-Output "BLOCKED_AWARE_MONITOR_STARTED_AT=$($NewStartUtc.ToString('o'))"
Write-Output "BLOCKED_AWARE_MONITOR_COMMAND=$($Cim.CommandLine)"
```

- [ ] **Step 4: Mark the repeated scheduler failure as blocked and verify exact Goal identity**

Use the root Goal tool once:

```text
update_goal({"status":"blocked"})
```

Then call `get_goal({})` and require exact thread ID, unchanged objective, and `status=blocked`. If either tool call fails, stop the new exact PID, set the Goal to `active` with the frozen one-shot, and report the handoff failure.

- [ ] **Step 5: Record provenance and the terminal recovery command**

Use `apply_patch` on the active document only. Record these exact keys with observed values:

```markdown
- stage2_formal_monitor_replaced_reason: `at least 7 consecutive paused-to-active Goal-engine continuations; user approved blocked-aware design A and written spec`
- stage2_formal_old_monitor_pid: `24620`
- stage2_formal_old_monitor_exit: `exact identity verified; exact PID stopped; no survivor`
- stage2_formal_blocked_aware_runtime_path: `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1`
- stage2_formal_blocked_aware_runtime_sha256: write the exact lowercase `RuntimeSha` emitted by Task 1 Step 5
- stage2_formal_monitor_pid: write the exact positive `NewPid` emitted by Task 2 Step 3
- stage2_formal_monitor_command_line: write the exact `Cim.CommandLine` observed in Task 2 Step 3
- stage2_formal_monitor_started_at_utc: write the exact UTC ISO `NewStartUtc` emitted by Task 2 Step 3
- stage2_formal_goal_status_after_scheduler_block: `blocked`
- stage2_formal_terminal_next_command: `after exact monitor exit, require exact Goal active; then perform frozen Task 5 Step 3 and Step 4 identity/artifact validation without redispatch`
```

Do not change the frozen helper SHA key. Re-read the active document and require each new key exactly once.

- [ ] **Step 6: Final local handoff verification**

```powershell
$ErrorActionPreference = 'Stop'
$Runtime = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat-blocked-aware.ps1'
$Frozen = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
if ((Get-FileHash -Algorithm SHA256 $Frozen).Hash.ToLowerInvariant() -cne '4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639') { throw 'Frozen helper changed' }
$RuntimeSha = (Get-FileHash -Algorithm SHA256 $Runtime).Hash.ToLowerInvariant()
$Matches = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
    $_.ProcessId -ne $PID -and $_.ExecutablePath -ceq 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -and
    ([string]$_.CommandLine).IndexOf($Runtime, [StringComparison]::OrdinalIgnoreCase) -ge 0 -and
    [string]$_.CommandLine -like '*31404086927*' -and
    [string]$_.CommandLine -like '*2133114d93af1c7cb18f1acdc5693e871d8632db*' -and
    [string]$_.CommandLine -like '*-IntervalSeconds 1800*' -and
    [string]$_.CommandLine -like '*-WakeAfterMinutes 300*'
})
if ($Matches.Count -ne 1) { throw 'Final exact heartbeat count is not one' }
if ($null -ne (Get-CimInstance Win32_Process -Filter 'ProcessId=24620' -ErrorAction SilentlyContinue)) { throw 'Old monitor survived' }
Write-Output "FINAL_RUNTIME_SHA256=$RuntimeSha"
Write-Output "FINAL_MONITOR_PID=$($Matches[0].ProcessId)"
```

Expected: frozen hash unchanged, one runtime-copy monitor, old PID absent, exact Goal blocked. End the turn without a GitHub status query; the new monitor owns the 1,800-second polling schedule.
