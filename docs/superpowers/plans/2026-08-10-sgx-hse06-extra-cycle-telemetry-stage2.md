# SGX HSE06 Full-order Telemetry Stage 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Stage 1 的 200/200 valid `NOT_REPRODUCED/HOLD` 之后，以一个独立 follow-up commit 恢复原 `test_finite_diff_grad` 的九子例同进程顺序，仅对第八个 settings-2/HSE06 调用启用现有 schema-v1 telemetry，并在 Windows Python 3.12、`omp4-blas1` 下先做 1-repeat installed-wheel witness、再条件性做 200-repeat Stage 2 判别。

**Architecture:** 不修改 Stage 1 已证明的 callback、marker schema、validator、runner、workflow 或科学断言；Stage 2 只切换 exact-singleton selector/contract，并给原九调用中的第八个调用增加 `telemetry=True`。本地 source runner 与远端 installed-wheel artifact 都继续由同一冻结 validator 以原 nodeid 验收；唯一 PS1 heartbeat 只负责固定 run/head 的 1,800 秒巡查和 Goal paused/active 交接。

**Tech Stack:** Python 3、`unittest`/pytest、PySCF SGX、Git、GitHub Actions/`gh`、Windows PowerShell 5.1、本地标准库-only telemetry validator、Codex GoalBridge PS1。

## Global Constraints

- Approved design: `docs/superpowers/specs/2026-08-10-sgx-hse06-extra-cycle-telemetry-design.md`；Stage 1 已由 run `31388225490` / artifact `9063452642` 证明为 `valid=true`、`200/200 pass`、`0 fail`、`0 nonconverged`、`finding_counts={}`、`NOT_REPRODUCED/HOLD`，并由独立 review `APPROVED`。这使 Stage 2 合法启动，但绝不表示 fixed。
- Stage 1 implementation branch/worktree/head: `codex/investigate/libxc-712-sgx-extra-cycle-telemetry`、`D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry`、`2cd242eec13d0f4a80059738540ea14418b94abd`。
- Stage 2 只允许修改三个 tracked path：`.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt`、`.github/workflows/test_precision_investigation_contract.py`、`pyscf/sgx/grad/test/test_rks.py`。
- Selector 与 contract 必须是 exact singleton `pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad`。Dedicated `test_finite_diff_grad_settings2_hse06_telemetry` 保留且仍会被模块级收集；模块级 collect/run 不能替代 exact-singleton 原 nodeid 的远端或 artifact 证据。
- 原九调用顺序不变。只有第八个 `ALL_SETTINGS[2], ALL_PRECISIONS[2], "HSE06"` 调用增加 `telemetry=True`；其余八调用的顺序、文本和参数不变。
- `delta=1e-4`、`conv_tol=1e-12`、`conv_check=True`、`max_cycle`、两条原 `assertAlmostEqual` 的顺序/文本/places `12/6`、Windows Python `3.12`、profile `4/1`、LibXC `7.1.2` 均不变。
- Stage 2 只恢复前七子例与目标子例处于同一 pytest 进程的 warm/cache/调用顺序。Telemetry callback、scalar copies、JSON serialization 与打印仍可能产生 Heisenberg allocator/timing 影响；不得声称完整复原或完全不扰动内存状态。
- Stage 2 是一个独立 follow-up commit，parent 必须是 Stage 1 head，subject 精确为 `test(sgx): restore full-order HSE06 telemetry [skip ci]`。
- 冻结 validator 为 `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py`，SHA-256 `38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2`；source、witness、formal 都传 `--expected-nodeid` 原 nodeid。
- 冻结 GoalBridge 为 `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1`，SHA-256 `4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639`；只允许一个 PS1 loop，间隔 `1800` 秒。Witness wake gate=`0`；formal wake gate=`300` 分钟。
- Native automation `libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse` 必须保持 `PAUSED`，当前 thread `019f64bd-77a5-7573-88e9-fd80b1882e70` 的 ACTIVE native heartbeat count 必须为 `0`；不得编辑 TOML/SQLite，不得并存第二个 PS1、`gh run watch` 或 sleep loop。
- 所有 `gh` 调用后立即检查 `$LASTEXITCODE`；所有 JSON 使用 `ConvertFrom-Json -ErrorAction Stop`；PowerShell 5.1 中所有可能单项/空项集合均用 `@(...)` 归一化。
- Run 绑定只接受 dispatch 前冻结的 `BeforeMax` 之后且 exact head 的唯一 row；绝不选择 latest。每个远端步骤从 fresh PowerShell shell 重新冻结 branch/head/run/job/artifact id/name/digest/size/expired 与 canonical run-metadata fields。
- Witness/formal dispatch 各自在 `D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches\` 用 `.NET FileMode.CreateNew` 建立 stage/head/BeforeMax-keyed UTF-8 no-BOM JSON one-shot latch。Latch 一经存在就永久拒绝本计划再次 dispatch；NOT_BOUND 或 crash 不删除 latch，只允许 hash/content-bound recovery query 或人工审计。
- Active doc 中整行严格匹配得到的 40-hex `stage2_head` 是各 fresh shell 的 literal `$ExpectedHead`；不得以当时的 `git rev-parse`、latest run 或前一 fence 的变量替代它。
- Artifact 上传延迟与 `INVALID` 分开：terminal run 在 60 秒有界查询后仍为零 artifact，只记录 exact-run retry 并停止；多 artifact、字段畸形或 validator 拒绝才是 `INVALID`。
- Artifact 中的科学 assertion failure 可形成 valid evidence；不得以 workflow/job failure 自动判 `INVALID`，也不得 retry 覆盖首个科学失败。
- 历史 Windows 3.12 `omp4-blas1` 原 nodeid formal run `31345422470` 已提供成本依据：三 nodeid × 200 的整 job 约 101 分钟，原 SGX 单次日志约 14–21 秒。因此 witness `SMOKE_PASS` 后直接派发 200 repeats，不派发 timing-20。
- 只有 witness verdict 精确为 `SMOKE_PASS` 才能派发 formal 200。Stage 2 `0/200` 只能写 `NOT_REPRODUCED/HOLD`，必须停止本轮；不得派发其他 profile、完整矩阵或把 issue `pyscf/pyscf#3312` 更新为 resolved。
- 不安装/升级依赖；不修改 runner/workflow/verifier/GoalBridge/validator/production modules；不创建 PR；不在本计划执行中建立最终上游修复分支。
- Tracked 修改只用 `apply_patch`；不得用 PowerShell 5.1 `Set-Content`、`Out-File`、`>` 或 `>>` 写 UTF-8 文件。保留 UTF-8 no BOM、无 lone CR，并用 `git -c core.whitespace=cr-at-eol diff --check` 处理既有 mixed EOL。

## File Map and Interfaces

| Path | Stage 2 responsibility |
| --- | --- |
| `.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt` | exact singleton 原 nodeid，供 source runner 与远端 workflow 共用 |
| `.github/workflows/test_precision_investigation_contract.py` | 通过现有 `load_runner().load_nodeids()` 锁定同一 exact singleton |
| `pyscf/sgx/grad/test/test_rks.py` | 保留 Stage 1 telemetry interface/dedicated method；仅让原九调用第八项传 `telemetry=True` |
| `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py` | 不修改；统一验收 source/installed-wheel evidence 与科学 verdict |
| `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1` | 不修改；唯一 run/head monitor 与 Goal paused/active bridge |
| `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md` | 本地忽略状态记录；每次 dispatch 前后用 `apply_patch` 持久化冻结身份和下一命令 |

---

### Task 1: Stage 2 Entry Gate and Exact-original Selector RED/GREEN
**Files:**
- Modify: `.github/workflows/test_precision_investigation_contract.py:63-72`
- Modify: `.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt:1`
**Interfaces:**
- Consumes: Stage 1 head `2cd242eec13d0f4a80059738540ea14418b94abd`；active doc frozen result；existing `load_runner().load_nodeids(path) -> list[str]`。
- Produces: selector/contract exact singleton `pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad`，供 Task 2 的真实 source runner 与所有远端 run 使用。
- [ ] **Step 1: Re-establish the frozen Stage 1 baseline in a fresh shell**
```powershell
$ErrorActionPreference = 'Stop'
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Stage1Dir = 'D:\workspace\pyscf\.agents\archive\precision-ci\experiments\31388225490-sgx-hse06-telemetry-stage1-windows-py312'
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$Stage1Head = '2cd242eec13d0f4a80059738540ea14418b94abd'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$OriginalNodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
$DedicatedNodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
$Selection = '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
Set-Location $Wt
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
if ((git branch --show-current).Trim() -cne $Branch) { throw 'Wrong implementation branch' }
if ((git rev-parse HEAD).Trim() -cne $Stage1Head) { throw 'Stage 1 head drift' }
if ((git status --short --untracked-files=no)) { throw 'Tracked worktree is not clean' }
$Dlls = @(Get-ChildItem -LiteralPath (Join-Path $Wt 'pyscf\lib') -Filter '*.dll' -File)
if ($Dlls.Count -ne 26) { throw "Expected the preserved 26 DLL fixtures, got $($Dlls.Count)" }
if ((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne '38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2') { throw 'Validator drift' }
$State = Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
foreach ($Gate in @(
  '(?m)^- stage1_run_id:\s*(?:31388225490|`31388225490`)\s*$',
  '(?m)^- stage1_formal_artifact_id:\s*(?:9063452642|`9063452642`)\s*$',
  '(?m)^- stage1_formal_records:\s*(?:200|`200`)\s*$',
  '(?m)^- stage1_formal_pass:\s*(?:200|`200`)\s*$',
  '(?m)^- stage1_formal_fail:\s*(?:0|`0`)\s*$',
  '(?m)^- stage1_formal_nonconverged:\s*(?:0|`0`)\s*$',
  '(?m)^- stage1_formal_verdict:\s*(?:NOT_REPRODUCED/HOLD|`NOT_REPRODUCED/HOLD`)\s*$',
  '(?m)^- stage1_formal_independent_review:\s*(?:APPROVED; [^`\r\n]+|`APPROVED; [^`\r\n]+`)\s*$'
)) {
  if ($State -notmatch $Gate) { throw "Stage 1 active-doc gate missing: $Gate" }
}
foreach ($Name in @('telemetry-validation.json', 'telemetry-validation-independent-review.json')) {
  $Path = Join-Path $Stage1Dir $Name
  if ((Get-FileHash -Algorithm SHA256 $Path).Hash.ToLowerInvariant() -cne '9c3af42952b2fdc58b8df8dad54893c5b163c6cc22ca98f61ece5dc4ed23c0c1') { throw "Stage 1 report hash mismatch: $Name" }
  $Report = Get-Content -LiteralPath $Path -Raw -Encoding utf8 | ConvertFrom-Json -ErrorAction Stop
  if (-not $Report.valid -or $Report.verdict -cne 'NOT_REPRODUCED' -or $Report.records -ne 200 -or $Report.pass -ne 200 -or $Report.fail -ne 0 -or $Report.nonconverged -ne 0) { throw "Stage 1 report contract mismatch: $Name" }
}
conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test
if ($LASTEXITCODE -ne 0) { throw 'Frozen validator self-test failed' }
```
Expected: Stage 2 entry is allowed because both frozen reports are valid `NOT_REPRODUCED`, while no output claims fixed or resolved。
- [ ] **Step 2: RED 1 — change only the contract expectation to the original nodeid**
Use `apply_patch` with this exact change; leave the selection file pointing at the dedicated nodeid:
```diff
@@
-            'pyscf/sgx/grad/test/test_rks.py::KnownValues::'
-            'test_finite_diff_grad_settings2_hse06_telemetry',
+            'pyscf/sgx/grad/test/test_rks.py::KnownValues::'
+            'test_finite_diff_grad',
```
Run only the selector contract and require the list mismatch, not an unrelated error:
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; Set-Location $Wt
function Invoke-NativeCapture {
  param([string]$FilePath, [string[]]$ArgumentList)
  $Previous = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try { $Output = @(& $FilePath @ArgumentList 2>&1); $ExitCode = $LASTEXITCODE }
  finally { $ErrorActionPreference = $Previous }
  [pscustomobject]@{ExitCode=[int]$ExitCode;Output=@($Output | ForEach-Object { [string]$_ })}
}
$Conda = (Get-Command conda -ErrorAction Stop).Source
$Red = Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','-m','pytest','-q','-p','no:cacheprovider','-c','pytest.ini','--rootdir','.', '.github/workflows/test_precision_investigation_contract.py::PrecisionInvestigationContractTest::test_sgx_hse06_telemetry_selection')
$RedText = $Red.Output -join "`n"; $Red.Output | ForEach-Object { Write-Output $_ }
if ($Red.ExitCode -eq 0 -or $RedText -notmatch 'AssertionError' -or
    $RedText -notmatch 'test_finite_diff_grad_settings2_hse06_telemetry' -or
    $RedText -notmatch 'test_finite_diff_grad') {
  throw 'RED 1 did not fail on the exact dedicated-vs-original singleton mismatch'
}
```
Expected RED 1: contract expects original nodeid；`runner.load_nodeids()` still returns the dedicated nodeid。
- [ ] **Step 3: GREEN the exact selector without touching test implementation**
Use `apply_patch` to replace the sole selection line:
```diff
@@
-pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry
+pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad
```
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
Set-Location $Wt
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  '.github/workflows/test_precision_investigation_contract.py::PrecisionInvestigationContractTest::test_sgx_hse06_telemetry_selection'
if ($LASTEXITCODE -ne 0) { throw 'Exact original selector contract failed' }
$SelectionLines = @((Get-Content -LiteralPath $Selection -Encoding utf8) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
if ($SelectionLines.Count -ne 1 -or $SelectionLines[0] -cne $OriginalNodeId) { throw 'Selection is not the exact original-nodeid singleton' }
if ((Select-String -LiteralPath 'pyscf/sgx/grad/test/test_rks.py' -SimpleMatch 'def test_finite_diff_grad_settings2_hse06_telemetry').Count -ne 1) { throw 'Dedicated method was not preserved' }
```
---
### Task 2: Real Marker RED, Minimal Full-order GREEN, and Follow-up Commit
**Files:**
- Modify: `pyscf/sgx/grad/test/test_rks.py:175-184`
- Verify: `.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt`
- Verify: `.github/workflows/test_precision_investigation_contract.py`
**Interfaces:**
- Consumes: Task 1 exact-original selection；existing `_check_finite_diff_grad(..., *, telemetry=False)`；frozen validator CLI `EVIDENCE_DIR --mode ... --expected-nodeid ... --expected-repeats 1|200 --report ...`。
- Produces: one follow-up commit whose original nodeid emits exactly one valid marker, while the dedicated nodeid continues to emit exactly one marker and the selection remains the exact original singleton。
- [ ] **Step 1: RED 2 — run the real source runner before enabling telemetry in the original method**
```powershell
$ErrorActionPreference = 'Stop'
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$Stage1Head = '2cd242eec13d0f4a80059738540ea14418b94abd'
$OriginalNodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
$Selection = '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
Set-Location $Wt
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:OMP_NUM_THREADS='4'; $env:OPENBLAS_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:BLIS_NUM_THREADS='1'; $env:VECLIB_MAXIMUM_THREADS='1'; $env:NUMEXPR_NUM_THREADS='1'
function Invoke-NativeCapture {
  param([string]$FilePath, [string[]]$ArgumentList)
  $Previous = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try { $Output = @(& $FilePath @ArgumentList 2>&1); $ExitCode = $LASTEXITCODE }
  finally { $ErrorActionPreference = $Previous }
  [pscustomobject]@{ExitCode=[int]$ExitCode;Output=@($Output | ForEach-Object { [string]$_ })}
}
$Conda = (Get-Command conda -ErrorAction Stop).Source
$RedOut = Join-Path $Wt 'tmp\stage2-red-original-marker0'
if (Test-Path -LiteralPath $RedOut) { throw "RED output already exists: $RedOut" }
$Runner = Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','.github/workflows/run_precision_tests.py','--nodeids-file',$Selection,'--repeats','1','--profile','4/1','--output-dir',$RedOut,'--tested-sha',$Stage1Head,'--working-directory','.','--rootdir','.','--pytest-config','pytest.ini','--environment-mode','source-tree','--collector','.github/workflows/collect_precision_environment.py')
$Runner.Output | ForEach-Object { Write-Output $_ }; $RunnerExit = $Runner.ExitCode
if (-not (Test-Path -LiteralPath (Join-Path $RedOut 'records.jsonl'))) { throw 'RED source runner produced no auditable record' }
$Utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $RedOut 'runner-exit-code.txt'), [string]$RunnerExit, $Utf8)
$RedReport = Join-Path $RedOut 'telemetry-validation.json'
$Validation = Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python',$Validator,$RedOut,'--mode','source-tree','--expected-sha',$Stage1Head,'--expected-nodeid',$OriginalNodeId,'--expected-profile','omp4-blas1','--expected-repeats','1','--source-root',$Wt,'--report',$RedReport)
$Validation.Output | ForEach-Object { Write-Output $_ }; $ValidatorExit = $Validation.ExitCode
$Red = Get-Content -LiteralPath $RedReport -Raw -Encoding utf8 | ConvertFrom-Json -ErrorAction Stop
$RedRecord = Get-Content -LiteralPath (Join-Path $RedOut 'records.jsonl') -Raw -Encoding utf8 | ConvertFrom-Json -ErrorAction Stop
if ($RedRecord.profile -cne 'omp4-blas1') { throw 'RED 2 record did not freeze omp4-blas1' }
if ($ValidatorExit -ne 2 -or $Red.valid -ne $false -or $Red.verdict -cne 'INVALID' -or
    @($Red.errors).Count -ne 1 -or $Red.errors[0] -cne 'Log has 0 strict telemetry markers; expected 1') {
  throw 'RED 2 did not fail solely on the real original-nodeid marker-count contract'
}
Write-Output "RED2_RUNNER_EXIT_OBSERVED=$RunnerExit"
```
The scientific runner exit is an observation only. It may be `0` or an original assertion failure；RED 2 is the frozen validator rejecting marker count `0`, never an assumed scientific failure。
- [ ] **Step 2: GREEN only the eighth original call**
Use `apply_patch` with this exact one-line implementation change:
```diff
@@
-        self._check_finite_diff_grad(ALL_SETTINGS[2], ALL_PRECISIONS[2], "HSE06")
+        self._check_finite_diff_grad(
+            ALL_SETTINGS[2], ALL_PRECISIONS[2], "HSE06", telemetry=True)
```
Do not change the dedicated method, helper signature/body, first seven calls, ninth call, delta, convergence settings, or assertions。
- [ ] **Step 3: Verify call order, telemetry placement, contract, collect, and both nodeids**
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; Set-Location $Wt
$env:OMP_NUM_THREADS='4'; $env:OPENBLAS_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:BLIS_NUM_THREADS='1'; $env:VECLIB_MAXIMUM_THREADS='1'; $env:NUMEXPR_NUM_THREADS='1'
function Invoke-NativeCapture {
  param([string]$FilePath, [string[]]$ArgumentList)
  $Previous=$ErrorActionPreference; $ErrorActionPreference='Continue'
  try { $Output=@(& $FilePath @ArgumentList 2>&1); $ExitCode=$LASTEXITCODE } finally { $ErrorActionPreference=$Previous }
  [pscustomobject]@{ExitCode=[int]$ExitCode;Output=@($Output | ForEach-Object { [string]$_ })}
}
$Conda=(Get-Command conda -ErrorAction Stop).Source
$TestDiff = @(git diff --unified=0 --ignore-space-at-eol -- pyscf/sgx/grad/test/test_rks.py)
$ChangedLines = @($TestDiff | Where-Object { ($_ -match '^[+-]') -and ($_ -notmatch '^(---|\+\+\+)') })
$ExpectedChangedLines = @(
  '-        self._check_finite_diff_grad(ALL_SETTINGS[2], ALL_PRECISIONS[2], "HSE06")',
  '+        self._check_finite_diff_grad(',
  '+            ALL_SETTINGS[2], ALL_PRECISIONS[2], "HSE06", telemetry=True)'
)
if (($ExpectedChangedLines -join "`n") -cne ($ChangedLines -join "`n")) { throw 'The SGX test diff is not the exact ordered eighth-call-only change' }

$Contract=Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','-m','pytest','-q','-p','no:cacheprovider','-c','pytest.ini','--rootdir','.','.github/workflows/test_precision_investigation_contract.py')
$Contract.Output | ForEach-Object { Write-Output $_ }; if ($Contract.ExitCode -ne 0) { throw 'Precision contract suite failed' }

$Collect=Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','-m','pytest','--collect-only','-q','-p','no:cacheprovider','-c','pytest.ini','--rootdir','.',$OriginalNodeId)
$Collect.Output | ForEach-Object { Write-Output $_ }
if ($Collect.ExitCode -ne 0 -or @($Collect.Output | Where-Object { ([string]$_).Trim() -ceq $OriginalNodeId }).Count -ne 1) { throw 'Original nodeid did not collect exactly once' }

$Prefix = 'PYSCF_SGX_HSE06_TELEMETRY_V1 '
foreach ($Case in @(
  [pscustomobject]@{Name='original';NodeId=$OriginalNodeId},
  [pscustomobject]@{Name='dedicated';NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'}
)) {
  $Direct=Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','-m','pytest','-q','-s','-p','no:cacheprovider','-c','pytest.ini','--rootdir','.',$Case.NodeId)
  $Direct.Output | ForEach-Object { Write-Output $_ }
  $Markers = @($Direct.Output | Where-Object { ([string]$_).StartsWith($Prefix) })
  if ($Markers.Count -ne 1) { throw "$($Case.Name) emitted $($Markers.Count) markers" }
  $Payload = ([string]$Markers[0]).Substring($Prefix.Length) | ConvertFrom-Json -ErrorAction Stop
  if ($Payload.schema_version -ne 1 -or $Payload.case.settings_index -ne 2 -or $Payload.case.xc -cne 'HSE06') { throw "$($Case.Name) marker identity mismatch" }
  if ($Direct.ExitCode -ne 0 -and ($Direct.Output -join "`n") -notmatch 'AssertionError') { throw "$($Case.Name) failed outside the original scientific assertion" }
}
```

- [ ] **Step 4: Protect EOL, DLL fixtures, and the exact three-path scope**
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; Set-Location $Wt
$Allowed = @(
  '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt',
  '.github/workflows/test_precision_investigation_contract.py',
  'pyscf/sgx/grad/test/test_rks.py'
)
$Actual = @(git diff --name-only)
if (@(Compare-Object $Allowed $Actual).Count -ne 0) { throw 'Stage 2 working-tree scope mismatch' }
foreach ($Relative in $Allowed) {
  $Bytes = [IO.File]::ReadAllBytes((Join-Path $Wt $Relative))
  if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 239 -and $Bytes[1] -eq 187 -and $Bytes[2] -eq 191) { throw "UTF-8 BOM introduced: $Relative" }
  $Text = [Text.Encoding]::UTF8.GetString($Bytes)
  if ([regex]::Matches($Text, "`r(?!`n)").Count -ne 0) { throw "Lone CR introduced: $Relative" }
}
$ContractText = [IO.File]::ReadAllText((Join-Path $Wt '.github\workflows\test_precision_investigation_contract.py'), (New-Object Text.UTF8Encoding($false)))
$TestText = [IO.File]::ReadAllText((Join-Path $Wt 'pyscf\sgx\grad\test\test_rks.py'), (New-Object Text.UTF8Encoding($false)))
if ([regex]::Matches($ContractText, "`r`n").Count -lt 440 -or [regex]::Matches($TestText, "`r`n").Count -lt 184) { throw 'Unexpected mixed-EOL normalization' }
git -c core.whitespace=cr-at-eol diff --check
if ($LASTEXITCODE -ne 0) { throw 'Stage 2 whitespace check failed' }
$Dlls = @(Get-ChildItem -LiteralPath (Join-Path $Wt 'pyscf\lib') -Filter '*.dll' -File)
if ($Dlls.Count -ne 26) { throw '26-DLL fixture boundary changed' }
if (@(git status --short | Where-Object { $_ -match '^\?\? pyscf/lib/.+\.dll$' }).Count -ne 26) { throw 'DLL fixtures are missing, staged, or no longer untracked' }
```

- [ ] **Step 5: Commit the one follow-up change set**
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $Stage1Head='2cd242eec13d0f4a80059738540ea14418b94abd'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $DedicatedNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
$Allowed=@('.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt','.github/workflows/test_precision_investigation_contract.py','pyscf/sgx/grad/test/test_rks.py'); Set-Location $Wt
$env:OMP_NUM_THREADS='4'; $env:OPENBLAS_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:BLIS_NUM_THREADS='1'; $env:VECLIB_MAXIMUM_THREADS='1'; $env:NUMEXPR_NUM_THREADS='1'
function Invoke-NativeCapture {
  param([string]$FilePath,[string[]]$ArgumentList)
  $Previous=$ErrorActionPreference; $ErrorActionPreference='Continue'
  try{$Output=@(& $FilePath @ArgumentList 2>&1);$ExitCode=$LASTEXITCODE}finally{$ErrorActionPreference=$Previous}
  [pscustomobject]@{ExitCode=[int]$ExitCode;Output=@($Output|ForEach-Object{[string]$_})}
}
$Conda=(Get-Command conda -ErrorAction Stop).Source
$Selected=@(Get-Content -LiteralPath $Selection -Encoding utf8|Where-Object{-not [string]::IsNullOrWhiteSpace($_)}); if($Selected.Count-ne1-or$Selected[0]-cne$OriginalNodeId){throw 'Commit gate selection mismatch'}
$Contract=Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','-m','pytest','-q','-p','no:cacheprovider','-c','pytest.ini','--rootdir','.','.github/workflows/test_precision_investigation_contract.py'); $Contract.Output|ForEach-Object{Write-Output $_}; if($Contract.ExitCode-ne0){throw 'Commit gate contract failed'}
$Collect=Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','-m','pytest','--collect-only','-q','-p','no:cacheprovider','-c','pytest.ini','--rootdir','.',$OriginalNodeId); if($Collect.ExitCode-ne0-or@($Collect.Output|Where-Object{([string]$_).Trim()-ceq$OriginalNodeId}).Count-ne1){throw 'Commit gate collect mismatch'}
$Prefix='PYSCF_SGX_HSE06_TELEMETRY_V1 '
foreach($Case in @([pscustomobject]@{Name='original';NodeId=$OriginalNodeId},[pscustomobject]@{Name='dedicated';NodeId=$DedicatedNodeId})){
  $Direct=Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','-m','pytest','-q','-s','-p','no:cacheprovider','-c','pytest.ini','--rootdir','.',$Case.NodeId); $Direct.Output|ForEach-Object{Write-Output $_}
  $Markers=@($Direct.Output|Where-Object{([string]$_).StartsWith($Prefix)}); if($Markers.Count-ne1){throw "Commit gate $($Case.Name) marker count mismatch"}
  $Payload=([string]$Markers[0]).Substring($Prefix.Length)|ConvertFrom-Json -ErrorAction Stop; if($Payload.schema_version-ne1-or$Payload.case.settings_index-ne2-or$Payload.case.xc-cne'HSE06'){throw "Commit gate $($Case.Name) marker identity mismatch"}
  if($Direct.ExitCode-ne0-and($Direct.Output-join"`n")-notmatch'AssertionError'){throw "Commit gate $($Case.Name) failed outside scientific assertion"}
}
$TestDiff=@(git diff --unified=0 --ignore-space-at-eol -- pyscf/sgx/grad/test/test_rks.py); $Changed=@($TestDiff|Where-Object{$_-match'^[+-]'-and$_-notmatch'^(---|\+\+\+)'}); $Expected=@('-        self._check_finite_diff_grad(ALL_SETTINGS[2], ALL_PRECISIONS[2], "HSE06")','+        self._check_finite_diff_grad(','+            ALL_SETTINGS[2], ALL_PRECISIONS[2], "HSE06", telemetry=True)'); if(($Changed-join"`n")-cne($Expected-join"`n")){throw 'Commit gate eighth-call diff mismatch'}
$Actual=@(git diff --name-only); if(@(Compare-Object $Allowed $Actual).Count-ne0){throw 'Commit gate scope mismatch'}
foreach($Relative in $Allowed){$Bytes=[IO.File]::ReadAllBytes((Join-Path $Wt $Relative));if($Bytes.Length-ge3-and$Bytes[0]-eq239-and$Bytes[1]-eq187-and$Bytes[2]-eq191){throw "BOM: $Relative"};$Text=[Text.Encoding]::UTF8.GetString($Bytes);if([regex]::Matches($Text,"`r(?!`n)").Count-ne0){throw "Lone CR: $Relative"}}
$ContractText=[IO.File]::ReadAllText((Join-Path $Wt '.github\workflows\test_precision_investigation_contract.py'),(New-Object Text.UTF8Encoding($false))); $TestText=[IO.File]::ReadAllText((Join-Path $Wt 'pyscf\sgx\grad\test\test_rks.py'),(New-Object Text.UTF8Encoding($false))); if([regex]::Matches($ContractText,"`r`n").Count-lt440-or[regex]::Matches($TestText,"`r`n").Count-lt184){throw 'Commit gate mixed-EOL normalization'}
git -c core.whitespace=cr-at-eol diff --check; if($LASTEXITCODE-ne0){throw 'Commit gate diff-check failed'}
$Dlls=@(Get-ChildItem -LiteralPath (Join-Path $Wt 'pyscf\lib') -Filter '*.dll' -File); if($Dlls.Count-ne26-or@(git status --short|Where-Object{$_-match'^\?\? pyscf/lib/.+\.dll$'}).Count-ne26){throw 'Commit gate 26-DLL boundary changed'}
git add -- $Allowed
if ($LASTEXITCODE -ne 0) { throw 'Stage 2 staging failed' }
$Staged = @(git diff --cached --name-only)
if (@(Compare-Object $Allowed $Staged).Count -ne 0) { throw 'Staged scope mismatch' }
git commit -m 'test(sgx): restore full-order HSE06 telemetry [skip ci]'
if ($LASTEXITCODE -ne 0) { throw 'Stage 2 commit failed' }
$Head = (git rev-parse HEAD).Trim()
$Parent = (git rev-parse HEAD^).Trim()
$Subject = (git log -1 --format='%s').Trim()
if ($Parent -cne $Stage1Head) { throw 'Stage 2 parent is not Stage 1 head' }
if ($Subject -cne 'test(sgx): restore full-order HSE06 telemetry [skip ci]') { throw 'Stage 2 subject mismatch' }
if ((git status --short --untracked-files=no)) { throw 'Tracked worktree dirty after Stage 2 commit' }
```

- [ ] **Step 6: Generate and validate committed source evidence with the original nodeid**
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
Set-Location $Wt
$env:OMP_NUM_THREADS='4'; $env:OPENBLAS_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'; $env:BLIS_NUM_THREADS='1'; $env:VECLIB_MAXIMUM_THREADS='1'; $env:NUMEXPR_NUM_THREADS='1'
function Invoke-NativeCapture {
  param([string]$FilePath, [string[]]$ArgumentList)
  $Previous=$ErrorActionPreference; $ErrorActionPreference='Continue'
  try { $Output=@(& $FilePath @ArgumentList 2>&1); $ExitCode=$LASTEXITCODE } finally { $ErrorActionPreference=$Previous }
  [pscustomobject]@{ExitCode=[int]$ExitCode;Output=@($Output | ForEach-Object { [string]$_ })}
}
$Conda=(Get-Command conda -ErrorAction Stop).Source
$Head = (git rev-parse HEAD).Trim()
$SourceOut = Join-Path $Wt "tmp\stage2-source-$($Head.Substring(0,12))"
if (Test-Path -LiteralPath $SourceOut) { throw "Source output exists: $SourceOut" }
$Source=Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python','.github/workflows/run_precision_tests.py','--nodeids-file',$Selection,'--repeats','1','--profile','4/1','--output-dir',$SourceOut,'--tested-sha',$Head,'--working-directory','.','--rootdir','.','--pytest-config','pytest.ini','--environment-mode','source-tree','--collector','.github/workflows/collect_precision_environment.py')
$Source.Output | ForEach-Object { Write-Output $_ }; $SourceExit=$Source.ExitCode
if (-not (Test-Path -LiteralPath (Join-Path $SourceOut 'records.jsonl'))) { throw 'Source runner produced no auditable record' }
$Utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $SourceOut 'runner-exit-code.txt'), [string]$SourceExit, $Utf8)
$SourceReport = Join-Path $SourceOut 'telemetry-validation.json'
$Validation=Invoke-NativeCapture $Conda @('run','--no-capture-output','-n','pyscf-win313-test','python',$Validator,$SourceOut,'--mode','source-tree','--expected-sha',$Head,'--expected-nodeid',$OriginalNodeId,'--expected-profile','omp4-blas1','--expected-repeats','1','--source-root',$Wt,'--report',$SourceReport)
$Validation.Output | ForEach-Object { Write-Output $_ }
if ($Validation.ExitCode -ne 0) { throw 'Committed Stage 2 source evidence is INVALID' }
$V = Get-Content -LiteralPath $SourceReport -Raw -Encoding utf8 | ConvertFrom-Json -ErrorAction Stop
if (-not $V.valid) { throw 'Committed Stage 2 source evidence is INVALID' }
if ($V.verdict -cnotin @('SMOKE_PASS','MECHANISM_CONFIRMED','MECHANISM_FALSIFIED','REPRODUCED_OTHER_ASSERTION','INCONCLUSIVE_NONCONVERGED')) { throw "Unexpected valid source verdict: $($V.verdict)" }
$Record = Get-Content -LiteralPath (Join-Path $SourceOut 'records.jsonl') -Raw -Encoding utf8 | ConvertFrom-Json -ErrorAction Stop
if ($Record.nodeid -cne $OriginalNodeId -or $Record.profile -cne 'omp4-blas1') { throw 'Source record is not original nodeid/omp4-blas1' }
$Log = Get-Content -LiteralPath (Join-Path $SourceOut $Record.log_file) -Raw -Encoding utf8
if (@($Log -split "`r?`n" | Where-Object { $_.StartsWith('PYSCF_SGX_HSE06_TELEMETRY_V1 ') }).Count -ne 1) { throw 'Source evidence does not contain exactly one marker' }
Copy-Item -LiteralPath $Validator -Destination (Join-Path $SourceOut 'validate_sgx_hse06_telemetry.py')
if ((Get-FileHash -Algorithm SHA256 (Join-Path $SourceOut 'validate_sgx_hse06_telemetry.py')).Hash.ToLowerInvariant() -cne $V.validator_sha256) { throw 'Archived source validator hash mismatch' }
if ($V.verdict -ceq 'SMOKE_PASS' -and ($V.records -ne 1 -or $V.pass -ne 1 -or $V.fail -ne 0 -or $V.nonconverged -ne 0)) { throw 'SMOKE_PASS is not exact 1/1' }
Write-Output "STAGE2_SOURCE_ROUTE=$($V.verdict)"
```
Use one `apply_patch` operation to atomically record `stage2_head/parent/validator_sha256/source_report/source_verdict/records/pass/fail/nonconverged/finding_counts/first_failure/first_finding`。Only exact `SMOKE_PASS 1/1` records `stage2_next_command: Task 3 push gate`。A valid `MECHANISM_CONFIRMED`、`MECHANISM_FALSIFIED`、`REPRODUCED_OTHER_ASSERTION` or `INCONCLUSIVE_NONCONVERGED` is retained as scientific evidence, records the corresponding Task 5 routing action, and stops before push；validator nonzero or `valid=false` alone is `INVALID`。
---
### Task 3: Fresh-shell Push Gate
**Files:**
- Verify only: the three Stage 2 tracked paths
- Update locally only: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
**Interfaces:**
- Consumes: committed Stage 2 head and exact `SMOKE_PASS` source evidence；long-term authorization for this investigation branch push。
- Produces: remote branch fast-forwarded to the exact frozen Stage 2 head；no CI dispatch caused by the `[skip ci]` commit itself。
- [ ] **Step 1: Rebuild every push invariant in a fresh shell**
```powershell
$ErrorActionPreference = 'Stop'; $Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'; $Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'; $Stage1Head = '2cd242eec13d0f4a80059738540ea14418b94abd'
$Allowed = @('.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt', '.github/workflows/test_precision_investigation_contract.py', 'pyscf/sgx/grad/test/test_rks.py')
Set-Location $Wt
$State = Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$HeadMatch=[regex]::Match($State,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $HeadMatch.Success){throw 'Missing strict Stage 2 head'}
$Head=if($HeadMatch.Groups[1].Success){$HeadMatch.Groups[1].Value}else{$HeadMatch.Groups[2].Value}
if ((git rev-parse HEAD).Trim() -cne $Head) { throw 'Local/frozen Stage 2 head mismatch' }
if ((git rev-parse HEAD^).Trim() -cne $Stage1Head) { throw 'Stage 2 parent drift' }
if ((git log -1 --format='%s').Trim() -cne 'test(sgx): restore full-order HSE06 telemetry [skip ci]') { throw 'Stage 2 subject drift' }
if ($State -notmatch '(?m)^- stage2_source_verdict:\s*(?:SMOKE_PASS|`SMOKE_PASS`)\s*$') { throw 'Source SMOKE_PASS gate missing' }
if ((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne '38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2') { throw 'Validator drift' }
$Actual = @(git diff --name-only "$Stage1Head...$Head")
if (@(Compare-Object $Allowed $Actual).Count -ne 0) { throw 'Stage 2 commit scope mismatch' }
if ((git status --short --untracked-files=no)) { throw 'Tracked tree dirty before push' }
$Dlls = @(Get-ChildItem -LiteralPath (Join-Path $Wt 'pyscf\lib') -Filter '*.dll' -File)
if ($Dlls.Count -ne 26) { throw '26-DLL fixture boundary changed before push' }
git -c core.whitespace=cr-at-eol diff --check "$Stage1Head...$Head"
if ($LASTEXITCODE -ne 0) { throw 'Committed Stage 2 diff check failed' }
$RemoteBefore = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($LASTEXITCODE -ne 0) { throw 'Failed to read remote branch before push' }
if ($RemoteBefore -cne $Stage1Head) { throw 'Remote branch is not at frozen Stage 1 head' }
gh auth status
if ($LASTEXITCODE -ne 0) { throw 'GitHub authentication failed' }
```
- [ ] **Step 2: Push the exact follow-up commit and verify remote SHA**
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'; $Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$Branch='codex/investigate/libxc-712-sgx-extra-cycle-telemetry'; $Stage1Head='2cd242eec13d0f4a80059738540ea14418b94abd'; $ExpectedValidatorSha='38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'; $Allowed=@('.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt','.github/workflows/test_precision_investigation_contract.py','pyscf/sgx/grad/test/test_rks.py'); Set-Location $Wt; $State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$M=[regex]::Match($State,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $M.Success){throw 'Missing strict Stage 2 head'}; $Head=if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value}
if($State-notmatch'(?m)^- stage2_source_verdict:\s*(?:SMOKE_PASS|`SMOKE_PASS`)\s*$'){throw 'Push source SMOKE_PASS gate missing'}
if((git rev-parse HEAD).Trim()-cne$Head-or(git rev-parse HEAD^).Trim()-cne$Stage1Head-or(git log -1 --format='%s').Trim()-cne'test(sgx): restore full-order HSE06 telemetry [skip ci]'){throw 'Push commit identity mismatch'}
if((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant()-cne$ExpectedValidatorSha){throw 'Push validator drift'}
$Actual=@(git diff --name-only "$Stage1Head...$Head"); if(@(Compare-Object $Allowed $Actual).Count-ne0){throw 'Push three-path scope mismatch'}
if(git status --short --untracked-files=no){throw 'Push tracked tree dirty'}; $Dlls=@(Get-ChildItem -LiteralPath (Join-Path $Wt 'pyscf\lib') -Filter '*.dll' -File); if($Dlls.Count-ne26-or@(git status --short|Where-Object{$_-match'^\?\? pyscf/lib/.+\.dll$'}).Count-ne26){throw 'Push 26-DLL boundary changed'}
git -c core.whitespace=cr-at-eol diff --check "$Stage1Head...$Head"; if($LASTEXITCODE-ne0){throw 'Push committed diff-check failed'}
$RemoteBefore=((git ls-remote origin "refs/heads/$Branch")-split'\s+')[0]; if($LASTEXITCODE-ne0-or$RemoteBefore-cne$Stage1Head){throw 'Push remote-before is not Stage 1 head'}
git push origin "HEAD:refs/heads/$Branch"
if ($LASTEXITCODE -ne 0) { throw 'Stage 2 push failed' }
$RemoteAfter = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($LASTEXITCODE -ne 0) { throw 'Failed to read remote branch after push' }
if ($RemoteAfter -cne $Head) { throw 'Remote Stage 2 SHA mismatch' }
```
Use `apply_patch` on the ignored active doc to record `stage2_push_gate: PASS`, exact `stage2_remote_branch`, `stage2_remote_head`, validator SHA, source verdict, three-path scope, commit subject, and `stage2_next_command: Task 4 witness dispatch`。
---
### Task 4: Windows 3.12 Installed-wheel Witness and Exact Artifact Validation
**Files:**
- Update locally only: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Archive after binding: `D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-sgx-hse06-telemetry-stage2-witness-windows-py312`
**Interfaces:**
- Consumes: pushed exact Stage 2 head；frozen validator/GoalBridge；workflow `ci-precision-check.yml` inputs `windows-latest`, Python `3.12`, profile `4/1`, repeats `1`。
- Produces: canonical run/job/artifact metadata plus a validator report；only exact `SMOKE_PASS` unlocks Task 5。
- [ ] **Step 1: Fresh-shell monitor/identity preflight and BeforeMax freeze**
```powershell
$ErrorActionPreference = 'Stop'; $Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'; $Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'; $Selection = '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
$Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'
$ThreadId = '019f64bd-77a5-7573-88e9-fd80b1882e70'; $AutomationId = 'libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse'; $AutomationRoot = 'C:\Users\ustcw\.codex\automations'
$AutomationPath = Join-Path $AutomationRoot "$AutomationId\automation.toml"
Set-Location $Wt
$State = Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$HeadMatch=[regex]::Match($State,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $HeadMatch.Success){throw 'Missing strict Stage 2 head'}
$ExpectedHead=if($HeadMatch.Groups[1].Success){$HeadMatch.Groups[1].Value}else{$HeadMatch.Groups[2].Value}
if ((git rev-parse HEAD).Trim() -cne $ExpectedHead) { throw 'Frozen Stage 2 head mismatch' }
if ($State -notmatch '(?m)^- stage2_source_verdict:\s*(?:SMOKE_PASS|`SMOKE_PASS`)\s*$') { throw 'Source gate missing' }
$RemoteHead = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($LASTEXITCODE -ne 0 -or $RemoteHead -cne $ExpectedHead) { throw 'Remote head mismatch before witness' }
if ((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne '38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2') { throw 'Validator drift' }
if ((Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne '4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639') { throw 'GoalBridge drift' }
function Read-TomlValue {
  param([string]$Text, [string]$Key)
  $Found = [regex]::Matches($Text, ('(?m)^' + [regex]::Escape($Key) + '\s*=\s*"([^"]*)"\s*$'))
  if ($Found.Count -ne 1) { throw "Expected one TOML key: $Key" }
  return $Found[0].Groups[1].Value
}
$TargetToml = [IO.File]::ReadAllText($AutomationPath, (New-Object Text.UTF8Encoding($false)))
$ExpectedToml = [ordered]@{id=$AutomationId;status='PAUSED';kind='heartbeat';target_thread_id=$ThreadId;rrule='RRULE:FREQ=MINUTELY;INTERVAL=30';prompt='检查CI状态'}
foreach ($Key in $ExpectedToml.Keys) { if ((Read-TomlValue $TargetToml $Key) -cne $ExpectedToml[$Key]) { throw "Target automation drift: $Key" } }
$ActiveNative = @(Get-ChildItem -LiteralPath $AutomationRoot -Filter automation.toml -File -Recurse | Where-Object {
  $Text = [IO.File]::ReadAllText($_.FullName, (New-Object Text.UTF8Encoding($false)))
  (Read-TomlValue $Text kind) -ceq 'heartbeat' -and (Read-TomlValue $Text status) -ceq 'ACTIVE' -and (Read-TomlValue $Text target_thread_id) -ceq $ThreadId
})
if ($ActiveNative.Count -ne 0) { throw 'Current-thread ACTIVE native heartbeat count is not zero' }
$Pollers = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
  $_.ProcessId -ne $PID -and -not [string]::IsNullOrWhiteSpace([string]$_.CommandLine) -and (
    ([string]$_.CommandLine).IndexOf($GoalBridge, [StringComparison]::OrdinalIgnoreCase) -ge 0 -or
    [string]$_.CommandLine -match '(?i)gh(?:\.exe)?(?:"|\s)+run\s+watch(?:\s|$)' -or
    ([string]$_.CommandLine -match '(?i)gh(?:\.exe)?(?:"|\s)+run\s+(?:view|list)(?:\s|$)' -and [string]$_.CommandLine -match '(?i)(?:Start-Sleep|sleep\.exe|while\s*\()')
  )
})
if ($Pollers.Count -ne 0) { throw 'Existing local CI poller detected' }
$RunningRaw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json status)
if ($LASTEXITCODE -ne 0) { throw 'Failed to list active runs' }
$RunningParsed = ConvertFrom-Json -InputObject ($RunningRaw -join "`n") -ErrorAction Stop
$Running = @(@($RunningParsed) | Where-Object { $_.status -in @('requested','queued','in_progress','waiting','pending') })
if ($Running.Count -ne 0) { throw 'Another active investigation run exists' }
$BeforeRaw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json databaseId)
if ($LASTEXITCODE -ne 0) { throw 'Failed to list pre-dispatch run ids' }
$BeforeParsed = ConvertFrom-Json -InputObject ($BeforeRaw -join "`n") -ErrorAction Stop
$BeforeRows = @($BeforeParsed)
$BeforeMax = if ($BeforeRows.Count -eq 0) { [long]0 } else { [long](($BeforeRows | Measure-Object -Property databaseId -Maximum).Maximum) }
$DispatchStartedAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
```
Before dispatch, use `apply_patch` on the active doc to persist exact keys: `stage2_witness_before_max`, `stage2_witness_dispatch_started_at_utc`, `stage2_witness_branch`, `stage2_witness_head`, `stage2_witness_workflow: ci-precision-check.yml`, `stage2_witness_selection`, `stage2_witness_nodeid`, inputs `windows-latest/3.12/4/1/repeats1`, expected artifact `precision-Windows-py3.12`, validator SHA, GoalBridge SHA, and terminal next command。
- [ ] **Step 2: Dispatch once, bind by BeforeMax plus exact head, then launch the only heartbeat**
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'; $Branch='codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'
$ExpectedValidatorSha='38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'; $ExpectedGoalBridgeSha='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
$ThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70'; $AutomationRoot='C:\Users\ustcw\.codex\automations'; $AutomationId='libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse'
Set-Location $Wt; $State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$M=[regex]::Match($State,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $M.Success){throw 'Missing strict Stage 2 head'}; $ExpectedHead=if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value}
$B=[regex]::Match($State,'(?m)^- stage2_witness_before_max:\s*(?:(\d+)|`(\d+)`)\s*$'); if(-not $B.Success){throw 'Missing strict witness BeforeMax'}; $BeforeMax=[long]$(if($B.Groups[1].Success){$B.Groups[1].Value}else{$B.Groups[2].Value})
if((git rev-parse HEAD).Trim() -cne $ExpectedHead){throw 'Local/frozen head mismatch'}
$Remote=((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]; if($LASTEXITCODE -ne 0 -or $Remote -cne $ExpectedHead){throw 'Remote/frozen head mismatch'}
if((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne $ExpectedValidatorSha -or (Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne $ExpectedGoalBridgeSha){throw 'Frozen helper drift'}
$Selected=@(Get-Content -LiteralPath $Selection -Encoding utf8 | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }); if($Selected.Count -ne 1 -or $Selected[0] -cne $OriginalNodeId){throw 'Selection is not exact original singleton'}
if($State-notmatch'(?m)^- stage2_source_verdict:\s*(?:SMOKE_PASS|`SMOKE_PASS`)\s*$'){throw 'Witness source SMOKE_PASS gate missing'}
if($State-match'(?m)^- stage2_witness_run_id:\s*(?:\d+|`\d+`)\s*$'){throw 'Witness run already bound; refuse replay'}
$TargetToml=[IO.File]::ReadAllText((Join-Path $AutomationRoot "$AutomationId\automation.toml"),(New-Object Text.UTF8Encoding($false))); foreach($Pattern in @('(?m)^id\s*=\s*"libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse"\s*$','(?m)^status\s*=\s*"PAUSED"\s*$','(?m)^kind\s*=\s*"heartbeat"\s*$','(?m)^target_thread_id\s*=\s*"019f64bd-77a5-7573-88e9-fd80b1882e70"\s*$','(?m)^rrule\s*=\s*"RRULE:FREQ=MINUTELY;INTERVAL=30"\s*$')){if($TargetToml-notmatch$Pattern){throw "Witness automation mismatch: $Pattern"}}
$ActiveNative=@(Get-ChildItem -LiteralPath $AutomationRoot -Filter automation.toml -File -Recurse|Where-Object{$T=[IO.File]::ReadAllText($_.FullName,(New-Object Text.UTF8Encoding($false)));$T-match'(?m)^kind\s*=\s*"heartbeat"\s*$'-and$T-match'(?m)^status\s*=\s*"ACTIVE"\s*$'-and$T-match('(?m)^target_thread_id\s*=\s*"'+[regex]::Escape($ThreadId)+'"\s*$')}); if($ActiveNative.Count-ne0){throw 'Witness ACTIVE native heartbeat exists'}
$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and-not[string]::IsNullOrWhiteSpace([string]$_.CommandLine)-and((([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0)-or[string]$_.CommandLine-match'(?i)gh(?:\.exe)?(?:"|\s)+run\s+watch(?:\s|$)'-or([string]$_.CommandLine-match'(?i)gh(?:\.exe)?(?:"|\s)+run\s+(?:view|list)(?:\s|$)'-and[string]$_.CommandLine-match'(?i)(?:Start-Sleep|sleep\.exe|while\s*\()'))}); if($Pollers.Count-ne0){throw 'Witness local poller exists'}
$RunningRaw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json status); if($LASTEXITCODE-ne0){throw 'Witness active-run query failed'}; $Running=ConvertFrom-Json -InputObject ($RunningRaw-join"`n") -ErrorAction Stop; if(@(@($Running)|Where-Object{$_.status-in@('requested','queued','in_progress','waiting','pending')}).Count-ne0){throw 'Witness active workflow run exists'}
$LatchRoot='D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches'; [void][IO.Directory]::CreateDirectory($LatchRoot); $CreatedAt=[DateTimeOffset]::UtcNow.ToString('o')
$Latch=[ordered]@{stage='stage2-witness';head=$ExpectedHead;branch=$Branch;beforeMax=$BeforeMax;workflow=$Workflow;selection=$Selection;repeats=1;platform='windows-latest';python='3.12';profile='4/1';createdAt=$CreatedAt}
$LatchPath=Join-Path $LatchRoot "stage2-witness-$ExpectedHead-$BeforeMax.json"; $LatchJson=$Latch|ConvertTo-Json -Compress; $Utf8=New-Object Text.UTF8Encoding($false); $Bytes=$Utf8.GetBytes($LatchJson)
try{$Stream=New-Object IO.FileStream($LatchPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$Stream.Write($Bytes,0,$Bytes.Length);$Stream.Flush($true)}finally{$Stream.Dispose()}}catch [IO.IOException]{throw "Witness dispatch latch exists or is unusable; refuse dispatch: $LatchPath"}
$LatchSha=(Get-FileHash -Algorithm SHA256 $LatchPath).Hash.ToLowerInvariant(); Write-Output "WITNESS_DISPATCH_LATCH_PATH=$LatchPath"; Write-Output "WITNESS_DISPATCH_LATCH_SHA256=$LatchSha"
gh workflow run $Workflow --repo $Repo --ref $Branch `
  --raw-field nodeids_file=$Selection --raw-field repeats=1 `
  --raw-field platform=windows-latest --raw-field python_version=3.12 `
  --raw-field profile=4/1
if ($LASTEXITCODE -ne 0) { throw 'Witness dispatch failed' }
$Candidates = @()
for ($i=0; $i -lt 12; $i++) {
  $CandidateRaw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 20 --json databaseId,headSha,url)
  if ($LASTEXITCODE -ne 0) { throw 'Failed to list witness candidates' }
  $CandidateParsed = ConvertFrom-Json -InputObject ($CandidateRaw -join "`n") -ErrorAction Stop
  $Candidates = @(@($CandidateParsed) | Where-Object { [long]$_.databaseId -gt $BeforeMax -and $_.headSha -ceq $ExpectedHead })
  if ($Candidates.Count -eq 1) { break }
  if ($Candidates.Count -gt 1) { throw 'Ambiguous witness binding' }
  Start-Sleep -Seconds 5
}
if ($Candidates.Count -ne 1) { Write-Output 'WITNESS_RUN_ID_NOT_BOUND'; return }
$RunId = [long]$Candidates[0].databaseId
```
Immediately use one `apply_patch` to persist exact `stage2_witness_dispatch_latch_path/sha256`, `stage2_witness_run_id: $RunId` when bound, URL/head/branch/BeforeMax/inputs/artifact/validator, and the next fresh-shell command. The latch remains after dispatch failure or `WITNESS_RUN_ID_NOT_BOUND`。An existing latch always forbids redispatch；if latch/hash was not durably recorded because of a crash, stop for manual audit。The next fence's run-id-missing branch is the only recovery binder and never dispatches。
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'; $Branch='codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'; $ThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70'
$ExpectedValidatorSha='38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'; $ExpectedGoalBridgeSha='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
Set-Location $Wt; $State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$M=[regex]::Match($State,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $M.Success){throw 'Missing strict Stage 2 head'}; $ExpectedHead=if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value}
if((git rev-parse HEAD).Trim() -cne $ExpectedHead){throw 'Local/frozen head mismatch'}
$Remote=((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]; if($LASTEXITCODE -ne 0 -or $Remote -cne $ExpectedHead){throw 'Remote/frozen head mismatch'}
if((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne $ExpectedValidatorSha -or (Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne $ExpectedGoalBridgeSha){throw 'Frozen helper drift'}
$Selected=@(Get-Content -LiteralPath $Selection -Encoding utf8 | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }); if($Selected.Count -ne 1 -or $Selected[0] -cne $OriginalNodeId){throw 'Selection is not exact original singleton'}
$R=[regex]::Match($State,'(?m)^- stage2_witness_run_id:\s*(?:(\d+)|`(\d+)`)\s*$')
if(-not $R.Success){
  $B=[regex]::Match($State,'(?m)^- stage2_witness_before_max:\s*(?:(\d+)|`(\d+)`)\s*$');if(-not$B.Success){throw 'Recovery missing strict witness BeforeMax'};$BeforeMax=[long]$(if($B.Groups[1].Success){$B.Groups[1].Value}else{$B.Groups[2].Value})
  $LatchPath=Join-Path 'D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches' "stage2-witness-$ExpectedHead-$BeforeMax.json"; $PathPattern='(?m)^- stage2_witness_dispatch_latch_path:\s*(?:'+[regex]::Escape($LatchPath)+'|`'+[regex]::Escape($LatchPath)+'`)\s*$'; if($State-notmatch$PathPattern){throw 'Recovery latch path missing; manual audit, no redispatch'}
  $H=[regex]::Match($State,'(?m)^- stage2_witness_dispatch_latch_sha256:\s*(?:([0-9a-f]{64})|`([0-9a-f]{64})`)\s*$');if(-not$H.Success){throw 'Recovery latch hash missing; manual audit, no redispatch'};$ExpectedLatchSha=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value}
  if(-not(Test-Path -LiteralPath $LatchPath -PathType Leaf)-or(Get-FileHash -Algorithm SHA256 $LatchPath).Hash.ToLowerInvariant()-cne$ExpectedLatchSha){throw 'Recovery latch hash mismatch'}
  $Latch=Get-Content -LiteralPath $LatchPath -Raw -Encoding utf8|ConvertFrom-Json -ErrorAction Stop; $Names=@($Latch.PSObject.Properties.Name); $ExpectedNames=@('stage','head','branch','beforeMax','workflow','selection','repeats','platform','python','profile','createdAt'); if(@(Compare-Object $ExpectedNames $Names).Count-ne0){throw 'Recovery latch fields mismatch'}
  $Created=[DateTimeOffset]::MinValue;if($Latch.stage-cne'stage2-witness'-or$Latch.head-cne$ExpectedHead-or$Latch.branch-cne$Branch-or[long]$Latch.beforeMax-ne$BeforeMax-or$Latch.workflow-cne$Workflow-or$Latch.selection-cne$Selection-or[long]$Latch.repeats-ne1-or$Latch.platform-cne'windows-latest'-or$Latch.python-cne'3.12'-or$Latch.profile-cne'4/1'-or-not[DateTimeOffset]::TryParse([string]$Latch.createdAt,[ref]$Created)){throw 'Recovery latch content mismatch'}
  $Raw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 50 --json databaseId,headSha,url);if($LASTEXITCODE-ne0){throw 'Witness recovery query failed'};$Rows=ConvertFrom-Json -InputObject ($Raw-join"`n") -ErrorAction Stop;$Candidates=@(@($Rows)|Where-Object{[long]$_.databaseId-gt$BeforeMax-and$_.headSha-ceq$ExpectedHead});if($Candidates.Count-eq0){Write-Output 'WITNESS_RECOVERY_NOT_READY';return};if($Candidates.Count-gt1){throw 'Ambiguous witness recovery binding'}
  Write-Output "WITNESS_RECOVERED_RUN_ID=$([long]$Candidates[0].databaseId)";Write-Output "WITNESS_RECOVERED_URL=$($Candidates[0].url)";return
}
$RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value})
$RunRaw=@(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,workflowName); if($LASTEXITCODE -ne 0){throw 'Witness run identity read failed'}
$Run=ConvertFrom-Json -InputObject ($RunRaw -join "`n") -ErrorAction Stop; if($Run.attempt -ne 1 -or $Run.event -cne 'workflow_dispatch' -or $Run.headBranch -cne $Branch -or $Run.headSha -cne $ExpectedHead -or $Run.workflowName -cne $WorkflowName){throw 'Witness run identity mismatch'}
$AutomationRoot='C:\Users\ustcw\.codex\automations'; $AutomationId='libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse'; $TargetToml=[IO.File]::ReadAllText((Join-Path $AutomationRoot "$AutomationId\automation.toml"),(New-Object Text.UTF8Encoding($false)))
foreach($Pattern in @('(?m)^id\s*=\s*"libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse"\s*$','(?m)^status\s*=\s*"PAUSED"\s*$','(?m)^kind\s*=\s*"heartbeat"\s*$','(?m)^target_thread_id\s*=\s*"019f64bd-77a5-7573-88e9-fd80b1882e70"\s*$','(?m)^rrule\s*=\s*"RRULE:FREQ=MINUTELY;INTERVAL=30"\s*$')){if($TargetToml-notmatch$Pattern){throw "Witness heartbeat automation mismatch: $Pattern"}}
$ActiveNative=@(Get-ChildItem -LiteralPath $AutomationRoot -Filter automation.toml -File -Recurse|Where-Object{$T=[IO.File]::ReadAllText($_.FullName,(New-Object Text.UTF8Encoding($false)));$T-match'(?m)^kind\s*=\s*"heartbeat"\s*$'-and$T-match'(?m)^status\s*=\s*"ACTIVE"\s*$'-and$T-match('(?m)^target_thread_id\s*=\s*"'+[regex]::Escape($ThreadId)+'"\s*$')}); if($ActiveNative.Count-ne0){throw 'Witness ACTIVE native heartbeat exists before launch'}
$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and-not[string]::IsNullOrWhiteSpace([string]$_.CommandLine)-and((([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0)-or[string]$_.CommandLine-match'(?i)gh(?:\.exe)?(?:"|\s)+run\s+watch(?:\s|$)'-or([string]$_.CommandLine-match'(?i)gh(?:\.exe)?(?:"|\s)+run\s+(?:view|list)(?:\s|$)'-and[string]$_.CommandLine-match'(?i)(?:Start-Sleep|sleep\.exe|while\s*\()'))}); if($Pollers.Count-ne0){throw 'Witness existing monitor/poller before launch'}
$PowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$Args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$GoalBridge,'-TargetRunIds',[string]$RunId,'-TargetHeadSha',$ExpectedHead,'-IntervalSeconds','1800','-WakeAfterMinutes','0')
$HeartbeatPid=$null;$HeartbeatStartUtc=$null
$Heartbeat = Start-Process -FilePath $PowerShell -ArgumentList $Args -WindowStyle Hidden -PassThru
$ChildTokens=@($GoalBridge,[string]$RunId,$ExpectedHead,'-IntervalSeconds 1800','-WakeAfterMinutes 0')
try{
  $HeartbeatPid=$Heartbeat.Id;$HeartbeatStartUtc=$Heartbeat.StartTime.ToUniversalTime();Start-Sleep -Seconds 2;if($Heartbeat.HasExited){throw "Witness heartbeat exited early: $($Heartbeat.ExitCode)"};$Cim=Get-CimInstance Win32_Process -Filter "ProcessId=$HeartbeatPid" -ErrorAction Stop
  $Exact=$Cim.ExecutablePath-ceq$PowerShell;foreach($Token in $ChildTokens){$Exact=$Exact-and([string]$Cim.CommandLine-like"*$Token*")};if(-not$Exact){throw 'Witness heartbeat identity mismatch'}
  $GoalRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus paused);if($LASTEXITCODE-ne0){throw 'Goal pause/readback failed'};$Goal=ConvertFrom-Json -InputObject ($GoalRaw-join"`n") -ErrorAction Stop;if($Goal.threadId-cne$ThreadId-or$Goal.status-cne'paused'){throw 'Paused Goal identity mismatch'}
  $After=Get-CimInstance Win32_Process -Filter "ProcessId=$($Heartbeat.Id)" -ErrorAction SilentlyContinue;$Alive=$null-ne$After-and$After.ExecutablePath-ceq$PowerShell;foreach($Token in $ChildTokens){$Alive=$Alive-and([string]$After.CommandLine-like"*$Token*")};if(-not$Alive){throw 'Witness heartbeat disappeared after pause'}
  $ExactMonitors=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and$_.ExecutablePath-ceq$PowerShell-and([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0});if($ExactMonitors.Count-ne1-or$ExactMonitors[0].ProcessId-ne$HeartbeatPid){throw 'Witness normal handoff is not exactly one direct child'}
}catch{
  $Primary=$_.Exception;$CleanupErrors=New-Object 'Collections.Generic.List[string]'
  try{$Heartbeat.Refresh();if(-not$Heartbeat.HasExited){if(($null-ne$HeartbeatPid-and$Heartbeat.Id-ne$HeartbeatPid)-or($null-ne$HeartbeatStartUtc-and$Heartbeat.StartTime.ToUniversalTime()-ne$HeartbeatStartUtc)){throw 'Direct-child handle indicates unrelated PID reuse'};$Heartbeat.Kill();if(-not$Heartbeat.WaitForExit(10000)){throw 'Direct child did not exit within 10 seconds'};$Heartbeat.Refresh();if(-not$Heartbeat.HasExited){throw 'Direct child handle is not gone'}}}catch{$CleanupErrors.Add("direct-child cleanup: $($_.Exception.Message)")}
  $Previous=$ErrorActionPreference;$ErrorActionPreference='Continue';try{$RestoreRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus active 2>&1);$RestoreExit=$LASTEXITCODE}finally{$ErrorActionPreference=$Previous};if($RestoreExit-ne0){$CleanupErrors.Add("Goal active setter exit $RestoreExit")}else{try{$Restore=ConvertFrom-Json -InputObject (($RestoreRaw|ForEach-Object{[string]$_})-join"`n") -ErrorAction Stop;if($Restore.threadId-cne$ThreadId-or$Restore.status-cne'active'){throw 'Goal active identity mismatch'}}catch{$CleanupErrors.Add("Goal active reconcile: $($_.Exception.Message)")}}
  $Cleanup=if($CleanupErrors.Count){$CleanupErrors-join'; '}else{'cleanup verified'};throw [InvalidOperationException]::new("Witness heartbeat handoff failed: $($Primary.Message); $Cleanup",$Primary)
}
```
If the recovery branch prints `WITNESS_RECOVERY_NOT_READY`, stop with the latch intact；if it prints one `WITNESS_RECOVERED_RUN_ID`, use `apply_patch` to persist that exact ID/URL and rerun this fence, which then enters heartbeat launch。The recovery branch always returns before `Start-Process` and contains no dispatch。On normal launch, use `apply_patch` to record monitor kind `ps1`, PID, executable/full command line, exact run/head, interval `1800`, wake gate `0`, launch time, expected artifact, validator SHA, and terminal validation command。
- [ ] **Step 3: In a fresh shell, freeze terminal run/job/artifact metadata and validate**
```powershell
$ErrorActionPreference = 'Stop'; $Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'; $Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$ArchiveRoot = 'D:\workspace\pyscf\.agents\archive\precision-ci\experiments'; $Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'; $OriginalNodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $ThreadId = '019f64bd-77a5-7573-88e9-fd80b1882e70'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'; $ExpectedValidatorSha='38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'; $ExpectedGoalBridgeSha='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
Set-Location $Wt
$Text = Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$M=[regex]::Match($Text,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $M.Success){throw 'Missing strict Stage 2 head'}; $Head=if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value}; if((git rev-parse HEAD).Trim() -cne $Head){throw 'Local/frozen head mismatch'}
$R=[regex]::Match($Text,'(?m)^- stage2_witness_run_id:\s*(?:(\d+)|`(\d+)`)\s*$'); if(-not $R.Success){throw 'Missing strict witness run id'}; $RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value})
$P=[regex]::Match($Text,'(?m)^- stage2_witness_monitor_pid:\s*(?:(\d+)|`(\d+)`)\s*$'); if(-not $P.Success){throw 'Missing strict witness monitor PID'}; $MonitorPid=[long]$(if($P.Groups[1].Success){$P.Groups[1].Value}else{$P.Groups[2].Value})
if((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne $ExpectedValidatorSha -or (Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne $ExpectedGoalBridgeSha){throw 'Frozen helper drift'}
$Selected=@(Get-Content -LiteralPath $Selection -Encoding utf8 | Where-Object {-not [string]::IsNullOrWhiteSpace($_)}); if($Selected.Count -ne 1 -or $Selected[0] -cne $OriginalNodeId){throw 'Selection is not exact original singleton'}
if ($null -ne (Get-CimInstance Win32_Process -Filter "ProcessId=$MonitorPid" -ErrorAction SilentlyContinue)) { throw 'Witness heartbeat still running' }
$PowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$GoalRaw = @(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus active)
if ($LASTEXITCODE -ne 0) { throw 'Goal active reconciliation failed' }
$Goal = ConvertFrom-Json -InputObject ($GoalRaw -join "`n") -ErrorAction Stop
if ($Goal.threadId -cne $ThreadId -or $Goal.status -cne 'active') { throw 'Active Goal readback mismatch' }
$RemoteHead = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($LASTEXITCODE -ne 0 -or $RemoteHead -cne $Head) { throw 'Witness local/remote head mismatch' }
$RunRaw = @(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,conclusion,workflowName,jobs,url)
if ($LASTEXITCODE -ne 0) { throw 'Failed to read witness run' }
$Run = ConvertFrom-Json -InputObject ($RunRaw -join "`n") -ErrorAction Stop
$Jobs = @($Run.jobs)
if ($Run.status -cne 'completed' -or $Run.attempt -ne 1 -or $Run.event -cne 'workflow_dispatch' -or $Run.headSha -cne $Head -or $Run.headBranch -cne $Branch -or $Run.workflowName -cne $WorkflowName -or $Jobs.Count -ne 1 -or $Jobs[0].name -cne 'precision' -or $Jobs[0].status -cne 'completed') { throw 'Witness run/job identity invalid' }
function Test-JsonInteger { param($Value) return ($Value -is [int] -or $Value -is [long] -or $Value -is [uint32] -or $Value -is [uint64]) }
$Artifacts = @()
for ($i=0; $i -lt 12; $i++) {
  $ApiRaw = @(gh api "repos/$Repo/actions/runs/$RunId/artifacts")
  if ($LASTEXITCODE -ne 0) { throw 'Failed to read witness artifacts' }
  $Api = ConvertFrom-Json -InputObject ($ApiRaw -join "`n") -ErrorAction Stop
  $Artifacts = @($Api.artifacts)
  if (-not (Test-JsonInteger $Api.total_count) -or [long]$Api.total_count -ne $Artifacts.Count) { throw 'Witness artifact envelope invalid' }
  if ($Artifacts.Count -gt 1) { throw 'Multiple witness artifacts' }
  if ($Artifacts.Count -eq 1) { break }
  Start-Sleep -Seconds 5
}
if ($Artifacts.Count -eq 0) { Write-Output 'WITNESS_ARTIFACT_NOT_READY'; return }
$Artifact = $Artifacts[0]
if (-not (Test-JsonInteger $Artifact.id) -or $Artifact.id -le 0 -or $Artifact.name -cne $ExpectedArtifact -or $Artifact.expired -ne $false -or -not (Test-JsonInteger $Artifact.size_in_bytes) -or $Artifact.size_in_bytes -le 0 -or $Artifact.digest -cnotmatch '^sha256:[0-9a-f]{64}$') { throw 'Witness artifact metadata invalid' }
$Dir = Join-Path $ArchiveRoot "$RunId-sgx-hse06-telemetry-stage2-witness-windows-py312"
if (Test-Path -LiteralPath $Dir) { throw "Witness archive exists: $Dir" }
New-Item -ItemType Directory -Path $Dir | Out-Null
$Job = $Jobs[0]
$Meta = [ordered]@{databaseId=$RunId;attempt=$Run.attempt;event=$Run.event;workflowName=$Run.workflowName;headSha=$Run.headSha;headBranch=$Run.headBranch;status=$Run.status;conclusion=$Run.conclusion;jobs=@([ordered]@{name=$Job.name;status=$Job.status;conclusion=$Job.conclusion});artifacts=@([ordered]@{id=$Artifact.id;name=$Artifact.name;digest=$Artifact.digest;sizeInBytes=$Artifact.size_in_bytes;expired=$Artifact.expired})}
$Utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $Dir 'run-metadata.json'), ($Meta | ConvertTo-Json -Depth 5), $Utf8)
gh run download $RunId --repo $Repo --name $Artifact.name --dir $Dir
if ($LASTEXITCODE -ne 0) { throw 'Witness artifact download failed' }
$Report = Join-Path $Dir 'telemetry-validation.json'
conda run --no-capture-output -n pyscf-win313-test python $Validator $Dir `
  --mode installed-wheel --expected-sha $Head --expected-nodeid $OriginalNodeId `
  --expected-profile omp4-blas1 --expected-repeats 1 --expected-native-count 26 `
  --run-metadata (Join-Path $Dir 'run-metadata.json') --expected-run-id $RunId `
  --expected-branch $Branch --report $Report
$ValidatorExit = $LASTEXITCODE
$V = Get-Content -LiteralPath $Report -Raw -Encoding utf8 | ConvertFrom-Json -ErrorAction Stop
Copy-Item -LiteralPath $Validator -Destination (Join-Path $Dir 'validate_sgx_hse06_telemetry.py')
if ((Get-FileHash -Algorithm SHA256 (Join-Path $Dir 'validate_sgx_hse06_telemetry.py')).Hash.ToLowerInvariant() -cne $V.validator_sha256) { throw 'Witness validator hash mismatch' }
if ($ValidatorExit -ne 0 -or -not $V.valid) { throw 'Witness evidence INVALID' }
```
`WITNESS_ARTIFACT_NOT_READY` means upload latency: keep Goal active, record exact run/head/monitor PID/observation time and re-run only this fresh-shell artifact query later；do not redispatch and do not label `INVALID`。
Use `apply_patch` to record canonical run/job fields, artifact id/name/digest/size/expired, validator SHA, report path, counts and verdict. If verdict is not exact `SMOKE_PASS`, retain valid evidence and stop before Task 5；do not rerun。Only `SMOKE_PASS` records `stage2_next_command: Task 5 formal dispatch`。
---
### Task 5: Conditional Direct-200 Formal Run, 300-minute Gate, and Verdict Routing
**Files:**
- Update locally only: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Archive after binding: `D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-sgx-hse06-telemetry-stage2-windows-py312`
**Interfaces:**
- Consumes: exact Stage 2 witness `SMOKE_PASS` on the same head/validator；historical run `31345422470` cost evidence；the same exact-original selector and validator。
- Produces: one valid 200-repeat Stage 2 verdict and a fail-closed next action；no other profile, timing preflight, full matrix, PR, or resolved issue update。
- [ ] **Step 1: In a fresh shell, require witness SMOKE_PASS and freeze formal BeforeMax**
```powershell
$ErrorActionPreference = 'Stop'; $Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'; $Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'; $Selection = '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $ThreadId = '019f64bd-77a5-7573-88e9-fd80b1882e70'
$Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'
Set-Location $Wt
$State = Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$HeadMatch=[regex]::Match($State,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $HeadMatch.Success){throw 'Missing strict Stage 2 head'}
$ExpectedHead=if($HeadMatch.Groups[1].Success){$HeadMatch.Groups[1].Value}else{$HeadMatch.Groups[2].Value}; if((git rev-parse HEAD).Trim() -cne $ExpectedHead){throw 'Local/frozen head mismatch'}
if ($State -notmatch '(?m)^- stage2_witness_verdict:\s*(?:SMOKE_PASS|`SMOKE_PASS`)\s*$') { throw 'Witness is not exact SMOKE_PASS' }
$WitnessHead='(?m)^- stage2_witness_head:\s*(?:'+[regex]::Escape($ExpectedHead)+'|`'+[regex]::Escape($ExpectedHead)+'`)\s*$'; if($State -notmatch $WitnessHead){throw 'Witness/head mismatch'}
if ($State -notmatch '(?m)^- stage2_witness_validator_sha256:\s*(?:38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2|`38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2`)\s*$') { throw 'Witness validator mismatch' }
$RemoteHead = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($LASTEXITCODE -ne 0 -or $RemoteHead -cne $ExpectedHead) { throw 'Remote head mismatch before formal dispatch' }
if ((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne '38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2') { throw 'Validator drift' }
if ((Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne '4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639') { throw 'GoalBridge drift' }
$Pollers = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object { $_.ProcessId -ne $PID -and -not [string]::IsNullOrWhiteSpace([string]$_.CommandLine) -and (([string]$_.CommandLine).IndexOf($GoalBridge, [StringComparison]::OrdinalIgnoreCase) -ge 0 -or [string]$_.CommandLine -match '(?i)gh(?:\.exe)?(?:"|\s)+run\s+watch(?:\s|$)' -or ([string]$_.CommandLine -match '(?i)gh(?:\.exe)?(?:"|\s)+run\s+(?:view|list)(?:\s|$)' -and [string]$_.CommandLine -match '(?i)(?:Start-Sleep|sleep\.exe|while\s*\()')) })
if ($Pollers.Count -ne 0) { throw 'A local poller survives before formal dispatch' }
$AutomationRoot = 'C:\Users\ustcw\.codex\automations'
$AutomationId = 'libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse'
$TargetToml = [IO.File]::ReadAllText((Join-Path $AutomationRoot "$AutomationId\automation.toml"), (New-Object Text.UTF8Encoding($false)))
foreach ($Pattern in @(
  '(?m)^id\s*=\s*"libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse"\s*$', '(?m)^status\s*=\s*"PAUSED"\s*$', '(?m)^kind\s*=\s*"heartbeat"\s*$',
  '(?m)^target_thread_id\s*=\s*"019f64bd-77a5-7573-88e9-fd80b1882e70"\s*$', '(?m)^rrule\s*=\s*"RRULE:FREQ=MINUTELY;INTERVAL=30"\s*$')) { if ($TargetToml -notmatch $Pattern) { throw "Native automation metadata mismatch: $Pattern" } }
$ActiveNative = @(Get-ChildItem -LiteralPath $AutomationRoot -Filter automation.toml -File -Recurse | Where-Object { $T=[IO.File]::ReadAllText($_.FullName,(New-Object Text.UTF8Encoding($false))); $T -match '(?m)^kind\s*=\s*"heartbeat"\s*$' -and $T -match '(?m)^status\s*=\s*"ACTIVE"\s*$' -and $T -match ('(?m)^target_thread_id\s*=\s*"' + [regex]::Escape($ThreadId) + '"\s*$') })
if ($ActiveNative.Count -ne 0) { throw 'Current-thread ACTIVE native heartbeat count is not zero' }
$RunningRaw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json status)
if ($LASTEXITCODE -ne 0) { throw 'Failed to list active formal runs' }
$RunningParsed = ConvertFrom-Json -InputObject ($RunningRaw -join "`n") -ErrorAction Stop
if (@(@($RunningParsed) | Where-Object { $_.status -in @('requested','queued','in_progress','waiting','pending') }).Count -ne 0) { throw 'Another active investigation run exists' }
$BeforeRaw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json databaseId)
if ($LASTEXITCODE -ne 0) { throw 'Failed to list pre-formal run ids' }
$BeforeParsed = ConvertFrom-Json -InputObject ($BeforeRaw -join "`n") -ErrorAction Stop
$BeforeRows = @($BeforeParsed)
$BeforeMax = if ($BeforeRows.Count -eq 0) { [long]0 } else { [long](($BeforeRows | Measure-Object -Property databaseId -Maximum).Maximum) }
$DispatchStartedAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
```
Record exact keys including `stage2_formal_before_max`, formal branch/head/workflow/selection/original nodeid/inputs/artifact/validator/GoalBridge/dispatch time/300-minute gate in the active doc with `apply_patch`. Also record `timing_preflight: NOT_DISPATCHED` and cost basis `run 31345422470; 3 nodeids x 200 about 101m; original SGX logs about 14-21s`。
- [ ] **Step 2: Dispatch direct 200, exact-bind, launch the single formal heartbeat, and pause Goal**
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'; $Branch='codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'
$ExpectedValidatorSha='38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'; $ExpectedGoalBridgeSha='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
$ThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70'; $AutomationRoot='C:\Users\ustcw\.codex\automations'; $AutomationId='libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse'
Set-Location $Wt; $State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$M=[regex]::Match($State,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $M.Success){throw 'Missing strict Stage 2 head'}; $ExpectedHead=if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value}
$B=[regex]::Match($State,'(?m)^- stage2_formal_before_max:\s*(?:(\d+)|`(\d+)`)\s*$'); if(-not $B.Success){throw 'Missing strict formal BeforeMax'}; $BeforeMax=[long]$(if($B.Groups[1].Success){$B.Groups[1].Value}else{$B.Groups[2].Value})
if((git rev-parse HEAD).Trim() -cne $ExpectedHead){throw 'Local/frozen head mismatch'}
$Remote=((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]; if($LASTEXITCODE -ne 0 -or $Remote -cne $ExpectedHead){throw 'Remote/frozen head mismatch'}
if((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne $ExpectedValidatorSha -or (Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne $ExpectedGoalBridgeSha){throw 'Frozen helper drift'}
if($State -notmatch '(?m)^- stage2_witness_verdict:\s*(?:SMOKE_PASS|`SMOKE_PASS`)\s*$'){throw 'Witness SMOKE_PASS gate missing'}
$Selected=@(Get-Content -LiteralPath $Selection -Encoding utf8 | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }); if($Selected.Count -ne 1 -or $Selected[0] -cne $OriginalNodeId){throw 'Selection is not exact original singleton'}
if($State-match'(?m)^- stage2_formal_run_id:\s*(?:\d+|`\d+`)\s*$'){throw 'Formal run already bound; refuse replay'}
$TargetToml=[IO.File]::ReadAllText((Join-Path $AutomationRoot "$AutomationId\automation.toml"),(New-Object Text.UTF8Encoding($false))); foreach($Pattern in @('(?m)^id\s*=\s*"libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse"\s*$','(?m)^status\s*=\s*"PAUSED"\s*$','(?m)^kind\s*=\s*"heartbeat"\s*$','(?m)^target_thread_id\s*=\s*"019f64bd-77a5-7573-88e9-fd80b1882e70"\s*$','(?m)^rrule\s*=\s*"RRULE:FREQ=MINUTELY;INTERVAL=30"\s*$')){if($TargetToml-notmatch$Pattern){throw "Formal automation mismatch: $Pattern"}}
$ActiveNative=@(Get-ChildItem -LiteralPath $AutomationRoot -Filter automation.toml -File -Recurse|Where-Object{$T=[IO.File]::ReadAllText($_.FullName,(New-Object Text.UTF8Encoding($false)));$T-match'(?m)^kind\s*=\s*"heartbeat"\s*$'-and$T-match'(?m)^status\s*=\s*"ACTIVE"\s*$'-and$T-match('(?m)^target_thread_id\s*=\s*"'+[regex]::Escape($ThreadId)+'"\s*$')}); if($ActiveNative.Count-ne0){throw 'Formal ACTIVE native heartbeat exists'}
$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and-not[string]::IsNullOrWhiteSpace([string]$_.CommandLine)-and((([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0)-or[string]$_.CommandLine-match'(?i)gh(?:\.exe)?(?:"|\s)+run\s+watch(?:\s|$)'-or([string]$_.CommandLine-match'(?i)gh(?:\.exe)?(?:"|\s)+run\s+(?:view|list)(?:\s|$)'-and[string]$_.CommandLine-match'(?i)(?:Start-Sleep|sleep\.exe|while\s*\()'))}); if($Pollers.Count-ne0){throw 'Formal local poller exists'}
$RunningRaw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json status); if($LASTEXITCODE-ne0){throw 'Formal active-run query failed'}; $Running=ConvertFrom-Json -InputObject ($RunningRaw-join"`n") -ErrorAction Stop; if(@(@($Running)|Where-Object{$_.status-in@('requested','queued','in_progress','waiting','pending')}).Count-ne0){throw 'Formal active workflow run exists'}
$LatchRoot='D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches'; [void][IO.Directory]::CreateDirectory($LatchRoot); $CreatedAt=[DateTimeOffset]::UtcNow.ToString('o')
$Latch=[ordered]@{stage='stage2-formal';head=$ExpectedHead;branch=$Branch;beforeMax=$BeforeMax;workflow=$Workflow;selection=$Selection;repeats=200;platform='windows-latest';python='3.12';profile='4/1';createdAt=$CreatedAt}
$LatchPath=Join-Path $LatchRoot "stage2-formal-$ExpectedHead-$BeforeMax.json"; $LatchJson=$Latch|ConvertTo-Json -Compress; $Utf8=New-Object Text.UTF8Encoding($false); $Bytes=$Utf8.GetBytes($LatchJson)
try{$Stream=New-Object IO.FileStream($LatchPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$Stream.Write($Bytes,0,$Bytes.Length);$Stream.Flush($true)}finally{$Stream.Dispose()}}catch [IO.IOException]{throw "Formal dispatch latch exists or is unusable; refuse dispatch: $LatchPath"}
$LatchSha=(Get-FileHash -Algorithm SHA256 $LatchPath).Hash.ToLowerInvariant(); Write-Output "FORMAL_DISPATCH_LATCH_PATH=$LatchPath"; Write-Output "FORMAL_DISPATCH_LATCH_SHA256=$LatchSha"
gh workflow run $Workflow --repo $Repo --ref $Branch `
  --raw-field nodeids_file=$Selection --raw-field repeats=200 `
  --raw-field platform=windows-latest --raw-field python_version=3.12 `
  --raw-field profile=4/1
if ($LASTEXITCODE -ne 0) { throw 'Formal dispatch failed' }
$Candidates = @()
for ($i=0; $i -lt 12; $i++) {
  $Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 20 --json databaseId,headSha,url)
  if ($LASTEXITCODE -ne 0) { throw 'Failed to list formal candidates' }
  $Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
  $Candidates = @(@($Parsed) | Where-Object { [long]$_.databaseId -gt $BeforeMax -and $_.headSha -ceq $ExpectedHead })
  if ($Candidates.Count -eq 1) { break }
  if ($Candidates.Count -gt 1) { throw 'Ambiguous formal binding' }
  Start-Sleep -Seconds 5
}
if ($Candidates.Count -ne 1) { Write-Output 'FORMAL_RUN_ID_NOT_BOUND'; return }
$RunId = [long]$Candidates[0].databaseId
```
Immediately use one `apply_patch` to persist exact `stage2_formal_dispatch_latch_path/sha256`, `stage2_formal_run_id` when bound, URL/head/branch/BeforeMax/inputs/artifact/validator and terminal next command. The latch remains after dispatch failure or `FORMAL_RUN_ID_NOT_BOUND`。An existing latch always forbids redispatch；missing durable latch hash after a crash requires manual audit。The next fence's run-id-missing branch is the only recovery binder and never dispatches。
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'; $Branch='codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'; $ThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70'
$ExpectedValidatorSha='38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'; $ExpectedGoalBridgeSha='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
Set-Location $Wt; $State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$M=[regex]::Match($State,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $M.Success){throw 'Missing strict Stage 2 head'}; $ExpectedHead=if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value}
if((git rev-parse HEAD).Trim() -cne $ExpectedHead){throw 'Local/frozen head mismatch'}
$Remote=((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]; if($LASTEXITCODE -ne 0 -or $Remote -cne $ExpectedHead){throw 'Remote/frozen head mismatch'}
if((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne $ExpectedValidatorSha -or (Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne $ExpectedGoalBridgeSha){throw 'Frozen helper drift'}
$Selected=@(Get-Content -LiteralPath $Selection -Encoding utf8 | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }); if($Selected.Count -ne 1 -or $Selected[0] -cne $OriginalNodeId){throw 'Selection is not exact original singleton'}
$R=[regex]::Match($State,'(?m)^- stage2_formal_run_id:\s*(?:(\d+)|`(\d+)`)\s*$')
if(-not $R.Success){
  $B=[regex]::Match($State,'(?m)^- stage2_formal_before_max:\s*(?:(\d+)|`(\d+)`)\s*$');if(-not$B.Success){throw 'Recovery missing strict formal BeforeMax'};$BeforeMax=[long]$(if($B.Groups[1].Success){$B.Groups[1].Value}else{$B.Groups[2].Value})
  $LatchPath=Join-Path 'D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches' "stage2-formal-$ExpectedHead-$BeforeMax.json"; $PathPattern='(?m)^- stage2_formal_dispatch_latch_path:\s*(?:'+[regex]::Escape($LatchPath)+'|`'+[regex]::Escape($LatchPath)+'`)\s*$'; if($State-notmatch$PathPattern){throw 'Recovery latch path missing; manual audit, no redispatch'}
  $H=[regex]::Match($State,'(?m)^- stage2_formal_dispatch_latch_sha256:\s*(?:([0-9a-f]{64})|`([0-9a-f]{64})`)\s*$');if(-not$H.Success){throw 'Recovery latch hash missing; manual audit, no redispatch'};$ExpectedLatchSha=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value}
  if(-not(Test-Path -LiteralPath $LatchPath -PathType Leaf)-or(Get-FileHash -Algorithm SHA256 $LatchPath).Hash.ToLowerInvariant()-cne$ExpectedLatchSha){throw 'Recovery latch hash mismatch'}
  $Latch=Get-Content -LiteralPath $LatchPath -Raw -Encoding utf8|ConvertFrom-Json -ErrorAction Stop; $Names=@($Latch.PSObject.Properties.Name); $ExpectedNames=@('stage','head','branch','beforeMax','workflow','selection','repeats','platform','python','profile','createdAt'); if(@(Compare-Object $ExpectedNames $Names).Count-ne0){throw 'Recovery latch fields mismatch'}
  $Created=[DateTimeOffset]::MinValue;if($Latch.stage-cne'stage2-formal'-or$Latch.head-cne$ExpectedHead-or$Latch.branch-cne$Branch-or[long]$Latch.beforeMax-ne$BeforeMax-or$Latch.workflow-cne$Workflow-or$Latch.selection-cne$Selection-or[long]$Latch.repeats-ne200-or$Latch.platform-cne'windows-latest'-or$Latch.python-cne'3.12'-or$Latch.profile-cne'4/1'-or-not[DateTimeOffset]::TryParse([string]$Latch.createdAt,[ref]$Created)){throw 'Recovery latch content mismatch'}
  $Raw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 50 --json databaseId,headSha,url);if($LASTEXITCODE-ne0){throw 'Formal recovery query failed'};$Rows=ConvertFrom-Json -InputObject ($Raw-join"`n") -ErrorAction Stop;$Candidates=@(@($Rows)|Where-Object{[long]$_.databaseId-gt$BeforeMax-and$_.headSha-ceq$ExpectedHead});if($Candidates.Count-eq0){Write-Output 'FORMAL_RECOVERY_NOT_READY';return};if($Candidates.Count-gt1){throw 'Ambiguous formal recovery binding'}
  Write-Output "FORMAL_RECOVERED_RUN_ID=$([long]$Candidates[0].databaseId)";Write-Output "FORMAL_RECOVERED_URL=$($Candidates[0].url)";return
}
$RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value})
$RunRaw=@(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,workflowName); if($LASTEXITCODE -ne 0){throw 'Formal run identity read failed'}
$Run=ConvertFrom-Json -InputObject ($RunRaw -join "`n") -ErrorAction Stop; if($Run.attempt -ne 1 -or $Run.event -cne 'workflow_dispatch' -or $Run.headBranch -cne $Branch -or $Run.headSha -cne $ExpectedHead -or $Run.workflowName -cne $WorkflowName){throw 'Formal run identity mismatch'}
$AutomationRoot='C:\Users\ustcw\.codex\automations'; $AutomationId='libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse'; $TargetToml=[IO.File]::ReadAllText((Join-Path $AutomationRoot "$AutomationId\automation.toml"),(New-Object Text.UTF8Encoding($false)))
foreach($Pattern in @('(?m)^id\s*=\s*"libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse"\s*$','(?m)^status\s*=\s*"PAUSED"\s*$','(?m)^kind\s*=\s*"heartbeat"\s*$','(?m)^target_thread_id\s*=\s*"019f64bd-77a5-7573-88e9-fd80b1882e70"\s*$','(?m)^rrule\s*=\s*"RRULE:FREQ=MINUTELY;INTERVAL=30"\s*$')){if($TargetToml-notmatch$Pattern){throw "Formal heartbeat automation mismatch: $Pattern"}}
$ActiveNative=@(Get-ChildItem -LiteralPath $AutomationRoot -Filter automation.toml -File -Recurse|Where-Object{$T=[IO.File]::ReadAllText($_.FullName,(New-Object Text.UTF8Encoding($false)));$T-match'(?m)^kind\s*=\s*"heartbeat"\s*$'-and$T-match'(?m)^status\s*=\s*"ACTIVE"\s*$'-and$T-match('(?m)^target_thread_id\s*=\s*"'+[regex]::Escape($ThreadId)+'"\s*$')}); if($ActiveNative.Count-ne0){throw 'Formal ACTIVE native heartbeat exists before launch'}
$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and-not[string]::IsNullOrWhiteSpace([string]$_.CommandLine)-and((([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0)-or[string]$_.CommandLine-match'(?i)gh(?:\.exe)?(?:"|\s)+run\s+watch(?:\s|$)'-or([string]$_.CommandLine-match'(?i)gh(?:\.exe)?(?:"|\s)+run\s+(?:view|list)(?:\s|$)'-and[string]$_.CommandLine-match'(?i)(?:Start-Sleep|sleep\.exe|while\s*\()'))}); if($Pollers.Count-ne0){throw 'Formal existing monitor/poller before launch'}
$PowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$Args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$GoalBridge,'-TargetRunIds',[string]$RunId,'-TargetHeadSha',$ExpectedHead,'-IntervalSeconds','1800','-WakeAfterMinutes','300')
$HeartbeatPid=$null;$HeartbeatStartUtc=$null
$Heartbeat = Start-Process -FilePath $PowerShell -ArgumentList $Args -WindowStyle Hidden -PassThru
$ChildTokens=@($GoalBridge,[string]$RunId,$ExpectedHead,'-IntervalSeconds 1800','-WakeAfterMinutes 300')
try{
  $HeartbeatPid=$Heartbeat.Id;$HeartbeatStartUtc=$Heartbeat.StartTime.ToUniversalTime();Start-Sleep -Seconds 2;if($Heartbeat.HasExited){throw "Formal heartbeat exited early: $($Heartbeat.ExitCode)"};$Cim=Get-CimInstance Win32_Process -Filter "ProcessId=$HeartbeatPid" -ErrorAction Stop
  $Exact=$Cim.ExecutablePath-ceq$PowerShell;foreach($Token in $ChildTokens){$Exact=$Exact-and([string]$Cim.CommandLine-like"*$Token*")};if(-not$Exact){throw 'Formal heartbeat identity mismatch'}
  $GoalRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus paused);if($LASTEXITCODE-ne0){throw 'Goal pause/readback failed'};$Goal=ConvertFrom-Json -InputObject ($GoalRaw-join"`n") -ErrorAction Stop;if($Goal.threadId-cne$ThreadId-or$Goal.status-cne'paused'){throw 'Paused Goal identity mismatch'}
  $After=Get-CimInstance Win32_Process -Filter "ProcessId=$($Heartbeat.Id)" -ErrorAction SilentlyContinue;$Alive=$null-ne$After-and$After.ExecutablePath-ceq$PowerShell;foreach($Token in $ChildTokens){$Alive=$Alive-and([string]$After.CommandLine-like"*$Token*")};if(-not$Alive){throw 'Formal heartbeat disappeared after pause'}
  $ExactMonitors=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and$_.ExecutablePath-ceq$PowerShell-and([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0});if($ExactMonitors.Count-ne1-or$ExactMonitors[0].ProcessId-ne$HeartbeatPid){throw 'Formal normal handoff is not exactly one direct child'}
}catch{
  $Primary=$_.Exception;$CleanupErrors=New-Object 'Collections.Generic.List[string]'
  try{$Heartbeat.Refresh();if(-not$Heartbeat.HasExited){if(($null-ne$HeartbeatPid-and$Heartbeat.Id-ne$HeartbeatPid)-or($null-ne$HeartbeatStartUtc-and$Heartbeat.StartTime.ToUniversalTime()-ne$HeartbeatStartUtc)){throw 'Direct-child handle indicates unrelated PID reuse'};$Heartbeat.Kill();if(-not$Heartbeat.WaitForExit(10000)){throw 'Direct child did not exit within 10 seconds'};$Heartbeat.Refresh();if(-not$Heartbeat.HasExited){throw 'Direct child handle is not gone'}}}catch{$CleanupErrors.Add("direct-child cleanup: $($_.Exception.Message)")}
  $Previous=$ErrorActionPreference;$ErrorActionPreference='Continue';try{$RestoreRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus active 2>&1);$RestoreExit=$LASTEXITCODE}finally{$ErrorActionPreference=$Previous};if($RestoreExit-ne0){$CleanupErrors.Add("Goal active setter exit $RestoreExit")}else{try{$Restore=ConvertFrom-Json -InputObject (($RestoreRaw|ForEach-Object{[string]$_})-join"`n") -ErrorAction Stop;if($Restore.threadId-cne$ThreadId-or$Restore.status-cne'active'){throw 'Goal active identity mismatch'}}catch{$CleanupErrors.Add("Goal active reconcile: $($_.Exception.Message)")}}
  $Cleanup=if($CleanupErrors.Count){$CleanupErrors-join'; '}else{'cleanup verified'};throw [InvalidOperationException]::new("Formal heartbeat handoff failed: $($Primary.Message); $Cleanup",$Primary)
}
```

If the recovery branch prints `FORMAL_RECOVERY_NOT_READY`, stop with the latch intact；if it prints one `FORMAL_RECOVERED_RUN_ID`, use `apply_patch` to persist that exact ID/URL and rerun this fence。Recovery returns before `Start-Process` and never dispatches。On normal launch, record monitor PID/executable/command, exact run/head, interval `1800`, wake gate `300`, start time, validator/artifact, and root-side Task 5 Step 3 command with `apply_patch`。

- [ ] **Step 3: Fresh-shell root identity recheck; cancel only after the 300-minute gate**
```powershell
$ErrorActionPreference = 'Stop'; $Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'; $Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'; $ThreadId = '019f64bd-77a5-7573-88e9-fd80b1882e70'
$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'; $ExpectedValidatorSha='38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'; $ExpectedGoalBridgeSha='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
Set-Location $Wt
$Text = Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$M=[regex]::Match($Text,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $M.Success){throw 'Missing strict Stage 2 head'}; $Head=if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value}; if((git rev-parse HEAD).Trim() -cne $Head){throw 'Local/frozen head mismatch'}
$R=[regex]::Match($Text,'(?m)^- stage2_formal_run_id:\s*(?:(\d+)|`(\d+)`)\s*$'); if(-not $R.Success){throw 'Missing strict formal run id'}; $RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value})
$P=[regex]::Match($Text,'(?m)^- stage2_formal_monitor_pid:\s*(?:(\d+)|`(\d+)`)\s*$'); if(-not $P.Success){throw 'Missing strict formal monitor PID'}; $MonitorPid=[long]$(if($P.Groups[1].Success){$P.Groups[1].Value}else{$P.Groups[2].Value})
if((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne $ExpectedValidatorSha -or (Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne $ExpectedGoalBridgeSha){throw 'Frozen helper drift'}
$Selected=@(Get-Content -LiteralPath $Selection -Encoding utf8 | Where-Object {-not [string]::IsNullOrWhiteSpace($_)}); if($Selected.Count -ne 1 -or $Selected[0] -cne $OriginalNodeId){throw 'Selection is not exact original singleton'}
$Remote=((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]; if($LASTEXITCODE -ne 0 -or $Remote -cne $Head){throw 'Remote/frozen head mismatch'}
if ($null -ne (Get-CimInstance Win32_Process -Filter "ProcessId=$MonitorPid" -ErrorAction SilentlyContinue)) { throw 'Formal heartbeat still running; do not validate or cancel' }
$PowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$GoalRaw = @(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus active)
if ($LASTEXITCODE -ne 0) { throw 'Goal active reconciliation failed' }
$Goal = ConvertFrom-Json -InputObject ($GoalRaw -join "`n") -ErrorAction Stop
if ($Goal.threadId -cne $ThreadId -or $Goal.status -cne 'active') { throw 'Active Goal readback mismatch' }
$RunRaw = @(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,conclusion,workflowName,jobs,url)
if ($LASTEXITCODE -ne 0) { throw 'Failed to read formal run' }
$Run = ConvertFrom-Json -InputObject ($RunRaw -join "`n") -ErrorAction Stop
$Jobs = @($Run.jobs)
if ($Run.attempt -ne 1 -or $Run.event -cne 'workflow_dispatch' -or $Run.headSha -cne $Head -or $Run.headBranch -cne $Branch -or $Run.workflowName -cne $WorkflowName -or $Jobs.Count -ne 1 -or $Jobs[0].name -cne 'precision') { throw 'Formal run/job identity invalid; do not cancel or download' }
if ($Run.status -cne 'completed') {
  if ($Text -notmatch '(?m)^- stage2_formal_timeout_gate_minutes:\s*(?:300|`300`)\s*$') { throw '300-minute gate not armed' }
  if ($Run.status -cne 'in_progress' -or $Jobs[0].status -cne 'in_progress' -or [string]::IsNullOrWhiteSpace([string]$Jobs[0].startedAt)) { throw 'No exact in-progress precision job; do not cancel' }
  $StartedAt = [DateTimeOffset]::MinValue
  if (-not [DateTimeOffset]::TryParse([string]$Jobs[0].startedAt, [ref]$StartedAt)) { throw 'Invalid startedAt; do not cancel' }
  $ElapsedMinutes = ([DateTimeOffset]::UtcNow - $StartedAt.ToUniversalTime()).TotalMinutes
  if ($ElapsedMinutes -lt 300) { throw 'Formal job is below the 300-minute gate; do not cancel' }
  gh run cancel $RunId --repo $Repo
  if ($LASTEXITCODE -ne 0) { throw '300-minute timeout cancellation failed' }
  Write-Output 'FORMAL_TIMEOUT_CANCELLED'
  return
}
if ($Jobs[0].status -cne 'completed') { throw 'Completed run has nonterminal precision job' }
```
If cancelled, record exact elapsed time, run/head/job identity, cancellation result and infrastructure `INVALID`; stop without rerun or artifact validation。
- [ ] **Step 4: Freeze/download/validate the terminal formal artifact in the same fresh shell**
```powershell
$ErrorActionPreference='Stop'; $Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'; $ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'; $Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'; $GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$ArchiveRoot='D:\workspace\pyscf\.agents\archive\precision-ci\experiments'; $Branch='codex/investigate/libxc-712-sgx-extra-cycle-telemetry'; $Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'; $OriginalNodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'; $Repo='psiQAQ/pyscf'; $Workflow='ci-precision-check.yml'; $WorkflowName='Precision investigation'; $ExpectedArtifact='precision-Windows-py3.12'; $ExpectedValidatorSha='38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'; $ExpectedGoalBridgeSha='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
Set-Location $Wt; $Text=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding utf8
$M=[regex]::Match($Text,'(?m)^- stage2_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$'); if(-not $M.Success){throw 'Missing strict Stage 2 head'}; $Head=if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value}; if((git rev-parse HEAD).Trim() -cne $Head){throw 'Local/frozen head mismatch'}
$R=[regex]::Match($Text,'(?m)^- stage2_formal_run_id:\s*(?:(\d+)|`(\d+)`)\s*$'); if(-not $R.Success){throw 'Missing strict formal run id'}; $RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value})
if((Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant() -cne $ExpectedValidatorSha -or (Get-FileHash -Algorithm SHA256 $GoalBridge).Hash.ToLowerInvariant() -cne $ExpectedGoalBridgeSha){throw 'Frozen helper drift'}
$Selected=@(Get-Content -LiteralPath $Selection -Encoding utf8 | Where-Object {-not [string]::IsNullOrWhiteSpace($_)}); if($Selected.Count -ne 1 -or $Selected[0] -cne $OriginalNodeId){throw 'Selection is not exact original singleton'}
$Remote=((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]; if($LASTEXITCODE -ne 0 -or $Remote -cne $Head){throw 'Remote/frozen head mismatch'}
$RunRaw=@(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,conclusion,workflowName,jobs,url); if($LASTEXITCODE -ne 0){throw 'Formal run read failed'}
$Run=ConvertFrom-Json -InputObject ($RunRaw -join "`n") -ErrorAction Stop; $Jobs=@($Run.jobs); if($Run.status -cne 'completed' -or $Run.attempt -ne 1 -or $Run.event -cne 'workflow_dispatch' -or $Run.headSha -cne $Head -or $Run.headBranch -cne $Branch -or $Run.workflowName -cne $WorkflowName -or $Jobs.Count -ne 1 -or $Jobs[0].name -cne 'precision' -or $Jobs[0].status -cne 'completed'){throw 'Formal terminal identity mismatch'}
function Test-JsonInteger { param($Value) return ($Value -is [int] -or $Value -is [long] -or $Value -is [uint32] -or $Value -is [uint64]) }
$Artifacts = @()
for ($i=0; $i -lt 12; $i++) {
  $ApiRaw = @(gh api "repos/$Repo/actions/runs/$RunId/artifacts")
  if ($LASTEXITCODE -ne 0) { throw 'Failed to read formal artifacts' }
  $Api = ConvertFrom-Json -InputObject ($ApiRaw -join "`n") -ErrorAction Stop
  $Artifacts = @($Api.artifacts)
  if (-not (Test-JsonInteger $Api.total_count) -or [long]$Api.total_count -ne $Artifacts.Count) { throw 'Formal artifact envelope invalid' }
  if ($Artifacts.Count -gt 1) { throw 'Multiple formal artifacts' }
  if ($Artifacts.Count -eq 1) { break }
  Start-Sleep -Seconds 5
}
if ($Artifacts.Count -eq 0) { Write-Output 'FORMAL_ARTIFACT_NOT_READY'; return }
$Artifact = $Artifacts[0]
if (-not (Test-JsonInteger $Artifact.id) -or $Artifact.id -le 0 -or $Artifact.name -cne $ExpectedArtifact -or $Artifact.expired -ne $false -or -not (Test-JsonInteger $Artifact.size_in_bytes) -or $Artifact.size_in_bytes -le 0 -or $Artifact.digest -cnotmatch '^sha256:[0-9a-f]{64}$') { throw 'Formal artifact metadata invalid' }
$Dir = Join-Path $ArchiveRoot "$RunId-sgx-hse06-telemetry-stage2-windows-py312"
if (Test-Path -LiteralPath $Dir) { throw "Formal archive exists: $Dir" }
New-Item -ItemType Directory -Path $Dir | Out-Null
$Job = $Jobs[0]
$Meta = [ordered]@{databaseId=$RunId;attempt=$Run.attempt;event=$Run.event;workflowName=$Run.workflowName;headSha=$Run.headSha;headBranch=$Run.headBranch;status=$Run.status;conclusion=$Run.conclusion;jobs=@([ordered]@{name=$Job.name;status=$Job.status;conclusion=$Job.conclusion});artifacts=@([ordered]@{id=$Artifact.id;name=$Artifact.name;digest=$Artifact.digest;sizeInBytes=$Artifact.size_in_bytes;expired=$Artifact.expired})}
$Utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $Dir 'run-metadata.json'), ($Meta | ConvertTo-Json -Depth 5), $Utf8)
gh run download $RunId --repo $Repo --name $Artifact.name --dir $Dir
if ($LASTEXITCODE -ne 0) { throw 'Formal artifact download failed' }
$Report = Join-Path $Dir 'telemetry-validation.json'
conda run --no-capture-output -n pyscf-win313-test python $Validator $Dir `
  --mode installed-wheel --expected-sha $Head --expected-nodeid $OriginalNodeId `
  --expected-profile omp4-blas1 --expected-repeats 200 --expected-native-count 26 `
  --run-metadata (Join-Path $Dir 'run-metadata.json') --expected-run-id $RunId `
  --expected-branch $Branch --report $Report
$ValidatorExit = $LASTEXITCODE
$V = Get-Content -LiteralPath $Report -Raw -Encoding utf8 | ConvertFrom-Json -ErrorAction Stop
Copy-Item -LiteralPath $Validator -Destination (Join-Path $Dir 'validate_sgx_hse06_telemetry.py')
if ((Get-FileHash -Algorithm SHA256 (Join-Path $Dir 'validate_sgx_hse06_telemetry.py')).Hash.ToLowerInvariant() -cne $V.validator_sha256) { throw 'Formal validator hash mismatch' }
if ($ValidatorExit -ne 0 -or -not $V.valid) { throw 'Formal evidence INVALID' }
```
`FORMAL_ARTIFACT_NOT_READY` is upload latency, not `INVALID`: keep Goal active, record exact run/head/monitor PID/observation time, and retry only the exact artifact query later without redispatch。
- [ ] **Step 5: Record the exact verdict and take only the allowed next action**
Use `apply_patch` on the active doc to record run/job/artifact canonical fields, validator SHA, 26-DLL/LibXC 7.1.2 checks, `records/pass/fail/nonconverged/finding_counts/first_failure/first_finding/verdict`, report path and timestamp. Then obey exactly one branch:
- `MECHANISM_CONFIRMED`: stop Stage 2；using the valid failure evidence, write a separate design for the smallest RED/GREEN production fix/test, refresh real-time `pyscf/pyscf:master`, and only then plan a new focused branch from that live master。Do not create that branch in this plan。
- `MECHANISM_FALSIFIED`: stop Stage 2；write a separate design for the smallest density/Fock/`veff` boundary probe。Do not add arrays or a broad diagnostic framework here。
- `INCONCLUSIVE_NONCONVERGED`: retain valid evidence and stop；distinguish main-loop `scf_conv=False` from post-check `post_converged=False`，then design the next minimal convergence-specific experiment。
- `REPRODUCED_OTHER_ASSERTION`: retain valid translation-assertion evidence and stop；do not use it to confirm or falsify finite-difference Extra-cycle mechanism。
- `NOT_REPRODUCED`: record exact text `Stage 2 0/200, NOT_REPRODUCED/HOLD` and stop this round。Do not dispatch another profile, timing run, complete matrix, or update `pyscf/pyscf#3312` as resolved；write a separate next-minimal-experiment plan so the long-term Goal remains active。
- `INVALID`: repair only the experiment/evidence contract for this exact run。Do not draw a scientific conclusion or overwrite the first run with a rerun。

---
## Final Verification
- [ ] Stage 1 gate cites run `31388225490`, artifact `9063452642`, two identical frozen valid reports, `200/200`, independent `APPROVED`, and explicitly avoids fixed/resolved language。
- [ ] RED 1 is the exact contract-vs-selection singleton mismatch；RED 2 is a real original-nodeid source runner whose frozen validator reports marker count `0`, independent of scientific pass/fail。
- [ ] Stage 2 commit parent is `2cd242eec13d0f4a80059738540ea14418b94abd`，subject is `test(sgx): restore full-order HSE06 telemetry [skip ci]`，and exactly three allowed paths differ。
- [ ] Selector/contract/source/witness/formal all use exact singleton original nodeid；dedicated nodeid remains collected and emits one marker but never substitutes for original-nodeid evidence。
- [ ] Original nine-call order remains exact；only the eighth settings-2/HSE06 call has `telemetry=True`；two assertions, delta and convergence parameters remain unchanged。
- [ ] Source original nodeid has one `omp4-blas1` record and exactly one marker；exact `SMOKE_PASS 1/1` unlocks push, while a valid scientific verdict is archived and routed without being mislabeled pipeline failure；dedicated nodeid still emits exactly one marker。
- [ ] UTF-8 no BOM、no lone CR、mixed-EOL guard、`git -c core.whitespace=cr-at-eol diff --check`、26 untracked DLL guard and tracked-clean checks all pass。
- [ ] Every remote shell freezes local/doc/remote head, branch, BeforeMax, exact run id, one precision job, unique artifact id/name/digest/size/expired and canonical metadata fields；every `gh` exit and JSON parse is checked。
- [ ] Both dispatches atomically `CreateNew` an exact-content latch before `gh workflow run`；both recovery branches verify active-doc latch hash/content and only bind `databaseId > BeforeMax` plus exact head。Both heartbeat catches stop/verify only the exact child, reconcile exact Goal active, then aggregate/rethrow；normal success proves exactly one child。
- [ ] Planning self-audit uses only a disposable temp latch and harmless hidden `Start-Sleep` child to runtime-check CreateNew replay refusal, UTF-8 no BOM, inline-parent exclusion, token-mismatch exception followed by exact direct-handle kill/wait/gone, and aggregate rethrow；it never calls real GoalBridge setters or GitHub dispatch。
- [ ] Native automation remains exact `PAUSED`，current-thread ACTIVE count is zero，only one PS1 heartbeat exists，interval is `1800`，Goal is paused while waiting and exact active after terminal/diagnostic/timeout。
- [ ] Witness must be exact `SMOKE_PASS` before direct 200；run `31345422470` cost evidence replaces timing-20；formal cancellation occurs only after fresh root identity and parseable job `startedAt` prove at least 300 minutes。
- [ ] Upload latency is not mislabeled `INVALID`；valid scientific workflow failure remains valid evidence and is never hidden by retry。
- [ ] Stage 2 only restores same-process warm/cache/call order；the plan states telemetry may still perturb allocator/timing and makes no complete-memory-state claim。
- [ ] Verdict routing matches the approved spec；`NOT_REPRODUCED 0/200` is HOLD and stops this round without other profiles/full matrix/issue resolution。
- [ ] No dependency change、runner/workflow/validator/GoalBridge modification、PR、final fix branch or complete matrix is included。
