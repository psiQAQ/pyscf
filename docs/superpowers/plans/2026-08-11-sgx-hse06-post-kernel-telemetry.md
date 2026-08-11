# SGX HSE06 Low-disturbance Post-kernel Telemetry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从已验证但 `NOT_REPRODUCED/HOLD` 的 Stage 2 head 创建独立调查分支，用 base/plus/minus 三个 operation-scoped `post_kernel` wrapper 替换 per-cycle callback，以 schema-v2 证据在 Windows Python 3.12、`omp4-blas1` 下重新执行 1-repeat installed-wheel witness 与 200-repeat formal 实验。

**Architecture:** 调查分支继续运行原始九子例 SGX nodeid，只在第八个 settings-2/HSE06 子例启用诊断。一个 module-local helper 在每个 SCF operation 周围临时安装 owner-specific `post_kernel` wrapper，先调用原 hook、再复制一次 JSON-safe scalar，并在所有成功/异常路径恢复 instance/class lookup；新的本地 ignored validator独立验收 schema-v2，旧 schema-v1 validator与历史 archive 保持冻结。

**Tech Stack:** Python 3.13 local source environment、PySCF SGX/unittest/pytest、标准库 JSON validator、Git worktree、GitHub Actions/`gh`、Windows PowerShell 5.1、Windows installed wheel、LibXC 7.1.2。

## Global Constraints

- Approved spec: `docs/superpowers/specs/2026-08-11-sgx-hse06-post-kernel-telemetry-design.md`，approval commit `e4597c7cf46d0ca2deb4443419d134e7c081cc7d`，content SHA-256 `f780095b97f4ddf3051a0118d43f98ba5bb593e86655765c4e8b6d6ca4626fe9`。
- 新分支必须从 Stage 2 exact head `2133114d93af1c7cb18f1acdc5693e871d8632db` 创建；分支名固定为 `codex/investigate/libxc-712-sgx-post-kernel-telemetry`，worktree 固定为 `D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry`。
- 旧 Stage 2 branch/head、run `31404086927`、artifact `9071911403`、archive 与 validator 不修改、不覆盖、不重写。
- 旧 validator固定为 `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py`，SHA-256 必须始终为 `38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2`。
- 新 validator固定为 `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py`；只使用 Python 标准库，不进入 Git commit、push、PR 或 wheel。
- Tracked scope 只有 `.github/workflows/test_precision_investigation_contract.py` 与 `pyscf/sgx/grad/test/test_rks.py`；selection `.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt` 保持 exact singleton 且不修改。
- Exact remote nodeid 固定为 `pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad`；dedicated method只用于本地辅助检查，不能替代远端证据。
- 原九调用顺序、`delta=1e-4`、`mf.conv_tol=1e-12`、`conv_check=True`、`max_cycle`、两条原 `assertAlmostEqual` 的顺序/表达式/places `12/6` 均保持不变。
- 新 prefix固定为 `PYSCF_SGX_HSE06_POST_KERNEL_TELEMETRY_V2 `，marker `schema_version` 固定为整数 `2`；每个有效 attempt 恰好一行 marker、三个 phase。
- 不修改 PySCF production module、workflow、runner、collector、Windows build/verifier、依赖或科学容差；不添加 retry、不隐藏异常、不派其他 profile/三-nodeid 矩阵/600-repeat。
- Local source smoke 使用现有 `pyscf-win313-test` Conda 环境，不安装或升级包；Windows authoritative evidence 仅来自 GitHub installed-wheel job。
- `test_rks.py` 当前 blob `37743f21fce5ae0d9e39b225ac3a15f5a44a4b5b` 为 mixed EOL；禁止整文件重写或 restage normalization。验收使用 UTF-8 no BOM、no lone CR、`git -c core.whitespace=cr-at-eol diff --check` 与 word-diff scope。
- 远端 dispatch 前必须冻结 local/doc/remote head、BeforeMax、branch、inputs、selection、validator SHA 与 one-shot latch；绝不选择 latest 或重复 dispatch。
- CI 纯等待阶段只允许一个已审计 PS1 heartbeat，间隔 `1800` 秒；Goal 用 exact `paused`/`active` read-back，禁止用 `blocked` 冒充暂停，禁止与 native automation、第二 PS1、`gh run watch` 或人工 sleep loop 并存。
- GoalBridge固定为 `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1`，SHA-256 `4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639`。
- Valid scientific assertion failure 是证据，不等于 infrastructure `INVALID`；Actions failure 不得被 retry 覆盖。`0/200` 固定为 `NOT_REPRODUCED/HOLD`，不能更新 `pyscf/pyscf#3312` 为 resolved。

## File Map

| Path | Responsibility | Lifecycle |
| --- | --- | --- |
| `pyscf/sgx/grad/test/test_rks.py` | operation-scoped hook、schema-v2 payload、fake-owner lifecycle tests、原科学 nodeid | 调查分支 tracked |
| `.github/workflows/test_precision_investigation_contract.py` | failed-attempt raw-log v2 marker preservation、exact singleton selection contract | 调查分支 tracked |
| `.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt` | exact original nodeid | tracked but unchanged |
| `.agents/active/precision-ci/scripts/validate_sgx_hse06_post_kernel_telemetry.py` | strict schema-v2/source/installed-wheel/run/artifact validator | local ignored, frozen per evidence |
| `.agents/active/libxc-712-release-revalidation.md` | live heads、hashes、run IDs、monitor、verdict、next command | local ignored authority |
| `.agents/archive/precision-ci/experiments/RUN_ID-sgx-hse06-post-kernel-*` | immutable downloaded evidence、metadata、validator copy、report | local ignored archive |

---

### Task 1: Create the Isolated Worktree and Freeze the Baseline

**Files:**
- Create worktree: `D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry`
- Update: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Preserve: 26 untracked `pyscf/lib/*.dll` fixtures outside Git

**Interfaces:**
- Consumes: Stage 2 head `2133114d93af1c7cb18f1acdc5693e871d8632db` and the approved spec.
- Produces: clean tracked branch `codex/investigate/libxc-712-sgx-post-kernel-telemetry` with exact 26-DLL local source runtime and a recorded baseline.

- [ ] **Step 1: Invoke the worktree skill and verify source identity**

Use `superpowers:using-git-worktrees` before creating the worktree. Then run this fresh Windows PowerShell block:

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\workspace\pyscf'
$Source = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Target = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$Branch = 'codex/investigate/libxc-712-sgx-post-kernel-telemetry'
$Base = '2133114d93af1c7cb18f1acdc5693e871d8632db'

if ((git -C $Source rev-parse HEAD).Trim() -cne $Base) { throw 'Stage 2 source head drift' }
if (@(git -C $Source status --short --untracked-files=no).Count -ne 0) { throw 'Stage 2 source has tracked changes' }
if (Test-Path -LiteralPath $Target) { throw "Target worktree already exists: $Target" }
git -C $Repo show-ref --verify --quiet "refs/heads/$Branch"
if ($LASTEXITCODE -eq 0) { throw "Local branch already exists: $Branch" }
$remote = @(git -C $Repo ls-remote --heads origin "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $remote.Count -ne 0) { throw 'Remote branch exists or could not be checked' }
```

Expected: no output after the guards and exit code `0`.

- [ ] **Step 2: Create the exact branch/worktree**

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\workspace\pyscf'
$Target = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$Branch = 'codex/investigate/libxc-712-sgx-post-kernel-telemetry'
$Base = '2133114d93af1c7cb18f1acdc5693e871d8632db'
git -C $Repo worktree add -b $Branch $Target $Base
if ($LASTEXITCODE -ne 0) { throw 'git worktree add failed' }
if ((git -C $Target rev-parse HEAD).Trim() -cne $Base) { throw 'New worktree head mismatch' }
if ((git -C $Target branch --show-current).Trim() -cne $Branch) { throw 'New worktree branch mismatch' }
```

Expected: `Preparing worktree` followed by the exact base checkout.

- [ ] **Step 3: Copy and hash only the 26 existing DLL fixtures**

```powershell
$ErrorActionPreference = 'Stop'
$SourceLib = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry\pyscf\lib'
$TargetLib = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry\pyscf\lib'
$sourceFiles = @(Get-ChildItem -LiteralPath $SourceLib -File -Filter '*.dll')
$sourceNames = [string[]]@($sourceFiles | ForEach-Object Name)
[Array]::Sort($sourceNames, [StringComparer]::Ordinal)
if ($sourceNames.Count -ne 26) { throw "Expected 26 source DLLs, found $($sourceNames.Count)" }
foreach ($name in $sourceNames) {
    $destination = Join-Path $TargetLib $name
    if (Test-Path -LiteralPath $destination) { throw "Target DLL already exists: $destination" }
    [IO.File]::Copy((Join-Path $SourceLib $name), $destination, $false)
}
$targetFiles = @(Get-ChildItem -LiteralPath $TargetLib -File -Filter '*.dll')
$targetNames = [string[]]@($targetFiles | ForEach-Object Name)
[Array]::Sort($targetNames, [StringComparer]::Ordinal)
if (($targetNames -join "`n") -cne ($sourceNames -join "`n")) { throw 'DLL name set mismatch' }
foreach ($name in $sourceNames) {
    $sourceHash = (Get-FileHash -LiteralPath (Join-Path $SourceLib $name) -Algorithm SHA256).Hash
    $targetHash = (Get-FileHash -LiteralPath (Join-Path $TargetLib $name) -Algorithm SHA256).Hash
    if ($sourceHash -cne $targetHash) { throw "DLL hash mismatch: $name" }
}
```

Expected: exit `0`; no tracked files changed.

- [ ] **Step 4: Freeze branch, selection, EOL and DLL guards in the active document**

Run:

```powershell
$ErrorActionPreference = 'Stop'
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$Selection = Join-Path $Wt '.github\workflows\precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
$NodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
$selected = @(Get-Content -LiteralPath $Selection -Encoding UTF8 | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
if ($selected.Count -ne 1 -or $selected[0] -cne $NodeId) { throw 'Selection is not the exact original singleton' }
$dlls = @(Get-ChildItem -LiteralPath (Join-Path $Wt 'pyscf\lib') -File -Filter '*.dll')
if ($dlls.Count -ne 26) { throw 'Target DLL count changed' }
if (@(git -C $Wt status --short --untracked-files=no).Count -ne 0) { throw 'New worktree is not tracked-clean' }
git -C $Wt ls-files --eol -- pyscf/sgx/grad/test/test_rks.py
git -C $Wt status --short
```

Expected: `i/mixed w/mixed` for `test_rks.py`; status contains only the 26 DLLs. Use `apply_patch` on the active document to record exact base/branch/worktree, selection, DLL name/hash manifest, blob `37743f21fce5ae0d9e39b225ac3a15f5a44a4b5b`, EOL output and the next Task 2 command.

---

### Task 2: Derive and Freeze the Independent Schema-v2 Validator

**Files:**
- Source read-only: `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py`
- Create: `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py`
- Test: same file via `--self-test`
- Update: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`

**Interfaces:**
- Consumes: schema-v1 validator generic file/runtime/run/artifact contract and approved schema-v2 design.
- Produces: `PREFIX = 'PYSCF_SGX_HSE06_POST_KERNEL_TELEMETRY_V2 '`, strict v2 normalization/classification, independent SHA-256, self-tests, and v1 evidence rejection.

- [ ] **Step 1: Verify and copy the frozen baseline with `apply_patch`**

```powershell
$ErrorActionPreference = 'Stop'
$Old = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$New = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py'
$ExpectedOld = '38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'
if ((Get-FileHash -LiteralPath $Old -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedOld) { throw 'Frozen v1 validator drift' }
if (Test-Path -LiteralPath $New) { throw "New v2 validator already exists: $New" }
```

Use `apply_patch` to create `$New` with the exact current `$Old` content. Do not modify `$Old`, do not import `$Old` from `$New`, and do not create a shared mutable module.

- [ ] **Step 2: Write the v2 RED self-tests before changing validation logic**

Add these exact classifier cases to the copied `ValidatorSelfTest`:

```python
def test_classify_missing_extra_is_inconclusive(self):
    item = self.attempt(all_extra_executed=False)
    result = classify_attempts([item], 1)
    self.assertEqual(result['verdict'], 'INCONCLUSIVE_NONCONVERGED')

def test_classify_confirmed_requires_reconstruction(self):
    item = self.attempt(
        status='fail', pre_pass=True, post_pass=False,
        reconstruction_residual=2e-12)
    result = classify_attempts([item], 1)
    self.assertEqual(result['verdict'], 'MECHANISM_FALSIFIED')
```

Change `ValidatorSelfTest.attempt()` to expose `reconstruction_residual` instead of `shift_residual`, and add boundary mutations with these exact names:

```python
POST_KERNEL_MUTATIONS = (
    'v1-prefix', 'wrong-instrumentation', 'wrong-configured-conv-tol',
    'wrong-effective-conv-tol', 'wrong-effective-conv-tol-grad',
    'wrong-extra-executed', 'wrong-pre-null', 'wrong-extra-shift',
    'wrong-reconstruction-residual',
)
```

Extend the existing direct `InvalidEvidence` and CLI exit-`2` loops to run `MUTATIONS + POST_KERNEL_MUTATIONS`.
Remove the obsolete schema-v1 entries `'wrong-conv-tol'` and `'wrong-conv-check'` from `MUTATIONS`; their stricter schema-v2 replacements are the four configured/effective/extra cases above. Adapt the existing `'wrong-null'` mutation to set `payload['phases']['plus']['extra_shift'] = None` directly.

- [ ] **Step 3: Run self-tests and preserve the intended RED**

```powershell
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py'
conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test
if ($LASTEXITCODE -eq 0) { throw 'Did not observe the schema-v2 validator RED' }
```

Expected: failure includes the missing-extra classifier mismatch and v2 fixture/schema failures; no import, syntax or path error is acceptable as RED.

- [ ] **Step 4: Implement the exact v2 prefix, phase normalization and classifier**

Replace the copied prefix and marker normalization with these interfaces:

```python
PREFIX = 'PYSCF_SGX_HSE06_POST_KERNEL_TELEMETRY_V2 '


def _validate_phase(name, phase):
    fields = (
        'cycle', 'configured_conv_tol', 'effective_conv_tol',
        'effective_conv_tol_grad', 'conv_check', 'extra_executed',
        'pre_extra_energy', 'post_energy', 'extra_shift',
        'final_converged', 'final_norm_gorb', 'final_norm_ddm',
    )
    _require_keys(phase, fields, f'phases.{name}')
    _require(_is_int(phase['cycle']) and phase['cycle'] > 0,
             f'phases.{name}.cycle must be a positive integer')
    for field in ('conv_check', 'extra_executed', 'final_converged'):
        _require(isinstance(phase[field], bool),
                 f'phases.{name}.{field} is not boolean')
    configured = _require_float(
        phase['configured_conv_tol'],
        f'phases.{name}.configured_conv_tol')
    effective = _require_float(
        phase['effective_conv_tol'],
        f'phases.{name}.effective_conv_tol')
    effective_grad = _require_float(
        phase['effective_conv_tol_grad'],
        f'phases.{name}.effective_conv_tol_grad')
    post = _require_float(phase['post_energy'], f'phases.{name}.post_energy')
    _require_float(phase['final_norm_gorb'], f'phases.{name}.final_norm_gorb')
    _require_float(phase['final_norm_ddm'], f'phases.{name}.final_norm_ddm')
    _require(configured == 1e-12,
             f'phases.{name}.configured_conv_tol mismatch')
    _require(phase['conv_check'] is True,
             f'phases.{name}.conv_check must be true')
    expected_extra = phase['conv_check'] and effective == configured * 10
    _require(phase['extra_executed'] is expected_extra,
             f'phases.{name}.extra_executed mismatch')
    if expected_extra:
        _require_close(effective_grad, configured ** .5 * 3,
                       f'phases.{name}.effective_conv_tol_grad')
        pre = _require_float(
            phase['pre_extra_energy'],
            f'phases.{name}.pre_extra_energy')
        shift = _require_float(
            phase['extra_shift'], f'phases.{name}.extra_shift')
        _require_close(shift, post - pre, f'phases.{name}.extra_shift')
    else:
        _require(phase['pre_extra_energy'] is None,
                 f'phases.{name}.pre_extra_energy must be null')
        _require(phase['extra_shift'] is None,
                 f'phases.{name}.extra_shift must be null')
        pre = shift = None
    return {
        'cycle': phase['cycle'],
        'extra_executed': expected_extra,
        'pre_extra_energy': pre,
        'post_energy': post,
        'extra_shift': shift,
        'final_converged': phase['final_converged'],
    }
```

`validate_marker(payload, record)` must enforce exact top-level keys `schema_version`, `instrumentation`, `units`, `case`, `phases`, `result`; exact schema `2`; exact instrumentation below; and the existing exact units/case values:

```python
instrumentation = {
    'mode': 'post_kernel_once_per_phase',
    'per_cycle_callback': False,
    'expected_phase_count': 3,
}
```

For `base`, `plus`, `minus`, call `_validate_phase`. Recompute results exactly:

```python
fd_post = ((plus['post_energy'] - minus['post_energy'])
           / (2 * delta) * BOHR)
if plus['extra_executed'] and minus['extra_executed']:
    fd_pre = ((plus['pre_extra_energy'] - minus['pre_extra_energy'])
              / (2 * delta) * BOHR)
    extra_contribution = ((plus['extra_shift'] - minus['extra_shift'])
                          / (2 * delta) * BOHR)
    reconstruction_residual = fd_post - fd_pre - extra_contribution
    error_pre = analytic_gradient - fd_pre
    pre_pass = bool(round(abs(error_pre), 6) == 0)
else:
    fd_pre = error_pre = extra_contribution = None
    reconstruction_residual = None
    pre_pass = None
error_post = analytic_gradient - fd_post
post_pass = bool(round(abs(error_post), 6) == 0)
```

Require all non-null result floats to be finite, all nulls to match the branch above, `translation_assertion_pass` and finite-difference pass fields to mirror Python `round`, and record status to equal the original two-assertion result. Normalize to:

```python
{
    'attempt': record['attempt'],
    'status': record['status'],
    'translation_pass': translation_pass,
    'pre_pass': pre_pass,
    'post_pass': post_pass,
    'all_converged': all(
        phase['final_converged'] for phase in phases.values()),
    'all_extra_executed': all(
        phase['extra_executed'] for phase in phases.values()),
    'reconstruction_residual': reconstruction_residual,
    'payload': payload,
}
```

Replace the classifier branch with:

```python
if item['status'] == 'fail':
    failures.append(item)
    if not item['translation_pass']:
        verdict = 'REPRODUCED_OTHER_ASSERTION'
    elif not item['all_converged'] or not item['all_extra_executed']:
        verdict = 'INCONCLUSIVE_NONCONVERGED'
    elif (not item['post_pass'] and item['pre_pass']
          and abs(item['reconstruction_residual']) <= 1e-12):
        verdict = 'MECHANISM_CONFIRMED'
    else:
        verdict = 'MECHANISM_FALSIFIED'
elif not item['all_converged'] or not item['all_extra_executed']:
    verdict = 'INCONCLUSIVE_NONCONVERGED'
```

- [ ] **Step 5: Update complete fixtures and mutation implementations**

Replace `_fixture_payload()` with this deterministic valid schema-v2 fixture:

```python
def _fixture_payload():
    delta = 1e-4
    phases = {}
    for name, post, shift in (
            ('base', -76.0, 1e-10),
            ('plus', -75.999999, 2e-10),
            ('minus', -76.000001, 1e-10)):
        pre = post - shift
        phases[name] = {
            'cycle': 22,
            'configured_conv_tol': 1e-12,
            'effective_conv_tol': 1e-11,
            'effective_conv_tol_grad': 3e-6,
            'conv_check': True,
            'extra_executed': True,
            'pre_extra_energy': pre,
            'post_energy': post,
            'extra_shift': post - pre,
            'final_converged': True,
            'final_norm_gorb': 1e-10,
            'final_norm_ddm': 2e-10,
        }
    fd_post = ((phases['plus']['post_energy']
                - phases['minus']['post_energy'])
               / (2 * delta) * BOHR)
    fd_pre = ((phases['plus']['pre_extra_energy']
               - phases['minus']['pre_extra_energy'])
              / (2 * delta) * BOHR)
    contribution = ((phases['plus']['extra_shift']
                     - phases['minus']['extra_shift'])
                    / (2 * delta) * BOHR)
    analytic = fd_post
    error_pre = analytic - fd_pre
    error_post = analytic - fd_post
    return {
        'schema_version': 2,
        'instrumentation': {
            'mode': 'post_kernel_once_per_phase',
            'per_cycle_callback': False,
            'expected_phase_count': 3,
        },
        'units': {
            'energy': 'Hartree',
            'gradient': 'Hartree/Bohr',
            'displacement': 'Angstrom',
        },
        'case': {
            'settings_index': 2,
            'settings': [True, True, True, True, True],
            'precision': 6,
            'xc': 'HSE06',
            'delta': delta,
            'translation_places': 12,
            'finite_difference_places': 6,
        },
        'phases': phases,
        'result': {
            'analytic_gradient': analytic,
            'translation_l1': 0.0,
            'translation_assertion_pass': True,
            'finite_difference_pre': fd_pre,
            'finite_difference_post': fd_post,
            'gradient_error_pre': error_pre,
            'gradient_error_post': error_post,
            'finite_difference_pre_pass': bool(
                round(abs(error_pre), 6) == 0),
            'finite_difference_post_pass': True,
            'extra_contribution': contribution,
            'reconstruction_residual': fd_post - fd_pre - contribution,
        },
    }
```

Implement `_recompute_fixture_result()` with the formulas from Step 4 and emit `None` for the entire pre/extra/reconstruction group whenever plus or minus has `extra_executed=False`.

Add these exact branches before the generic mutation branches; every case corrupts one trust boundary and then rewrites only the marker unless it is the prefix case:

```python
if mutation == 'v1-prefix':
    path = root / 'logs' / 'node-001-attempt-0001.log'
    text = path.read_text(encoding='utf-8')
    path.write_text(
        text.replace(PREFIX, 'PYSCF_SGX_HSE06_TELEMETRY_V1 ', 1),
        encoding='utf-8', newline='\n')
elif mutation in POST_KERNEL_MUTATIONS:
    payload = _load_fixture_marker(root)
    phase = payload['phases']['plus']
    if mutation == 'wrong-instrumentation':
        payload['instrumentation']['per_cycle_callback'] = True
    elif mutation == 'wrong-configured-conv-tol':
        phase['configured_conv_tol'] = 1e-10
    elif mutation == 'wrong-effective-conv-tol':
        phase['effective_conv_tol'] = 1e-12
    elif mutation == 'wrong-effective-conv-tol-grad':
        phase['effective_conv_tol_grad'] = 1e-5
    elif mutation == 'wrong-extra-executed':
        phase['extra_executed'] = False
    elif mutation == 'wrong-pre-null':
        phase['pre_extra_energy'] = None
    elif mutation == 'wrong-extra-shift':
        phase['extra_shift'] += 1e-8
    elif mutation == 'wrong-reconstruction-residual':
        payload['result']['reconstruction_residual'] = 2e-12
    _write_fixture_marker(root, payload)
```

Keep every generic provenance mutation active. Add a fixture test that sets both plus/minus `extra_executed=False`, their pre/shift fields to `None`, calls `_recompute_fixture_result()`, and asserts the four pre/extra/reconstruction result fields are all `None` while validation remains structurally valid and classifies `INCONCLUSIVE_NONCONVERGED`.

- [ ] **Step 6: Run complete v2 self-tests and prove v1 isolation**

```powershell
$ErrorActionPreference = 'Stop'
$Old = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$New = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py'
$ExpectedOld = '38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'
conda run --no-capture-output -n pyscf-win313-test python $New --self-test
if ($LASTEXITCODE -ne 0) { throw 'Schema-v2 validator self-tests failed' }
conda run --no-capture-output -n pyscf-win313-test python $Old --self-test
if ($LASTEXITCODE -ne 0) { throw 'Frozen schema-v1 self-tests regressed' }
if ((Get-FileHash -LiteralPath $Old -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedOld) { throw 'Frozen schema-v1 hash changed' }
conda run --no-capture-output -n pyscf-win313-test python -m py_compile $New
if ($LASTEXITCODE -ne 0) { throw 'Schema-v2 validator py_compile failed' }
[pscustomobject]@{
    old_sha256 = $ExpectedOld
    new_sha256 = (Get-FileHash -LiteralPath $New -Algorithm SHA256).Hash.ToLowerInvariant()
} | ConvertTo-Json -Compress
```

Expected: both self-test suites pass; old hash is unchanged; new hash is a different 64-hex value. Record the exact new hash, self-test count, mutation count and review result in the active document. Do not stage either validator.

---

### Task 3: Update the Failed-attempt Raw-log Contract to Schema v2

**Files:**
- Modify: `.github/workflows/test_precision_investigation_contract.py`
- Test: `.github/workflows/test_precision_investigation_contract.py::PrecisionInvestigationContractTest::test_failed_attempt_keeps_complete_evidence_and_exits_nonzero`

**Interfaces:**
- Consumes: v2 prefix/instrumentation from Task 2.
- Produces: runner evidence contract proving a failed pytest attempt retains exactly one parseable v2 marker without runner changes.

- [ ] **Step 1: Write the v2 expectation while leaving the synthetic fixture v1**

Change the constant to:

```python
SGX_HSE06_TELEMETRY_PREFIX = (
    'PYSCF_SGX_HSE06_POST_KERNEL_TELEMETRY_V2 '
)
```

Change only the final expected payload to schema `2` and add:

```python
expected_instrumentation = {
    'mode': 'post_kernel_once_per_phase',
    'per_cycle_callback': False,
    'expected_phase_count': 3,
}
```

Leave the synthetic `payload` definition at schema `1` for this RED.

- [ ] **Step 2: Run the exact RED**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
Set-Location $Wt
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  .github/workflows/test_precision_investigation_contract.py::PrecisionInvestigationContractTest::test_failed_attempt_keeps_complete_evidence_and_exits_nonzero `
  -c pytest.ini -q
if ($LASTEXITCODE -eq 0) { throw 'Did not observe the v2 raw-log contract RED' }
```

Expected: one assertion mismatch showing actual schema `1`/missing instrumentation versus expected schema `2`; runner startup, collection or permission failures are not acceptable.

- [ ] **Step 3: Update the synthetic fixture to v2**

Make the fixture payload exactly:

```python
payload = {
    'schema_version': 2,
    'instrumentation': {
        'mode': 'post_kernel_once_per_phase',
        'per_cycle_callback': False,
        'expected_phase_count': 3,
    },
    'case': {
        'settings_index': 2,
        'settings': [True, True, True, True, True],
        'precision': 6,
        'xc': 'HSE06',
        'delta': 1e-4,
        'translation_places': 12,
        'finite_difference_places': 6,
    },
    'result': {
        'translation_assertion_pass': True,
        'finite_difference_post_pass': False,
    },
}
```

This test intentionally proves only raw-log preservation, not the complete scientific schema; do not add a second runner or parser.

- [ ] **Step 4: Run narrow and full contract suites**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
Set-Location $Wt
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  .github/workflows/test_precision_investigation_contract.py::PrecisionInvestigationContractTest::test_failed_attempt_keeps_complete_evidence_and_exits_nonzero `
  -c pytest.ini -q
if ($LASTEXITCODE -ne 0) { throw 'Narrow v2 raw-log contract failed' }
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  .github/workflows/test_precision_investigation_contract.py -c pytest.ini -q
if ($LASTEXITCODE -ne 0) { throw 'Full precision contract failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'Contract diff check failed' }
```

Expected: narrow pass and the complete contract file passes with the existing exact singleton selection unchanged.

- [ ] **Step 5: Commit only the contract**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
Set-Location $Wt
$Path = '.github/workflows/test_precision_investigation_contract.py'
$changed = @(git diff --name-only)
if ($changed.Count -ne 1 -or $changed[0] -cne $Path) { throw 'Unexpected Task 3 scope' }
git add -- $Path
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw 'Task 3 staged diff check failed' }
git commit -m "test(ci): preserve post-kernel telemetry evidence [skip ci]"
if ($LASTEXITCODE -ne 0) { throw 'Task 3 commit failed' }
```

Expected: one commit whose parent is exact base `2133114d93af1c7cb18f1acdc5693e871d8632db` and whose only path is the contract file.

---

### Task 4: Add the Operation-scoped Hook with Fake-owner TDD

**Files:**
- Modify: `pyscf/sgx/grad/test/test_rks.py`
- Test: new `PostKernelSnapshotTest` methods in the same file

**Interfaces:**
- Produces: `_run_with_post_kernel_snapshot(owner, phase, snapshots, operation, snapshotter, *args, **kwargs)` with exact owner restoration and unchanged operation result/exception semantics.
- Consumed by: Task 5 scientific telemetry integration.

- [ ] **Step 1: Add fake-owner tests before defining the helper**

Add a new `PostKernelSnapshotTest(unittest.TestCase)` before `KnownValues`. The tests must call the not-yet-defined helper and cover these exact cases:

```python
class PostKernelSnapshotTest(unittest.TestCase):
    class Owner:
        def __init__(self):
            self.events = []

        def post_kernel(self, envs):
            self.events.append('original')

    def test_calls_original_before_snapshot_and_restores_class_lookup(self):
        owner = self.Owner()
        snapshots = {}
        envs = {}

        def snapshotter(value):
            owner.events.append('snapshot')
            self.assertIs(value, envs)
            return {'value': 1}

        def operation():
            owner.post_kernel(envs)
            return 'result'

        result = _run_with_post_kernel_snapshot(
            owner, 'base', snapshots, operation, snapshotter)
        self.assertEqual(result, 'result')
        self.assertEqual(owner.events, ['original', 'snapshot'])
        self.assertEqual(snapshots, {'base': {'value': 1}})
        self.assertNotIn('post_kernel', owner.__dict__)

    def test_restores_after_operation_error(self):
        owner = self.Owner()
        with self.assertRaisesRegex(ValueError, 'operation'):
            _run_with_post_kernel_snapshot(
                owner, 'base', {},
                lambda: (_ for _ in ()).throw(ValueError('operation')),
                lambda envs: {})
        self.assertNotIn('post_kernel', owner.__dict__)

    def test_restores_after_snapshot_error(self):
        owner = self.Owner()
        def operation():
            owner.post_kernel({})
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            _run_with_post_kernel_snapshot(
                owner, 'base', {}, operation,
                lambda envs: (_ for _ in ()).throw(ValueError('snapshot')))
        self.assertEqual(owner.events, ['original'])
        self.assertNotIn('post_kernel', owner.__dict__)

    def test_restores_existing_instance_shadow(self):
        owner = self.Owner()
        shadow = lambda envs: owner.events.append('shadow')
        owner.post_kernel = shadow
        def operation():
            owner.post_kernel({})
        _run_with_post_kernel_snapshot(
            owner, 'plus', {}, operation, lambda envs: {})
        self.assertIs(owner.__dict__['post_kernel'], shadow)
        self.assertEqual(owner.events, ['shadow'])

    def test_rejects_zero_or_multiple_post_kernel_calls(self):
        owner = self.Owner()
        with self.assertRaisesRegex(RuntimeError, 'exactly once'):
            _run_with_post_kernel_snapshot(
                owner, 'base', {}, lambda: None, lambda envs: {})
        self.assertNotIn('post_kernel', owner.__dict__)
        def twice():
            owner.post_kernel({})
            owner.post_kernel({})
        with self.assertRaisesRegex(RuntimeError, 'exactly once'):
            _run_with_post_kernel_snapshot(
                owner, 'base', {}, twice, lambda envs: {})
        self.assertNotIn('post_kernel', owner.__dict__)
```

- [ ] **Step 2: Run the helper RED**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
Set-Location $Wt
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::PostKernelSnapshotTest `
  -c pytest.ini -q
if ($LASTEXITCODE -eq 0) { throw 'Did not observe undefined-helper RED' }
```

Expected: collection succeeds and tests fail with `_run_with_post_kernel_snapshot` undefined; memory allocation, DLL or collection errors are not acceptable.

- [ ] **Step 3: Implement the minimal operation-scoped helper**

Add this module-local function before the test classes:

```python
def _run_with_post_kernel_snapshot(
        owner, phase, snapshots, operation, snapshotter, *args, **kwargs):
    had_shadow = 'post_kernel' in owner.__dict__
    previous_shadow = owner.__dict__.get('post_kernel')
    original = owner.post_kernel
    calls = 0

    def wrapped(envs):
        nonlocal calls
        original(envs)
        calls += 1
        if calls != 1:
            raise RuntimeError('post_kernel must be called exactly once')
        snapshots[phase] = snapshotter(envs)

    owner.post_kernel = wrapped
    try:
        result = operation(*args, **kwargs)
        if calls != 1:
            raise RuntimeError('post_kernel must be called exactly once')
        return result
    finally:
        if had_shadow:
            owner.__dict__['post_kernel'] = previous_shadow
        else:
            owner.__dict__.pop('post_kernel', None)
```

- [ ] **Step 4: Run helper tests and existing dedicated scientific nodeid**

Pin local resource variables before every scientific invocation:

```powershell
$ErrorActionPreference = 'Stop'
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$env:OMP_NUM_THREADS='1';$env:OPENBLAS_NUM_THREADS='1';$env:MKL_NUM_THREADS='1'
$env:BLIS_NUM_THREADS='1';$env:VECLIB_MAXIMUM_THREADS='1';$env:NUMEXPR_NUM_THREADS='1'
Set-Location $Wt
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::PostKernelSnapshotTest `
  -c pytest.ini -q
if ($LASTEXITCODE -ne 0) { throw 'Post-kernel helper tests failed' }
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry `
  -c pytest.ini -q
if ($LASTEXITCODE -ne 0) { throw 'Existing dedicated telemetry nodeid regressed before integration' }
```

Expected: helper suite passes; existing dedicated nodeid still passes with the old v1 marker because Task 5 has not changed scientific telemetry yet.

- [ ] **Step 5: Commit helper and tests only**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
Set-Location $Wt
$Path = 'pyscf/sgx/grad/test/test_rks.py'
$changed = @(git diff --name-only)
if ($changed.Count -ne 1 -or $changed[0] -cne $Path) { throw 'Unexpected Task 4 scope' }
git add -- $Path
git -c core.whitespace=cr-at-eol diff --cached --check
if ($LASTEXITCODE -ne 0) { throw 'Task 4 staged diff check failed' }
git commit -m "test(sgx): add scoped post-kernel telemetry hook [skip ci]"
if ($LASTEXITCODE -ne 0) { throw 'Task 4 commit failed' }
```

Expected: second branch commit; only `test_rks.py` differs from the Task 3 head.

---

### Task 5: Replace Per-cycle Telemetry with the Schema-v2 Scientific Payload

**Files:**
- Modify: `pyscf/sgx/grad/test/test_rks.py`
- Test: dedicated and original SGX nodeids, helper tests, precision contract

**Interfaces:**
- Consumes: Task 4 helper and Task 2 validator.
- Produces: one v2 marker per telemetry-enabled `_check_finite_diff_grad`, with base/plus/minus post-kernel snapshots and unchanged original assertions.

- [ ] **Step 1: Preserve a real v1-to-v2 integration RED**

Before modifying scientific telemetry, run the dedicated nodeid through the canonical runner and new validator:

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py'
$NodeFile=Join-Path $Wt 'tmp\post-kernel-red-nodeids.txt'
$Output=Join-Path $Wt 'tmp\post-kernel-v1-red'
$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
$utf8=New-Object Text.UTF8Encoding($false)
[void][IO.Directory]::CreateDirectory((Join-Path $Wt 'tmp'))
if(Test-Path -LiteralPath $Output){throw "Integration RED output already exists: $Output"}
[IO.File]::WriteAllText($NodeFile,"$NodeId`n",$utf8)
$Head=(git -C $Wt rev-parse HEAD).Trim()
$previous=$ErrorActionPreference;$ErrorActionPreference='Continue'
try {
  conda run --no-capture-output -n pyscf-win313-test python (Join-Path $Wt '.github\workflows\run_precision_tests.py') `
    --nodeids-file $NodeFile --repeats 1 --profile 4/1 --output-dir $Output `
    --tested-sha $Head --working-directory $Wt --rootdir $Wt `
    --pytest-config (Join-Path $Wt 'pytest.ini') --environment-mode source-tree `
    --collector (Join-Path $Wt '.github\workflows\collect_precision_environment.py')
  $runnerExit=$LASTEXITCODE
} finally { $ErrorActionPreference=$previous }
[IO.File]::WriteAllText((Join-Path $Output 'runner-exit-code.txt'),"$runnerExit`n",(New-Object Text.UTF8Encoding($false)))
$Report=Join-Path $Output 'telemetry-validation.json'
conda run --no-capture-output -n pyscf-win313-test python $Validator $Output `
  --mode source-tree --expected-sha $Head --expected-nodeid $NodeId `
  --expected-profile omp4-blas1 --expected-repeats 1 --source-root $Wt `
  --report $Report
if ($LASTEXITCODE -ne 2) { throw 'Expected v2 validator exit 2 against v1 evidence' }
$V=Get-Content -LiteralPath $Report -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop
if($V.valid-ne$false-or$V.verdict-cne'INVALID'-or($V.errors-join' ') -notmatch 'marker'){throw 'Unexpected integration RED'}
```

Expected: scientific pytest may pass, but v2 validator returns exit `2`, `INVALID`, solely because no strict v2 marker exists. Preserve this ignored evidence directory until Task 5 review completes.

- [ ] **Step 2: Add the exact post-kernel scalar snapshot**

Replace `TELEMETRY_PREFIX` and add:

```python
TELEMETRY_PREFIX = 'PYSCF_SGX_HSE06_POST_KERNEL_TELEMETRY_V2 '


def _snapshot_post_kernel(envs):
    configured_conv_tol = float(envs['mf'].conv_tol)
    effective_conv_tol = float(envs['conv_tol'])
    conv_check = bool(envs['conv_check'])
    extra_executed = (
        conv_check
        and effective_conv_tol == configured_conv_tol * 10
    )
    post_energy = float(envs['e_tot'])
    if extra_executed:
        pre_extra_energy = float(envs['last_hf_e'])
        extra_shift = post_energy - pre_extra_energy
    else:
        pre_extra_energy = None
        extra_shift = None
    return {
        'cycle': int(envs['cycle']) + 1,
        'configured_conv_tol': configured_conv_tol,
        'effective_conv_tol': effective_conv_tol,
        'effective_conv_tol_grad': float(envs['conv_tol_grad']),
        'conv_check': conv_check,
        'extra_executed': extra_executed,
        'pre_extra_energy': pre_extra_energy,
        'post_energy': post_energy,
        'extra_shift': extra_shift,
        'final_converged': bool(envs['scf_conv']),
        'final_norm_gorb': float(envs['norm_gorb']),
        'final_norm_ddm': float(envs['norm_ddm']),
    }
```

- [ ] **Step 3: Replace callback state with three operation-scoped calls**

Inside `_check_finite_diff_grad`, delete `phase`, `main_cycles`, `post`, `snapshot_main_cycle`, and `mf.callback`. Use:

```python
snapshots = {}
gradient = mf.nuc_grad_method().set(
    sgx_grid_response=True, grid_response=True)
if telemetry:
    g = _run_with_post_kernel_snapshot(
        mf, 'base', snapshots, gradient.kernel, _snapshot_post_kernel)
else:
    g = gradient.kernel()

mol1 = mol.copy()
mf_scanner = mf.as_scanner()
delta = 1e-4
plus_mol = mol1.set_geom_(
    f'O  0. 0. {delta:f}; 1  0. -0.757 0.587; 1  0. 0.757 0.587')
if telemetry:
    e1 = _run_with_post_kernel_snapshot(
        mf_scanner, 'plus', snapshots, mf_scanner,
        _snapshot_post_kernel, plus_mol)
else:
    e1 = mf_scanner(plus_mol)

minus_mol = mol1.set_geom_(
    f'O  0. 0. -{delta:f}; 1  0. -0.757 0.587; 1  0. 0.757 0.587')
if telemetry:
    e2 = _run_with_post_kernel_snapshot(
        mf_scanner, 'minus', snapshots, mf_scanner,
        _snapshot_post_kernel, minus_mol)
else:
    e2 = mf_scanner(minus_mol)
```

Do not change either original assertion below this block.

- [ ] **Step 4: Build the exact schema-v2 result before the original assertions**

In the telemetry branch, require `set(snapshots) == {'base', 'plus', 'minus'}`. Compute:

```python
analytic_gradient = float(g[0,2])
translation_l1 = float(numpy.abs(g.sum(axis=0)).sum())
fd_post = (e1 - e2) / (2 * delta) * lib.param.BOHR
error_post = analytic_gradient - fd_post
if (snapshots['plus']['extra_executed']
        and snapshots['minus']['extra_executed']):
    fd_pre = (
        snapshots['plus']['pre_extra_energy']
        - snapshots['minus']['pre_extra_energy']
    ) / (2 * delta) * lib.param.BOHR
    error_pre = analytic_gradient - fd_pre
    extra_contribution = (
        snapshots['plus']['extra_shift']
        - snapshots['minus']['extra_shift']
    ) / (2 * delta) * lib.param.BOHR
    reconstruction_residual = (
        fd_post - fd_pre - extra_contribution)
    pre_pass = bool(round(abs(error_pre), 6) == 0)
else:
    fd_pre = None
    error_pre = None
    extra_contribution = None
    reconstruction_residual = None
    pre_pass = None
```

Build the payload with exact `instrumentation`, `units`, `case`, `phases=snapshots`, and:

```python
result = {
    'analytic_gradient': analytic_gradient,
    'translation_l1': translation_l1,
    'translation_assertion_pass': bool(
        round(abs(translation_l1), 12) == 0),
    'finite_difference_pre': fd_pre,
    'finite_difference_post': fd_post,
    'gradient_error_pre': error_pre,
    'gradient_error_post': error_post,
    'finite_difference_pre_pass': pre_pass,
    'finite_difference_post_pass': bool(
        round(abs(error_post), 6) == 0),
    'extra_contribution': extra_contribution,
    'reconstruction_residual': reconstruction_residual,
}
```

Print exactly one line with `json.dumps(..., sort_keys=True, separators=(',', ':'), allow_nan=False)` immediately before the unchanged assertions.

- [ ] **Step 5: Run helper, dedicated, original and contract checks**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$env:OMP_NUM_THREADS='1';$env:OPENBLAS_NUM_THREADS='1';$env:MKL_NUM_THREADS='1'
$env:BLIS_NUM_THREADS='1';$env:VECLIB_MAXIMUM_THREADS='1';$env:NUMEXPR_NUM_THREADS='1'
Set-Location $Wt
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::PostKernelSnapshotTest -c pytest.ini -q
if($LASTEXITCODE-ne0){throw 'Helper tests failed'}
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry `
  -c pytest.ini -q
if($LASTEXITCODE-ne0){throw 'Dedicated v2 nodeid failed'}
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad `
  -c pytest.ini -q
if($LASTEXITCODE-ne0){throw 'Original nine-case nodeid failed'}
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  .github/workflows/test_precision_investigation_contract.py -c pytest.ini -q
if($LASTEXITCODE-ne0){throw 'Precision contract failed'}
```

Capture and validate both outputs with this exact block; a nonzero scientific assertion is retained, while any other failure stops the task:

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$Prefix='PYSCF_SGX_HSE06_POST_KERNEL_TELEMETRY_V2 '
$V1Prefix='PYSCF_SGX_HSE06_TELEMETRY_V1 '
$Utf8=New-Object Text.UTF8Encoding($false)
[void][IO.Directory]::CreateDirectory((Join-Path $Wt 'tmp'))
function Invoke-Node([string]$NodeId,[string]$LogName) {
  $Previous=$ErrorActionPreference;$ErrorActionPreference='Continue'
  try {
    $Raw=@(conda run --no-capture-output -n pyscf-win313-test python -m pytest `
      $NodeId -c pytest.ini -q -s 2>&1)
    $Exit=$LASTEXITCODE
  } finally { $ErrorActionPreference=$Previous }
  $Text=($Raw|ForEach-Object{[string]$_})-join"`n"
  [IO.File]::WriteAllText((Join-Path $Wt $LogName),$Text+"`n",$Utf8)
  $Markers=@($Text-split"`r?`n"|Where-Object{$_.StartsWith($Prefix,[StringComparison]::Ordinal)})
  if($Markers.Count-ne1){throw "$LogName marker count is $($Markers.Count), expected 1"}
  if(($Text-split"`r?`n"|Where-Object{$_.StartsWith($V1Prefix,[StringComparison]::Ordinal)}).Count-ne0){throw "$LogName contains v1 marker"}
  $Payload=$Markers[0].Substring($Prefix.Length)|ConvertFrom-Json -ErrorAction Stop
  if($Payload.schema_version-ne2-or$Payload.instrumentation.mode-cne'post_kernel_once_per_phase'-or$Payload.instrumentation.per_cycle_callback-ne$false-or$Payload.instrumentation.expected_phase_count-ne3-or$Payload.case.settings_index-ne2-or$Payload.case.xc-cne'HSE06'){throw "$LogName payload identity mismatch"}
  if($Exit-ne0-and$Text-notmatch'AssertionError'){throw "$LogName failed outside a scientific assertion"}
  [pscustomobject]@{Exit=$Exit;Payload=$Payload;Log=(Join-Path $Wt $LogName)}
}
Set-Location $Wt
$Dedicated=Invoke-Node `
  'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry' `
  'tmp\post-kernel-dedicated.log'
$Original=Invoke-Node `
  'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad' `
  'tmp\post-kernel-original.log'
Write-Output "DEDICATED_EXIT=$($Dedicated.Exit)"
Write-Output "ORIGINAL_EXIT=$($Original.Exit)"
```

Do not rely on visual log inspection. If either exit is nonzero only because an original assertion reproduced, preserve both logs and proceed to Task 6 so the canonical runner/validator can classify it; do not commit a claimed `SMOKE_PASS`.

- [ ] **Step 6: Commit the scientific telemetry change**

```powershell
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
Set-Location $Wt
$Path='pyscf/sgx/grad/test/test_rks.py'
$changed=@(git diff --name-only)
if($changed.Count-ne1-or$changed[0]-cne$Path){throw 'Unexpected Task 5 scope'}
git add -- $Path
git -c core.whitespace=cr-at-eol diff --cached --check
if($LASTEXITCODE-ne0){throw 'Task 5 staged diff check failed'}
git commit -m "test(sgx): emit post-kernel HSE06 telemetry [skip ci]"
if($LASTEXITCODE-ne0){throw 'Task 5 commit failed'}
```

Expected: third branch commit; branch diff from base remains exactly two tracked paths.

---

### Task 6: Produce Canonical Source Evidence, Freeze the Head, Review, and Push

**Files:**
- Verify: the two tracked branch paths and unchanged selection file
- Create ignored evidence: `tmp/post-kernel-source-HEAD_SHORT`
- Create ignored immutable freeze: `.agents/active/precision-ci/freezes/post-kernel-source-HEAD.json`
- Update: `.agents/active/libxc-712-release-revalidation.md`

**Interfaces:**
- Consumes: three focused commits, the exact original-nodeid selection, schema-v2 validator, and 26 local DLL fixtures.
- Produces: one canonical source-tree record, an immutable head/validator/source-report binding, independent branch review, and only then the exact remote investigation branch.

- [ ] **Step 1: Re-run both validator suites and freeze the old validator**

```powershell
$ErrorActionPreference='Stop'
$Old='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$New='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py'
if((Get-FileHash -LiteralPath $Old -Algorithm SHA256).Hash.ToLowerInvariant()-cne'38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2'){throw 'Frozen v1 validator drift'}
conda run --no-capture-output -n pyscf-win313-test python $Old --self-test
if($LASTEXITCODE-ne0){throw 'Frozen v1 validator self-test failed'}
conda run --no-capture-output -n pyscf-win313-test python $New --self-test
if($LASTEXITCODE-ne0){throw 'Schema-v2 validator self-test failed'}
conda run --no-capture-output -n pyscf-win313-test python -m py_compile $New
if($LASTEXITCODE-ne0){throw 'Schema-v2 validator py_compile failed'}
$NewSha=(Get-FileHash -LiteralPath $New -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Output "POST_KERNEL_VALIDATOR_SHA256=$NewSha"
```

- [ ] **Step 2: Run the canonical source-tree evidence path even when the assertion fails**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
$Selection=Join-Path $Wt '.github\workflows\precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
$Runner=Join-Path $Wt '.github\workflows\run_precision_tests.py'
$Collector=Join-Path $Wt '.github\workflows\collect_precision_environment.py'
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py'
$Head=(git -C $Wt rev-parse HEAD).Trim();if($LASTEXITCODE-ne0-or$Head-cnotmatch'^[0-9a-f]{40}$'){throw 'Invalid branch head'}
$Short=$Head.Substring(0,12);$Evidence=Join-Path $Wt "tmp\post-kernel-source-$Short"
if(Test-Path -LiteralPath $Evidence){throw "Source evidence already exists: $Evidence"}
$Selected=@(Get-Content -LiteralPath $Selection -Encoding UTF8|Where-Object{-not[string]::IsNullOrWhiteSpace($_)})
if($Selected.Count-ne1-or$Selected[0]-cne$NodeId){throw 'Selection is not exact original singleton'}
$env:OMP_NUM_THREADS='4';$env:OPENBLAS_NUM_THREADS='1';$env:MKL_NUM_THREADS='1'
$env:BLIS_NUM_THREADS='1';$env:VECLIB_MAXIMUM_THREADS='1';$env:NUMEXPR_NUM_THREADS='1'
$Previous=$ErrorActionPreference;$ErrorActionPreference='Continue'
try {
  conda run --no-capture-output -n pyscf-win313-test python $Runner `
    --nodeids-file $Selection --repeats 1 --profile 4/1 `
    --output-dir $Evidence --tested-sha $Head --working-directory $Wt `
    --rootdir $Wt --pytest-config (Join-Path $Wt 'pytest.ini') `
    --collector $Collector --environment-mode source-tree
  $RunnerExit=$LASTEXITCODE
} finally {$ErrorActionPreference=$Previous}
if(-not(Test-Path -LiteralPath (Join-Path $Evidence 'records.jsonl'))){throw 'Runner produced no records'}
$Utf8=New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $Evidence 'runner-exit-code.txt'),[string]$RunnerExit+"`n",$Utf8)
$Report=Join-Path $Evidence 'post-kernel-validation.json'
conda run --no-capture-output -n pyscf-win313-test python $Validator $Evidence `
  --mode source-tree --expected-sha $Head --expected-nodeid $NodeId `
  --expected-profile omp4-blas1 --expected-repeats 1 --source-root $Wt `
  --report $Report
$ValidatorExit=$LASTEXITCODE
$V=Get-Content -LiteralPath $Report -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop
if($ValidatorExit-ne0-or-not$V.valid){throw 'Canonical source evidence is INVALID'}
Copy-Item -LiteralPath $Validator -Destination (Join-Path $Evidence 'validate_sgx_hse06_post_kernel_telemetry.py')
if((Get-FileHash -LiteralPath (Join-Path $Evidence 'validate_sgx_hse06_post_kernel_telemetry.py') -Algorithm SHA256).Hash.ToLowerInvariant()-cne$V.validator_sha256){throw 'Source validator copy/hash mismatch'}
Write-Output "SOURCE_HEAD=$Head"
Write-Output "SOURCE_RUNNER_EXIT=$RunnerExit"
Write-Output "SOURCE_VERDICT=$($V.verdict)"
Write-Output "SOURCE_REPORT=$Report"
```

Use `apply_patch` to record exact keys `post_kernel_head`, `post_kernel_validator_sha256`, `post_kernel_source_runner_exit`, `post_kernel_source_report`, `post_kernel_source_records/pass/fail/nonconverged`, `post_kernel_source_first_failure`, `post_kernel_source_first_finding`, and `post_kernel_source_verdict`. Only exact `SMOKE_PASS` continues. Any valid scientific finding is retained and routes directly to Task 8 Step 5 without push; `INVALID` repairs the evidence contract only.

- [ ] **Step 3: Create the one-shot source freeze and run final local review**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$Base='2133114d93af1c7cb18f1acdc5693e871d8632db'
$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry'
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py'
$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Head=(git -C $Wt rev-parse HEAD).Trim();$Short=$Head.Substring(0,12)
$Evidence=Join-Path $Wt "tmp\post-kernel-source-$Short";$Report=Join-Path $Evidence 'post-kernel-validation.json'
$V=Get-Content -LiteralPath $Report -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop
if(-not$V.valid-or$V.verdict-cne'SMOKE_PASS'-or$V.records-ne1-or$V.pass-ne1){throw 'Source freeze requires exact SMOKE_PASS 1/1'}
$ValidatorSha=(Get-FileHash -LiteralPath $Validator -Algorithm SHA256).Hash.ToLowerInvariant()
if($ValidatorSha-cne$V.validator_sha256){throw 'Source report/validator mismatch'}
$Subjects=@(git -C $Wt log --format='%s' "$Base..$Head")
$ExpectedSubjects=@('test(sgx): emit post-kernel HSE06 telemetry [skip ci]','test(sgx): add scoped post-kernel telemetry hook [skip ci]','test(ci): preserve post-kernel telemetry evidence [skip ci]')
if(@(Compare-Object $ExpectedSubjects $Subjects).Count-ne0-or$Subjects.Count-ne3){throw 'Three-commit identity mismatch'}
$Allowed=@('.github/workflows/test_precision_investigation_contract.py','pyscf/sgx/grad/test/test_rks.py')
$Actual=@(git -C $Wt diff --name-only "$Base...$Head")
if(@(Compare-Object $Allowed $Actual).Count-ne0){throw 'Tracked scope mismatch'}
if(git -C $Wt status --short --untracked-files=no){throw 'Tracked worktree is dirty'}
$DllStatus=@(git -C $Wt status --short|Where-Object{$_-match'^\?\? pyscf/lib/.+\.dll$'})
if($DllStatus.Count-ne26){throw '26-DLL untracked boundary changed'}
git -C $Wt -c core.whitespace=cr-at-eol diff --check "$Base...$Head"
if($LASTEXITCODE-ne0){throw 'Committed diff check failed'}
$Selection=Join-Path $Wt '.github\workflows\precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
$Selected=@(Get-Content -LiteralPath $Selection -Encoding UTF8|Where-Object{-not[string]::IsNullOrWhiteSpace($_)})
if($Selected.Count-ne1-or$Selected[0]-cne$NodeId){throw 'Selection drift'}
$FreezeRoot='D:\workspace\pyscf\.agents\active\precision-ci\freezes';[void][IO.Directory]::CreateDirectory($FreezeRoot)
$FreezePath=Join-Path $FreezeRoot "post-kernel-source-$Head.json"
$Freeze=[ordered]@{kind='sgx-post-kernel-source-freeze';head=$Head;base=$Base;branch=$Branch;validatorSha256=$ValidatorSha;sourceReport=$Report;sourceReportSha256=(Get-FileHash -LiteralPath $Report -Algorithm SHA256).Hash.ToLowerInvariant();createdAt=[DateTimeOffset]::UtcNow.ToString('o')}
$Utf8=New-Object Text.UTF8Encoding($false);$Bytes=$Utf8.GetBytes(($Freeze|ConvertTo-Json -Compress))
try{$Stream=New-Object IO.FileStream($FreezePath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$Stream.Write($Bytes,0,$Bytes.Length);$Stream.Flush($true)}finally{$Stream.Dispose()}}catch [IO.IOException]{throw "Source freeze already exists or is unusable: $FreezePath"}
Write-Output "SOURCE_FREEZE_PATH=$FreezePath"
Write-Output "SOURCE_FREEZE_SHA256=$((Get-FileHash -LiteralPath $FreezePath -Algorithm SHA256).Hash.ToLowerInvariant())"
```

Request a fresh spec-compliance and code-quality review before push. Both must verify the exact base/head, three commits, two-path scope, default-off original eight calls, exact eighth-call telemetry, hook restoration on success/exception, schema/formulas, v1 validator immutability, source report/freeze hashes, mixed-EOL byte boundary, and `SMOKE_PASS 1/1`.

- [ ] **Step 4: Push only the reviewed frozen head**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry'
$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry'
$Base='2133114d93af1c7cb18f1acdc5693e871d8632db'
$FreezeRoot='D:\workspace\pyscf\.agents\active\precision-ci\freezes'
$Head=(git -C $Wt rev-parse HEAD).Trim();$FreezePath=Join-Path $FreezeRoot "post-kernel-source-$Head.json"
$Freeze=Get-Content -LiteralPath $FreezePath -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop
if($Freeze.kind-cne'sgx-post-kernel-source-freeze'-or$Freeze.head-cne$Head-or$Freeze.base-cne$Base-or$Freeze.branch-cne$Branch){throw 'Source freeze identity mismatch'}
if((Get-FileHash -LiteralPath $Freeze.sourceReport -Algorithm SHA256).Hash.ToLowerInvariant()-cne$Freeze.sourceReportSha256){throw 'Frozen source report drift'}
$V=Get-Content -LiteralPath $Freeze.sourceReport -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop
if(-not$V.valid-or$V.verdict-cne'SMOKE_PASS'-or$V.validator_sha256-cne$Freeze.validatorSha256){throw 'Frozen source gate mismatch'}
if(git -C $Wt status --short --untracked-files=no){throw 'Tracked tree dirty before push'}
$RemoteBefore=@(git -C $Wt ls-remote --heads origin "refs/heads/$Branch")
if($LASTEXITCODE-ne0-or$RemoteBefore.Count-ne0){throw 'Remote branch exists or query failed'}
gh auth status
if($LASTEXITCODE-ne0){throw 'GitHub authentication failed'}
git -C $Wt push --set-upstream origin "HEAD:refs/heads/$Branch"
if($LASTEXITCODE-ne0){throw 'Investigation branch push failed'}
$RemoteAfter=((git -C $Wt ls-remote origin "refs/heads/$Branch")-split'\s+')[0]
if($LASTEXITCODE-ne0-or$RemoteAfter-cne$Head){throw 'Remote head mismatch after push'}
```

Use `apply_patch` to record exact keys `post_kernel_head`, `post_kernel_source_freeze_path`, `post_kernel_source_freeze_sha256`, `post_kernel_validator_sha256`, both review verdicts, `post_kernel_remote_branch`, `post_kernel_remote_head`, push time, and `next_command: Task 7 witness preflight`.

---

### Task 7: Dispatch and Strictly Validate the 1-repeat Installed-wheel Witness

**Files:**
- Update: `.agents/active/libxc-712-release-revalidation.md`
- Create one-shot latch: `.agents/active/precision-ci/dispatch-latches/post-kernel-witness-HEAD-BEFORE_MAX.json`
- Archive: `.agents/archive/precision-ci/experiments/RUN_ID-sgx-hse06-post-kernel-witness-windows-py312`

**Interfaces:**
- Consumes: reviewed/pushed source freeze and exact original-nodeid selector.
- Produces: one Windows Python 3.12 `omp4-blas1` installed-wheel attempt with canonical run/job/artifact provenance; only `SMOKE_PASS` unlocks Task 8.

- [ ] **Step 1: Freeze the witness preflight and BeforeMax in a fresh shell**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$Repo='psiQAQ/pyscf';$Workflow='ci-precision-check.yml';$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad';$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py';$GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$Head=(git -C $Wt rev-parse HEAD).Trim();$FreezePath="D:\workspace\pyscf\.agents\active\precision-ci\freezes\post-kernel-source-$Head.json";$Freeze=Get-Content -LiteralPath $FreezePath -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop
if($Freeze.head-cne$Head-or$Freeze.branch-cne$Branch-or(Get-FileHash -LiteralPath $Validator -Algorithm SHA256).Hash.ToLowerInvariant()-cne$Freeze.validatorSha256){throw 'Witness source freeze drift'}
if((Get-FileHash -LiteralPath $GoalBridge -Algorithm SHA256).Hash.ToLowerInvariant()-cne'4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'){throw 'GoalBridge drift'}
$Remote=((git -C $Wt ls-remote origin "refs/heads/$Branch")-split'\s+')[0];if($LASTEXITCODE-ne0-or$Remote-cne$Head){throw 'Witness remote head mismatch'}
$Selected=@(Get-Content -LiteralPath (Join-Path $Wt $Selection) -Encoding UTF8|Where-Object{-not[string]::IsNullOrWhiteSpace($_)});if($Selected.Count-ne1-or$Selected[0]-cne$NodeId){throw 'Witness selection drift'}
$AutomationFiles=@(Get-ChildItem -LiteralPath 'C:\Users\ustcw\.codex\automations' -Filter automation.toml -File -Recurse -ErrorAction SilentlyContinue)
if($AutomationFiles.Count-ne0){throw 'A native automation exists; refuse dual scheduling'}
$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and-not[string]::IsNullOrWhiteSpace([string]$_.CommandLine)-and(([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0-or[string]$_.CommandLine-match'(?i)gh(?:\.exe)?\s+run\s+watch')});if($Pollers.Count-ne0){throw 'Existing local poller detected'}
$Raw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json databaseId,status);if($LASTEXITCODE-ne0){throw 'Witness run list failed'};$Rows=ConvertFrom-Json -InputObject ($Raw-join"`n") -ErrorAction Stop;$Rows=@($Rows)
if(@($Rows|Where-Object{$_.status-in@('requested','queued','in_progress','waiting','pending')}).Count-ne0){throw 'Active witness/formal run already exists'}
$BeforeMax=if($Rows.Count){[long](($Rows|Measure-Object databaseId -Maximum).Maximum)}else{[long]0}
Write-Output "POST_KERNEL_WITNESS_BEFORE_MAX=$BeforeMax"
Write-Output "POST_KERNEL_WITNESS_HEAD=$Head"
```

Use `apply_patch` before dispatch to persist exact keys `post_kernel_head`, `post_kernel_witness_branch`, `post_kernel_witness_before_max`, workflow, selection, nodeid, inputs `windows-latest/3.12/4/1/repeats1`, expected artifact `precision-Windows-py3.12`, validator/freeze/GoalBridge hashes, and dispatch start time.

- [ ] **Step 2: Create a one-shot latch, dispatch once, and bind the unique run**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$Repo='psiQAQ/pyscf';$Workflow='ci-precision-check.yml';$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
$GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';$Head=(git -C $Wt rev-parse HEAD).Trim();$State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8
$M=[regex]::Match($State,'(?m)^- post_kernel_witness_before_max:\s*(?:(\d+)|`(\d+)`)\s*$');if(-not$M.Success){throw 'Missing strict witness BeforeMax'};$BeforeMax=[long]$(if($M.Groups[1].Success){$M.Groups[1].Value}else{$M.Groups[2].Value})
if($State-match'(?m)^- post_kernel_witness_run_id:\s*(?:\d+|`\d+`)\s*$'){throw 'Witness already bound; refuse replay'}
$LatchRoot='D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches';[void][IO.Directory]::CreateDirectory($LatchRoot);$LatchPath=Join-Path $LatchRoot "post-kernel-witness-$Head-$BeforeMax.json"
$Latch=[ordered]@{stage='post-kernel-witness';head=$Head;branch=$Branch;beforeMax=$BeforeMax;workflow=$Workflow;selection=$Selection;repeats=1;platform='windows-latest';python='3.12';profile='4/1';createdAt=[DateTimeOffset]::UtcNow.ToString('o')};$Utf8=New-Object Text.UTF8Encoding($false);$Bytes=$Utf8.GetBytes(($Latch|ConvertTo-Json -Compress))
try{$S=New-Object IO.FileStream($LatchPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($Bytes,0,$Bytes.Length);$S.Flush($true)}finally{$S.Dispose()}}catch [IO.IOException]{throw "Witness latch exists; never redispatch: $LatchPath"}
$LatchSha=(Get-FileHash -LiteralPath $LatchPath -Algorithm SHA256).Hash.ToLowerInvariant()
gh workflow run $Workflow --repo $Repo --ref $Branch --raw-field nodeids_file=$Selection --raw-field repeats=1 --raw-field platform=windows-latest --raw-field python_version=3.12 --raw-field profile=4/1
if($LASTEXITCODE-ne0){throw 'Witness dispatch failed; retain latch and audit manually'}
$Candidates=@();for($i=0;$i-lt12;$i++){$Raw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json databaseId,headSha,url);if($LASTEXITCODE-ne0){throw 'Witness bind query failed'};$Rows=ConvertFrom-Json -InputObject ($Raw-join"`n") -ErrorAction Stop;$Candidates=@(@($Rows)|Where-Object{[long]$_.databaseId-gt$BeforeMax-and$_.headSha-ceq$Head});if($Candidates.Count-eq1){break};if($Candidates.Count-gt1){throw 'Ambiguous witness binding'};Start-Sleep -Seconds 5}
if($Candidates.Count-ne1){Write-Output "WITNESS_NOT_BOUND_LATCH=$LatchPath";Write-Output "WITNESS_LATCH_SHA256=$LatchSha";return}
$RunId=[long]$Candidates[0].databaseId
Write-Output "WITNESS_RUN_ID=$RunId";Write-Output "WITNESS_URL=$($Candidates[0].url)";Write-Output "WITNESS_LATCH_SHA256=$LatchSha"
```

Immediately use `apply_patch` to record exact keys `post_kernel_witness_latch_path`, `post_kernel_witness_latch_sha256`, `post_kernel_witness_run_id`, `post_kernel_witness_url`, head and validator hash before starting any monitor. If binding prints `WITNESS_NOT_BOUND_LATCH`, never redispatch: verify this exact latch/hash and query only `databaseId > BeforeMax` plus exact head until zero/one/multiple can be decided.

The recovery query is a separate fresh-shell command and contains no dispatch or Goal mutation:

```powershell
$ErrorActionPreference='Stop'
$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Repo='psiQAQ/pyscf';$Workflow='ci-precision-check.yml';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8
$H=[regex]::Match($State,'(?m)^- post_kernel_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$');$B=[regex]::Match($State,'(?m)^- post_kernel_witness_before_max:\s*(?:(\d+)|`(\d+)`)\s*$');$L=[regex]::Match($State,'(?m)^- post_kernel_witness_latch_path:\s*(?:([^`\r\n]+)|`([^`\r\n]+)`)\s*$');$S=[regex]::Match($State,'(?m)^- post_kernel_witness_latch_sha256:\s*(?:([0-9a-f]{64})|`([0-9a-f]{64})`)\s*$');if(-not$H.Success-or-not$B.Success-or-not$L.Success-or-not$S.Success){throw 'Incomplete witness recovery state'}
$Head=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value};$BeforeMax=[long]$(if($B.Groups[1].Success){$B.Groups[1].Value}else{$B.Groups[2].Value});$LatchPath=$(if($L.Groups[1].Success){$L.Groups[1].Value.Trim()}else{$L.Groups[2].Value});$ExpectedSha=if($S.Groups[1].Success){$S.Groups[1].Value}else{$S.Groups[2].Value}
if((Get-FileHash -LiteralPath $LatchPath -Algorithm SHA256).Hash.ToLowerInvariant()-cne$ExpectedSha){throw 'Witness recovery latch hash mismatch'};$Latch=Get-Content -LiteralPath $LatchPath -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop
if($Latch.stage-cne'post-kernel-witness'-or$Latch.head-cne$Head-or$Latch.branch-cne$Branch-or[long]$Latch.beforeMax-ne$BeforeMax-or[long]$Latch.repeats-ne1){throw 'Witness recovery latch content mismatch'}
$Raw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 50 --json databaseId,headSha,url);if($LASTEXITCODE-ne0){throw 'Witness recovery query failed'};$Rows=ConvertFrom-Json -InputObject ($Raw-join"`n") -ErrorAction Stop;$Candidates=@(@($Rows)|Where-Object{[long]$_.databaseId-gt$BeforeMax-and$_.headSha-ceq$Head});if($Candidates.Count-eq0){Write-Output 'WITNESS_RECOVERY_NOT_READY';return};if($Candidates.Count-gt1){throw 'Ambiguous witness recovery binding'};Write-Output "WITNESS_RECOVERED_RUN_ID=$([long]$Candidates[0].databaseId)";Write-Output "WITNESS_RECOVERED_URL=$($Candidates[0].url)"
```

Persist the recovered ID/URL with `apply_patch`, then launch the heartbeat portion once. `WITNESS_RECOVERY_NOT_READY` leaves the latch intact and ends this turn.

- [ ] **Step 3: Launch the sole witness heartbeat only after durable run binding**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$Repo='psiQAQ/pyscf';$WorkflowName='Precision investigation';$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt';$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad';$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py';$GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';$ThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70';$State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8
$H=[regex]::Match($State,'(?m)^- post_kernel_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$');$R=[regex]::Match($State,'(?m)^- post_kernel_witness_run_id:\s*(?:(\d+)|`(\d+)`)\s*$');if(-not$H.Success-or-not$R.Success){throw 'Missing strict witness head/run id'};$Head=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value};$RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value})
if((git -C $Wt rev-parse HEAD).Trim()-cne$Head){throw 'Witness local head mismatch'};$Remote=((git -C $Wt ls-remote origin "refs/heads/$Branch")-split'\s+')[0];if($LASTEXITCODE-ne0-or$Remote-cne$Head){throw 'Witness remote head mismatch'}
$FreezePath="D:\workspace\pyscf\.agents\active\precision-ci\freezes\post-kernel-source-$Head.json";$Freeze=Get-Content -LiteralPath $FreezePath -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop;if($Freeze.head-cne$Head-or$Freeze.branch-cne$Branch-or(Get-FileHash -LiteralPath $Validator -Algorithm SHA256).Hash.ToLowerInvariant()-cne$Freeze.validatorSha256){throw 'Witness freeze/validator drift'}
if((Get-FileHash -LiteralPath $GoalBridge -Algorithm SHA256).Hash.ToLowerInvariant()-cne'4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'){throw 'Witness GoalBridge drift'}
$Selected=@(Get-Content -LiteralPath (Join-Path $Wt $Selection) -Encoding UTF8|Where-Object{-not[string]::IsNullOrWhiteSpace($_)});if($Selected.Count-ne1-or$Selected[0]-cne$NodeId){throw 'Witness selection drift'}
if(@(Get-ChildItem -LiteralPath 'C:\Users\ustcw\.codex\automations' -Filter automation.toml -File -Recurse -ErrorAction SilentlyContinue).Count-ne0){throw 'A native automation exists before witness heartbeat'}
$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and-not[string]::IsNullOrWhiteSpace([string]$_.CommandLine)-and(([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0-or[string]$_.CommandLine-match'(?i)gh(?:\.exe)?\s+run\s+watch')});if($Pollers.Count-ne0){throw 'Existing witness poller detected'}
$RunRaw=@(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,workflowName);if($LASTEXITCODE-ne0){throw 'Witness run identity read failed'};$Run=ConvertFrom-Json -InputObject ($RunRaw-join"`n") -ErrorAction Stop;if($Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.headBranch-cne$Branch-or$Run.headSha-cne$Head-or$Run.workflowName-cne$WorkflowName){throw 'Witness run identity mismatch'}
$PowerShell='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe';$Args=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$GoalBridge,'-TargetRunIds',[string]$RunId,'-TargetHeadSha',$Head,'-IntervalSeconds','1800','-WakeAfterMinutes','0');$Heartbeat=$null;$HeartbeatPid=$null;$HeartbeatStartUtc=$null
try{$Heartbeat=Start-Process -FilePath $PowerShell -ArgumentList $Args -WindowStyle Hidden -PassThru;$HeartbeatPid=$Heartbeat.Id;$HeartbeatStartUtc=$Heartbeat.StartTime.ToUniversalTime();Start-Sleep -Seconds 2;if($Heartbeat.HasExited){throw "Witness heartbeat exited early: $($Heartbeat.ExitCode)"};$Cim=Get-CimInstance Win32_Process -Filter "ProcessId=$HeartbeatPid" -ErrorAction Stop;if($Cim.ExecutablePath-cne$PowerShell-or([string]$Cim.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-lt0-or([string]$Cim.CommandLine).IndexOf([string]$RunId,[StringComparison]::Ordinal)-lt0-or([string]$Cim.CommandLine).IndexOf($Head,[StringComparison]::Ordinal)-lt0){throw 'Witness heartbeat identity mismatch'};$GoalRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus paused);if($LASTEXITCODE-ne0){throw 'Witness Goal pause failed'};$Goal=ConvertFrom-Json -InputObject ($GoalRaw-join"`n") -ErrorAction Stop;if($Goal.threadId-cne$ThreadId-or$Goal.status-cne'paused'){throw 'Witness Goal pause readback mismatch'}}catch{$Primary=$_.Exception;$Cleanup=New-Object 'Collections.Generic.List[string]';if($null-ne$Heartbeat){try{$Heartbeat.Refresh();if(-not$Heartbeat.HasExited){if(($null-ne$HeartbeatPid-and$Heartbeat.Id-ne$HeartbeatPid)-or($null-ne$HeartbeatStartUtc-and$Heartbeat.StartTime.ToUniversalTime()-ne$HeartbeatStartUtc)){throw 'Direct-child PID reuse guard failed'};$Heartbeat.Kill();if(-not$Heartbeat.WaitForExit(10000)){throw 'Witness child did not exit'};$Heartbeat.Refresh();if(-not$Heartbeat.HasExited){throw 'Witness child still alive'}}}catch{$Cleanup.Add($_.Exception.Message)}};try{$RestoreRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus active);if($LASTEXITCODE-ne0){throw 'Goal active setter failed'};$Restore=ConvertFrom-Json -InputObject ($RestoreRaw-join"`n") -ErrorAction Stop;if($Restore.threadId-cne$ThreadId-or$Restore.status-cne'active'){throw 'Goal active readback mismatch'}}catch{$Cleanup.Add($_.Exception.Message)};throw [InvalidOperationException]::new("Witness handoff failed: $($Primary.Message); cleanup=$($Cleanup-join'; ')",$Primary)}
$Exact=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and$_.ExecutablePath-ceq$PowerShell-and([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0});if($Exact.Count-ne1-or$Exact[0].ProcessId-ne$HeartbeatPid){throw 'Witness handoff does not have exactly one monitor'}
Write-Output "WITNESS_MONITOR_PID=$HeartbeatPid";Write-Output 'WITNESS_INTERVAL_SECONDS=1800';Write-Output 'WITNESS_WAKE_AFTER_MINUTES=0'
```

Use `apply_patch` to record exact key `post_kernel_witness_monitor_pid` plus executable/command/start time, run/head, interval `1800`, wake `0`, Goal paused readback, and the terminal-validation command.

- [ ] **Step 4: At terminal wake, freeze and validate the unique artifact**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$Repo='psiQAQ/pyscf';$WorkflowName='Precision investigation';$ExpectedArtifact='precision-Windows-py3.12';$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py';$GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad';$ThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70'
$Text=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8;$H=[regex]::Match($Text,'(?m)^- post_kernel_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$');$R=[regex]::Match($Text,'(?m)^- post_kernel_witness_run_id:\s*(?:(\d+)|`(\d+)`)\s*$');$P=[regex]::Match($Text,'(?m)^- post_kernel_witness_monitor_pid:\s*(?:(\d+)|`(\d+)`)\s*$');if(-not$H.Success-or-not$R.Success-or-not$P.Success){throw 'Missing strict witness state'};$Head=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value};$RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value});$MonitorPid=[long]$(if($P.Groups[1].Success){$P.Groups[1].Value}else{$P.Groups[2].Value})
if($null-ne(Get-CimInstance Win32_Process -Filter "ProcessId=$MonitorPid" -ErrorAction SilentlyContinue)){throw 'Witness heartbeat still running'}
$PowerShell='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe';$GoalRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus active);if($LASTEXITCODE-ne0){throw 'Witness Goal active reconciliation failed'};$Goal=ConvertFrom-Json -InputObject ($GoalRaw-join"`n") -ErrorAction Stop;if($Goal.threadId-cne$ThreadId-or$Goal.status-cne'active'){throw 'Witness Goal active readback mismatch'}
$RunRaw=@(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,conclusion,workflowName,jobs,url);if($LASTEXITCODE-ne0){throw 'Witness run read failed'};$Run=ConvertFrom-Json -InputObject ($RunRaw-join"`n") -ErrorAction Stop;$Jobs=@($Run.jobs);if($Run.status-cne'completed'-or$Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.headSha-cne$Head-or$Run.headBranch-cne$Branch-or$Run.workflowName-cne$WorkflowName-or$Jobs.Count-ne1-or$Jobs[0].name-cne'precision'-or$Jobs[0].status-cne'completed'){throw 'Witness terminal run/job identity mismatch'}
function Test-JsonInteger($Value){$Value-is[int]-or$Value-is[long]-or$Value-is[uint32]-or$Value-is[uint64]}
$Artifacts=@();for($i=0;$i-lt12;$i++){$ApiRaw=@(gh api "repos/$Repo/actions/runs/$RunId/artifacts");if($LASTEXITCODE-ne0){throw 'Witness artifact API failed'};$Api=ConvertFrom-Json -InputObject ($ApiRaw-join"`n") -ErrorAction Stop;$Artifacts=@($Api.artifacts);if(-not(Test-JsonInteger $Api.total_count)-or[long]$Api.total_count-ne$Artifacts.Count){throw 'Witness artifact envelope invalid'};if($Artifacts.Count-gt1){throw 'Witness has multiple artifacts'};if($Artifacts.Count-eq1){break};Start-Sleep -Seconds 5}
if($Artifacts.Count-eq0){Write-Output 'WITNESS_ARTIFACT_NOT_READY';return};$Artifact=$Artifacts[0]
if(-not(Test-JsonInteger $Artifact.id)-or[long]$Artifact.id-le0-or$Artifact.name-cne$ExpectedArtifact-or$Artifact.expired-isnot[bool]-or$Artifact.expired-ne$false-or-not(Test-JsonInteger $Artifact.size_in_bytes)-or[long]$Artifact.size_in_bytes-le0-or$Artifact.digest-cnotmatch'^sha256:[0-9a-f]{64}$'){throw 'Witness artifact metadata invalid'}
$Dir="D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-sgx-hse06-post-kernel-witness-windows-py312";if(Test-Path -LiteralPath $Dir){throw "Witness archive exists: $Dir"};[void][IO.Directory]::CreateDirectory($Dir);$Job=$Jobs[0]
$Meta=[ordered]@{databaseId=$RunId;attempt=$Run.attempt;event=$Run.event;workflowName=$Run.workflowName;headSha=$Run.headSha;headBranch=$Run.headBranch;status=$Run.status;conclusion=$Run.conclusion;jobs=@([ordered]@{name=$Job.name;status=$Job.status;conclusion=$Job.conclusion});artifacts=@([ordered]@{id=[long]$Artifact.id;name=$Artifact.name;digest=$Artifact.digest;sizeInBytes=[long]$Artifact.size_in_bytes;expired=[bool]$Artifact.expired})};$Utf8=New-Object Text.UTF8Encoding($false);[IO.File]::WriteAllText((Join-Path $Dir 'run-metadata.json'),($Meta|ConvertTo-Json -Depth 6),$Utf8)
gh run download $RunId --repo $Repo --name $Artifact.name --dir $Dir;if($LASTEXITCODE-ne0){throw 'Witness artifact download failed'}
$Report=Join-Path $Dir 'post-kernel-validation.json';conda run --no-capture-output -n pyscf-win313-test python $Validator $Dir --mode installed-wheel --expected-sha $Head --expected-nodeid $NodeId --expected-profile omp4-blas1 --expected-repeats 1 --expected-native-count 26 --run-metadata (Join-Path $Dir 'run-metadata.json') --expected-run-id $RunId --expected-branch $Branch --report $Report;$Exit=$LASTEXITCODE;$V=Get-Content -LiteralPath $Report -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop;Copy-Item -LiteralPath $Validator -Destination (Join-Path $Dir 'validate_sgx_hse06_post_kernel_telemetry.py')
if((Get-FileHash -LiteralPath (Join-Path $Dir 'validate_sgx_hse06_post_kernel_telemetry.py') -Algorithm SHA256).Hash.ToLowerInvariant()-cne$V.validator_sha256){throw 'Witness validator copy mismatch'}
if($Exit-ne0-or-not$V.valid){throw 'Witness evidence INVALID'}
Write-Output "WITNESS_VERDICT=$($V.verdict)";Write-Output "WITNESS_REPORT=$Report"
```

`WITNESS_ARTIFACT_NOT_READY` is upload latency, not `INVALID`; retry only this exact run’s artifact query, never dispatch again. Use `apply_patch` to record run/job/artifact identity, validator SHA, counts, finding fields, report/archive and exact key `post_kernel_witness_verdict`. Continue only for exact `SMOKE_PASS`; any other valid verdict stops before Task 8.

---

### Task 8: Conditional 200-repeat Formal Run, 300-minute Gate, and Scientific Routing

**Files:**
- Update: `.agents/active/libxc-712-release-revalidation.md`
- Create one-shot latch: `.agents/active/precision-ci/dispatch-latches/post-kernel-formal-HEAD-BEFORE_MAX.json`
- Archive: `.agents/archive/precision-ci/experiments/RUN_ID-sgx-hse06-post-kernel-formal-windows-py312`

**Interfaces:**
- Consumes: exact witness `SMOKE_PASS` on the same head and validator.
- Produces: up to 200 authoritative installed-wheel attempts and exactly one bounded scientific routing decision; no broader matrix in this plan.

- [ ] **Step 1: Fresh-shell formal preflight, one-shot latch, dispatch, and binding**

This block reconstructs every formal invariant independently and refuses dispatch unless the witness, source freeze, remote head, validator, selection and scheduler boundary all agree:

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$Repo='psiQAQ/pyscf';$Workflow='ci-precision-check.yml';$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt';$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad';$Head=(git -C $Wt rev-parse HEAD).Trim();$State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8
if($State-notmatch'(?m)^- post_kernel_witness_verdict:\s*(?:SMOKE_PASS|`SMOKE_PASS`)\s*$'){throw 'Formal witness SMOKE_PASS gate missing'}
$FreezePath="D:\workspace\pyscf\.agents\active\precision-ci\freezes\post-kernel-source-$Head.json";$Freeze=Get-Content -LiteralPath $FreezePath -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop;$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py';if($Freeze.head-cne$Head-or$Freeze.branch-cne$Branch-or(Get-FileHash -LiteralPath $Validator -Algorithm SHA256).Hash.ToLowerInvariant()-cne$Freeze.validatorSha256){throw 'Formal source freeze/validator drift'}
$Selected=@(Get-Content -LiteralPath (Join-Path $Wt $Selection) -Encoding UTF8|Where-Object{-not[string]::IsNullOrWhiteSpace($_)});if($Selected.Count-ne1-or$Selected[0]-cne$NodeId){throw 'Formal selection drift'}
$Remote=((git -C $Wt ls-remote origin "refs/heads/$Branch")-split'\s+')[0];if($LASTEXITCODE-ne0-or$Remote-cne$Head){throw 'Formal remote head mismatch'}
$GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';if((Get-FileHash -LiteralPath $GoalBridge -Algorithm SHA256).Hash.ToLowerInvariant()-cne'4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'){throw 'GoalBridge drift'}
if(@(Get-ChildItem -LiteralPath 'C:\Users\ustcw\.codex\automations' -Filter automation.toml -File -Recurse -ErrorAction SilentlyContinue).Count-ne0){throw 'A native automation exists; refuse dual scheduling'}
$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and-not[string]::IsNullOrWhiteSpace([string]$_.CommandLine)-and(([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0-or[string]$_.CommandLine-match'(?i)gh(?:\.exe)?\s+run\s+watch')});if($Pollers.Count-ne0){throw 'Existing formal poller detected'}
$Raw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json databaseId,status);if($LASTEXITCODE-ne0){throw 'Formal run list failed'};$Rows=ConvertFrom-Json -InputObject ($Raw-join"`n") -ErrorAction Stop;$Rows=@($Rows);if(@($Rows|Where-Object{$_.status-in@('requested','queued','in_progress','waiting','pending')}).Count-ne0){throw 'Active formal run exists'};$BeforeMax=if($Rows.Count){[long](($Rows|Measure-Object databaseId -Maximum).Maximum)}else{[long]0}
$LatchRoot='D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches';[void][IO.Directory]::CreateDirectory($LatchRoot);$LatchPath=Join-Path $LatchRoot "post-kernel-formal-$Head-$BeforeMax.json";$Latch=[ordered]@{stage='post-kernel-formal';head=$Head;branch=$Branch;beforeMax=$BeforeMax;workflow=$Workflow;selection=$Selection;repeats=200;platform='windows-latest';python='3.12';profile='4/1';createdAt=[DateTimeOffset]::UtcNow.ToString('o')};$Utf8=New-Object Text.UTF8Encoding($false);$Bytes=$Utf8.GetBytes(($Latch|ConvertTo-Json -Compress));try{$S=New-Object IO.FileStream($LatchPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($Bytes,0,$Bytes.Length);$S.Flush($true)}finally{$S.Dispose()}}catch [IO.IOException]{throw "Formal latch exists; never redispatch: $LatchPath"};$LatchSha=(Get-FileHash -LiteralPath $LatchPath -Algorithm SHA256).Hash.ToLowerInvariant()
gh workflow run $Workflow --repo $Repo --ref $Branch --raw-field nodeids_file=$Selection --raw-field repeats=200 --raw-field platform=windows-latest --raw-field python_version=3.12 --raw-field profile=4/1
if($LASTEXITCODE-ne0){throw 'Formal dispatch failed; retain latch and audit manually'}
$Candidates=@();for($i=0;$i-lt12;$i++){$Q=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 30 --json databaseId,headSha,url);if($LASTEXITCODE-ne0){throw 'Formal bind query failed'};$Rows=ConvertFrom-Json -InputObject ($Q-join"`n") -ErrorAction Stop;$Candidates=@(@($Rows)|Where-Object{[long]$_.databaseId-gt$BeforeMax-and$_.headSha-ceq$Head});if($Candidates.Count-eq1){break};if($Candidates.Count-gt1){throw 'Ambiguous formal binding'};Start-Sleep -Seconds 5};if($Candidates.Count-ne1){Write-Output "FORMAL_NOT_BOUND_LATCH=$LatchPath";Write-Output "FORMAL_LATCH_SHA256=$LatchSha";Write-Output "FORMAL_BEFORE_MAX=$BeforeMax";return};$RunId=[long]$Candidates[0].databaseId;Write-Output "FORMAL_RUN_ID=$RunId";Write-Output "FORMAL_URL=$($Candidates[0].url)";Write-Output "FORMAL_BEFORE_MAX=$BeforeMax";Write-Output "FORMAL_LATCH_SHA256=$LatchSha"
```

Persist exact keys `post_kernel_formal_before_max`, `post_kernel_formal_latch_path`, `post_kernel_formal_latch_sha256`, `post_kernel_formal_run_id`, and formal URL/head with `apply_patch`. A missing binding uses only the content/hash-bound recovery query `databaseId > BeforeMax` plus exact head; it never redispatches.

Use this exact recovery command if no run was bound:

```powershell
$ErrorActionPreference='Stop'
$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Repo='psiQAQ/pyscf';$Workflow='ci-precision-check.yml';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8
$H=[regex]::Match($State,'(?m)^- post_kernel_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$');$B=[regex]::Match($State,'(?m)^- post_kernel_formal_before_max:\s*(?:(\d+)|`(\d+)`)\s*$');$L=[regex]::Match($State,'(?m)^- post_kernel_formal_latch_path:\s*(?:([^`\r\n]+)|`([^`\r\n]+)`)\s*$');$S=[regex]::Match($State,'(?m)^- post_kernel_formal_latch_sha256:\s*(?:([0-9a-f]{64})|`([0-9a-f]{64})`)\s*$');if(-not$H.Success-or-not$B.Success-or-not$L.Success-or-not$S.Success){throw 'Incomplete formal recovery state'}
$Head=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value};$BeforeMax=[long]$(if($B.Groups[1].Success){$B.Groups[1].Value}else{$B.Groups[2].Value});$LatchPath=$(if($L.Groups[1].Success){$L.Groups[1].Value.Trim()}else{$L.Groups[2].Value});$ExpectedSha=if($S.Groups[1].Success){$S.Groups[1].Value}else{$S.Groups[2].Value}
if((Get-FileHash -LiteralPath $LatchPath -Algorithm SHA256).Hash.ToLowerInvariant()-cne$ExpectedSha){throw 'Formal recovery latch hash mismatch'};$Latch=Get-Content -LiteralPath $LatchPath -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop
if($Latch.stage-cne'post-kernel-formal'-or$Latch.head-cne$Head-or$Latch.branch-cne$Branch-or[long]$Latch.beforeMax-ne$BeforeMax-or[long]$Latch.repeats-ne200){throw 'Formal recovery latch content mismatch'}
$Raw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 50 --json databaseId,headSha,url);if($LASTEXITCODE-ne0){throw 'Formal recovery query failed'};$Rows=ConvertFrom-Json -InputObject ($Raw-join"`n") -ErrorAction Stop;$Candidates=@(@($Rows)|Where-Object{[long]$_.databaseId-gt$BeforeMax-and$_.headSha-ceq$Head});if($Candidates.Count-eq0){Write-Output 'FORMAL_RECOVERY_NOT_READY';return};if($Candidates.Count-gt1){throw 'Ambiguous formal recovery binding'};Write-Output "FORMAL_RECOVERED_RUN_ID=$([long]$Candidates[0].databaseId)";Write-Output "FORMAL_RECOVERED_URL=$($Candidates[0].url)"
```

Persist the recovered ID/URL with `apply_patch`; `FORMAL_RECOVERY_NOT_READY` ends the turn without dispatch or Goal mutation.

- [ ] **Step 2: Launch the sole formal heartbeat and pause Goal**

After persisting the formal latch path/hash, run ID/URL, head and BeforeMax with `apply_patch`, run this fresh-shell handoff:

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$Repo='psiQAQ/pyscf';$WorkflowName='Precision investigation';$Selection='.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt';$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad';$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py';$GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';$ThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70';$State=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8
$H=[regex]::Match($State,'(?m)^- post_kernel_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$');$R=[regex]::Match($State,'(?m)^- post_kernel_formal_run_id:\s*(?:(\d+)|`(\d+)`)\s*$');if(-not$H.Success-or-not$R.Success){throw 'Missing strict formal head/run id'};$Head=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value};$RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value})
if((git -C $Wt rev-parse HEAD).Trim()-cne$Head){throw 'Formal local head mismatch'};$Remote=((git -C $Wt ls-remote origin "refs/heads/$Branch")-split'\s+')[0];if($LASTEXITCODE-ne0-or$Remote-cne$Head){throw 'Formal remote head mismatch'}
$FreezePath="D:\workspace\pyscf\.agents\active\precision-ci\freezes\post-kernel-source-$Head.json";$Freeze=Get-Content -LiteralPath $FreezePath -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop;if($Freeze.head-cne$Head-or$Freeze.branch-cne$Branch-or(Get-FileHash -LiteralPath $Validator -Algorithm SHA256).Hash.ToLowerInvariant()-cne$Freeze.validatorSha256){throw 'Formal freeze/validator drift'}
if((Get-FileHash -LiteralPath $GoalBridge -Algorithm SHA256).Hash.ToLowerInvariant()-cne'4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'){throw 'Formal GoalBridge drift'}
$Selected=@(Get-Content -LiteralPath (Join-Path $Wt $Selection) -Encoding UTF8|Where-Object{-not[string]::IsNullOrWhiteSpace($_)});if($Selected.Count-ne1-or$Selected[0]-cne$NodeId){throw 'Formal selection drift'}
if(@(Get-ChildItem -LiteralPath 'C:\Users\ustcw\.codex\automations' -Filter automation.toml -File -Recurse -ErrorAction SilentlyContinue).Count-ne0){throw 'A native automation exists before formal heartbeat'}
$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and-not[string]::IsNullOrWhiteSpace([string]$_.CommandLine)-and(([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0-or[string]$_.CommandLine-match'(?i)gh(?:\.exe)?\s+run\s+watch')});if($Pollers.Count-ne0){throw 'Existing formal poller detected'}
$RunRaw=@(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,workflowName);if($LASTEXITCODE-ne0){throw 'Formal run identity read failed'};$Run=ConvertFrom-Json -InputObject ($RunRaw-join"`n") -ErrorAction Stop;if($Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.headBranch-cne$Branch-or$Run.headSha-cne$Head-or$Run.workflowName-cne$WorkflowName){throw 'Formal run identity mismatch'}
$PowerShell='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe';$Args=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$GoalBridge,'-TargetRunIds',[string]$RunId,'-TargetHeadSha',$Head,'-IntervalSeconds','1800','-WakeAfterMinutes','300');$Heartbeat=$null;$HeartbeatPid=$null;$HeartbeatStartUtc=$null
try{$Heartbeat=Start-Process -FilePath $PowerShell -ArgumentList $Args -WindowStyle Hidden -PassThru;$HeartbeatPid=$Heartbeat.Id;$HeartbeatStartUtc=$Heartbeat.StartTime.ToUniversalTime();Start-Sleep -Seconds 2;if($Heartbeat.HasExited){throw "Formal heartbeat exited early: $($Heartbeat.ExitCode)"};$Cim=Get-CimInstance Win32_Process -Filter "ProcessId=$HeartbeatPid" -ErrorAction Stop;if($Cim.ExecutablePath-cne$PowerShell-or([string]$Cim.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-lt0-or([string]$Cim.CommandLine).IndexOf([string]$RunId,[StringComparison]::Ordinal)-lt0-or([string]$Cim.CommandLine).IndexOf($Head,[StringComparison]::Ordinal)-lt0){throw 'Formal heartbeat identity mismatch'};$GoalRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus paused);if($LASTEXITCODE-ne0){throw 'Formal Goal pause failed'};$Goal=ConvertFrom-Json -InputObject ($GoalRaw-join"`n") -ErrorAction Stop;if($Goal.threadId-cne$ThreadId-or$Goal.status-cne'paused'){throw 'Formal Goal pause readback mismatch'}}catch{$Primary=$_.Exception;$Cleanup=New-Object 'Collections.Generic.List[string]';if($null-ne$Heartbeat){try{$Heartbeat.Refresh();if(-not$Heartbeat.HasExited){if(($null-ne$HeartbeatPid-and$Heartbeat.Id-ne$HeartbeatPid)-or($null-ne$HeartbeatStartUtc-and$Heartbeat.StartTime.ToUniversalTime()-ne$HeartbeatStartUtc)){throw 'Direct-child PID reuse guard failed'};$Heartbeat.Kill();if(-not$Heartbeat.WaitForExit(10000)){throw 'Formal child did not exit'};$Heartbeat.Refresh();if(-not$Heartbeat.HasExited){throw 'Formal child still alive'}}}catch{$Cleanup.Add($_.Exception.Message)}};try{$RestoreRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus active);if($LASTEXITCODE-ne0){throw 'Goal active setter failed'};$Restore=ConvertFrom-Json -InputObject ($RestoreRaw-join"`n") -ErrorAction Stop;if($Restore.threadId-cne$ThreadId-or$Restore.status-cne'active'){throw 'Goal active readback mismatch'}}catch{$Cleanup.Add($_.Exception.Message)};throw [InvalidOperationException]::new("Formal handoff failed: $($Primary.Message); cleanup=$($Cleanup-join'; ')",$Primary)}
$Exact=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.ProcessId-ne$PID-and$_.ExecutablePath-ceq$PowerShell-and([string]$_.CommandLine).IndexOf($GoalBridge,[StringComparison]::OrdinalIgnoreCase)-ge0});if($Exact.Count-ne1-or$Exact[0].ProcessId-ne$HeartbeatPid){throw 'Formal handoff does not have exactly one monitor'}
Write-Output "FORMAL_MONITOR_PID=$HeartbeatPid";Write-Output 'FORMAL_INTERVAL_SECONDS=1800';Write-Output 'FORMAL_WAKE_AFTER_MINUTES=300'
```

Use `apply_patch` to record exact key `post_kernel_formal_monitor_pid`, executable/full command, start time, exact run/head, interval `1800`, `post_kernel_formal_timeout_gate_minutes: 300`, and terminal root command.

- [ ] **Step 3: At wake, cancel only an identity-bound job that has actually exceeded 300 minutes**

```powershell
$ErrorActionPreference='Stop'
$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Repo='psiQAQ/pyscf';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$WorkflowName='Precision investigation';$Text=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8
$H=[regex]::Match($Text,'(?m)^- post_kernel_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$');$R=[regex]::Match($Text,'(?m)^- post_kernel_formal_run_id:\s*(?:(\d+)|`(\d+)`)\s*$');if(-not$H.Success-or-not$R.Success){throw 'Missing formal state'};$Head=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value};$RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value})
$Raw=@(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,conclusion,workflowName,jobs,url);if($LASTEXITCODE-ne0){throw 'Formal run read failed'};$Run=ConvertFrom-Json -InputObject ($Raw-join"`n") -ErrorAction Stop;$Jobs=@($Run.jobs)
if($Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.headBranch-cne$Branch-or$Run.headSha-cne$Head-or$Run.workflowName-cne$WorkflowName-or$Jobs.Count-ne1-or$Jobs[0].name-cne'precision'){throw 'Formal run/job identity invalid; never cancel'}
if($Run.status-ceq'completed'){Write-Output 'FORMAL_TERMINAL';return}
if($Run.status-cne'in_progress'-or$Jobs[0].status-cne'in_progress'-or[string]::IsNullOrWhiteSpace([string]$Jobs[0].startedAt)){Write-Output 'FORMAL_NOT_CANCELLABLE';return}
$Started=[DateTimeOffset]::MinValue;if(-not[DateTimeOffset]::TryParse([string]$Jobs[0].startedAt,[ref]$Started)){throw 'Unparseable startedAt; never cancel'};$Elapsed=([DateTimeOffset]::UtcNow-$Started.ToUniversalTime()).TotalMinutes
if($Elapsed-lt300){Write-Output "FORMAL_BELOW_GATE_MINUTES=$Elapsed";return}
gh run cancel $RunId --repo $Repo;if($LASTEXITCODE-ne0){throw 'Formal cancellation failed'};Write-Output "FORMAL_TIMEOUT_CANCELLED_MINUTES=$Elapsed"
```

A timeout cancellation is infrastructure `INVALID`; record it and stop without rerun or scientific inference.

- [ ] **Step 4: Validate the terminal formal artifact with the same frozen validator**

```powershell
$ErrorActionPreference='Stop'
$Wt='D:\workspace\pyscf\.worktrees\libxc-712-sgx-post-kernel-telemetry';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Branch='codex/investigate/libxc-712-sgx-post-kernel-telemetry';$Repo='psiQAQ/pyscf';$WorkflowName='Precision investigation';$ExpectedArtifact='precision-Windows-py3.12';$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_post_kernel_telemetry.py';$GoalBridge='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';$NodeId='pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad';$ThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70';$Text=Get-Content -LiteralPath $ActiveDoc -Raw -Encoding UTF8
$H=[regex]::Match($Text,'(?m)^- post_kernel_head:\s*(?:([0-9a-f]{40})|`([0-9a-f]{40})`)\s*$');$R=[regex]::Match($Text,'(?m)^- post_kernel_formal_run_id:\s*(?:(\d+)|`(\d+)`)\s*$');$P=[regex]::Match($Text,'(?m)^- post_kernel_formal_monitor_pid:\s*(?:(\d+)|`(\d+)`)\s*$');if(-not$H.Success-or-not$R.Success-or-not$P.Success){throw 'Missing strict formal state'};$Head=if($H.Groups[1].Success){$H.Groups[1].Value}else{$H.Groups[2].Value};$RunId=[long]$(if($R.Groups[1].Success){$R.Groups[1].Value}else{$R.Groups[2].Value});$MonitorPid=[long]$(if($P.Groups[1].Success){$P.Groups[1].Value}else{$P.Groups[2].Value})
if($null-ne(Get-CimInstance Win32_Process -Filter "ProcessId=$MonitorPid" -ErrorAction SilentlyContinue)){throw 'Formal heartbeat still running'}
$PowerShell='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe';$GoalRaw=@(& $PowerShell -NoProfile -ExecutionPolicy Bypass -File $GoalBridge -SetGoalStatus active);if($LASTEXITCODE-ne0){throw 'Formal Goal active reconciliation failed'};$Goal=ConvertFrom-Json -InputObject ($GoalRaw-join"`n") -ErrorAction Stop;if($Goal.threadId-cne$ThreadId-or$Goal.status-cne'active'){throw 'Formal Goal active readback mismatch'}
$FreezePath="D:\workspace\pyscf\.agents\active\precision-ci\freezes\post-kernel-source-$Head.json";$Freeze=Get-Content -LiteralPath $FreezePath -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop;if($Freeze.head-cne$Head-or$Freeze.branch-cne$Branch-or(Get-FileHash -LiteralPath $Validator -Algorithm SHA256).Hash.ToLowerInvariant()-cne$Freeze.validatorSha256){throw 'Formal freeze/validator drift'}
$RunRaw=@(gh run view $RunId --repo $Repo --json attempt,event,headBranch,headSha,status,conclusion,workflowName,jobs,url);if($LASTEXITCODE-ne0){throw 'Formal run read failed'};$Run=ConvertFrom-Json -InputObject ($RunRaw-join"`n") -ErrorAction Stop;$Jobs=@($Run.jobs);if($Run.status-cne'completed'-or$Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.headSha-cne$Head-or$Run.headBranch-cne$Branch-or$Run.workflowName-cne$WorkflowName-or$Jobs.Count-ne1-or$Jobs[0].name-cne'precision'-or$Jobs[0].status-cne'completed'){throw 'Formal terminal run/job identity mismatch'}
function Test-JsonInteger($Value){$Value-is[int]-or$Value-is[long]-or$Value-is[uint32]-or$Value-is[uint64]}
$Artifacts=@();for($i=0;$i-lt12;$i++){$ApiRaw=@(gh api "repos/$Repo/actions/runs/$RunId/artifacts");if($LASTEXITCODE-ne0){throw 'Formal artifact API failed'};$Api=ConvertFrom-Json -InputObject ($ApiRaw-join"`n") -ErrorAction Stop;$Artifacts=@($Api.artifacts);if(-not(Test-JsonInteger $Api.total_count)-or[long]$Api.total_count-ne$Artifacts.Count){throw 'Formal artifact envelope invalid'};if($Artifacts.Count-gt1){throw 'Formal has multiple artifacts'};if($Artifacts.Count-eq1){break};Start-Sleep -Seconds 5}
if($Artifacts.Count-eq0){Write-Output 'FORMAL_ARTIFACT_NOT_READY';return};$Artifact=$Artifacts[0]
if(-not(Test-JsonInteger $Artifact.id)-or[long]$Artifact.id-le0-or$Artifact.name-cne$ExpectedArtifact-or$Artifact.expired-isnot[bool]-or$Artifact.expired-ne$false-or-not(Test-JsonInteger $Artifact.size_in_bytes)-or[long]$Artifact.size_in_bytes-le0-or$Artifact.digest-cnotmatch'^sha256:[0-9a-f]{64}$'){throw 'Formal artifact metadata invalid'}
$Dir="D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-sgx-hse06-post-kernel-formal-windows-py312";if(Test-Path -LiteralPath $Dir){throw "Formal archive exists: $Dir"};[void][IO.Directory]::CreateDirectory($Dir);$Job=$Jobs[0]
$Meta=[ordered]@{databaseId=$RunId;attempt=$Run.attempt;event=$Run.event;workflowName=$Run.workflowName;headSha=$Run.headSha;headBranch=$Run.headBranch;status=$Run.status;conclusion=$Run.conclusion;jobs=@([ordered]@{name=$Job.name;status=$Job.status;conclusion=$Job.conclusion});artifacts=@([ordered]@{id=[long]$Artifact.id;name=$Artifact.name;digest=$Artifact.digest;sizeInBytes=[long]$Artifact.size_in_bytes;expired=[bool]$Artifact.expired})};$Utf8=New-Object Text.UTF8Encoding($false);[IO.File]::WriteAllText((Join-Path $Dir 'run-metadata.json'),($Meta|ConvertTo-Json -Depth 6),$Utf8)
gh run download $RunId --repo $Repo --name $Artifact.name --dir $Dir;if($LASTEXITCODE-ne0){throw 'Formal artifact download failed'}
$Report=Join-Path $Dir 'post-kernel-validation.json';conda run --no-capture-output -n pyscf-win313-test python $Validator $Dir --mode installed-wheel --expected-sha $Head --expected-nodeid $NodeId --expected-profile omp4-blas1 --expected-repeats 200 --expected-native-count 26 --run-metadata (Join-Path $Dir 'run-metadata.json') --expected-run-id $RunId --expected-branch $Branch --report $Report;$Exit=$LASTEXITCODE;$V=Get-Content -LiteralPath $Report -Raw -Encoding UTF8|ConvertFrom-Json -ErrorAction Stop;Copy-Item -LiteralPath $Validator -Destination (Join-Path $Dir 'validate_sgx_hse06_post_kernel_telemetry.py')
if((Get-FileHash -LiteralPath (Join-Path $Dir 'validate_sgx_hse06_post_kernel_telemetry.py') -Algorithm SHA256).Hash.ToLowerInvariant()-cne$V.validator_sha256){throw 'Formal validator copy mismatch'}
if($Exit-ne0-or-not$V.valid){throw 'Formal evidence INVALID'}
Write-Output "FORMAL_VERDICT=$($V.verdict)";Write-Output "FORMAL_REPORT=$Report"
```

`FORMAL_ARTIFACT_NOT_READY` is upload latency rather than `INVALID`; retry only this exact run’s artifact query. More than one artifact or malformed metadata is `INVALID` and must not be replaced by a rerun.

- [ ] **Step 5: Record exactly one scientific route**

Use `apply_patch` to record canonical run/job/artifact identity, runtime LibXC/DLL provenance, validator SHA, counts, findings, report, archive, and verdict. Then take exactly one route:

- `MECHANISM_CONFIRMED`: the same reproduced failure has `post_pass=false`, `pre_pass=true`, all required Extra cycles, and reconstruction residual within `1e-12`. Stop this investigation branch; refresh live `pyscf/pyscf:master`, then write a separate production RED/GREEN design. Do not create a fix branch in this plan.
- `MECHANISM_FALSIFIED`: retain the reproduced post-kernel failure and write the next smallest density/Fock/`veff` boundary design.
- `INCONCLUSIVE_NONCONVERGED`: separate main-loop from post-check convergence and design only the minimum convergence probe.
- `REPRODUCED_OTHER_ASSERTION`: retain the translation-assertion evidence; do not use it to decide the finite-difference mechanism.
- `NOT_REPRODUCED`: record exact text `post-kernel 0/200, NOT_REPRODUCED/HOLD`; do not claim fixed, update issue `#3312` as resolved, dispatch another profile, or start a wider matrix. Continue the long-term Goal with a separately approved next-minimal experiment.
- `INVALID`: repair only this exact evidence/experiment contract; never overwrite the first run with a rerun or draw a scientific conclusion.

Only after a production fix has its own RED/GREEN proof and the three LibXC-related nodeids have final CI evidence may the authorized long-term workflow update `pyscf/pyscf#3312` with nodeid status, exact run/artifact links, cause, and maintained resolution. Unresolved nodeids remain explicitly open.

---

## Final Verification

- [ ] Approved spec commit/hash, exact Stage 2 base, branch/worktree, original singleton nodeid, old/new validator boundaries and GoalBridge hash are frozen.
- [ ] Three commits have exact subjects and exactly two tracked paths differ; selection is unchanged; original assertions, places, delta, convergence settings and nine-case order remain unchanged.
- [ ] Hook lifecycle tests prove instance/class lookup restoration on success and exception; no wrapper survives across base/plus/minus operations.
- [ ] Schema-v2 validator rejects v1 evidence, validates formulas independently, exercises all listed mutations, writes complete atomic reports, and the old validator hash remains unchanged.
- [ ] Dedicated and original local nodes each emit exactly one v2 marker and zero v1 markers; canonical source evidence is exact original nodeid/profile/head and valid before push.
- [ ] Witness and formal dispatch each use a unique `CreateNew` latch, BeforeMax plus exact head binding, one PS1 heartbeat at 1,800 seconds, exact Goal paused/active readback, one precision job and one strict artifact.
- [ ] Witness is exact `SMOKE_PASS` before formal; formal cancellation is possible only after full identity and a parseable elapsed time of at least 300 minutes.
- [ ] A valid scientific failure is retained rather than retried; `0/200` remains `NOT_REPRODUCED/HOLD`; no issue nodeid is marked resolved without a separately maintained fix and final evidence.
- [ ] Active document records current state, exact evidence, next command and short plan after every boundary; completed phases move to `.agents/completed/` only when actually complete.
