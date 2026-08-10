# SGX HSE06 Extra-cycle Telemetry Implementation Plan

> **Execution:** Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans`. Use TDD for Tasks 1–4 and verification-before-completion before every commit or push.

**Goal:** 在隔离调查分支中，为 SGX settings-2/HSE06 原有限差分断言增加默认关闭的标量遥测；先用 Windows Python 3.12、`omp4-blas1`、1-repeat installed-wheel witness 验证 evidence 管线，再用 200 repeats 判断 Extra-cycle energy shift 是否解释已观测 mismatch。

**Architecture:** 原数值路径和两条 `assertAlmostEqual` 保持不变。新增 diagnostic nodeid 显式启用 callback，在 assertion 前输出一行 schema-v1 JSON。仓库中不新增 workflow、parser 或 production code；一个本地忽略、标准库-only validator 统一验收 source、remote witness 和 formal artifact。

## Fixed constraints

- Approved base: `37fc114e1c0519ea83197e81826afaa62d2aac89`。
- Implementation branch: `codex/investigate/libxc-712-sgx-extra-cycle-telemetry`。
- Relative to base only these paths may change:
  - `.github/workflows/test_precision_investigation_contract.py`
  - `.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt`
  - `pyscf/sgx/grad/test/test_rks.py`
- Do not change `delta=1e-4`, `conv_tol=1e-12`, `conv_check=True`, `max_cycle`, `OMP=4`, BLAS=`1`, LibXC `7.1.2`, or assertion places `12/6`。
- Do not modify runner/workflow/verifier/dependencies/production modules; do not monkeypatch `SGX.post_kernel()` or retain callback `envs/locals()` references。
- Prefix: `PYSCF_SGX_HSE06_TELEMETRY_V1 `; schema integer `1`; `json.dumps(..., allow_nan=False)`。
- Assertion remains the only scientific pass/fail gate. Valid scientific failure is not an invalid pipeline。
- Exactly three implementation commits, all ending `[skip ci]`; no PR and no full matrix。
- This plan ends after Stage 1. A valid, converged `0/200` produces `NOT_REPRODUCED/HOLD`, then a separate Stage 2 plan; it is never called PASS/FIXED。
- CI wait uses exactly one monitor: prefer a callable Codex heartbeat; when that interface is absent, use the user-authorized audited PS1 fallback specified below。Witness interval is 15 minutes, formal interval is 30 minutes; Goal is paused while waiting and resumed after terminal state。

---

### Task 1: Isolated worktree and failed-attempt marker contract

**Files:** Modify `.github/workflows/test_precision_investigation_contract.py`

- [ ] **1.1 Create and verify the worktree**

```powershell
$BaseWt = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$Base = '37fc114e1c0519ea83197e81826afaa62d2aac89'
git -C $BaseWt rev-parse --verify "$Base^{commit}"
git -C $BaseWt worktree add $Wt -b $Branch $Base
git -C $Wt branch --show-current
git -C $Wt status --short
git -C $Wt merge-base --is-ancestor $Base HEAD
```

Expected: exact branch, clean worktree, no inherited untracked DLLs。

- [ ] **1.2 Run baseline**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
Set-Location $Wt
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  .github/workflows/test_precision_investigation_contract.py
if ($LASTEXITCODE -ne 0) { throw 'Baseline precision contract failed' }
```

- [ ] **1.3 RED: failed attempt must preserve one marker**

Add module constant:

```python
SGX_HSE06_TELEMETRY_PREFIX = 'PYSCF_SGX_HSE06_TELEMETRY_V1 '
```

In existing `test_failed_attempt_keeps_complete_evidence_and_exits_nonzero`, after its current record/file assertions add:

```python
            attempt_log = (
                output / records[0]['log_file']
            ).read_text(encoding='utf-8')
            markers = [
                line for line in attempt_log.splitlines()
                if line.startswith(SGX_HSE06_TELEMETRY_PREFIX)
            ]
            self.assertEqual(len(markers), 1)
            self.assertEqual(
                json.loads(markers[0][len(SGX_HSE06_TELEMETRY_PREFIX):]),
                {
                    'schema_version': 1,
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
                },
            )
```

Run only that test and require the intended marker-count failure:

```powershell
$RedOutput = @(& conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  '.github/workflows/test_precision_investigation_contract.py::PrecisionInvestigationContractTest::test_failed_attempt_keeps_complete_evidence_and_exits_nonzero' 2>&1)
$RedExit = $LASTEXITCODE
$RedOutput | ForEach-Object { Write-Output $_ }
if ($RedExit -eq 0 -or ($RedOutput -join "`n") -notmatch 'AssertionError:\s+0\s+!=\s+1') {
  throw 'Did not observe the intended missing-marker RED'
}
```

Expected RED: marker count is 0 while all other failure evidence still exists。

- [ ] **1.4 GREEN: print marker before the synthetic assertion**

Change only the temporary `test_sample.py` fixture:

```python
            payload = {
                'schema_version': 1,
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
            (root / 'test_sample.py').write_text(
                'import json\n'
                f'PREFIX = {SGX_HSE06_TELEMETRY_PREFIX!r}\n'
                f'PAYLOAD = {payload!r}\n'
                'def test_failure():\n'
                '    print(PREFIX + json.dumps(PAYLOAD), flush=True)\n'
                '    assert False\n',
                encoding='utf-8',
            )
```

This proves raw-log preservation, not the scientific schema。

- [ ] **1.5 Verify and commit**

```powershell
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  '.github/workflows/test_precision_investigation_contract.py::PrecisionInvestigationContractTest::test_failed_attempt_keeps_complete_evidence_and_exits_nonzero'
if ($LASTEXITCODE -ne 0) { throw 'Target marker contract failed' }
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  .github/workflows/test_precision_investigation_contract.py
if ($LASTEXITCODE -ne 0) { throw 'Full precision contract failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'Task 1 diff check failed' }
git add .github/workflows/test_precision_investigation_contract.py
git diff --cached --name-status
git commit -m 'test(ci): preserve telemetry markers on failure [skip ci]'
```

---

### Task 2: Exact Stage 1 selector and dedicated nodeid

**Files:**
- Create `.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt`
- Modify `.github/workflows/test_precision_investigation_contract.py`
- Modify `pyscf/sgx/grad/test/test_rks.py`

- [ ] **2.1 Re-establish task context**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Selection = '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
$NodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
Set-Location $Wt
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
git status --short --untracked-files=no
```

- [ ] **2.2 RED/GREEN selector contract**

Add this exact contract, observe file-not-found RED, then create the selection with one line:

```python
    def test_sgx_hse06_telemetry_selection(self):
        runner = load_runner()
        selection = (
            ROOT / '.github/workflows/'
            'precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
        )
        self.assertEqual(runner.load_nodeids(selection), [
            'pyscf/sgx/grad/test/test_rks.py::KnownValues::'
            'test_finite_diff_grad_settings2_hse06_telemetry',
        ])
```

```text
pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry
```

Before creating the selection file, run:

```powershell
if (Test-Path -LiteralPath $Selection) { throw 'Selection unexpectedly exists before RED' }
$RedOutput = @(& conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  '.github/workflows/test_precision_investigation_contract.py::PrecisionInvestigationContractTest::test_sgx_hse06_telemetry_selection' 2>&1)
$RedExit = $LASTEXITCODE
$RedOutput | ForEach-Object { Write-Output $_ }
if ($RedExit -eq 0 -or ($RedOutput -join "`n") -notmatch 'FileNotFoundError') {
  throw 'Did not observe the intended missing-selection RED'
}
```

- [ ] **2.3 Prepare non-authoritative source-tree DLL fixtures**

```powershell
$DllSource = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\pyscf\lib'
$DllTarget = Join-Path $Wt 'pyscf\lib'
$Dlls = @(Get-ChildItem -LiteralPath $DllSource -Filter '*.dll' -File)
if ($Dlls.Count -ne 26) { throw "Expected 26 DLLs, got $($Dlls.Count)" }
foreach ($Dll in $Dlls) {
  $Target = Join-Path $DllTarget $Dll.Name
  if (Test-Path -LiteralPath $Target) { throw "Unexpected DLL: $Target" }
  Copy-Item -LiteralPath $Dll.FullName -Destination $Target
  if ((Get-FileHash $Dll.FullName).Hash -ne (Get-FileHash $Target).Hash) {
    throw "DLL hash mismatch: $($Dll.Name)"
  }
}
conda run --no-capture-output -n pyscf-win313-test python -c `
  "import pathlib,pyscf; from pyscf.dft import libxc; root=pathlib.Path.cwd().resolve(); p=pathlib.Path(pyscf.__file__).resolve(); assert root in p.parents,p; assert libxc.libxc_version() == '7.1.2'"
if ($LASTEXITCODE -ne 0) { throw 'Source-tree DLL smoke failed' }
```

These untracked DLLs support local functional tests only; they are not wheel/provenance evidence。

- [ ] **2.4 RED/GREEN dedicated nodeid**

Run exact `--collect-only`; require nodeid-not-found RED:

```powershell
$CollectRed = @(& conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  --collect-only -q -p no:cacheprovider -c pytest.ini --rootdir . $NodeId 2>&1)
$CollectRedExit = $LASTEXITCODE
$CollectRed | ForEach-Object { Write-Output $_ }
if ($CollectRedExit -eq 0 -or ($CollectRed -join "`n") -notmatch 'not found|no match') {
  throw 'Did not observe the intended missing-nodeid RED'
}
```

Then add before the original nine-case test:

```python
    def test_finite_diff_grad_settings2_hse06_telemetry(self):
        self._check_finite_diff_grad(
            ALL_SETTINGS[2], ALL_PRECISIONS[2], 'HSE06')
```

Do not alter any original call/order/argument。

- [ ] **2.5 Verify and commit**

```powershell
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  --collect-only -q -p no:cacheprovider -c pytest.ini --rootdir . $NodeId
if ($LASTEXITCODE -ne 0) { throw 'Dedicated nodeid collection failed' }
$NodeOutput = @(& conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . $NodeId 2>&1)
$NodeExit = $LASTEXITCODE
$NodeOutput | ForEach-Object { Write-Output $_ }
if ($NodeExit -ne 0 -and ($NodeOutput -join "`n") -notmatch 'AssertionError[\s\S]*assertAlmostEqual|assertAlmostEqual[\s\S]*AssertionError') {
  throw 'Dedicated nodeid failed outside the original scientific assertion'
}
if ($NodeExit -ne 0) { Write-Output 'LOCAL_SCIENTIFIC_ASSERTION_OBSERVED' }
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  .github/workflows/test_precision_investigation_contract.py
if ($LASTEXITCODE -ne 0) { throw 'Precision contract failed after selector change' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'Task 2 diff check failed' }
git add $Selection .github/workflows/test_precision_investigation_contract.py `
  pyscf/sgx/grad/test/test_rks.py
git diff --cached --name-status
git commit -m 'test(ci): select isolated SGX HSE06 telemetry [skip ci]'
```

---

### Task 3: Default-off base/plus/minus scalar telemetry

**Files:** Modify `pyscf/sgx/grad/test/test_rks.py`

- [ ] **3.1 Re-establish task context**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Selection = '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
$NodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
Set-Location $Wt
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
git status --short --untracked-files=no
```

- [ ] **3.2 RED: enable a missing keyword**

Change only the dedicated call to `telemetry=True`, then require the intended signature RED:

```powershell
$RedOutput = @(& conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . $NodeId 2>&1)
$RedExit = $LASTEXITCODE
$RedOutput | ForEach-Object { Write-Output $_ }
if ($RedExit -eq 0 -or ($RedOutput -join "`n") -notmatch "unexpected keyword argument 'telemetry'") {
  throw 'Did not observe the intended telemetry-keyword RED'
}
```

- [ ] **3.3 GREEN: implement the approved telemetry interface**

Add `import json`, prefix constant, and keyword-only default:

```python
TELEMETRY_PREFIX = 'PYSCF_SGX_HSE06_TELEMETRY_V1 '

def _check_finite_diff_grad(
        self, df_settings, order, xc, *, telemetry=False):
```

When telemetry is true:

1. Before gradient kernel, set `phase='base'`, attach callback, and immediately copy these exact JSON-safe scalars on every cycle: `cycle`, `e_tot`, `last_hf_e`, `delta_e`, `norm_gorb`, `norm_ddm`, `scf_conv`, `conv_tol`, `conv_tol_grad`, `conv_check`. Never retain `envs`。
2. Save base `mf.e_tot/mf.converged` immediately after gradient kernel; only then create scanner。
3. Set phase plus; save `e1` and scanner convergence immediately; only then set minus; save `e2` and convergence immediately。
4. Each phase has exact keys `main/post_energy/post_converged/extra_executed/extra_shift`; `extra_executed = main.scf_conv and main.conv_check`; false requires JSON null, true requires `post_energy-main.e_tot`。

Implement the ordering with this concrete skeleton around the existing calls:

```python
        phase = 'base'
        main_cycles = {}
        post = {}
        if telemetry:
            def snapshot_main_cycle(envs):
                main_cycles[phase] = {
                    'cycle': int(envs['cycle']) + 1,
                    'e_tot': float(envs['e_tot']),
                    'last_hf_e': float(envs['last_hf_e']),
                    'delta_e': float(envs['e_tot'] - envs['last_hf_e']),
                    'norm_gorb': float(envs['norm_gorb']),
                    'norm_ddm': float(envs['norm_ddm']),
                    'scf_conv': bool(envs['scf_conv']),
                    'conv_tol': float(envs['conv_tol']),
                    'conv_tol_grad': float(envs['conv_tol_grad']),
                    'conv_check': bool(envs['conv_check']),
                }
            mf.callback = snapshot_main_cycle

        g = mf.nuc_grad_method().set(
            sgx_grid_response=True, grid_response=True).kernel()
        if telemetry:
            post['base'] = (float(mf.e_tot), bool(mf.converged))
        mol1 = mol.copy()
        mf_scanner = mf.as_scanner()
        delta = 1e-4
        if telemetry:
            phase = 'plus'
        e1 = mf_scanner(mol1.set_geom_(
            f'O  0. 0. {delta:f}; 1  0. -0.757 0.587; 1  0. 0.757 0.587'
        ))
        if telemetry:
            post['plus'] = (float(e1), bool(mf_scanner.converged))
            phase = 'minus'
        e2 = mf_scanner(mol1.set_geom_(
            f'O  0. 0. -{delta:f}; 1  0. -0.757 0.587; 1  0. 0.757 0.587'
        ))
        if telemetry:
            post['minus'] = (float(e2), bool(mf_scanner.converged))
            phases = {}
            for name in ('base', 'plus', 'minus'):
                main = main_cycles[name]
                post_energy, post_converged = post[name]
                extra_executed = main['scf_conv'] and main['conv_check']
                phases[name] = {
                    'main': main,
                    'post_energy': post_energy,
                    'post_converged': post_converged,
                    'extra_executed': extra_executed,
                    'extra_shift': (
                        post_energy - main['e_tot']
                        if extra_executed else None),
                }
```

5. Emit one marker before either assertion with exact schema:

```text
schema_version = 1
units = {energy: Hartree, gradient: Hartree/Bohr, displacement: Angstrom}
case = {settings_index: 2, settings: [true,true,true,true,true], precision: 6,
        xc: HSE06, delta: 1e-4, translation_places: 12,
        finite_difference_places: 6}
phases = {base, plus, minus}
result = {analytic_gradient, translation_l1, translation_assertion_pass,
          finite_difference_pre, finite_difference_post,
          gradient_error_pre, gradient_error_post,
          finite_difference_pre_pass, finite_difference_post_pass,
          extra_contribution, closure_residual}
```

Use these exact formulas:

```python
fd_pre = (plus_main - minus_main) / (2 * delta) * lib.param.BOHR
fd_post = (e1 - e2) / (2 * delta) * lib.param.BOHR
error_pre = analytic_gradient - fd_pre
error_post = analytic_gradient - fd_post
extra_contribution = fd_post - fd_pre
closure_residual = error_post - (error_pre - extra_contribution)
translation_pass = round(abs(translation_l1), 12) == 0
pre_pass = round(abs(error_pre), 6) == 0
post_pass = round(abs(error_post), 6) == 0
```

Serialize with `sort_keys=True`, compact separators, `allow_nan=False`, and `flush=True`. Keep these original gates verbatim and in order:

```python
self.assertAlmostEqual(numpy.abs(g.sum(axis=0)).sum(), 0, 12)
self.assertAlmostEqual(g[0,2], (e1-e2)/(2*delta)*lib.param.BOHR, order)
```

- [ ] **3.4 Verify old/new paths and commit**

```powershell
$Prefix = 'PYSCF_SGX_HSE06_TELEMETRY_V1 '
$DedicatedOutput = @(& conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -s -p no:cacheprovider -c pytest.ini --rootdir . $NodeId 2>&1)
$DedicatedExit = $LASTEXITCODE
$DedicatedOutput | ForEach-Object { Write-Output $_ }
$DedicatedMarkers = @($DedicatedOutput | Where-Object { ([string]$_).StartsWith($Prefix) })
if ($DedicatedMarkers.Count -ne 1) { throw "Expected one dedicated marker, got $($DedicatedMarkers.Count)" }
if ($DedicatedExit -ne 0 -and ($DedicatedOutput -join "`n") -notmatch 'AssertionError[\s\S]*assertAlmostEqual|assertAlmostEqual[\s\S]*AssertionError') {
  throw 'Dedicated diagnostic failed outside the original scientific assertion'
}
if ($DedicatedExit -ne 0) { Write-Output 'LOCAL_DEDICATED_SCIENTIFIC_ASSERTION_OBSERVED' }

$OriginalOutput = @(& conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -s -p no:cacheprovider -c pytest.ini --rootdir . `
  'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad' 2>&1)
$OriginalExit = $LASTEXITCODE
$OriginalOutput | ForEach-Object { Write-Output $_ }
$OriginalMarkers = @($OriginalOutput | Where-Object { ([string]$_).StartsWith($Prefix) })
if ($OriginalMarkers.Count -ne 0) { throw "Original path leaked $($OriginalMarkers.Count) marker(s)" }
if ($OriginalExit -ne 0 -and ($OriginalOutput -join "`n") -notmatch 'AssertionError[\s\S]*assertAlmostEqual|assertAlmostEqual[\s\S]*AssertionError') {
  throw 'Original nine-case nodeid failed outside a scientific assertion'
}
if ($OriginalExit -ne 0) { Write-Output 'LOCAL_ORIGINAL_SCIENTIFIC_ASSERTION_OBSERVED' }

conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  .github/workflows/test_precision_investigation_contract.py
if ($LASTEXITCODE -ne 0) { throw 'Precision contract failed after telemetry change' }
conda run --no-capture-output -n pyscf-win313-test python -m py_compile `
  pyscf/sgx/grad/test/test_rks.py `
  .github/workflows/test_precision_investigation_contract.py
if ($LASTEXITCODE -ne 0) { throw 'Task 3 py_compile failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'Task 3 diff check failed' }
git add pyscf/sgx/grad/test/test_rks.py
git diff --cached --name-status
git commit -m 'test(sgx): emit HSE06 extra-cycle telemetry [skip ci]'
```

Expected: dedicated path one marker; original path zero markers; commit only `test_rks.py`。

- [ ] **3.5 Generate committed source evidence**

```powershell
$Head = (git rev-parse HEAD).Trim()
$SourceOut = Join-Path $Wt "tmp\stage1-source-$($Head.Substring(0,12))"
if (Test-Path $SourceOut) { throw "Output exists: $SourceOut" }
conda run --no-capture-output -n pyscf-win313-test python `
  .github/workflows/run_precision_tests.py `
  --nodeids-file $Selection --repeats 1 --profile 4/1 `
  --output-dir $SourceOut --tested-sha $Head `
  --working-directory . --rootdir . --pytest-config pytest.ini `
  --environment-mode source-tree `
  --collector .github/workflows/collect_precision_environment.py
$SourceExit = $LASTEXITCODE
if (-not (Test-Path (Join-Path $SourceOut 'records.jsonl'))) {
  throw 'Source runner produced no auditable records'
}
$Utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $SourceOut 'runner-exit-code.txt'), ([string]$SourceExit), $Utf8)
```

Do not classify `$SourceExit` before Task 4. A valid assertion failure is audited from the completed evidence; only missing evidence is an immediate harness error。

---

### Task 4: Local fail-closed evidence validator

**Files:** Create locally only `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py`

- [ ] **4.1 Re-establish task context**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$NodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
Set-Location $Wt
$Head = (git rev-parse HEAD).Trim()
$SourceOut = Join-Path $Wt "tmp\stage1-source-$($Head.Substring(0,12))"
```

- [ ] **4.2 RED: add self-tests before validator implementation**

The script uses only `argparse/csv/hashlib/json/math/pathlib/shutil/sys/tempfile/unittest`. Fixed CLI:

```text
validate_sgx_hse06_telemetry.py EVIDENCE_DIR
  --mode source-tree|installed-wheel
  --expected-sha SHA --expected-nodeid NODEID
  --expected-profile omp4-blas1 --expected-repeats 1|200
  [--source-root PATH]
  [--expected-native-count 26 --run-metadata PATH
   --expected-run-id ID --expected-branch BRANCH]
  --report PATH
validate_sgx_hse06_telemetry.py --self-test
```

Use this exact module boundary; the filesystem loader produces normalized attempt dictionaries for the pure classifier, and no validation layer may read global state:

```python
BOHR = 0.52917721092
PREFIX = 'PYSCF_SGX_HSE06_TELEMETRY_V1 '


def new_report():
    return {
        'validator_sha256': hashlib.sha256(
            pathlib.Path(__file__).read_bytes()).hexdigest(),
        'valid': False,
        'verdict': 'INVALID',
        'records': 0,
        'pass': 0,
        'fail': 0,
        'nonconverged': 0,
        'finding_counts': {},
        'first_failure': None,
        'first_finding': None,
        'errors': [],
    }


class InvalidEvidence(Exception):
    pass


def parse_args(argv=None):
    """Return the fixed CLI namespace above."""
    raise NotImplementedError('parse_args')


def load_json_strict(path):
    """Load UTF-8 JSON while rejecting duplicate keys."""
    raise NotImplementedError('load_json_strict')


def load_evidence(options):
    """Return the exact bundle documented in Task 4.3."""
    raise NotImplementedError('load_evidence')


def validate_file_contract(bundle, options):
    """Validate selection, records, CSV, summaries, logs, and exit code."""
    raise NotImplementedError('validate_file_contract')


def parse_log_marker(text):
    """Return the sole strict marker payload from one attempt log."""
    raise NotImplementedError('parse_log_marker')


def validate_marker(payload, record):
    """Return one normalized telemetry attempt or raise InvalidEvidence."""
    raise NotImplementedError('validate_marker')


def validate_runtime(bundle, options):
    """Validate source-tree or installed-wheel provenance."""
    raise NotImplementedError('validate_runtime')


def validate_run_metadata(bundle, options):
    """Validate the remote run, job, and unique artifact identity."""
    raise NotImplementedError('validate_run_metadata')


def classify_attempts(attempts, expected_repeats):
    """Return verdict, finding counts, first failure, and first finding."""
    raise NotImplementedError('classify_attempts')


def validate_evidence(options):
    """Run every layer and return the exact report dictionary."""
    raise NotImplementedError('validate_evidence')


def write_report(path, report):
    """Write sorted UTF-8-no-BOM/LF JSON atomically."""
    raise NotImplementedError('write_report')
```

Add these runnable pure RED bodies first; they must fail at `classify_attempts`, not at import or syntax:

```python
class ValidatorSelfTest(unittest.TestCase):
    @staticmethod
    def attempt(**updates):
        value = {
            'attempt': 1,
            'status': 'pass',
            'translation_pass': True,
            'pre_pass': True,
            'post_pass': True,
            'all_converged': True,
            'all_extra_executed': True,
            'shift_residual': 0.0,
        }
        value.update(updates)
        return value

    def test_classify_smoke_pass(self):
        result = classify_attempts([self.attempt()], 1)
        self.assertEqual(result['verdict'], 'SMOKE_PASS')

    def test_classify_not_reproduced(self):
        attempts = [self.attempt(attempt=i) for i in range(1, 201)]
        result = classify_attempts(attempts, 200)
        self.assertEqual(result['verdict'], 'NOT_REPRODUCED')

    def test_classify_nonconverged_before_all_pass(self):
        item = self.attempt(all_converged=False)
        result = classify_attempts([item], 1)
        self.assertEqual(result['verdict'], 'INCONCLUSIVE_NONCONVERGED')

    def test_classify_confirmed_failure(self):
        item = self.attempt(
            status='fail', pre_pass=True, post_pass=False)
        result = classify_attempts([item], 1)
        self.assertEqual(result['verdict'], 'MECHANISM_CONFIRMED')

    def test_classify_falsified_failure(self):
        item = self.attempt(
            status='fail', pre_pass=False, post_pass=False)
        result = classify_attempts([item], 1)
        self.assertEqual(result['verdict'], 'MECHANISM_FALSIFIED')

    def test_classify_translation_failure(self):
        item = self.attempt(status='fail', translation_pass=False)
        result = classify_attempts([item], 1)
        self.assertEqual(result['verdict'], 'REPRODUCED_OTHER_ASSERTION')


def run_self_tests():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ValidatorSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ['--self-test']:
        return run_self_tests()
    options = parse_args(argv)
    try:
        report = validate_evidence(options)
    except InvalidEvidence as error:
        report = new_report()
        report['errors'] = [str(error)]
    if set(report) != set(new_report()):
        raise RuntimeError('Validator returned an incomplete report schema')
    write_report(options.report, report)
    return 0 if report['valid'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
```

Run the RED explicitly:

```powershell
$RedOutput = @(& conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test 2>&1)
$RedExit = $LASTEXITCODE
$RedOutput | ForEach-Object { Write-Output $_ }
if ($RedExit -eq 0 -or ($RedOutput -join "`n") -notmatch 'NotImplementedError: classify_attempts') {
  throw 'Did not observe the intended validator-classifier RED'
}
```

Then add tempfile-backed tests around the same public functions. `--self-test` must cover these exact cases:

- source/1 valid fixture → `SMOKE_PASS`。
- installed/200 valid fixture with 200 generated logs and 26 native entries → `NOT_REPRODUCED`。
- mutation table (duplicate JSON key; wrong units/case/formula/null/path/SHA/profile/mode/pip/native/run identity; any phase `conv_tol != 1e-12` or `conv_check != true`) → `INVALID`, process exit 2。
- scientific table: translation failure, pass+nonconvergence, confirmed FD mechanism, falsified FD mechanism → their exact verdicts, process exit 0。

Use this exact fixture/test boundary and replace the earlier `run_self_tests` with the two-class suite below. Implement `build_fixture` as test-only code that writes the same paths consumed by `load_evidence`; `mutate_fixture` changes exactly one field/file per named mutation:

```python
MUTATIONS = (
    'duplicate-json-key', 'wrong-units', 'wrong-case', 'wrong-formula',
    'wrong-null', 'escaping-log-path', 'wrong-sha', 'wrong-profile',
    'wrong-mode', 'pip-failure', 'wrong-native-count',
    'native-linkage-failure', 'wrong-run-id', 'wrong-job',
    'wrong-artifact-count', 'wrong-conv-tol', 'wrong-conv-check',
)


def build_fixture(root, *, mode, repeats):
    """Write a complete valid evidence tree and return an argparse namespace."""
    raise NotImplementedError('build_fixture')


def mutate_fixture(root, mutation):
    """Apply exactly one MUTATIONS corruption to an existing fixture."""
    raise NotImplementedError('mutate_fixture')


class EvidenceBoundarySelfTest(unittest.TestCase):
    def test_source_one_is_smoke_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            options = build_fixture(
                root, mode='source-tree', repeats=1)
            report = validate_evidence(options)
            self.assertTrue(report['valid'])
            self.assertEqual(report['verdict'], 'SMOKE_PASS')
            self.assertEqual(report['records'], 1)

    def test_installed_two_hundred_is_not_reproduced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            options = build_fixture(
                root, mode='installed-wheel', repeats=200)
            report = validate_evidence(options)
            self.assertTrue(report['valid'])
            self.assertEqual(report['verdict'], 'NOT_REPRODUCED')
            self.assertEqual(report['records'], 200)

    def test_each_trust_boundary_mutation_is_invalid(self):
        for mutation in MUTATIONS:
            with self.subTest(mutation=mutation):
                with tempfile.TemporaryDirectory() as directory:
                    root = pathlib.Path(directory)
                    options = build_fixture(
                        root, mode='installed-wheel', repeats=1)
                    mutate_fixture(root, mutation)
                    with self.assertRaises(InvalidEvidence):
                        validate_evidence(options)


def run_self_tests():
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite((
        loader.loadTestsFromTestCase(ValidatorSelfTest),
        loader.loadTestsFromTestCase(EvidenceBoundarySelfTest),
    ))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1
```

After the pure classifier turns GREEN, add this class to `run_self_tests`, run `--self-test`, and observe `NotImplementedError: build_fixture` before implementing any loader. Then implement one trust boundary at a time until every table row is GREEN。

- [ ] **4.3 GREEN: implement exact automatic checks**

The validator must fail closed and perform all of these itself:

`load_evidence` returns exactly this internal bundle: `root: Path`, `selection: list[str]`, `records: list[dict]`, `csv_rows: list[dict]`, `physical_logs: dict[str,str]`, `summary_counts: dict[str,int]`, `runtime: dict`, `run_metadata: dict|None`, and `exit_code: int`。`validate_marker` returns the normalized keys used by `classify_attempts`: `attempt/status/translation_pass/pre_pass/post_pass/all_converged/all_extra_executed/shift_residual` plus the original payload。

Use this minimal orchestration; validation functions raise `InvalidEvidence` and never silently append warnings:

```python
def validate_evidence(options):
    bundle = load_evidence(options)
    validate_file_contract(bundle, options)
    attempts = [
        validate_marker(
            parse_log_marker(bundle['physical_logs'][record['log_file']]),
            record)
        for record in bundle['records']
    ]
    validate_runtime(bundle, options)
    if options.mode == 'installed-wheel':
        validate_run_metadata(bundle, options)
    finding = classify_attempts(attempts, options.expected_repeats)
    report = new_report()
    report.update({
        'valid': True,
        'verdict': finding['verdict'],
        'records': len(attempts),
        'pass': sum(item['status'] == 'pass' for item in attempts),
        'fail': sum(item['status'] == 'fail' for item in attempts),
        'nonconverged': sum(
            not item['all_converged'] for item in attempts),
        'finding_counts': finding['finding_counts'],
        'first_failure': finding['first_failure'],
        'first_finding': finding['first_finding'],
    })
    return report
```

- Exact singleton selection; JSONL/CSV/physical+referenced logs all N; attempts exactly `1..N`; no retry, duplicate, extra log, missing reference, or path escaping evidence root。
- `summary.csv` header must be exactly `tested_sha,nodeid,attempt,profile,status,duration_seconds,pytest_summary,log_file,environment_file,nodeids_file`; every row must equal its JSONL record for all fields。`summary.md` must exist and its status counts must equal the records。
- Every log has exactly one strict JSON marker; reject duplicate object keys。
- Exact schema/key/type/unit/case sets. `schema_version/settings_index/precision/places/cycle` are non-bool integers; settings and convergence/assertion flags are bool; all energies/norms/tolerances/FD/errors/contribution/closure are finite floats; only `extra_executed=False` permits `extra_shift=null`。
- Fix `BOHR=0.52917721092`; require `extra_executed is (main.scf_conv and main.conv_check)` and every phase `conv_tol == 1e-12`, `conv_check is True`; then recompute `delta_e`, `extra_shift`, both FDs, both errors, contribution, closure, and three Python `round` mirrors with absolute tolerance `1e-12`。
- When plus/minus both executed Extra cycle, define and recompute `shift_residual = extra_contribution - (plus.extra_shift - minus.extra_shift) / (2*delta) * BOHR`; this is distinct from the algebraic `closure_residual` and is required to satisfy `abs(shift_residual) <= 1e-12` for mechanism confirmation。
- Record status equals the two original mirrors; failed record log contains `AssertionError`。Source `runner-exit-code.txt` and installed `pytest-exit-code.txt` must be 0 iff all records pass and nonzero iff any record fails。
- Runtime schema v2, mode, LibXC 7.1.2, OMP=4/all BLAS=1。Source requires every record SHA plus `runtime.git_commit.returncode=0/output=expected SHA`, and import below source root. Installed requires every record SHA plus `runtime.environment.PRECISION_TESTED_SHA=expected SHA`, Windows Python 3.12 site-packages, pip clean, exactly 26 SHA-sized DLL entries with linkage rc0, and `libxc_itrf.dll` resolves wheel-local `libxc.dll`。
- Installed run metadata must match run id/attempt 1/workflow_dispatch/workflow/head/branch/completed and one unexpired `precision-Windows-py3.12` artifact with id/digest/positive size。The single job must be `{name: precision, status: completed}`; all records pass requires run/job conclusion `success`, while any scientific failed record requires run/job conclusion `failure` and remains valid evidence。

Classification priority is automatic: first classify the lowest `status=fail` attempt; only when `fail=0` may pass+nonconverged become the overall finding。Report also records `finding_counts` and `first_failure`。

```text
structure/provenance mismatch -> INVALID, exit 2
translation false             -> REPRODUCED_OTHER_ASSERTION, exit 0
any main/post nonconverged     -> INCONCLUSIVE_NONCONVERGED, exit 0
post FD false + pre true + all three phases main/post converged,
all three extra_executed + abs(shift_residual) <= 1e-12
                              -> MECHANISM_CONFIRMED, exit 0
other valid FD failure         -> MECHANISM_FALSIFIED, exit 0
N=1 all valid/converged/pass   -> SMOKE_PASS, exit 0
N=200 all valid/converged/pass -> NOT_REPRODUCED, exit 0
```

Pass+nonconverged must never count toward 0/N. Report JSON is UTF-8 no BOM/LF/sorted and always records `validator_sha256, valid, verdict, records, pass, fail, nonconverged, finding_counts, first_failure, first_finding, errors`。

```powershell
conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test
if ($LASTEXITCODE -ne 0) { throw 'Validator self-test failed' }
conda run --no-capture-output -n pyscf-win313-test python -m py_compile $Validator
if ($LASTEXITCODE -ne 0) { throw 'Validator py_compile failed' }
```

- [ ] **4.4 Validate source evidence and freeze validator identity**

```powershell
$Report = Join-Path $SourceOut 'telemetry-validation.json'
conda run --no-capture-output -n pyscf-win313-test python $Validator $SourceOut `
  --mode source-tree --expected-sha $Head --expected-nodeid $NodeId `
  --expected-profile omp4-blas1 --expected-repeats 1 `
  --source-root $Wt --report $Report
if ($LASTEXITCODE -ne 0) { throw 'Source evidence INVALID' }
$V = Get-Content -Raw -Encoding utf8 $Report | ConvertFrom-Json -ErrorAction Stop
Copy-Item $Validator (Join-Path $SourceOut 'validate_sgx_hse06_telemetry.py')
$ArchivedValidator = Join-Path $SourceOut 'validate_sgx_hse06_telemetry.py'
if ((Get-FileHash $ArchivedValidator).Hash.ToLowerInvariant() -ne $V.validator_sha256) {
  throw 'Validator SHA mismatch'
}
```

Use `apply_patch` to write exact keys `stage1_head: $Head`, `stage1_validator_sha256: $V.validator_sha256`, `stage1_source_verdict: $V.verdict`, counts, first finding, and report path into `$ActiveDoc`。If verdict is not `SMOKE_PASS`, retain evidence and stop cleanly before Task 5; do not call it a pipeline error or rerun it。The validator remains local/ignored and is never staged. Every later shell must compare the current validator, local/remote head, and prior witness verdict against these frozen keys。

- [ ] **4.5 Prepare the user-authorized PS1 heartbeat fallback**

Search callable tools for `automation_update` once at execution and record the result. The current 2026-08-10 root inventory does not expose it, so this plan's executable route is the user-authorized PS1/background fallback。If a future executor wants to switch back to a newly available native heartbeat, amend/review this plan first rather than improvising two schedulers。

Before using PS1, open Codex Scheduled Tasks and delete/pause the stale automation id `libxc-3-pbc-hse06-sgx-finite-difference-hse06-pbc-hse`; verify no active app heartbeat remains for this task. If that cannot be verified, stop before remote dispatch rather than double-poll。

Modify local-only audited script `D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1` with `apply_patch`; preserve its old defaults and Goal identity logic, and add:

```powershell
param(
  [switch]$CheckOnce,
  [switch]$NoResume,
  [ValidateSet('active', 'paused')]
  [string]$SetGoalStatus,
  [switch]$SelfTest,
  [long[]]$TargetRunIds,
  [ValidatePattern('^[0-9a-f]{40}$')][string]$TargetHeadSha,
  [ValidateRange(60,3600)][int]$IntervalSeconds = 1800,
  [ValidateRange(0,360)][int]$WakeAfterMinutes = 0
)
```

Keep the existing `-NoResume`/`-SetGoalStatus` incompatibility guard, then add this fail-closed target contract before any Goal mutation or GitHub read:

```powershell
$HasTargetRuns = $PSBoundParameters.ContainsKey('TargetRunIds')
$HasTargetHead = $PSBoundParameters.ContainsKey('TargetHeadSha')
if ($HasTargetRuns -xor $HasTargetHead) {
  throw '-TargetRunIds and -TargetHeadSha must be supplied together'
}
if ($HasTargetRuns -and (
    $TargetRunIds.Count -eq 0 -or
    @($TargetRunIds | Where-Object { $_ -le 0 }).Count -ne 0 -or
    @($TargetRunIds | Select-Object -Unique).Count -ne $TargetRunIds.Count)) {
  throw '-TargetRunIds must contain unique positive IDs'
}
if ($SelfTest -and ($CheckOnce -or $NoResume -or
    $PSBoundParameters.ContainsKey('SetGoalStatus') -or $HasTargetRuns)) {
  throw '-SelfTest cannot be combined with runtime or Goal parameters'
}
```

When the paired target values are supplied, map them to existing `$RunIds/$ExpectedHeadSha/$CheckIntervalSeconds`; otherwise preserve the seven-run legacy defaults。Extend `gh run view --json` with `jobs` and add pure `Get-WakeReason(states, nowUtc, wakeAfterMinutes)`:

- completed runs never trigger timeout。
- queued/waiting or zero-job state continues waiting and never casts/cancels null `startedAt`。
- `wakeAfterMinutes == 0` disables timeout wake completely；an in-progress run continues waiting until terminal。
- only one `in_progress` job with non-null `startedAt` may be timed。
- only when `wakeAfterMinutes > 0`, elapsed below threshold continues waiting and elapsed at/above threshold returns `timeout:<run-id>`。
- unexpected job count or in-progress without `startedAt` returns a diagnostic wake reason, never a cancel。

When a wake reason exists, log it, use the already-reviewed exact Goal read/set reconciliation to set Goal active, and exit; the background script never cancels GitHub itself。`--SelfTest` uses synthetic states for completed, queued/no-job, in-progress with a non-null `startedAt` and zero threshold, in-progress below/at a positive threshold, missing startedAt, and multiple jobs。The zero-threshold case must return no wake reason。Run:

```powershell
$Heartbeat = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Heartbeat -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Heartbeat self-test failed' }
$Tokens = $null; $Errors = $null
[Management.Automation.Language.Parser]::ParseFile($Heartbeat, [ref]$Tokens, [ref]$Errors) | Out-Null
if ($Errors.Count) { throw ($Errors | Out-String) }
```

Request an independent read-only review of the modified local script before dispatch。Do not stage it. Actual launch commands are fully specified in Task 5。

---

### Task 5: Frozen remote witness, then conditional 200-repeat Stage 1

**Files:**
- Update locally only `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Archive under `D:\workspace\pyscf\.agents\archive\precision-ci\experiments\<run-id>-sgx-hse06-telemetry-*`

- [ ] **5.1 Re-establish context, verify, and push**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$ArchiveRoot = 'D:\workspace\pyscf\.agents\archive\precision-ci\experiments'
$Base = '37fc114e1c0519ea83197e81826afaa62d2aac89'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$Selection = '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
$NodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
Set-Location $Wt
$Head = (git rev-parse HEAD).Trim()
$State = Get-Content -Raw -Encoding utf8 $ActiveDoc
if ($State -notmatch 'stage1_head:\s*([0-9a-f]{40})') { throw 'Missing frozen Stage 1 head' }
$FrozenHead = $Matches[1]
if ($State -notmatch 'stage1_validator_sha256:\s*([0-9a-f]{64})') { throw 'Missing frozen validator SHA' }
$FrozenValidatorSha = $Matches[1]
if ($State -notmatch 'stage1_source_verdict:\s*SMOKE_PASS') { throw 'Source evidence did not pass its gate' }
$CurrentValidatorSha = (Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant()
if ($Head -ne $FrozenHead -or $CurrentValidatorSha -ne $FrozenValidatorSha) { throw 'Head or validator drifted after source validation' }

conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test
if ($LASTEXITCODE -ne 0) { throw 'Validator self-test failed' }
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  -q -p no:cacheprovider -c pytest.ini --rootdir . `
  .github/workflows/test_precision_investigation_contract.py
if ($LASTEXITCODE -ne 0) { throw 'Precision contract failed' }
git diff --check "$Base...$Head"
if ($LASTEXITCODE -ne 0) { throw 'Diff check failed' }
$Expected = @('.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt', '.github/workflows/test_precision_investigation_contract.py', 'pyscf/sgx/grad/test/test_rks.py')
$Actual = @(git diff --name-only "$Base...$Head")
if (@(Compare-Object $Expected $Actual).Count) { throw 'Scope mismatch' }
if ((git status --short --untracked-files=no)) { throw 'Tracked tree dirty' }
$Subjects = @(git log "$Base..$Head" --format='%s')
if ($Subjects.Count -ne 3 -or @($Subjects | Where-Object {-not $_.EndsWith('[skip ci]')}).Count) { throw 'Commit contract mismatch' }
gh auth status
if ($LASTEXITCODE -ne 0) { throw 'GitHub authentication failed' }
git push --set-upstream origin "HEAD:refs/heads/$Branch"
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
$Remote = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($Remote -ne $Head) { throw 'Remote SHA mismatch' }
```

- [ ] **5.2 Dispatch and identify the 1-repeat witness**

```powershell
$RunningRaw = @(gh run list --repo psiQAQ/pyscf --workflow ci-precision-check.yml --branch $Branch --event workflow_dispatch --limit 20 --json status)
if ($LASTEXITCODE -ne 0) { throw 'Failed to list active witness runs' }
$RunningParsed = ConvertFrom-Json -InputObject ($RunningRaw -join "`n") -ErrorAction Stop
$RunningRows = @($RunningParsed)
$Running = @($RunningRows | Where-Object {$_.status -in @('requested','queued','in_progress','waiting','pending')})
if ($Running.Count) { throw 'Duplicate active run' }
$BeforeRaw = @(gh run list --repo psiQAQ/pyscf --workflow ci-precision-check.yml --branch $Branch --event workflow_dispatch --limit 20 --json databaseId)
if ($LASTEXITCODE -ne 0) { throw 'Failed to list pre-dispatch witness runs' }
$BeforeParsed = ConvertFrom-Json -InputObject ($BeforeRaw -join "`n") -ErrorAction Stop
$Before = @($BeforeParsed)
$BeforeMax = if ($Before.Count) { [long](($Before | Measure-Object -Property databaseId -Maximum).Maximum) } else { [long]0 }
gh workflow run ci-precision-check.yml --repo psiQAQ/pyscf --ref $Branch `
  --raw-field nodeids_file=$Selection --raw-field repeats=1 `
  --raw-field platform=windows-latest --raw-field python_version=3.12 `
  --raw-field profile=4/1
if ($LASTEXITCODE -ne 0) { throw 'Dispatch failed' }
$Candidates = @()
for ($i=0; $i -lt 12; $i++) {
  $CandidateRaw = @(gh run list --repo psiQAQ/pyscf --workflow ci-precision-check.yml --branch $Branch --event workflow_dispatch --limit 10 --json databaseId,headSha,url)
  if ($LASTEXITCODE -ne 0) { throw 'Failed to list witness candidates' }
  $CandidateParsed = ConvertFrom-Json -InputObject ($CandidateRaw -join "`n") -ErrorAction Stop
  $CandidateRows = @($CandidateParsed)
  $Candidates = @($CandidateRows | Where-Object {[long]$_.databaseId -gt $BeforeMax -and $_.headSha -eq $Head})
  if ($Candidates.Count -eq 1) { break }
  if ($Candidates.Count -gt 1) { throw 'Ambiguous witness runs' }
  Start-Sleep -Seconds 5
}
if ($Candidates.Count -ne 1) { throw 'Witness not found in 60 seconds' }
$WitnessRunId = [long]$Candidates[0].databaseId
```

Use `apply_patch` to record `stage1_witness_run_id/head/branch/selection/inputs/artifact` in active doc. Create/update the sole heartbeat with:

```powershell
$Heartbeat = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$PowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$HeartbeatArgs = @(
  '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Heartbeat,
  '-TargetRunIds', [string]$WitnessRunId,
  '-TargetHeadSha', $Head,
  '-IntervalSeconds', '900',
  '-WakeAfterMinutes', '0'
)
$HeartbeatProcess = Start-Process -FilePath $PowerShell -ArgumentList $HeartbeatArgs `
  -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 2
if ($HeartbeatProcess.HasExited) { throw "Witness heartbeat exited early: $($HeartbeatProcess.ExitCode)" }
$HeartbeatCim = Get-CimInstance Win32_Process -Filter "ProcessId=$($HeartbeatProcess.Id)"
if ($HeartbeatCim.ExecutablePath -ne $PowerShell) { throw 'Heartbeat executable mismatch' }
```

Use `apply_patch` to record heartbeat PID, executable, arguments, 900-second interval, and run id in active doc。The script verifies Goal paused before polling, checks only `$WitnessRunId`, and exits after terminal state while verifying Goal active。Do not also run an app automation, another PS loop, or `gh run watch`。

- [ ] **5.3 Freeze/download/validate witness in a fresh shell**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$ArchiveRoot = 'D:\workspace\pyscf\.agents\archive\precision-ci\experiments'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$NodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
Set-Location $Wt
$Head = (git rev-parse HEAD).Trim()
$Text = Get-Content -Raw -Encoding utf8 $ActiveDoc
if ($Text -notmatch 'stage1_head:\s*([0-9a-f]{40})') { throw 'Missing frozen head' }
$FrozenHead = $Matches[1]
if ($Text -notmatch 'stage1_validator_sha256:\s*([0-9a-f]{64})') { throw 'Missing frozen validator SHA' }
$FrozenValidatorSha = $Matches[1]
if ($Text -notmatch 'stage1_source_verdict:\s*SMOKE_PASS') { throw 'Source gate missing' }
$CurrentValidatorSha = (Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant()
$RemoteHead = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($Head -ne $FrozenHead -or $Head -ne $RemoteHead -or $CurrentValidatorSha -ne $FrozenValidatorSha) { throw 'Head or validator drifted before witness validation' }
if ($Text -notmatch 'stage1_witness_run_id:\s*(\d+)') { throw 'Missing witness id' }
$RunId = [long]$Matches[1]
$RunRaw = @(gh run view $RunId --repo psiQAQ/pyscf --json attempt,event,headBranch,headSha,status,conclusion,workflowName,jobs,url)
if ($LASTEXITCODE -ne 0) { throw 'Failed to read witness run' }
$Run = ConvertFrom-Json -InputObject ($RunRaw -join "`n") -ErrorAction Stop
if ($Run.status -ne 'completed' -or $Run.attempt -ne 1 -or $Run.event -ne 'workflow_dispatch' -or $Run.headSha -ne $Head -or $Run.headBranch -ne $Branch -or $Run.workflowName -ne 'Precision investigation' -or @($Run.jobs).Count -ne 1) { throw 'Witness identity invalid' }
$A = @()
for ($i=0; $i -lt 12; $i++) {
  $ApiRaw = @(gh api "repos/psiQAQ/pyscf/actions/runs/$RunId/artifacts")
  if ($LASTEXITCODE -ne 0) { throw 'Failed to read witness artifacts' }
  $Api = ConvertFrom-Json -InputObject ($ApiRaw -join "`n") -ErrorAction Stop
  $A = @($Api.artifacts)
  if ($Api.total_count -gt 1 -or $A.Count -gt 1) { throw 'Multiple witness artifacts' }
  $ArtifactReady = $Api.total_count -eq 1 -and $A.Count -eq 1 -and `
    $A[0].name -eq 'precision-Windows-py3.12' -and -not $A[0].expired -and `
    $A[0].size_in_bytes -gt 0 -and $A[0].digest -match '^sha256:[0-9a-f]{64}$'
  if ($ArtifactReady) { break }
  Start-Sleep -Seconds 5
}
if ($Api.total_count -ne 1 -or $A.Count -ne 1 -or $A[0].name -ne 'precision-Windows-py3.12' -or $A[0].expired -or $A[0].size_in_bytes -le 0 -or $A[0].digest -notmatch '^sha256:[0-9a-f]{64}$') { throw 'Witness artifact invalid' }
$Dir = Join-Path $ArchiveRoot "$RunId-sgx-hse06-telemetry-stage1-witness-windows-py312"
if (Test-Path $Dir) { throw "Archive exists: $Dir" }
New-Item -ItemType Directory $Dir | Out-Null
$Job = @($Run.jobs)[0]
$Meta = [ordered]@{run_id=$RunId;run_attempt=$Run.attempt;event=$Run.event;workflow=$Run.workflowName;head_sha=$Run.headSha;head_branch=$Run.headBranch;status=$Run.status;conclusion=$Run.conclusion;job_count=@($Run.jobs).Count;job=[ordered]@{name=$Job.name;status=$Job.status;conclusion=$Job.conclusion};artifact_count=$Api.total_count;artifact=[ordered]@{id=$A[0].id;name=$A[0].name;digest=$A[0].digest;size_in_bytes=$A[0].size_in_bytes;expired=$A[0].expired}}
$Utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $Dir 'run-metadata.json'), ($Meta | ConvertTo-Json -Depth 5), $Utf8)
gh run download $RunId --repo psiQAQ/pyscf --name $A[0].name --dir $Dir
if ($LASTEXITCODE -ne 0) { throw 'Witness download failed' }
$Report = Join-Path $Dir 'telemetry-validation.json'
conda run --no-capture-output -n pyscf-win313-test python $Validator $Dir --mode installed-wheel --expected-sha $Head --expected-nodeid $NodeId --expected-profile omp4-blas1 --expected-repeats 1 --expected-native-count 26 --run-metadata (Join-Path $Dir 'run-metadata.json') --expected-run-id $RunId --expected-branch $Branch --report $Report
if ($LASTEXITCODE -ne 0) { throw 'Witness INVALID' }
$V = Get-Content -Raw -Encoding utf8 $Report | ConvertFrom-Json -ErrorAction Stop
Copy-Item $Validator (Join-Path $Dir 'validate_sgx_hse06_telemetry.py')
$ArchivedValidator = Join-Path $Dir 'validate_sgx_hse06_telemetry.py'
if ((Get-FileHash $ArchivedValidator).Hash.ToLowerInvariant() -ne $V.validator_sha256) { throw 'Validator SHA mismatch' }
```

Use `apply_patch` to record `stage1_witness_verdict: $V.verdict`, `stage1_witness_head: $Head`, `stage1_witness_validator_sha256: $V.validator_sha256`, counts, first finding, run id, artifact id/digest/size, and report path in active doc。If verdict is not `SMOKE_PASS`, retain the valid evidence and stop cleanly before 5.4; do not throw it as a pipeline error and do not rerun。

- [ ] **5.4 Dispatch and identify 200-repeat run**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$Selection = '.github/workflows/precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
Set-Location $Wt
$Head = (git rev-parse HEAD).Trim()
$State = Get-Content -Raw -Encoding utf8 $ActiveDoc
if ($State -notmatch 'stage1_head:\s*([0-9a-f]{40})') { throw 'Missing frozen head' }
$FrozenHead = $Matches[1]
if ($State -notmatch 'stage1_validator_sha256:\s*([0-9a-f]{64})') { throw 'Missing frozen validator SHA' }
$FrozenValidatorSha = $Matches[1]
if ($State -notmatch 'stage1_source_verdict:\s*SMOKE_PASS') { throw 'Source gate missing' }
if ($State -notmatch 'stage1_witness_verdict:\s*SMOKE_PASS') { throw 'Witness was not validated' }
if ($State -notmatch 'stage1_witness_head:\s*([0-9a-f]{40})') { throw 'Missing witness head' }
$WitnessHead = $Matches[1]
if ($State -notmatch 'stage1_witness_validator_sha256:\s*([0-9a-f]{64})') { throw 'Missing witness validator SHA' }
$WitnessValidatorSha = $Matches[1]
$CurrentValidatorSha = (Get-FileHash -Algorithm SHA256 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py').Hash.ToLowerInvariant()
$RemoteHead = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($Head -ne $FrozenHead -or $Head -ne $WitnessHead -or $Head -ne $RemoteHead -or $CurrentValidatorSha -ne $FrozenValidatorSha -or $CurrentValidatorSha -ne $WitnessValidatorSha) { throw 'Head or validator drifted after witness' }
$RunningRaw = @(gh run list --repo psiQAQ/pyscf --workflow ci-precision-check.yml --branch $Branch --event workflow_dispatch --limit 20 --json status)
if ($LASTEXITCODE -ne 0) { throw 'Failed to list active formal runs' }
$RunningParsed = ConvertFrom-Json -InputObject ($RunningRaw -join "`n") -ErrorAction Stop
$RunningRows = @($RunningParsed)
$Running = @($RunningRows | Where-Object {$_.status -in @('requested','queued','in_progress','waiting','pending')})
if ($Running.Count) { throw 'Duplicate active run' }
$BeforeRaw = @(gh run list --repo psiQAQ/pyscf --workflow ci-precision-check.yml --branch $Branch --event workflow_dispatch --limit 20 --json databaseId)
if ($LASTEXITCODE -ne 0) { throw 'Failed to list pre-dispatch formal runs' }
$BeforeParsed = ConvertFrom-Json -InputObject ($BeforeRaw -join "`n") -ErrorAction Stop
$Before = @($BeforeParsed)
$BeforeMax = if ($Before.Count) { [long](($Before | Measure-Object -Property databaseId -Maximum).Maximum) } else { [long]0 }
gh workflow run ci-precision-check.yml --repo psiQAQ/pyscf --ref $Branch `
  --raw-field nodeids_file=$Selection --raw-field repeats=200 `
  --raw-field platform=windows-latest --raw-field python_version=3.12 `
  --raw-field profile=4/1
if ($LASTEXITCODE -ne 0) { throw 'Dispatch failed' }
$Candidates = @()
for ($i=0; $i -lt 12; $i++) {
  $CandidateRaw = @(gh run list --repo psiQAQ/pyscf --workflow ci-precision-check.yml --branch $Branch --event workflow_dispatch --limit 10 --json databaseId,headSha,url)
  if ($LASTEXITCODE -ne 0) { throw 'Failed to list formal candidates' }
  $CandidateParsed = ConvertFrom-Json -InputObject ($CandidateRaw -join "`n") -ErrorAction Stop
  $CandidateRows = @($CandidateParsed)
  $Candidates = @($CandidateRows | Where-Object {[long]$_.databaseId -gt $BeforeMax -and $_.headSha -eq $Head})
  if ($Candidates.Count -eq 1) { break }
  if ($Candidates.Count -gt 1) { throw 'Ambiguous formal runs' }
  Start-Sleep -Seconds 5
}
if ($Candidates.Count -ne 1) { throw 'Formal run not found in 60 seconds' }
$RunId = [long]$Candidates[0].databaseId
```

Use `apply_patch` to write `$RunId` as `stage1_run_id` plus head/branch/selection/inputs/artifact in active doc。

```powershell
$Heartbeat = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$PowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$HeartbeatArgs = @(
  '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Heartbeat,
  '-TargetRunIds', [string]$RunId,
  '-TargetHeadSha', $Head,
  '-IntervalSeconds', '1800',
  '-WakeAfterMinutes', '300'
)
$HeartbeatProcess = Start-Process -FilePath $PowerShell -ArgumentList $HeartbeatArgs `
  -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 2
if ($HeartbeatProcess.HasExited) { throw "Formal heartbeat exited early: $($HeartbeatProcess.ExitCode)" }
$HeartbeatCim = Get-CimInstance Win32_Process -Filter "ProcessId=$($HeartbeatProcess.Id)"
if ($HeartbeatCim.ExecutablePath -ne $PowerShell) { throw 'Heartbeat executable mismatch' }
```

Use `apply_patch` to record heartbeat PID, executable, arguments, 1800-second interval, 300-minute wake gate, and run id。The script wakes the Goal on either terminal state or the precise in-progress threshold, then exits and releases its mutex。Do not run any second monitor。

- [ ] **5.5 Freeze/download/validate formal artifact in a fresh shell**

```powershell
$Wt = 'D:\workspace\pyscf\.worktrees\libxc-712-sgx-extra-cycle-telemetry'
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_sgx_hse06_telemetry.py'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$ArchiveRoot = 'D:\workspace\pyscf\.agents\archive\precision-ci\experiments'
$Branch = 'codex/investigate/libxc-712-sgx-extra-cycle-telemetry'
$NodeId = 'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad_settings2_hse06_telemetry'
Set-Location $Wt
$Head = (git rev-parse HEAD).Trim()
$Text = Get-Content -Raw -Encoding utf8 $ActiveDoc
if ($Text -notmatch 'stage1_head:\s*([0-9a-f]{40})') { throw 'Missing frozen head' }
$FrozenHead = $Matches[1]
if ($Text -notmatch 'stage1_validator_sha256:\s*([0-9a-f]{64})') { throw 'Missing frozen validator SHA' }
$FrozenValidatorSha = $Matches[1]
if ($Text -notmatch 'stage1_witness_verdict:\s*SMOKE_PASS') { throw 'Witness gate missing' }
if ($Text -notmatch 'stage1_witness_head:\s*([0-9a-f]{40})') { throw 'Missing witness head' }
$WitnessHead = $Matches[1]
if ($Text -notmatch 'stage1_witness_validator_sha256:\s*([0-9a-f]{64})') { throw 'Missing witness validator SHA' }
$WitnessValidatorSha = $Matches[1]
$CurrentValidatorSha = (Get-FileHash -Algorithm SHA256 $Validator).Hash.ToLowerInvariant()
$RemoteHead = ((git ls-remote origin "refs/heads/$Branch") -split '\s+')[0]
if ($Head -ne $FrozenHead -or $Head -ne $WitnessHead -or $Head -ne $RemoteHead -or $CurrentValidatorSha -ne $FrozenValidatorSha -or $CurrentValidatorSha -ne $WitnessValidatorSha) { throw 'Head or validator drifted before formal validation' }
if ($Text -notmatch 'stage1_run_id:\s*(\d+)') { throw 'Missing formal run id' }
$RunId = [long]$Matches[1]
$SnapshotRaw = @(gh run view $RunId --repo psiQAQ/pyscf --json status,jobs)
if ($LASTEXITCODE -ne 0) { throw 'Failed to read formal run state' }
$Snapshot = ConvertFrom-Json -InputObject ($SnapshotRaw -join "`n") -ErrorAction Stop
if ($Snapshot.status -ne 'completed') {
  $Jobs = @($Snapshot.jobs)
  if ($Jobs.Count -ne 1 -or $Jobs[0].status -ne 'in_progress' -or [string]::IsNullOrWhiteSpace([string]$Jobs[0].startedAt)) {
    throw 'Heartbeat woke on a nonterminal state without a valid timeout; do not cancel'
  }
  $ElapsedMinutes = ((Get-Date).ToUniversalTime() - ([datetime]$Jobs[0].startedAt).ToUniversalTime()).TotalMinutes
  if ($ElapsedMinutes -lt 300) { throw 'Heartbeat woke before the 300-minute gate; do not cancel' }
  gh run cancel $RunId --repo psiQAQ/pyscf
  if ($LASTEXITCODE -ne 0) { throw 'Formal timeout cancel failed' }
  Write-Output 'FORMAL_TIMEOUT_CANCELLED'
  return
}
$RunRaw = @(gh run view $RunId --repo psiQAQ/pyscf --json attempt,event,headBranch,headSha,status,conclusion,workflowName,jobs,url)
if ($LASTEXITCODE -ne 0) { throw 'Failed to read formal run' }
$Run = ConvertFrom-Json -InputObject ($RunRaw -join "`n") -ErrorAction Stop
if ($Run.status -ne 'completed' -or $Run.attempt -ne 1 -or $Run.event -ne 'workflow_dispatch' -or $Run.headSha -ne $Head -or $Run.headBranch -ne $Branch -or $Run.workflowName -ne 'Precision investigation' -or @($Run.jobs).Count -ne 1) { throw 'Formal run identity invalid' }
$A = @()
for ($i=0; $i -lt 12; $i++) {
  $ApiRaw = @(gh api "repos/psiQAQ/pyscf/actions/runs/$RunId/artifacts")
  if ($LASTEXITCODE -ne 0) { throw 'Failed to read formal artifacts' }
  $Api = ConvertFrom-Json -InputObject ($ApiRaw -join "`n") -ErrorAction Stop
  $A = @($Api.artifacts)
  if ($Api.total_count -gt 1 -or $A.Count -gt 1) { throw 'Multiple formal artifacts' }
  $ArtifactReady = $Api.total_count -eq 1 -and $A.Count -eq 1 -and `
    $A[0].name -eq 'precision-Windows-py3.12' -and -not $A[0].expired -and `
    $A[0].size_in_bytes -gt 0 -and $A[0].digest -match '^sha256:[0-9a-f]{64}$'
  if ($ArtifactReady) { break }
  Start-Sleep -Seconds 5
}
if ($Api.total_count -ne 1 -or $A.Count -ne 1 -or $A[0].name -ne 'precision-Windows-py3.12' -or $A[0].expired -or $A[0].size_in_bytes -le 0 -or $A[0].digest -notmatch '^sha256:[0-9a-f]{64}$') { throw 'Formal artifact invalid' }
$Dir = Join-Path $ArchiveRoot "$RunId-sgx-hse06-telemetry-stage1-windows-py312"
if (Test-Path $Dir) { throw "Archive exists: $Dir" }
New-Item -ItemType Directory $Dir | Out-Null
$Job = @($Run.jobs)[0]
$Meta = [ordered]@{run_id=$RunId;run_attempt=$Run.attempt;event=$Run.event;workflow=$Run.workflowName;head_sha=$Run.headSha;head_branch=$Run.headBranch;status=$Run.status;conclusion=$Run.conclusion;job_count=@($Run.jobs).Count;job=[ordered]@{name=$Job.name;status=$Job.status;conclusion=$Job.conclusion};artifact_count=$Api.total_count;artifact=[ordered]@{id=$A[0].id;name=$A[0].name;digest=$A[0].digest;size_in_bytes=$A[0].size_in_bytes;expired=$A[0].expired}}
$Utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $Dir 'run-metadata.json'), ($Meta | ConvertTo-Json -Depth 5), $Utf8)
gh run download $RunId --repo psiQAQ/pyscf --name $A[0].name --dir $Dir
if ($LASTEXITCODE -ne 0) { throw 'Formal download failed' }
$Report = Join-Path $Dir 'telemetry-validation.json'
conda run --no-capture-output -n pyscf-win313-test python $Validator $Dir --mode installed-wheel --expected-sha $Head --expected-nodeid $NodeId --expected-profile omp4-blas1 --expected-repeats 200 --expected-native-count 26 --run-metadata (Join-Path $Dir 'run-metadata.json') --expected-run-id $RunId --expected-branch $Branch --report $Report
$ValidatorExit = $LASTEXITCODE
$V = Get-Content -Raw -Encoding utf8 $Report | ConvertFrom-Json -ErrorAction Stop
Copy-Item $Validator (Join-Path $Dir 'validate_sgx_hse06_telemetry.py')
$ArchivedValidator = Join-Path $Dir 'validate_sgx_hse06_telemetry.py'
if ((Get-FileHash $ArchivedValidator).Hash.ToLowerInvariant() -ne $V.validator_sha256) { throw 'Validator SHA mismatch' }
if ($ValidatorExit -ne 0 -or -not $V.valid) { throw 'Formal evidence INVALID' }
```

If the preflight prints `FORMAL_TIMEOUT_CANCELLED`, use `apply_patch` to record elapsed time and timing/infrastructure `INVALID`, then stop without artifact validation or rerun。Otherwise continue with the terminal artifact commands。Do not rerun over a first scientific failure。

Use `apply_patch` to record run/artifact ids, digest, validator SHA, counts, verdict, first finding, and next command in active doc. Stop rules:

- `INVALID`: repair experiment/evidence contract only。
- `REPRODUCED_OTHER_ASSERTION`: retain evidence; no Extra-cycle conclusion。
- `INCONCLUSIVE_NONCONVERGED`: retain evidence; no confirm/falsify and no Stage 2。
- `MECHANISM_CONFIRMED`: stop; later derive minimal RED/GREEN fix/test from live upstream master。
- `MECHANISM_FALSIFIED`: stop; design the next smallest density/Fock/`veff` boundary probe。
- `NOT_REPRODUCED`: write `Stage 1 0/200, NOT_REPRODUCED/HOLD`; invoke `superpowers:writing-plans` for a separate Stage 2 plan。

---

## Final verification

- [ ] Exactly 3 `[skip ci]` commits and 3 allowed paths relative to approved base。
- [ ] Original nine-case parameters/order/assertions unchanged; diagnostic attempt emits exactly one marker。
- [ ] Validator self-tests pass; source is `SMOKE_PASS`; each archive stores validator copy/hash。
- [ ] Frozen remote 1-repeat installed-wheel witness passes before the only 200-repeat run is dispatched。
- [ ] Run/head/job and unique artifact id/name/digest/size/expiry are frozen before download。
- [ ] Validator automatically checks all records/CSV/logs/runtime/DLL/pip/schema/formulas/nonconvergence; valid scientific failure remains valid evidence。
- [ ] Exactly one 15/30-minute heartbeat while waiting; exact 300-minute cancel gate。
- [ ] No PR, no complete matrix, no Stage 2 code, and no PASS/FIXED claim from `0/200`。
