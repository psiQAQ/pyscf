# SGX Extra-cycle Convergence Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 以通用 rejected-Extra-cycle continuation 和 SGX energy-and-gradient convergence 两个独立上游提交，修复原 SGX finite-difference nodeid 的偶发失败，并完成三个 LibXC 相关 nodeid 的 installed-wheel 正式矩阵与 `pyscf/pyscf#3312` 证据闭环。

**Architecture:** 通用 `SCF.kernel()` 负责在 Extra cycle 被拒绝后保留物理 density/Fock 并继续循环；`_SGXHF.check_convergence()` 只负责 SGX 的 AND predicate。两个 production branch 都从执行时实时 upstream master 创建，validation branch 再叠加两者及既有 precision CI 基础设施，诊断代码不进入上游 PR。

**Tech Stack:** Python 3、unittest/pytest、PySCF SCF/SGX、Windows PowerShell 5.1、Git/Git worktree、GitHub Actions/`gh`、本地标准库 evidence validator。

## Global Constraints

- Approved spec: `docs/superpowers/specs/2026-08-11-sgx-extra-cycle-convergence-production-design.md` at commit `0e4e1b60fdca7fd87ef9357a95146c80ead04072`, SHA-256 `8024398188669599f046a6c692582c71f3287d8da84d2367df5d243dda59e883`.
- Confirmed mechanism evidence: run `31455915215`, artifact `9089592334`, attempt 65, verdict `MECHANISM_CONFIRMED`; this evidence is immutable.
- Live baseline when the spec was approved: `pyscf/pyscf:master@aa2ad20897104dead09d53fc532a5d3b34203d83`.
- Before implementation, fetch live upstream. If any target-file blob differs from the frozen hashes below, stop and amend/reapprove the spec rather than guessing:

| File | Approved-baseline blob |
| --- | --- |
| `pyscf/scf/hf.py` | `fee8d2b3a88b212612842fffc043e9217a205b14` |
| `pyscf/scf/smearing.py` | `9026181054c1f414c7fb44ec1953716cde9a5cdf` |
| `pyscf/scf/test/test_addons.py` | `d36824f6cc4ad4fead905d162504ad2c61b43988` |
| `pyscf/sgx/sgx.py` | `887783e0e0856cf587fe33c647ba8ee97e151f1a` |
| `pyscf/sgx/test/test_sgx.py` | `dba0f1b0d8b59c255abd0c007c830c3824553e2f` |
| `pyscf/sgx/grad/test/test_rks.py` | `22212fa30100b9d8bb97848178e36e32276176f4` |

- Do not install or upgrade dependencies. Reuse `conda` environment `pyscf-win313-test` and existing 26-DLL LibXC 7.1.2 fixture.
- Preserve original `test_finite_diff_grad`: nine calls/order, `delta=1e-4`, `conv_tol=1e-12`, `conv_check=True`, translation places 12, finite-difference places 6.
- Do not add retries, change `max_cycle`, relax assertions, disable `conv_check`, or change LibXC/runtime packaging.
- Production commits must contain no telemetry prefix, diagnostic selection, validator, workflow, artifact parser, or dependency change.
- Use `apply_patch` for source/document edits. Preserve existing encoding/EOL; do not restage whole mixed-EOL files.
- Run every RED before its GREEN implementation. A failure outside the expected assertion/signature is a blocker, not an acceptable RED.
- Every commit gets a fresh spec-compliance review and code-quality review before the next production task.
- Validation branch pushes and workflow dispatches are within the approved investigation goal. Rewriting PR #3331, creating the SGX PR, or editing issue #3312 requires the explicit checkpoint written in the relevant task.
- While CI is the only remaining work, use exactly one reviewed heartbeat: `.agents/active/libxc-712-ci-heartbeat.ps1`, SHA-256 `4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639`, `-IntervalSeconds 1800`. Do not combine it with native automation, `gh run watch`, another PS1, or manual background polling.
- Every heartbeat handoff must re-run its 18-case `-SelfTest`, prove no matching PS1 or active native scheduler exists, capture and verify the exact PID/executable/command-line run IDs/head, and independently read back Goal `paused`. On wake, require that PID gone and Goal `active` before CI validation. These checks apply equally to single-run and encoded multi-run launches.
- A green Actions conclusion is not a scientific verdict. Validate run/job/artifact identity, records, logs, summary, runtime, import mode, LibXC 7.1.2, pip-check semantics, platform-native linkage (including 26 wheel DLLs on Windows) and tested SHA.
- A structurally valid scientific failure is preserved as `SCIENTIFIC_FAILURE`; only evidence/provenance corruption is `INVALID`.
- Every remote dispatch is guarded by an immutable UTF-8-no-BOM `FileMode.CreateNew` journal written and flushed before `gh workflow run`. An existing journal always routes to ID recovery and never to redispatch. If the native dispatch command fails, retain the journal; delete it and retry only after exact `databaseId > before_max` queries prove that no run was created and the user approves that one scoped retry.

## File Map

### Generic production branch

- Modify `pyscf/scf/hf.py`: rejected Extra-cycle continuation and immutable relaxed environment.
- Modify `pyscf/scf/smearing.py`: active-smearing AND predicate, existing non-smearing fallback.
- Modify `pyscf/scf/test/test_addons.py`: deterministic continuation RED and smearing predicate table.

### SGX production branch

- Modify `pyscf/sgx/sgx.py`: `_SGXHF.check_convergence(envs)`.
- Modify `pyscf/sgx/test/test_sgx.py`: attempt-65 predicate table and instance-override regression.
- Do not modify `pyscf/sgx/grad/test/test_rks.py`; its blob is an end-to-end guard.

### Validation-only branch/local evidence

- Create `.github/workflows/precision-sgx-extra-cycle-production-nodeids.txt`: one original SGX nodeid.
- Create `.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt`: one original UHF-smearing nodeid.
- Reuse `.github/workflows/precision-libxc-712-nodeids.txt`: the three final LibXC nodeids.
- Create ignored `.agents/active/precision-ci/scripts/validate_precision_production.py`: no-diagnostic production artifact validator.
- Update `.agents/active/libxc-712-release-revalidation.md` and `.agents/active/precision-stability.md` after each evidence-changing gate.

---

### Task 1: Implement Generic Rejected-Extra-cycle Continuation

**Files:**
- Modify: `pyscf/scf/hf.py:190-245`
- Modify/Test: `pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing`

**Interfaces:**
- Consumes: existing `SCF.check_convergence(envs) -> bool`, `conv_check`, `fock_last`, main-loop density/Fock state.
- Produces: internal `extra_cycle: bool` environment key; a rejected Extra cycle resumes the next main iteration from its physical state.

- [ ] **Step 1: Freeze live upstream and create the generic worktree**

Use `superpowers:using-git-worktrees`. Run in a fresh Windows PowerShell 5.1 shell:

```powershell
$ErrorActionPreference = 'Stop'
$Root = 'D:\workspace\pyscf'
$Worktree = 'D:\workspace\pyscf\.worktrees\uhf-smearing-convergence-v2'
$Branch = 'codex/fix/uhf-smearing-convergence-v2'
$Remote = 'https://github.com/pyscf/pyscf.git'
$ActiveDoc = "$Root\.agents\active\libxc-712-release-revalidation.md"

git -c safe.directory=$Root -C $Root fetch $Remote `
  '+refs/heads/master:refs/remotes/pyscf-upstream/master'
if ($LASTEXITCODE -ne 0) { throw 'upstream fetch failed' }
$Upstream = (git -c safe.directory=$Root -C $Root rev-parse refs/remotes/pyscf-upstream/master).Trim()
if ($Upstream -notmatch '^[0-9a-f]{40}$') { throw "Invalid upstream SHA: $Upstream" }

$Expected = [ordered]@{
  'pyscf/scf/hf.py' = 'fee8d2b3a88b212612842fffc043e9217a205b14'
  'pyscf/scf/smearing.py' = '9026181054c1f414c7fb44ec1953716cde9a5cdf'
  'pyscf/scf/test/test_addons.py' = 'd36824f6cc4ad4fead905d162504ad2c61b43988'
  'pyscf/sgx/sgx.py' = '887783e0e0856cf587fe33c647ba8ee97e151f1a'
  'pyscf/sgx/test/test_sgx.py' = 'dba0f1b0d8b59c255abd0c007c830c3824553e2f'
  'pyscf/sgx/grad/test/test_rks.py' = '22212fa30100b9d8bb97848178e36e32276176f4'
}
foreach ($Entry in $Expected.GetEnumerator()) {
  $Actual = (git -c safe.directory=$Root -C $Root rev-parse "$Upstream`:$($Entry.Key)").Trim()
  if ($Actual -ne $Entry.Value) {
    throw "Approved target changed: $($Entry.Key) expected $($Entry.Value), got $Actual"
  }
}
if (Test-Path -LiteralPath $Worktree) { throw "Worktree path exists: $Worktree" }
git -c safe.directory=$Root -C $Root show-ref --verify --quiet "refs/heads/$Branch"
if ($LASTEXITCODE -eq 0) { throw "Branch exists: $Branch" }
git -c safe.directory=$Root -C $Root worktree add -b $Branch $Worktree $Upstream
if ($LASTEXITCODE -ne 0) { throw 'worktree add failed' }
git -c safe.directory=$Worktree -C $Worktree status --short --branch
```

Use `apply_patch` to record `production_fix_upstream_sha`, worktree and branch in the active document. Do not continue if the target blobs changed.

- [ ] **Step 2: Add the deterministic continuation RED**

Append this block at the end of `test_uhf_smearing`, after the existing `mu` energy/entropy assertions:

```python
        extra_checks = 0
        rejected_extra_energy = None
        continued_from_rejected_extra = False

        def reject_first_extra(envs):
            nonlocal extra_checks
            nonlocal rejected_extra_energy
            nonlocal continued_from_rejected_extra
            energy_converged = (
                abs(envs['e_tot'] - envs['last_hf_e']) < envs['conv_tol'])
            gradient_converged = envs['norm_gorb'] < envs['conv_tol_grad']
            is_extra = envs.get(
                'extra_cycle', envs['conv_tol'] > myhf_s.conv_tol)
            if rejected_extra_energy is not None and not is_extra:
                continued_from_rejected_extra = (
                    abs(envs['last_hf_e'] - rejected_extra_energy) < 1e-12)
            if is_extra:
                extra_checks += 1
                if extra_checks == 1:
                    rejected_extra_energy = envs['e_tot']
                    return False
            return energy_converged and gradient_converged

        myhf_s.check_convergence = reject_first_extra
        myhf_s.kernel(dm0=myhf_s.make_rdm1())
        with self.subTest('rejected extra cycle resumes SCF'):
            self.assertGreaterEqual(extra_checks, 2)
            self.assertTrue(continued_from_rejected_extra)
            self.assertTrue(myhf_s.converged)
```

- [ ] **Step 3: Run the RED and preserve its exact signature**

```powershell
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:BLIS_NUM_THREADS = '1'
$env:VECLIB_MAXIMUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'
Set-Location 'D:\workspace\pyscf\.worktrees\uhf-smearing-convergence-v2'
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing -c pytest.ini -vv
```

Expected: pytest exits nonzero because the current driver observes only one rejected Extra check and returns without the required continuation. A dependency/import/allocation failure is not the intended RED.

- [ ] **Step 4: Implement the minimal driver continuation**

Modify `hf.kernel()` so the main convergence block and Extra cycle follow this exact structure:

```python
        extra_cycle = False
        if callable(mf.check_convergence):
            scf_conv = mf.check_convergence(locals())
        elif abs(e_tot-last_hf_e) < conv_tol and norm_gorb < conv_tol_grad:
            scf_conv = True

        if dump_chk and mf.chkfile:
            mf.dump_chk(locals())

        if callable(callback):
            callback(locals())

        cput1 = log.timer('cycle= %d'%(cycle+1), *cput1)

        if not scf_conv:
            continue
        if not conv_check:
            break

        extra_cycle = True
        # An extra diagonalization, to remove level shift
        #fock = mf.get_fock(h1e, s1e, vhf, dm)  # = h1e + vhf
        mo_energy, mo_coeff = mf.eig(fock, s1e, x=x_orth)
        mo_occ = mf.get_occ(mo_energy, mo_coeff)
        dm, dm_last = mf.make_rdm1(mo_coeff, mo_occ), dm
        vhf = mf.get_veff(mol, dm, dm_last, vhf)
        e_tot, last_hf_e = mf.energy_tot(dm, h1e, vhf), e_tot

        fock = mf.get_fock(h1e, s1e, vhf, dm, level_shift_factor=0)
        norm_gorb = numpy.linalg.norm(mf.get_grad(mo_coeff, mo_occ, fock))
        if not TIGHT_GRAD_CONV_TOL:
            norm_gorb = norm_gorb / numpy.sqrt(norm_gorb.size)
        norm_ddm = numpy.linalg.norm(dm-dm_last)

        extra_envs = dict(locals(),
                          conv_tol=conv_tol * 10,
                          conv_tol_grad=conv_tol_grad * 3)
        if callable(mf.check_convergence):
            scf_conv = mf.check_convergence(extra_envs)
        elif (abs(e_tot-last_hf_e) < extra_envs['conv_tol'] or
              norm_gorb < extra_envs['conv_tol_grad']):
            scf_conv = True
        else:
            scf_conv = False
        extra_envs['scf_conv'] = scf_conv
        log.info('Extra cycle  E= %.15g  delta_E= %4.3g  |g|= %4.3g  |ddm|= %4.3g',
                 e_tot, e_tot-last_hf_e, norm_gorb, norm_ddm)
        if dump_chk and mf.chkfile:
            mf.dump_chk(extra_envs)
        if scf_conv:
            break
        # Continue from the physical-Fock density rejected by the extra check.
        fock_last = fock

    mf.cycles = cycle + 1
```

Move the existing Extra-cycle calculation inside the `for cycle` loop; do not duplicate it. Do not mutate `conv_tol` or `conv_tol_grad` in place. Do not add an Extra-cycle callback or intermediate `post_kernel()` call.

- [ ] **Step 5: Run GREEN and focused generic regressions**

```powershell
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing -c pytest.ini -vv
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/scf/test/test_h2o.py pyscf/scf/test/test_he.py -c pytest.ini -q
```

Expected: all commands exit 0; continuation assertions prove at least two Extra checks and state continuity.

- [ ] **Step 6: Verify and commit Task 1**

```powershell
$Worktree = 'D:\workspace\pyscf\.worktrees\uhf-smearing-convergence-v2'
git -c safe.directory=$Worktree -C $Worktree diff --check
git -c safe.directory=$Worktree -C $Worktree diff --name-only
git -c safe.directory=$Worktree -C $Worktree add -- `
  pyscf/scf/hf.py pyscf/scf/test/test_addons.py
git -c safe.directory=$Worktree -C $Worktree diff --cached --check
git -c safe.directory=$Worktree -C $Worktree commit -m `
  'fix(scf): continue after rejected extra cycles'
```

Expected staged scope: exactly `hf.py` and `test_addons.py`. Record the exact commit in the active document with `apply_patch`.

---

### Task 2: Add the Smearing-specific Convergence Predicate

**Files:**
- Modify: `pyscf/scf/smearing.py:130-165`
- Modify/Test: `pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing`

**Interfaces:**
- Consumes: Task 1 `extra_cycle` environment and relaxed thresholds.
- Produces: `_SmearingSCF.check_convergence(envs) -> bool`.

- [ ] **Step 1: Add the smearing predicate RED**

Before the Task 1 continuation block in `test_uhf_smearing`, add:

```python
        observed_extra = {
            'e_tot': -243.086993624352,
            'last_hf_e': -243.086988432792,
            'conv_tol': 1e-6,
            'norm_gorb': 1.08e-5,
            'conv_tol_grad': 3 * numpy.sqrt(1e-7),
            'extra_cycle': True,
        }
        with self.subTest('active smearing requires stable energy'):
            self.assertTrue(callable(myhf_s.check_convergence))
            self.assertFalse(myhf_s.check_convergence(observed_extra))

        saved_sigma = myhf_s.sigma
        try:
            myhf_s.sigma = 0
            with self.subTest('inactive smearing keeps extra-cycle OR'):
                self.assertTrue(myhf_s.check_convergence(observed_extra))
            main_envs = dict(observed_extra, extra_cycle=False)
            with self.subTest('inactive smearing keeps main-cycle AND'):
                self.assertFalse(myhf_s.check_convergence(main_envs))
        finally:
            myhf_s.sigma = saved_sigma
```

The inactive-smearing `extra_cycle=True` subtest is the explicit regression for
the generic relaxed Extra-cycle OR fallback; the adjacent main-cycle case locks
the generic AND rule. Do not replace these with an assertion on copied formula
text.

- [ ] **Step 2: Run the predicate RED**

Run the exact Task 1 target command. Expected: nonzero because `myhf_s.check_convergence` is not callable before `_SmearingSCF` implements the method. The Task 1 continuation assertions must not be the first failure.

- [ ] **Step 3: Implement `_SmearingSCF.check_convergence`**

Add immediately after `undo_smearing()`:

```python
    def check_convergence(self, envs):
        energy_converged = (
            abs(envs['e_tot'] - envs['last_hf_e']) < envs['conv_tol'])
        gradient_converged = envs['norm_gorb'] < envs['conv_tol_grad']
        if self.sigma and self.smearing_method:
            # Fractional occupations can change the density while the orbital
            # gradient alone is small.
            return energy_converged and gradient_converged
        if envs.get('extra_cycle', False):
            return energy_converged or gradient_converged
        return energy_converged and gradient_converged
```

- [ ] **Step 4: Run GREEN and commit Task 2**

Run the Task 1 focused commands again. Then:

```powershell
$Worktree = 'D:\workspace\pyscf\.worktrees\uhf-smearing-convergence-v2'
git -c safe.directory=$Worktree -C $Worktree diff --check
git -c safe.directory=$Worktree -C $Worktree add -- `
  pyscf/scf/smearing.py pyscf/scf/test/test_addons.py
git -c safe.directory=$Worktree -C $Worktree diff --cached --check
git -c safe.directory=$Worktree -C $Worktree commit -m `
  'fix(scf): require stable energy for smeared SCF'
```

Record both generic commit SHAs and the branch head in the active document. Run a fresh spec-compliance review and code-quality review; any finding is fixed and reverified before Task 3.

---

### Task 3: Add the SGX Energy-and-gradient Predicate

**Files:**
- Modify: `pyscf/sgx/sgx.py::_SGXHF`
- Modify/Test: `pyscf/sgx/test/test_sgx.py::KnownValues`
- Guard only: `pyscf/sgx/grad/test/test_rks.py`

**Interfaces:**
- Consumes: `check_convergence(envs)` hook API and Task 1 relaxed environment.
- Produces: `_SGXHF.check_convergence(envs) -> bool`; instance callables still shadow it.

- [ ] **Step 1: Create the independent SGX worktree from the same frozen upstream**

Read `production_fix_upstream_sha` from the active document and require a single 40-hex match. Create:

```text
D:\workspace\pyscf\.worktrees\sgx-extra-cycle-convergence
codex/fix/sgx-extra-cycle-convergence
```

Use `git worktree add -b` from that exact upstream SHA. Refuse an existing path or branch. Recheck all three SGX baseline blobs before editing.

```powershell
$ErrorActionPreference = 'Stop'
$Root = 'D:\workspace\pyscf'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-convergence'
$Branch = 'codex/fix/sgx-extra-cycle-convergence'
$ActiveDoc = "$Root\.agents\active\libxc-712-release-revalidation.md"
$Text = [IO.File]::ReadAllText($ActiveDoc, [Text.UTF8Encoding]::new($false))
$Matches = [regex]::Matches(
  $Text, '(?m)^- production_fix_upstream_sha: `([0-9a-f]{40})`$')
if ($Matches.Count -ne 1) { throw 'Expected one production_fix_upstream_sha' }
$Upstream = $Matches[0].Groups[1].Value
if (Test-Path -LiteralPath $Worktree) { throw "Worktree path exists: $Worktree" }
git -c safe.directory=$Root -C $Root show-ref --verify --quiet "refs/heads/$Branch"
if ($LASTEXITCODE -eq 0) { throw "Branch exists: $Branch" }
foreach ($Entry in @(
  @('pyscf/sgx/sgx.py', '887783e0e0856cf587fe33c647ba8ee97e151f1a'),
  @('pyscf/sgx/test/test_sgx.py', 'dba0f1b0d8b59c255abd0c007c830c3824553e2f'),
  @('pyscf/sgx/grad/test/test_rks.py', '22212fa30100b9d8bb97848178e36e32276176f4')
)) {
  $Actual = (git -c safe.directory=$Root -C $Root rev-parse `
    "$Upstream`:$($Entry[0])").Trim()
  if ($Actual -ne $Entry[1]) { throw "SGX baseline changed: $($Entry[0])" }
}
git -c safe.directory=$Root -C $Root worktree add -b $Branch $Worktree $Upstream
if ($LASTEXITCODE -ne 0) { throw 'SGX worktree add failed' }
```

- [ ] **Step 2: Add the attempt-65 RED and override regression**

Add this method to `pyscf/sgx/test/test_sgx.py::KnownValues`:

```python
    def test_check_convergence(self):
        mol = gto.M(atom='He', basis='sto-3g', verbose=0)
        mf = sgx.sgx_fit(scf.RHF(mol))
        base_envs = {
            'e_tot': 0.0,
            'last_hf_e': 0.0,
            'conv_tol': 1e-11,
            'norm_gorb': 0.0,
            'conv_tol_grad': 3e-6,
            'extra_cycle': True,
        }
        cases = (
            ('both pass', 0.5e-11, 0.5e-6, True),
            ('energy only', 0.5e-11, 4e-6, False),
            ('gradient only', 2.6267343855579384e-10,
             4.0347904631078535e-9, False),
            ('neither', 2e-11, 4e-6, False),
        )
        for name, delta_e, norm_gorb, expected in cases:
            with self.subTest(name):
                envs = dict(base_envs, e_tot=delta_e, norm_gorb=norm_gorb)
                self.assertEqual(mf.check_convergence(envs), expected)

        observed = dict(
            base_envs,
            e_tot=2.6267343855579384e-10,
            norm_gorb=4.0347904631078535e-9,
        )
        calls = []

        def custom_check(envs):
            calls.append(envs)
            return True

        mf.check_convergence = custom_check
        self.assertTrue(mf.check_convergence(observed))
        self.assertEqual(calls, [observed])

        mf.check_convergence = None
        self.assertIsNone(mf.check_convergence)
```

- [ ] **Step 3: Run the RED**

```powershell
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:BLIS_NUM_THREADS = '1'
$env:VECLIB_MAXIMUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'
Set-Location 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-convergence'
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/test/test_sgx.py::KnownValues::test_check_convergence -c pytest.ini -vv
```

Expected: nonzero at the first call because current `_SGXHF` has no callable default `check_convergence`. Import/DLL/allocation failures are not acceptable REDs.

- [ ] **Step 4: Implement the minimal SGX method**

Add immediately before `_SGXHF.post_kernel()`:

```python
    def check_convergence(self, envs):
        energy_converged = (
            abs(envs['e_tot'] - envs['last_hf_e']) < envs['conv_tol'])
        gradient_converged = envs['norm_gorb'] < envs['conv_tol_grad']
        return energy_converged and gradient_converged
```

Do not add `extra_cycle` branching: the driver supplies original thresholds for main cycles and relaxed thresholds for Extra cycles.

- [ ] **Step 5: Run GREEN and SGX regressions**

```powershell
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/test/test_sgx.py -c pytest.ini -q
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad -c pytest.ini -vv
```

Expected: all pass with the original gradient-test blob unchanged.

- [ ] **Step 6: Verify and commit Task 3**

```powershell
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-convergence'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$ActiveText = [IO.File]::ReadAllText(
  $ActiveDoc, [Text.UTF8Encoding]::new($false))
$Matches = [regex]::Matches(
  $ActiveText, '(?m)^- production_fix_upstream_sha: `([0-9a-f]{40})`$')
if ($Matches.Count -ne 1) { throw 'Expected one production_fix_upstream_sha' }
$Upstream = $Matches[0].Groups[1].Value
$OriginalBlob = (git -c safe.directory=$Worktree -C $Worktree rev-parse `
  "$Upstream`:pyscf/sgx/grad/test/test_rks.py").Trim()
$CurrentBlob = (git -c safe.directory=$Worktree -C $Worktree hash-object --no-filters `
  pyscf/sgx/grad/test/test_rks.py).Trim()
if ($CurrentBlob -ne $OriginalBlob) { throw 'Original SGX gradient test changed' }
git -c safe.directory=$Worktree -C $Worktree diff --check
git -c safe.directory=$Worktree -C $Worktree add -- `
  pyscf/sgx/sgx.py pyscf/sgx/test/test_sgx.py
git -c safe.directory=$Worktree -C $Worktree diff --cached --check
git -c safe.directory=$Worktree -C $Worktree commit -m `
  'fix(sgx): require stable energy after extra cycles'
```

Record the SGX commit SHA and review verdicts in the active document.

---

### Task 4: Build the Validation-only Integration Branch and Run Local Smoke

**Files:**
- Create: `.github/workflows/precision-sgx-extra-cycle-production-nodeids.txt`
- Create: `.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt`
- Reuse: `.github/workflows/precision-libxc-712-nodeids.txt`
- Guard: all production files and original `test_rks.py`

**Interfaces:**
- Consumes: exact upstream SHA, two generic commits, one SGX commit from active document.
- Produces: `codex/test/sgx-extra-cycle-convergence-validation` with CI infrastructure plus stacked production commits.

- [ ] **Step 1: Create the integration worktree from the frozen upstream**

Create fresh path `D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration` and branch `codex/test/sgx-extra-cycle-convergence-validation`. Parse and validate all four SHAs from the active document. Cherry-pick these existing CI-only commits in order:

```text
581c00b92  ci(windows): align installed-wheel verification
c1f4abb00  ci(precision): add reusable nodeid investigation template
5a28c1039  ci(precision): catalog unresolved investigation families
9e79ca1b7  chore: ignore local agent workspace
c80210777  ci: select LibXC 7.1.2 revalidation nodeids
127642432  fix(ci): collect source-tree precision environment
0d88f3434  fix(ci): record pip-check execution mode and result
07c0641e9  fix(ci): capture macOS linkage with otool -L
```

Then cherry-pick Task 1, Task 2 and Task 3 production commits in that order. Any cherry-pick conflict is a stop condition: abort the current cherry-pick, record the conflicting paths, and return for plan/spec review.

Use this fresh-shell parser and worktree command; the active document keys are written by Tasks 1–3:

```powershell
$ErrorActionPreference = 'Stop'
$Root = 'D:\workspace\pyscf'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$ActiveDoc = "$Root\.agents\active\libxc-712-release-revalidation.md"
$Text = [IO.File]::ReadAllText($ActiveDoc, [Text.UTF8Encoding]::new($false))
function Read-OneSha([string]$Key) {
  $Pattern = '(?m)^- ' + [regex]::Escape($Key) + ': `([0-9a-f]{40})`$'
  $Found = [regex]::Matches($Text, $Pattern)
  if ($Found.Count -ne 1) { throw "Expected one $Key" }
  $Found[0].Groups[1].Value
}
$Upstream = Read-OneSha 'production_fix_upstream_sha'
$ContinuationCommit = Read-OneSha 'production_generic_continuation_commit'
$SmearingCommit = Read-OneSha 'production_smearing_convergence_commit'
$SgxCommit = Read-OneSha 'production_sgx_convergence_commit'
if (Test-Path -LiteralPath $Worktree) { throw "Worktree path exists: $Worktree" }
git -c safe.directory=$Root -C $Root show-ref --verify --quiet "refs/heads/$Branch"
if ($LASTEXITCODE -eq 0) { throw "Branch exists: $Branch" }
git -c safe.directory=$Root -C $Root worktree add -b $Branch $Worktree $Upstream
if ($LASTEXITCODE -ne 0) { throw 'Integration worktree add failed' }
$Commits = @(
  '581c00b92', 'c1f4abb00', '5a28c1039', '9e79ca1b7',
  'c80210777', '127642432', '0d88f3434', '07c0641e9',
  $ContinuationCommit, $SmearingCommit, $SgxCommit
)
foreach ($Commit in $Commits) {
  git -c safe.directory=$Worktree -C $Worktree cherry-pick $Commit
  if ($LASTEXITCODE -ne 0) {
    git -c safe.directory=$Worktree -C $Worktree cherry-pick --abort
    throw "Cherry-pick failed and was aborted: $Commit"
  }
}
```

- [ ] **Step 2: Add exact validation-only selections**

Create with `apply_patch`:

```text
# .github/workflows/precision-sgx-extra-cycle-production-nodeids.txt
pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad
```

```text
# .github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt
pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing
```

Verify the existing three-nodeid file is exactly:

```text
pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda
pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad
pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_hse03_tda
```

Run `run_precision_tests.py --validate-only` separately for each selection,
using repeats 1, profile `4/1`, and the integration HEAD:

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Head = (git -c safe.directory=$Worktree -C $Worktree rev-parse HEAD).Trim()
$Selections = @(
  '.github/workflows/precision-sgx-extra-cycle-production-nodeids.txt',
  '.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt',
  '.github/workflows/precision-libxc-712-nodeids.txt'
)
foreach ($Selection in $Selections) {
  conda run --no-capture-output -n pyscf-win313-test python `
    "$Worktree\.github\workflows\run_precision_tests.py" `
    --nodeids-file "$Worktree\$Selection" --repeats 1 --profile 4/1 `
    --tested-sha $Head --working-directory $Worktree --rootdir $Worktree `
    --pytest-config "$Worktree\pytest.ini" `
    --collector "$Worktree\.github\workflows\collect_precision_environment.py" `
    --validate-only
  if ($LASTEXITCODE -ne 0) { throw "Selection validation failed: $Selection" }
}
```

- [ ] **Step 3: Commit only the validation selections**

```powershell
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
git -c safe.directory=$Worktree -C $Worktree add -- `
  .github/workflows/precision-sgx-extra-cycle-production-nodeids.txt `
  .github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt
git -c safe.directory=$Worktree -C $Worktree diff --cached --check
git -c safe.directory=$Worktree -C $Worktree commit -m `
  'test(ci): select Extra-cycle production validation [skip ci]'
```

- [ ] **Step 4: Copy and hash-check the 26 untracked DLL fixtures**

Use `D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\pyscf\lib` as source. Enumerate `*.dll`, sort names with `[Array]::Sort($Names, [StringComparer]::Ordinal)`, require exactly 26, require the integration target has zero DLLs, copy each exact binary with `Copy-Item -LiteralPath`, then compare every source/target SHA-256. DLLs remain untracked and unstaged; this is local source-smoke support only, not installed-wheel provenance.

```powershell
$ErrorActionPreference = 'Stop'
$Source = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\pyscf\lib'
$Target = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration\pyscf\lib'
$SourceFiles = @(Get-ChildItem -LiteralPath $Source -File -Filter '*.dll')
$Names = [string[]]@($SourceFiles.Name)
[Array]::Sort($Names, [StringComparer]::Ordinal)
if ($Names.Count -ne 26) { throw "Expected 26 source DLLs, got $($Names.Count)" }
if (@(Get-ChildItem -LiteralPath $Target -File -Filter '*.dll').Count -ne 0) {
  throw 'Integration target already has DLLs'
}
foreach ($Name in $Names) {
  $SourcePath = Join-Path $Source $Name
  $TargetPath = Join-Path $Target $Name
  Copy-Item -LiteralPath $SourcePath -Destination $TargetPath
  $SourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $SourcePath).Hash
  $TargetHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $TargetPath).Hash
  if ($SourceHash -ne $TargetHash) { throw "DLL hash mismatch: $Name" }
}
```

- [ ] **Step 5: Run stacked local validation**

With all six thread variables set first to `1`, run:

```powershell
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:BLIS_NUM_THREADS = '1'
$env:VECLIB_MAXIMUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'
Set-Location 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing -c pytest.ini -vv
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/test/test_sgx.py -c pytest.ini -q
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad -c pytest.ini -vv
```

Then set `OMP_NUM_THREADS=4`, `OPENBLAS_NUM_THREADS=1` and the other four variables consistently to the `4/1` profile, and rerun the original SGX nodeid once.

```powershell
$env:OMP_NUM_THREADS = '4'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:BLIS_NUM_THREADS = '1'
$env:VECLIB_MAXIMUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'
conda run --no-capture-output -n pyscf-win313-test python -m pytest `
  pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad -c pytest.ini -vv
```

- [ ] **Step 6: Enforce production/diagnostic boundaries**

Verify:

```powershell
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$ActiveText = [IO.File]::ReadAllText(
  $ActiveDoc, [Text.UTF8Encoding]::new($false))
$Matches = [regex]::Matches(
  $ActiveText, '(?m)^- production_fix_upstream_sha: `([0-9a-f]{40})`$')
if ($Matches.Count -ne 1) { throw 'Expected one production_fix_upstream_sha' }
$Upstream = $Matches[0].Groups[1].Value
git -c safe.directory=$Worktree -C $Worktree diff --check
git -c safe.directory=$Worktree -C $Worktree diff --name-status $Upstream..HEAD
$DiagnosticMatches = @(rg -n `
  'PYSCF_SGX_HSE06|TELEMETRY|post_kernel_once_per_phase' `
  "$Worktree\pyscf\scf" "$Worktree\pyscf\sgx")
if ($LASTEXITCODE -ne 1 -or $DiagnosticMatches.Count -ne 0) {
  throw 'Production source contains diagnostic telemetry'
}
```

Expected `rg` exit is 1/no matches. Compare the committed `test_rks.py` blob to `$Upstream`; it must be identical. Record the validation head under exact key `production_validation_head` and record all component commit SHAs in the active document.

---

### Task 5: Create a Frozen Production Evidence Validator

**Files:**
- Create ignored: `.agents/active/precision-ci/scripts/validate_precision_production.py`
- Archive per run: validator copy, SHA-256 and `production-validation.json`

**Interfaces:**
- CLI consumes an evidence directory and exact expected run/nodeid/profile/provenance values.
- CLI produces an atomic JSON report and exits `0` for structurally valid `PASS` or `SCIENTIFIC_FAILURE`, `2` for `INVALID`.

- [ ] **Step 1: Freeze the reviewed generic validator seed**

Require `.agents/active/precision-ci/scripts/validate_sgx_hse06_telemetry.py` SHA-256 exactly `38088856545baf89e8ab9c054b943d96272359a42bfd582501184260ccb3c8b2`. Make one byte-exact mechanical copy to the new filename, verify the copy hash still matches, then perform all authored changes with `apply_patch`. Never edit the frozen seed.

- [ ] **Step 2: Replace the diagnostic CLI with this exact interface**

```text
validate_precision_production.py EVIDENCE
  --mode source-tree|installed-wheel
  --expected-sha 40HEX
  --expected-nodeids-file PATH
  --expected-profile omp1-blas1|omp4-blas1|omp1-blas4|omp4-blas4
  --expected-repeats POSITIVE_INT
  --expected-platform windows-latest|ubuntu-latest|macos-latest
  --expected-python 3.8|3.12|3.13
  --expected-native-count POSITIVE_INT
  [--source-root PATH]
  [--run-metadata run.json]
  [--expected-run-id POSITIVE_INT]
  [--expected-branch BRANCH]
  [--expected-artifact-name NAME]
  --report report.json
```

The four remote-run options (`--run-metadata`, run ID, branch and artifact
name) are an all-or-none group. Local `source-tree` evidence requires
`--source-root` and omits the remote group. Remote `source-tree` evidence
requires the remote group and rejects `--source-root`; it validates the
absolute GitHub checkout path recorded in the artifact rather than pretending
that the Unix checkout exists on the Windows reviewer host. `installed-wheel`
requires the remote group and rejects `--source-root`.

Implement and use these exact helpers:

```python
DIAGNOSTIC_PREFIXES = (
    'PYSCF_SGX_HSE06_TELEMETRY_V1 ',
    'PYSCF_SGX_HSE06_POST_KERNEL_TELEMETRY_V2 ',
)

def load_expected_nodeids(path):
    values = []
    for raw in path.read_text(encoding='utf-8').splitlines():
        value = raw.strip()
        if value and not value.startswith('#'):
            if '::' not in value or value in values:
                raise InvalidEvidence(f'Invalid expected nodeid: {value!r}')
            values.append(value)
    if not values:
        raise InvalidEvidence('Expected nodeid selection is empty')
    return values

def validate_no_diagnostics(text, log_path):
    for line in text.splitlines():
        if line.startswith(DIAGNOSTIC_PREFIXES):
            raise InvalidEvidence(
                f'Diagnostic telemetry found in production log: {log_path}')

def classify_records(records):
    statuses = {record['status'] for record in records}
    if not statuses <= {'pass', 'fail'}:
        raise InvalidEvidence(f'Unexpected record statuses: {sorted(statuses)!r}')
    failed = [record for record in records if record['status'] == 'fail']
    if failed:
        return 'SCIENTIFIC_FAILURE', min(
            failed, key=lambda record: (record['nodeid'], record['attempt']))
    return 'PASS', None
```

The expected record count is `len(expected_nodeids) * expected_repeats`. For every expected nodeid require attempts exactly `1..N`, no duplicates, exact profile/tested SHA, one referenced physical log, matching CSV row, and no extra logs. A pass log must contain exactly one collected item and `1 passed`; a fail log must contain exactly one collected item plus both `FAILED` and either `AssertionError` or `ERROR`. No retry or unknown-status records are accepted.

- [ ] **Step 3: Preserve and generalize the provenance contract**

Copy these seed primitives without semantic changes: `load_json_strict`, `_loads_json_strict`, `_require`, `_is_int`, `_finite_number`, `_resolve_contained_path`, `_validate_reference`, and `write_report`. Rewrite `validate_file_contract` to use `load_expected_nodeids()` and the per-nodeid attempt rule from Step 2. Delete `parse_log_marker`, `validate_marker`, `_fixture_payload`, `_load_fixture_marker`, `_write_fixture_marker`, `_recompute_fixture_result` and all telemetry classification functions.

Generalize `validate_runtime` with these exact maps and checks:

```python
PROFILE_THREADS = {
    'omp1-blas1': ('1', '1'),
    'omp4-blas1': ('4', '1'),
    'omp1-blas4': ('1', '4'),
    'omp4-blas4': ('4', '4'),
}
PLATFORM_SYSTEMS = {
    'windows-latest': 'Windows',
    'ubuntu-latest': 'Linux',
    'macos-latest': 'Darwin',
}
```

Require `OMP_NUM_THREADS` to equal the first profile value and all five BLAS
thread variables to equal the second. Require `platform.system` and
`python.version` to match the explicit platform/Python inputs. Both modes
require LibXC `7.1.2`, exactly `expected_native_count` unique native libraries,
positive sizes, lowercase SHA-256 and linkage return code 0. Source-tree mode
always requires exact `git_commit` and LibXC interface linkage within the
recorded checkout. For local evidence, resolve `source_root` and the import path
strictly and require containment; Windows `libxc_itrf.dll` must resolve that
checkout's direct-child `libxc.dll`. For remote Linux/macOS evidence, require an
absolute canonical POSIX import path with no `.`/`..` component and the exact
suffix `runner/work/pyscf/pyscf/pyscf/__init__.py`; require every native library
under the sibling checkout `pyscf/lib`. Linux `libxc_itrf.so` must resolve
`pyscf/lib/deps/lib/libxc.so`; macOS `libxc_itrf.dylib` must list exactly one
`@rpath/libxc.15.dylib` dependency. Linux permits only the exact known
`pyscf-dispersion 1.5.0 requires pyscf, which is not installed.` pip-check
return-code-1 advisory, while macOS requires pip-check 0. The approved local
Windows source environment permits only its frozen return-code-1 advisory
`pyscf 2.13.1 requires psutil, which is not installed.`; it remains diagnostic
because the imported tested package is the checkout, not that installed
distribution. Installed-wheel mode
requires pip-check 0, `PRECISION_TESTED_SHA`, site-packages import, exactly 26
wheel-local DLLs, and `libxc_itrf.dll` resolving the wheel-local `libxc.dll`.

Generalize `validate_run_metadata` to compare the sole artifact name against
`options.expected_artifact_name` instead of a hard-coded Windows name. Preserve
the exact attempt/event/head/branch/workflow/job/artifact/digest checks from the
seed. `validate_evidence()` must call, in order: `load_evidence`,
`validate_file_contract`, `validate_no_diagnostics` for every log,
`validate_runtime`, optional `validate_run_metadata`, then `classify_records`.

Use this report schema for both valid and invalid results:

```python
{
    'valid': bool,
    'verdict': 'PASS' | 'SCIENTIFIC_FAILURE' | 'INVALID',
    'validator_sha256': str,
    'records': int,
    'pass': int,
    'fail': int,
    'nodeids': list[str],
    'profile': str | None,
    'tested_sha': str | None,
    'first_failure': dict | None,
    'errors': list[str],
}
```

If all records pass, run/job conclusion must be `success`. If any scientific record fails, run/job conclusion must be `failure`; this remains valid evidence. Only malformed or inconsistent evidence exits 2.

- [ ] **Step 4: Replace marker self-tests with production fixtures**

The built-in `--self-test` must run these exact named cases:

1. local Windows source-tree singleton, 1 repeat, PASS with only its exact pip advisory;
2. macOS source-tree singleton, 1 repeat, PASS;
3. Linux source-tree three nodeids, 200 repeats each, PASS with only its exact pip advisory;
4. Windows installed-wheel three nodeids, 200 repeats each, PASS;
5. Windows installed-wheel singleton with one assertion failure, valid `SCIENTIFIC_FAILURE` and exit 0;
6. one `mutation_NAME` test for each of: missing log, extra log, duplicate attempt, wrong SHA, wrong profile, wrong nodeid, unknown status, wrong platform, wrong Python, CSV mismatch, summary mismatch, source-shadow import, unexpected pip failure, wrong LibXC, wrong native count, missing DLL linkage, wrong artifact name, wrong artifact digest, diagnostic marker present. Every mutation must independently yield direct `InvalidEvidence` and CLI exit 2/`INVALID`.

Run:

```powershell
conda run --no-capture-output -n pyscf-win313-test python `
  D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py `
  --self-test
conda run --no-capture-output -n pyscf-win313-test python -m py_compile `
  D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py
```

Expected: all named self-tests pass and exit 0. Freeze the new SHA-256 in the active document and copy the exact validator into every evidence archive before validation.

- [ ] **Step 5: Validate one local source-tree smoke**

Use the canonical runner on the integration branch with the singleton SGX production selection, repeats 1, profile `4/1`, exact tested SHA and a new output directory. Save runner exit code in `runner-exit-code.txt`, then invoke the new validator with `--mode source-tree`. Expected report: `valid=true`, `verdict=PASS`, 1 record, no diagnostic prefix. A scientific failure is preserved and blocks remote expansion; an `INVALID` report requires fixing the evidence contract.

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Evidence = "$Worktree\tmp\production-source-smoke-4-1"
$Selection = "$Worktree\.github\workflows\precision-sgx-extra-cycle-production-nodeids.txt"
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py'
$Head = (git -c safe.directory=$Worktree -C $Worktree rev-parse HEAD).Trim()
$env:OMP_NUM_THREADS = '4'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:BLIS_NUM_THREADS = '1'
$env:VECLIB_MAXIMUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'
Set-Location $Worktree
conda run --no-capture-output -n pyscf-win313-test python `
  "$Worktree\.github\workflows\run_precision_tests.py" `
  --nodeids-file $Selection --repeats 1 --profile 4/1 `
  --output-dir $Evidence --tested-sha $Head `
  --working-directory $Worktree --rootdir $Worktree `
  --pytest-config "$Worktree\pytest.ini" `
  --collector "$Worktree\.github\workflows\collect_precision_environment.py" `
  --environment-mode source-tree
$RunnerExit = $LASTEXITCODE
[IO.File]::WriteAllText(
  "$Evidence\runner-exit-code.txt", "$RunnerExit`n",
  [Text.ASCIIEncoding]::new())
conda run --no-capture-output -n pyscf-win313-test python $Validator $Evidence `
  --mode source-tree --expected-sha $Head `
  --expected-nodeids-file $Selection --expected-profile omp4-blas1 `
  --expected-repeats 1 --expected-platform windows-latest `
  --expected-python 3.13 --expected-native-count 26 `
  --source-root $Worktree --report "$Evidence\production-validation.json"
if ($LASTEXITCODE -ne 0) { throw 'Source evidence INVALID' }
$Report = Get-Content -Raw -Encoding UTF8 `
  "$Evidence\production-validation.json" | ConvertFrom-Json -ErrorAction Stop
if (-not $Report.valid -or $Report.verdict -ne 'PASS') {
  throw "Source smoke did not pass: $($Report.verdict)"
}
```

---

### Task 6: Run the Windows Installed-wheel Witness

**Files:**
- Update ignored active document and archive only.
- Remote write: push validation branch and dispatch one workflow run.

**Interfaces:**
- Consumes: frozen integration head, singleton SGX selection, frozen production validator.
- Produces: one validated Windows Python 3.12 `omp4-blas1` installed-wheel artifact.

- [ ] **Step 1: Reverify and push the exact validation head**

Require tracked-clean integration worktree, expected production commits in ancestry, original `test_rks.py` blob unchanged, validator self-test green, `gh auth status` valid, no active run for the same branch/configuration, and no existing remote branch at a different SHA. Push:

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$Head = (git -c safe.directory=$Worktree -C $Worktree rev-parse HEAD).Trim()
if (@(git -c safe.directory=$Worktree -C $Worktree status --short |
      Where-Object { $_ -notmatch '^\?\? pyscf/lib/.+\.dll$' }).Count -ne 0) {
  throw 'Integration worktree is not tracked-clean'
}
gh auth status --hostname github.com
if ($LASTEXITCODE -ne 0) { throw 'GitHub authentication invalid' }
$RemoteBefore = @(git ls-remote https://github.com/psiQAQ/pyscf.git `
  "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $RemoteBefore.Count -gt 1) {
  throw 'Remote validation branch preflight failed'
}
if ($RemoteBefore.Count -eq 1) {
  $ExistingRemoteHead = ($RemoteBefore[0] -split "`t")[0]
  if ($ExistingRemoteHead -ne $Head) {
    throw "Remote branch exists at a different SHA: $ExistingRemoteHead"
  }
}
git -c safe.directory=$Worktree -C $Worktree push -u origin `
  $Branch
if ($LASTEXITCODE -ne 0) { throw 'Validation branch push failed' }
$RemoteLine = @(git ls-remote https://github.com/psiQAQ/pyscf.git `
  "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $RemoteLine.Count -ne 1) {
  throw 'Remote validation branch identity unavailable'
}
$RemoteHead = ($RemoteLine[0] -split "`t")[0]
if ($RemoteHead -ne $Head) { throw "Remote head mismatch: $RemoteHead" }
```

Read back the remote SHA with `git ls-remote` and require exact equality.

- [ ] **Step 2: Dispatch and bind one witness without timestamp matching**

Before dispatch, list workflow runs for the exact branch/event and freeze the maximum `databaseId`. Dispatch:

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'psiQAQ/pyscf'
$Workflow = 'ci-precision-check.yml'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Head = (git -c safe.directory=$Worktree -C $Worktree rev-parse HEAD).Trim()
$Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch `
  --event workflow_dispatch --limit 100 `
  --json databaseId,headSha,status,event,workflowName,headBranch,url)
if ($LASTEXITCODE -ne 0) { throw 'Witness baseline query failed' }
$Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
$Rows = @($Parsed)
$Active = @($Rows | Where-Object {
  $_.headSha -eq $Head -and
  $_.status -in @('requested','queued','in_progress','waiting','pending')
})
if ($Active.Count -ne 0) { throw 'Exact-head run already active' }
$BeforeMax = 0L
if ($Rows.Count -gt 0) {
  $BeforeMax = [long](($Rows | Measure-Object -Property databaseId -Maximum).Maximum)
}
$LatchRoot = 'D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches'
[IO.Directory]::CreateDirectory($LatchRoot) | Out-Null
$LatchPath = Join-Path $LatchRoot "production-witness-$Head.json"
$LatchPayload = [ordered]@{
  purpose = 'production-witness'
  repo = $Repo
  workflow = $Workflow
  branch = $Branch
  head = $Head
  before_max = $BeforeMax
  nodeids_file = '.github/workflows/precision-sgx-extra-cycle-production-nodeids.txt'
  repeats = 1
  platform = 'windows-latest'
  python = '3.12'
  profile = '4/1'
}
$LatchBytes = [Text.UTF8Encoding]::new($false).GetBytes(
  ($LatchPayload | ConvertTo-Json -Depth 4) + "`n")
$LatchStream = [IO.File]::Open(
  $LatchPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write,
  [IO.FileShare]::None)
try {
  $LatchStream.Write($LatchBytes, 0, $LatchBytes.Length)
  $LatchStream.Flush($true)
}
finally {
  $LatchStream.Dispose()
}
gh workflow run $Workflow --repo $Repo `
  --ref $Branch `
  -f nodeids_file=.github/workflows/precision-sgx-extra-cycle-production-nodeids.txt `
  -f repeats=1 `
  -f platform=windows-latest `
  -f python_version=3.12 `
  -f profile=4/1
if ($LASTEXITCODE -ne 0) { throw 'Witness dispatch failed' }

$Candidate = $null
for ($Attempt = 1; $Attempt -le 12; $Attempt++) {
  $Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch `
    --event workflow_dispatch --limit 100 `
    --json databaseId,headSha,status,event,workflowName,headBranch,url)
  if ($LASTEXITCODE -ne 0) { throw 'Witness binding query failed' }
  $Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
  $Rows = @($Parsed)
  $Candidates = @($Rows | Where-Object {
    [long]$_.databaseId -gt $BeforeMax -and $_.headSha -eq $Head -and
    $_.headBranch -eq $Branch -and $_.event -eq 'workflow_dispatch' -and
    $_.workflowName -eq 'Precision investigation'
  })
  if ($Candidates.Count -eq 1) { $Candidate = $Candidates[0]; break }
  if ($Candidates.Count -gt 1) { throw 'Ambiguous witness run binding' }
  Start-Sleep -Seconds 5
}
if ($null -eq $Candidate) {
  throw "Witness dispatch acknowledged but not bound; recover from $LatchPath without redispatch"
}
$RunId = [long]$Candidate.databaseId
```

Poll at most 12 times with five-second intervals. Candidate must have `databaseId > BeforeMax`, exact branch, exact head SHA, `event=workflow_dispatch`, workflow name `Precision investigation`; require exactly one candidate. Persist exact keys `production_witness_before_max`, `production_witness_run_id`, `production_witness_url`, `production_witness_head`, latch path/hash, the five workflow inputs, and expected artifact `precision-Windows-py3.12` in the active document before starting any monitor. The `CreateNew` latch makes this dispatch block one-shot. If it already exists or binding is temporarily absent, never rerun `gh workflow run`: read and hash-check the latch, query only IDs greater than its `before_max`, accept 0 as “wait”, exactly 1 exact-identity candidate as the bound run, and reject more than 1 as ambiguous.

- [ ] **Step 3: Start exactly one reviewed heartbeat**

Verify the heartbeat hash and `-SelfTest` 18/18. Ensure no existing matching PS1 and no active native heartbeat. Start hidden from this fresh shell:

```powershell
$ErrorActionPreference = 'Stop'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$HeartbeatPath = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$ExpectedHeartbeatHash = '4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639'
$Text = [IO.File]::ReadAllText($ActiveDoc, [Text.UTF8Encoding]::new($false))
$HeadMatch = [regex]::Matches(
  $Text, '(?m)^- production_witness_head: `([0-9a-f]{40})`$')
$RunMatch = [regex]::Matches(
  $Text, '(?m)^- production_witness_run_id: `([1-9][0-9]*)`$')
if ($HeadMatch.Count -ne 1 -or $RunMatch.Count -ne 1) {
  throw 'Witness heartbeat identity is not frozen'
}
$Head = $HeadMatch[0].Groups[1].Value
$RunId = [long]$RunMatch[0].Groups[1].Value
$HeartbeatHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $HeartbeatPath).Hash.ToLowerInvariant()
if ($HeartbeatHash -ne $ExpectedHeartbeatHash) { throw 'Heartbeat hash mismatch' }
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $HeartbeatPath -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Heartbeat self-test failed' }
$Existing = @(Get-CimInstance Win32_Process | Where-Object {
  $_.Name -ieq 'powershell.exe' -and
  $_.CommandLine -like "*$HeartbeatPath*" -and
  $_.CommandLine -like "*${RunId}*" -and
  $_.CommandLine -like "*$Head*"
})
if ($Existing.Count -ne 0) { throw 'Matching heartbeat already exists' }
$Heartbeat = Start-Process powershell.exe -WindowStyle Hidden -PassThru -ArgumentList @(
  '-NoProfile', '-ExecutionPolicy', 'Bypass',
  '-File', $HeartbeatPath,
  '-TargetRunIds', "$RunId",
  '-TargetHeadSha', $Head,
  '-IntervalSeconds', '1800',
  '-WakeAfterMinutes', '300'
)
$Heartbeat.Refresh()
if ($Heartbeat.HasExited) { throw 'Heartbeat exited during handoff' }
$Process = Get-CimInstance Win32_Process -Filter "ProcessId=$($Heartbeat.Id)"
if ($null -eq $Process -or $Process.ExecutablePath -notlike '*\WindowsPowerShell\v1.0\powershell.exe' -or
    $Process.CommandLine -notlike "*$HeartbeatPath*" -or
    $Process.CommandLine -notlike "*${RunId}*" -or
    $Process.CommandLine -notlike "*$Head*") {
  Stop-Process -Id $Heartbeat.Id
  throw 'Heartbeat process identity mismatch'
}
```

Verify the captured PID, executable path and command-line tokens, then independently verify the Goal is paused. During this wait do no manual polling.

- [ ] **Step 4: Freeze and validate the terminal artifact**

After heartbeat resumes the Goal, require the monitor PID is gone and Goal read-back is active. Re-query the exact run with full identity. Poll the artifacts API until either:

- `total_count=0` and array count 0: latency, retry later without redispatch;
- exactly one artifact with positive integral ID, exact name, positive size, `expired=false` bool and `sha256:` digest: ready;
- any other shape: `INVALID`.

Use this fresh-shell block. It writes `run.json` with run attempt/event/head/branch/workflow/status/conclusion, one `precision` job status/conclusion, and the sole artifact identity; it treats only an empty artifact envelope as propagation latency:

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'psiQAQ/pyscf'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py'
$Text = [IO.File]::ReadAllText($ActiveDoc, [Text.UTF8Encoding]::new($false))
function Read-One([string]$Pattern, [string]$Label) {
  $Found = [regex]::Matches($Text, $Pattern)
  if ($Found.Count -ne 1) { throw "Expected one $Label" }
  $Found[0].Groups[1].Value
}
$Head = Read-One '(?m)^- production_validation_head: `([0-9a-f]{40})`$' 'validation head'
$RunId = [long](Read-One '(?m)^- production_witness_run_id: `([1-9][0-9]*)`$' 'witness run ID')
$ExpectedValidatorHash = Read-One '(?m)^- production_validator_sha256: `([0-9a-f]{64})`$' 'validator SHA'
$LocalHead = (git -c safe.directory=$Worktree -C $Worktree rev-parse HEAD).Trim()
$RemoteLine = @(git ls-remote https://github.com/psiQAQ/pyscf.git "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $RemoteLine.Count -ne 1) { throw 'Remote head unavailable' }
$RemoteHead = ($RemoteLine[0] -split "`t")[0]
if ($LocalHead -ne $Head -or $RemoteHead -ne $Head) { throw 'Frozen head mismatch' }
$ValidatorHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Validator).Hash.ToLowerInvariant()
if ($ValidatorHash -ne $ExpectedValidatorHash) { throw 'Frozen validator mismatch' }

$RunRaw = @(gh api "repos/$Repo/actions/runs/$RunId")
if ($LASTEXITCODE -ne 0) { throw 'Run metadata query failed' }
$Run = ConvertFrom-Json -InputObject ($RunRaw -join "`n") -ErrorAction Stop
if ([long]$Run.id -ne $RunId -or [int]$Run.run_attempt -ne 1 -or
    $Run.event -ne 'workflow_dispatch' -or $Run.name -ne 'Precision investigation' -or
    $Run.head_sha -ne $Head -or $Run.head_branch -ne $Branch -or
    $Run.status -ne 'completed' -or $Run.conclusion -notin @('success','failure')) {
  throw 'Terminal run identity mismatch'
}
$JobsRaw = @(gh api "repos/$Repo/actions/runs/$RunId/jobs")
if ($LASTEXITCODE -ne 0) { throw 'Job metadata query failed' }
$JobsEnvelope = ConvertFrom-Json -InputObject ($JobsRaw -join "`n") -ErrorAction Stop
$Jobs = @($JobsEnvelope.jobs)
if ([int]$JobsEnvelope.total_count -ne 1 -or $Jobs.Count -ne 1 -or
    $Jobs[0].name -ne 'precision' -or $Jobs[0].status -ne 'completed' -or
    $Jobs[0].conclusion -ne $Run.conclusion) {
  throw 'Precision job identity mismatch'
}

$Artifact = $null
for ($Attempt = 1; $Attempt -le 12; $Attempt++) {
  $ArtifactsRaw = @(gh api "repos/$Repo/actions/runs/$RunId/artifacts")
  if ($LASTEXITCODE -ne 0) { throw 'Artifact metadata query failed' }
  $Envelope = ConvertFrom-Json -InputObject ($ArtifactsRaw -join "`n") -ErrorAction Stop
  $Artifacts = @($Envelope.artifacts)
  if ([int]$Envelope.total_count -eq 0 -and $Artifacts.Count -eq 0) {
    Start-Sleep -Seconds 10
    continue
  }
  if ([int]$Envelope.total_count -ne 1 -or $Artifacts.Count -ne 1) {
    throw 'Artifact cardinality is INVALID'
  }
  $CandidateArtifact = $Artifacts[0]
  $ArtifactId = 0L
  $IdValid = [long]::TryParse([string]$CandidateArtifact.id, [ref]$ArtifactId)
  if (-not $IdValid -or $ArtifactId -le 0 -or
      $CandidateArtifact.name -ne 'precision-Windows-py3.12' -or
      $CandidateArtifact.expired -isnot [bool] -or $CandidateArtifact.expired -or
      [long]$CandidateArtifact.size_in_bytes -le 0 -or
      [string]$CandidateArtifact.digest -notmatch '^sha256:[0-9a-f]{64}$') {
    throw 'Artifact identity is INVALID'
  }
  $Artifact = $CandidateArtifact
  break
}
if ($null -eq $Artifact) { throw 'Artifact metadata is still unavailable; retry without redispatch' }

$Evidence = "D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-production-witness-windows-py312"
if (Test-Path -LiteralPath $Evidence) { throw "Evidence path exists: $Evidence" }
[IO.Directory]::CreateDirectory($Evidence) | Out-Null
$RunMetadata = [ordered]@{
  databaseId = $RunId
  attempt = [int]$Run.run_attempt
  event = [string]$Run.event
  workflowName = [string]$Run.name
  headSha = [string]$Run.head_sha
  headBranch = [string]$Run.head_branch
  status = [string]$Run.status
  conclusion = [string]$Run.conclusion
  jobs = @([ordered]@{
    name = [string]$Jobs[0].name
    status = [string]$Jobs[0].status
    conclusion = [string]$Jobs[0].conclusion
  })
  artifacts = @([ordered]@{
    id = [long]$Artifact.id
    name = [string]$Artifact.name
    digest = [string]$Artifact.digest
    sizeInBytes = [long]$Artifact.size_in_bytes
    expired = [bool]$Artifact.expired
  })
}
[IO.File]::WriteAllText(
  "$Evidence\run.json", (($RunMetadata | ConvertTo-Json -Depth 6) + "`n"),
  [Text.UTF8Encoding]::new($false))
gh run download $RunId --repo $Repo --name precision-Windows-py3.12 --dir $Evidence
if ($LASTEXITCODE -ne 0) { throw 'Artifact download failed' }
$ValidatorCopy = "$Evidence\validate_precision_production.py"
Copy-Item -LiteralPath $Validator -Destination $ValidatorCopy
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $ValidatorCopy).Hash.ToLowerInvariant() -ne
    $ExpectedValidatorHash) { throw 'Archived validator hash mismatch' }

conda run --no-capture-output -n pyscf-win313-test python $ValidatorCopy `
  $Evidence `
  --mode installed-wheel `
  --expected-sha $Head `
  --expected-nodeids-file `
    "$Worktree\.github\workflows\precision-sgx-extra-cycle-production-nodeids.txt" `
  --expected-profile omp4-blas1 `
  --expected-repeats 1 `
  --expected-platform windows-latest `
  --expected-python 3.12 `
  --expected-native-count 26 `
  --run-metadata "$Evidence\run.json" `
  --expected-run-id $RunId `
  --expected-branch $Branch `
  --expected-artifact-name precision-Windows-py3.12 `
  --report "$Evidence\production-validation.json"
if ($LASTEXITCODE -ne 0) { throw 'Witness evidence is INVALID' }
```

Read the report back, require `valid=true` and `verdict=PASS`, then write exact
active-document keys `production_witness_verdict: PASS`, artifact ID/digest,
run URL, archive path and validator SHA. Only that frozen gate unlocks Task 7.

---

### Task 7: Run SGX Formal 200 and Focused #3331 CI

**Files:**
- Update active documents and evidence archives only.

**Interfaces:**
- Consumes: the exact witness-validated integration head.
- Produces: SGX 200-repeat formal artifact and focused UHF-smearing evidence.

- [ ] **Step 1: Dispatch the SGX formal 200**

In a fresh shell, parse exactly one `production_validation_head` and exactly one `production_witness_verdict: PASS` from the active document. Require local HEAD and `git ls-remote` both equal that head, and reject any active run for the exact branch. Then run:

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'psiQAQ/pyscf'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$Workflow = 'ci-precision-check.yml'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$ActiveText = [IO.File]::ReadAllText(
  $ActiveDoc, [Text.UTF8Encoding]::new($false))
$HeadMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_validation_head: `([0-9a-f]{40})`$')
$WitnessMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_witness_verdict: PASS$')
if ($HeadMatches.Count -ne 1 -or $WitnessMatches.Count -ne 1) {
  throw 'Formal gate is not frozen as one validated witness head'
}
$Head = $HeadMatches[0].Groups[1].Value
$Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch `
  --event workflow_dispatch --limit 100 `
  --json databaseId,headSha,status,event,workflowName,headBranch)
if ($LASTEXITCODE -ne 0) { throw 'gh run list failed' }
$Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
$Rows = @($Parsed)
$Active = @($Rows | Where-Object {
  $_.headSha -eq $Head -and
  $_.status -in @('requested','queued','in_progress','waiting','pending')
})
if ($Active.Count -ne 0) { throw 'Exact-head run already active' }
$BeforeMax = 0L
if ($Rows.Count -gt 0) {
  $BeforeMax = [long](($Rows | Measure-Object -Property databaseId -Maximum).Maximum)
}
$LatchRoot = 'D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches'
[IO.Directory]::CreateDirectory($LatchRoot) | Out-Null
$LatchPath = Join-Path $LatchRoot "production-sgx-formal-$Head.json"
$LatchPayload = [ordered]@{
  purpose='production-sgx-formal'; repo=$Repo; workflow=$Workflow
  branch=$Branch; head=$Head; before_max=$BeforeMax
  nodeids_file='.github/workflows/precision-sgx-extra-cycle-production-nodeids.txt'
  repeats=200; platform='windows-latest'; python='3.12'; profile='4/1'
}
$LatchBytes = [Text.UTF8Encoding]::new($false).GetBytes(
  ($LatchPayload | ConvertTo-Json -Depth 4) + "`n")
$LatchStream = [IO.File]::Open(
  $LatchPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write,
  [IO.FileShare]::None)
try {
  $LatchStream.Write($LatchBytes, 0, $LatchBytes.Length)
  $LatchStream.Flush($true)
}
finally { $LatchStream.Dispose() }
gh workflow run $Workflow --repo $Repo --ref $Branch `
  -f nodeids_file=.github/workflows/precision-sgx-extra-cycle-production-nodeids.txt `
  -f repeats=200 `
  -f platform=windows-latest `
  -f python_version=3.12 `
  -f profile=4/1
if ($LASTEXITCODE -ne 0) { throw 'Formal dispatch failed' }

$Candidate = $null
for ($Attempt = 1; $Attempt -le 12; $Attempt++) {
  $Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch `
    --event workflow_dispatch --limit 100 `
    --json databaseId,headSha,status,event,workflowName,headBranch,url)
  if ($LASTEXITCODE -ne 0) { throw 'Formal binding query failed' }
  $Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
  $Rows = @($Parsed)
  $Candidates = @($Rows | Where-Object {
    [long]$_.databaseId -gt $BeforeMax -and $_.headSha -eq $Head -and
    $_.headBranch -eq $Branch -and $_.event -eq 'workflow_dispatch' -and
    $_.workflowName -eq 'Precision investigation'
  })
  if ($Candidates.Count -eq 1) { $Candidate = $Candidates[0]; break }
  if ($Candidates.Count -gt 1) { throw 'Ambiguous formal run binding' }
  Start-Sleep -Seconds 5
}
if ($null -eq $Candidate) {
  throw "Formal dispatch acknowledged but not bound; recover from $LatchPath without redispatch"
}
$RunId = [long]$Candidate.databaseId
```

Use `apply_patch` to persist exact keys `production_sgx_formal_before_max`,
`production_sgx_formal_run_id`, `production_sgx_formal_head`, inputs and expected
artifact before starting the reviewed heartbeat with this exact invocation:

```powershell
$ErrorActionPreference = 'Stop'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$ActiveText = [IO.File]::ReadAllText(
  $ActiveDoc, [Text.UTF8Encoding]::new($false))
$HeadMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_sgx_formal_head: `([0-9a-f]{40})`$')
$RunMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_sgx_formal_run_id: `([1-9][0-9]*)`$')
if ($HeadMatches.Count -ne 1 -or $RunMatches.Count -ne 1) {
  throw 'Formal heartbeat identity is not uniquely frozen'
}
$Head = $HeadMatches[0].Groups[1].Value
$RunId = [long]$RunMatches[0].Groups[1].Value
$Monitor = Start-Process powershell.exe -WindowStyle Hidden -PassThru -ArgumentList @(
  '-NoProfile', '-ExecutionPolicy', 'Bypass',
  '-File', 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1',
  '-TargetRunIds', "$RunId", '-TargetHeadSha', $Head,
  '-IntervalSeconds', '1800', '-WakeAfterMinutes', '300'
)
```

The frozen workflow inputs are:

```text
nodeids_file=.github/workflows/precision-sgx-extra-cycle-production-nodeids.txt
repeats=200
platform=windows-latest
python_version=3.12
profile=4/1
```

Do not reuse witness run IDs, directories or run metadata. After terminal state,
freeze the exact run/job/artifact envelope into a new
`RUNID-production-sgx-formal-windows-py312` archive, using the strict ID,
cardinality, name, digest, size and expiry predicates from Task 6. Run the
archived validator with `--mode installed-wheel`, `--expected-platform
windows-latest`, `--expected-python 3.12`, `--expected-artifact-name
precision-Windows-py3.12`, `--expected-native-count 26`, and expected repeats
200. Required verdict: `PASS`, 200/200, zero retry, zero diagnostic markers,
original test blob unchanged. Record exact active key
`production_sgx_formal_verdict: PASS` only after reading the JSON report back.

- [ ] **Step 2: Dispatch focused UHF-smearing validation**

On the same frozen integration head, dispatch two separate 20-repeat runs using `.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt`:

| Platform | Python | Profile | Repeats |
| --- | --- | --- | --- |
| `windows-latest` | `3.12` | `4/4` | 20 |
| `ubuntu-latest` | `3.12` | `4/4` | 20 |

For each row, independently freeze `BeforeMax`, dispatch once, and bind one new
exact-head run. The second dispatch may see only the already-bound first run as
active; any other active exact-head run is a stop condition. Run this complete
fresh-shell block, which persists both IDs before starting one heartbeat:

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'psiQAQ/pyscf'
$Workflow = 'ci-precision-check.yml'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Text = [IO.File]::ReadAllText($ActiveDoc, [Text.UTF8Encoding]::new($false))
$HeadMatches = [regex]::Matches(
  $Text, '(?m)^- production_validation_head: `([0-9a-f]{40})`$')
$WitnessMatches = [regex]::Matches(
  $Text, '(?m)^- production_witness_verdict: PASS$')
$FormalMatches = [regex]::Matches(
  $Text, '(?m)^- production_sgx_formal_verdict: PASS$')
if ($HeadMatches.Count -ne 1 -or $WitnessMatches.Count -ne 1 -or
    $FormalMatches.Count -ne 1) { throw 'Focused UHF gate is not frozen' }
$Head = $HeadMatches[0].Groups[1].Value
$LocalHead = (git -c safe.directory=$Worktree -C $Worktree rev-parse HEAD).Trim()
$RemoteLine = @(git ls-remote https://github.com/psiQAQ/pyscf.git "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $RemoteLine.Count -ne 1) { throw 'Remote head unavailable' }
$RemoteHead = ($RemoteLine[0] -split "`t")[0]
if ($LocalHead -ne $Head -or $RemoteHead -ne $Head) { throw 'Focused UHF head mismatch' }
$Configs = @(
  [pscustomobject]@{
    platform='windows-latest'; python='3.12'; artifact='precision-Windows-py3.12'
  },
  [pscustomobject]@{
    platform='ubuntu-latest'; python='3.12'; artifact='precision-Linux-py3.12'
  }
)
$Runs = New-Object 'System.Collections.Generic.List[object]'
foreach ($Config in $Configs) {
  $Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch `
    --event workflow_dispatch --limit 100 `
    --json databaseId,headSha,status,event,workflowName,headBranch,url)
  if ($LASTEXITCODE -ne 0) { throw 'Focused UHF baseline query failed' }
  $Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
  $Rows = @($Parsed)
  $KnownIds = [long[]]@($Runs | ForEach-Object { [long]$_.run_id })
  $UnknownActive = @($Rows | Where-Object {
    $_.headSha -eq $Head -and
    $_.status -in @('requested','queued','in_progress','waiting','pending') -and
    [long]$_.databaseId -notin $KnownIds
  })
  if ($UnknownActive.Count -ne 0) { throw 'Unknown focused UHF run already active' }
  $BeforeMax = 0L
  if ($Rows.Count -gt 0) {
    $BeforeMax = [long](($Rows | Measure-Object -Property databaseId -Maximum).Maximum)
  }
  $LatchRoot = 'D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches'
  [IO.Directory]::CreateDirectory($LatchRoot) | Out-Null
  $LatchPath = Join-Path $LatchRoot `
    "production-uhf-$Head-$($Config.platform)-py$($Config.python).json"
  $LatchPayload = [ordered]@{
    purpose='production-uhf'; repo=$Repo; workflow=$Workflow
    branch=$Branch; head=$Head; before_max=$BeforeMax
    nodeids_file='.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt'
    repeats=20; platform=$Config.platform; python=$Config.python; profile='4/4'
  }
  $LatchBytes = [Text.UTF8Encoding]::new($false).GetBytes(
    ($LatchPayload | ConvertTo-Json -Depth 4) + "`n")
  $LatchStream = [IO.File]::Open(
    $LatchPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write,
    [IO.FileShare]::None)
  try {
    $LatchStream.Write($LatchBytes, 0, $LatchBytes.Length)
    $LatchStream.Flush($true)
  }
  finally { $LatchStream.Dispose() }
  gh workflow run $Workflow --repo $Repo --ref $Branch `
    -f nodeids_file=.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt `
    -f repeats=20 -f platform=$Config.platform `
    -f python_version=$Config.python -f profile=4/4
  if ($LASTEXITCODE -ne 0) { throw 'Focused UHF dispatch failed' }
  $Candidate = $null
  for ($Attempt = 1; $Attempt -le 12; $Attempt++) {
    $Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch `
      --event workflow_dispatch --limit 100 `
      --json databaseId,headSha,status,event,workflowName,headBranch,url)
    if ($LASTEXITCODE -ne 0) { throw 'Focused UHF binding query failed' }
    $Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
    $Rows = @($Parsed)
    $Candidates = @($Rows | Where-Object {
      [long]$_.databaseId -gt $BeforeMax -and $_.headSha -eq $Head -and
      $_.headBranch -eq $Branch -and $_.event -eq 'workflow_dispatch' -and
      $_.workflowName -eq 'Precision investigation'
    })
    if ($Candidates.Count -eq 1) { $Candidate = $Candidates[0]; break }
    if ($Candidates.Count -gt 1) { throw 'Ambiguous focused UHF binding' }
    Start-Sleep -Seconds 5
  }
  if ($null -eq $Candidate) {
    throw "Focused UHF dispatch acknowledged but not bound; recover from $LatchPath without redispatch"
  }
  $Runs.Add([pscustomobject]@{
    run_id=[long]$Candidate.databaseId
    before_max=$BeforeMax
    head=$Head
    branch=$Branch
    platform=$Config.platform
    python=$Config.python
    profile='4/4'
    repeats=20
    artifact=$Config.artifact
    url=$Candidate.url
  })
}
$RunIds = [long[]]@($Runs.run_id)
if ($RunIds.Count -ne 2 -or @($RunIds | Select-Object -Unique).Count -ne 2) {
  throw 'Focused UHF run identity mismatch'
}
$Manifest = 'D:\workspace\pyscf\.agents\active\precision-ci\production-uhf-runs.json'
[IO.File]::WriteAllText(
  $Manifest, (($Runs | ConvertTo-Json -Depth 5) + "`n"),
  [Text.UTF8Encoding]::new($false))
$HeartbeatPath = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$IdLiteral = (@($RunIds) | ForEach-Object { "'$([long]$_)'" }) -join ','
$Command = "& '$HeartbeatPath' -TargetRunIds @($IdLiteral) " +
  "-TargetHeadSha '$Head' -IntervalSeconds 1800 -WakeAfterMinutes 300"
$Encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
$Monitor = Start-Process powershell.exe -WindowStyle Hidden -PassThru `
  -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-EncodedCommand',$Encoded)
```

Validate each artifact separately with the production validator, expected nodeids
file set to the UHF singleton, expected repeats 20, profile `omp4-blas4`, and
the manifest's exact platform/Python/artifact name. Use native count 26 for
Windows installed-wheel and 16 for Linux source-tree. Both must be `PASS`; a
structurally valid failure blocks PR update and returns to the generic
RED/state-transfer review.

Each per-configuration `CreateNew` latch is one-shot. If execution stops after a
dispatch, recover that exact config from its immutable `before_max` and identity
predicate; do not restart the complete block or dispatch through an existing
latch.

- [ ] **Step 3: Review the three production commits**

Run fresh full diffs from upstream to each production branch, focused tests, `git diff --check`, encoding/EOL and commit-scope checks. Request separate spec-compliance and code-quality reviews for:

1. Task 1 generic continuation commit;
2. Task 2 smearing predicate commit;
3. Task 3 SGX predicate commit;
4. stacked integration behavior and evidence.

No review may infer correctness from Actions conclusion alone; include frozen validator reports.

---

### Task 8: Update #3331 and Publish the Independent SGX PR

**Files:**
- Generic PR branch: only `hf.py`, `smearing.py`, `test_addons.py`.
- SGX PR branch: only `sgx.py`, `test_sgx.py`.
- Remote: existing PR #3331, later one new SGX PR.

**Interfaces:**
- Consumes: approved commits and Task 7 evidence.
- Produces: upstream-maintainable generic and SGX review paths.

- [ ] **Step 1: Present the exact #3331 rewrite checkpoint**

Show the user:

- old remote head `2f1be97e3b522333d9f5aa4dd50d96421a275abe` or the newly read exact replacement if upstream changed;
- new two-commit candidate head;
- three-file diff;
- local tests and UHF/SGX validation links;
- force-with-lease command that will be used.

Record the reviewed old remote head under exact key
`production_3331_expected_old_head`, then wait for explicit approval before
rewriting the existing PR branch.

- [ ] **Step 2: Update #3331 safely**

After approval, first re-read the remote head. Push only with an exact lease:

```powershell
$ErrorActionPreference = 'Stop'
$GenericWorktree = 'D:\workspace\pyscf\.worktrees\uhf-smearing-convergence-v2'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Text = [IO.File]::ReadAllText($ActiveDoc, [Text.UTF8Encoding]::new($false))
$Matches = [regex]::Matches(
  $Text, '(?m)^- production_3331_expected_old_head: `([0-9a-f]{40})`$')
if ($Matches.Count -ne 1) { throw 'Expected one approved #3331 old head' }
$ExpectedOldHead = $Matches[0].Groups[1].Value
$LiveRemote = @(git ls-remote https://github.com/psiQAQ/pyscf.git `
  refs/heads/codex/fix/uhf-smearing-convergence)
if ($LASTEXITCODE -ne 0 -or $LiveRemote.Count -ne 1) {
  throw '#3331 remote head is unavailable'
}
$LiveRemoteHead = ($LiveRemote[0] -split "`t")[0]
if ($LiveRemoteHead -ne $ExpectedOldHead) {
  throw '#3331 head changed after approval; repeat the checkpoint'
}
git -c safe.directory=$GenericWorktree -C $GenericWorktree push `
  --force-with-lease=refs/heads/codex/fix/uhf-smearing-convergence:$ExpectedOldHead `
  origin HEAD:refs/heads/codex/fix/uhf-smearing-convergence
```

Read back the remote SHA and PR diff. Update the PR body/comment with: historical failures, reviewer `conv_tol=1e-8` experiment, deterministic rejected-Extra RED, physical-state continuation, focused CI, and explicit statement that SGX is a separate dependent fix. Keep Draft until requested checks and review are ready.

- [ ] **Step 3: Wait for #3331 integration without automated CI polling**

Track PR state in `.agents/active/upstream-prs.md`. Do not create the SGX PR while #3331 is unmerged unless a maintainer explicitly authorizes a stacked dependency. PR-review waiting is not a CI heartbeat use case; do not leave a background poller.

- [ ] **Step 4: Rebase the SGX commit after #3331 merges**

Fetch live upstream, require #3331 merge commit is an ancestor, and create clean
worktree `D:\workspace\pyscf\.worktrees\sgx-extra-cycle-upstream-pr` on branch
`codex/fix/sgx-extra-cycle-convergence-upstream` from that exact master.
Cherry-pick only the Task 3 SGX commit. Require final diff exactly
`pyscf/sgx/sgx.py` and `pyscf/sgx/test/test_sgx.py`; run SGX unit tests and
original gradient nodeid again.

- [ ] **Step 5: Create the SGX PR**

Present the exact two-file diff, proposed body and evidence to the user and
obtain explicit approval; then push the clean SGX branch and create a PR titled:

```text
fix(sgx): require stable energy after extra cycles
```

The body must state:

- root cause: SGX accepted an Extra-cycle state when relaxed gradient passed but relaxed energy failed;
- generic continuation dependency: merged #3331;
- attempt-65 numeric evidence and reconstruction residual;
- unchanged original scientific test;
- local unit/stacked tests and installed-wheel 200/200 link;
- no LibXC, tolerance, displacement, retry or packaging change.

Process reviewer comments with focused RED/GREEN updates. If requested changes alter the convergence formula or PR boundary, return to design approval rather than silently expanding scope.

---

### Task 9: Run the Post-merge Three-nodeid Formal Matrix

**Files:**
- Validation-only branch and `.agents/archive/precision-ci/experiments/`.
- No production PR changes.

**Interfaces:**
- Consumes: upstream master containing both merged fixes and the eight frozen CI-infrastructure commits.
- Produces: 28 validated artifacts and 16,800 records.

- [ ] **Step 1: Build a fresh post-merge validation branch**

Fetch live upstream and require both merge commits are ancestors. From that exact master create worktree `D:\workspace\pyscf\.worktrees\libxc-712-post-merge-validation` and branch `codex/test/libxc-712-post-merge-validation`; cherry-pick only the eight CI-infrastructure commits listed in Task 4. Do not cherry-pick old production commits because they are already upstream. Require `.github/workflows/precision-libxc-712-nodeids.txt` contains exactly the three original nodeids and original `test_rks.py` matches upstream. Record exact keys `production_matrix_head`, `production_matrix_validator_sha256` and `production_matrix_next_profile: 1/1` in the active document.

Before the first wave, query the exact remote ref. Allow only absent or equal to
the local head; reject a different SHA. Push without force, read back with
`git ls-remote`, and require exact equality with `production_matrix_head`.

- [ ] **Step 2: Define the exact matrix and artifact mapping**

Use:

```powershell
$Platforms = @(
  [pscustomobject]@{ platform='windows-latest'; python='3.12'; artifact='precision-Windows-py3.12' },
  [pscustomobject]@{ platform='windows-latest'; python='3.13'; artifact='precision-Windows-py3.13' },
  [pscustomobject]@{ platform='ubuntu-latest';  python='3.8';  artifact='precision-Linux-py3.8' },
  [pscustomobject]@{ platform='ubuntu-latest';  python='3.12'; artifact='precision-Linux-py3.12' },
  [pscustomobject]@{ platform='ubuntu-latest';  python='3.13'; artifact='precision-Linux-py3.13' },
  [pscustomobject]@{ platform='macos-latest';   python='3.8';  artifact='precision-macOS-py3.8' },
  [pscustomobject]@{ platform='macos-latest';   python='3.13'; artifact='precision-macOS-py3.13' }
)
$Profiles = @('1/1', '4/1', '1/4', '4/4')
```

Each run uses repeats 200 and `.github/workflows/precision-libxc-712-nodeids.txt`.

- [ ] **Step 3: Dispatch one seven-run profile wave**

For each `$Profile`, dispatch all seven platform/Python entries. Before every dispatch:

1. reject any active exact-branch/config run;
2. freeze `BeforeMax` from successfully parsed `gh run list` JSON;
3. dispatch once;
4. bind exactly one new ID greater than `BeforeMax` with exact head/branch/event/workflow;
5. append the run identity and expected artifact to an atomic UTF-8-no-BOM wave manifest.

After all seven IDs are bound, start exactly one heartbeat with all IDs, interval 1800 and wake gate 300 minutes. Do not dispatch the next profile wave until all seven artifacts in the current wave are terminal and validated.

Run this complete block in a fresh shell for one exact `$Profile` value at a time:

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'psiQAQ/pyscf'
$Workflow = 'ci-precision-check.yml'
$Branch = 'codex/test/libxc-712-post-merge-validation'
$Worktree = 'D:\workspace\pyscf\.worktrees\libxc-712-post-merge-validation'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$ActiveText = [IO.File]::ReadAllText(
  $ActiveDoc, [Text.UTF8Encoding]::new($false))
$HeadMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_matrix_head: `([0-9a-f]{40})`$')
$ProfileMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_matrix_next_profile: `(1/1|4/1|1/4|4/4)`$')
if ($HeadMatches.Count -ne 1 -or $ProfileMatches.Count -ne 1) {
  throw 'Matrix head/profile gate is not uniquely frozen'
}
$Head = $HeadMatches[0].Groups[1].Value
$Profile = $ProfileMatches[0].Groups[1].Value
$LocalHead = (git -c safe.directory=$Worktree -C $Worktree rev-parse HEAD).Trim()
$RemoteLine = @(git ls-remote https://github.com/psiQAQ/pyscf.git "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $RemoteLine.Count -ne 1) { throw 'Matrix remote head unavailable' }
$RemoteHead = ($RemoteLine[0] -split "`t")[0]
if ($LocalHead -ne $Head -or $RemoteHead -ne $Head) { throw 'Matrix frozen head mismatch' }
if ($Profile -notin @('1/1','4/1','1/4','4/4')) {
  throw "Invalid profile: $Profile"
}
$Platforms = @(
  [pscustomobject]@{ platform='windows-latest'; python='3.12'; artifact='precision-Windows-py3.12' },
  [pscustomobject]@{ platform='windows-latest'; python='3.13'; artifact='precision-Windows-py3.13' },
  [pscustomobject]@{ platform='ubuntu-latest';  python='3.8';  artifact='precision-Linux-py3.8' },
  [pscustomobject]@{ platform='ubuntu-latest';  python='3.12'; artifact='precision-Linux-py3.12' },
  [pscustomobject]@{ platform='ubuntu-latest';  python='3.13'; artifact='precision-Linux-py3.13' },
  [pscustomobject]@{ platform='macos-latest';   python='3.8';  artifact='precision-macOS-py3.8' },
  [pscustomobject]@{ platform='macos-latest';   python='3.13'; artifact='precision-macOS-py3.13' }
)
$Runs = New-Object 'System.Collections.Generic.List[object]'
foreach ($Platform in $Platforms) {
  $Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch `
    --event workflow_dispatch --limit 100 `
    --json databaseId,headSha,status,event,workflowName,headBranch,url)
  if ($LASTEXITCODE -ne 0) { throw 'Matrix baseline query failed' }
  $Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
  $Rows = @($Parsed)
  $Active = @($Rows | Where-Object {
    $_.headSha -eq $Head -and
    $_.status -in @('requested','queued','in_progress','waiting','pending')
  })
  $KnownIds = [long[]]@($Runs | ForEach-Object { [long]$_.run_id })
  $UnknownActive = @($Active | Where-Object {
    [long]$_.databaseId -notin $KnownIds
  })
  if ($UnknownActive.Count -ne 0) {
    throw 'Unknown exact-head matrix run already active'
  }
  $BeforeMax = 0L
  if ($Rows.Count -gt 0) {
    $BeforeMax = [long](($Rows | Measure-Object -Property databaseId -Maximum).Maximum)
  }
  $LatchRoot = 'D:\workspace\pyscf\.agents\active\precision-ci\dispatch-latches'
  [IO.Directory]::CreateDirectory($LatchRoot) | Out-Null
  $LatchPath = Join-Path $LatchRoot `
    "matrix-$Head-$($Profile.Replace('/','-'))-$($Platform.platform)-py$($Platform.python).json"
  $LatchPayload = [ordered]@{
    purpose='post-merge-matrix'; repo=$Repo; workflow=$Workflow
    branch=$Branch; head=$Head; before_max=$BeforeMax
    nodeids_file='.github/workflows/precision-libxc-712-nodeids.txt'
    repeats=200; platform=$Platform.platform; python=$Platform.python; profile=$Profile
  }
  $LatchBytes = [Text.UTF8Encoding]::new($false).GetBytes(
    ($LatchPayload | ConvertTo-Json -Depth 4) + "`n")
  $LatchStream = [IO.File]::Open(
    $LatchPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write,
    [IO.FileShare]::None)
  try {
    $LatchStream.Write($LatchBytes, 0, $LatchBytes.Length)
    $LatchStream.Flush($true)
  }
  finally { $LatchStream.Dispose() }
  gh workflow run $Workflow --repo $Repo --ref $Branch `
    -f nodeids_file=.github/workflows/precision-libxc-712-nodeids.txt `
    -f repeats=200 -f platform=$Platform.platform `
    -f python_version=$Platform.python -f profile=$Profile
  if ($LASTEXITCODE -ne 0) { throw "Dispatch failed: $($Platform.platform)/$($Platform.python)" }

  $Candidate = $null
  for ($Attempt = 1; $Attempt -le 12; $Attempt++) {
    $Raw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch `
      --event workflow_dispatch --limit 100 `
      --json databaseId,headSha,status,event,workflowName,headBranch,url)
    if ($LASTEXITCODE -ne 0) { throw 'Matrix binding query failed' }
    $Parsed = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
    $Rows = @($Parsed)
    $Candidates = @($Rows | Where-Object {
      [long]$_.databaseId -gt $BeforeMax -and $_.headSha -eq $Head -and
      $_.headBranch -eq $Branch -and $_.event -eq 'workflow_dispatch' -and
      $_.workflowName -eq 'Precision investigation'
    })
    if ($Candidates.Count -eq 1) { $Candidate = $Candidates[0]; break }
    if ($Candidates.Count -gt 1) { throw 'Ambiguous matrix run binding' }
    Start-Sleep -Seconds 5
  }
  if ($null -eq $Candidate) {
    throw "Matrix dispatch acknowledged but not bound; recover from $LatchPath without redispatch"
  }
  $Runs.Add([pscustomobject]@{
    run_id = [long]$Candidate.databaseId
    head = $Head
    branch = $Branch
    platform = $Platform.platform
    python = $Platform.python
    profile = $Profile
    artifact = $Platform.artifact
    url = $Candidate.url
  })
}
$Manifest = "D:\workspace\pyscf\.agents\active\precision-ci\matrix-$($Profile.Replace('/','-')).json"
[IO.File]::WriteAllText(
  $Manifest, (($Runs | ConvertTo-Json -Depth 5) + "`n"),
  [Text.UTF8Encoding]::new($false))
$RunIds = [long[]]@($Runs.run_id)
if ($RunIds.Count -ne 7 -or @($RunIds | Select-Object -Unique).Count -ne 7) {
  throw 'Matrix wave did not bind seven unique run IDs'
}
$HeartbeatPath = 'D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1'
$IdLiteral = ($RunIds | ForEach-Object { "'$_'" }) -join ','
$Command = "& '$HeartbeatPath' -TargetRunIds @($IdLiteral) " +
  "-TargetHeadSha '$Head' -IntervalSeconds 1800 -WakeAfterMinutes 300"
$Encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
$Monitor = Start-Process powershell.exe -WindowStyle Hidden -PassThru `
  -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-EncodedCommand',$Encoded)
```

The seven per-configuration `CreateNew` latches are immutable one-shot dispatch
journals. If a shell stops after dispatch, recover only that configuration from
its latch and exact `databaseId > before_max` predicate, append the unique bound
ID to the wave manifest, and never rerun `gh workflow run` through an existing
latch.

- [ ] **Step 4: Handle the 300-minute wake gate**

If heartbeat wakes for elapsed time rather than terminal state, re-query full run identity and the single `precision` job. Cancel only when all of these are true for that exact ID: attempt 1, workflow_dispatch, exact branch/head/workflow, job name `precision`, job `in_progress`, parseable `startedAt`, elapsed at least 300 minutes. Use `gh run cancel $RunId --repo psiQAQ/pyscf`, then classify it as timeout/operational, never numerical failure. Queued/waiting/requested jobs are not canceled by elapsed logic.

- [ ] **Step 5: Validate every artifact before the next wave**

For each terminal run, use the strict Task 6 artifact-envelope predicate: empty
`total_count=0` plus empty array is latency; any nonempty shape must be exactly
one positive-ID, nonexpired, positive-size, `sha256:` artifact with the manifest
name. Require exact run attempt/event/head/branch/workflow and one completed
`precision` job before downloading. Store each evidence directory as
`RUNID-matrix-PROFILE-PLATFORM-pyPYTHON` and write its exact `run.json`.
Poll at most 12 times at ten-second intervals; a still-empty envelope keeps that
exact run in terminal-validation state and never triggers redispatch or the next
wave.
Then run this fresh-shell validation loop:

```powershell
$ErrorActionPreference = 'Stop'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Worktree = 'D:\workspace\pyscf\.worktrees\libxc-712-post-merge-validation'
$Branch = 'codex/test/libxc-712-post-merge-validation'
$Validator = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py'
$ActiveText = [IO.File]::ReadAllText(
  $ActiveDoc, [Text.UTF8Encoding]::new($false))
$HeadMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_matrix_head: `([0-9a-f]{40})`$')
$ProfileMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_matrix_next_profile: `(1/1|4/1|1/4|4/4)`$')
$ValidatorMatches = [regex]::Matches(
  $ActiveText, '(?m)^- production_matrix_validator_sha256: `([0-9a-f]{64})`$')
if ($HeadMatches.Count -ne 1 -or $ProfileMatches.Count -ne 1 -or
    $ValidatorMatches.Count -ne 1) { throw 'Matrix validation gate is not unique' }
$Head = $HeadMatches[0].Groups[1].Value
$Profile = $ProfileMatches[0].Groups[1].Value
$ExpectedValidatorHash = $ValidatorMatches[0].Groups[1].Value
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Validator).Hash.ToLowerInvariant() -ne
    $ExpectedValidatorHash) { throw 'Matrix validator hash mismatch' }
$Manifest = "D:\workspace\pyscf\.agents\active\precision-ci\matrix-$($Profile.Replace('/','-')).json"
$ParsedRuns = Get-Content -Raw -Encoding UTF8 -LiteralPath $Manifest |
  ConvertFrom-Json -ErrorAction Stop
$Runs = @($ParsedRuns)
if ($Runs.Count -ne 7 -or @($Runs.run_id | Select-Object -Unique).Count -ne 7) {
  throw 'Matrix manifest identity mismatch'
}
$ProfileMap = @{
  '1/1' = 'omp1-blas1'
  '4/1' = 'omp4-blas1'
  '1/4' = 'omp1-blas4'
  '4/4' = 'omp4-blas4'
}
foreach ($Entry in $Runs) {
  if ($Entry.head -ne $Head -or $Entry.branch -ne $Branch -or
      $Entry.profile -ne $Profile) { throw 'Matrix manifest row mismatch' }
  $PlatformSlug = ([string]$Entry.platform).Replace('-latest','')
  $Evidence = "D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$($Entry.run_id)-matrix-$($Profile.Replace('/','-'))-$PlatformSlug-py$($Entry.python)"
  $Mode = if ($Entry.platform -eq 'windows-latest') { 'installed-wheel' } else { 'source-tree' }
  $NativeCount = if ($Mode -eq 'installed-wheel') { '26' } else { '16' }
  $Args = @(
    $Evidence,
    '--mode', $Mode,
    '--expected-sha', $Head,
    '--expected-nodeids-file', "$Worktree\.github\workflows\precision-libxc-712-nodeids.txt",
    '--expected-profile', $ProfileMap[$Profile],
    '--expected-repeats', '200',
    '--expected-platform', [string]$Entry.platform,
    '--expected-python', [string]$Entry.python,
    '--expected-native-count', $NativeCount,
    '--run-metadata', "$Evidence\run.json",
    '--expected-run-id', [string]$Entry.run_id,
    '--expected-branch', $Branch,
    '--expected-artifact-name', [string]$Entry.artifact,
    '--report', "$Evidence\production-validation.json"
  )
  conda run --no-capture-output -n pyscf-win313-test python $Validator @Args
  if ($LASTEXITCODE -ne 0) { throw "Artifact INVALID: $($Entry.run_id)" }
  $Report = Get-Content -Raw -Encoding UTF8 `
    -LiteralPath "$Evidence\production-validation.json" |
    ConvertFrom-Json -ErrorAction Stop
  if (-not $Report.valid -or $Report.verdict -ne 'PASS') {
    throw "Matrix scientific gate failed: $($Entry.run_id) $($Report.verdict)"
  }
}
```

Windows mode is `installed-wheel`; Unix mode is `source-tree`, with the documented Linux `pyscf-dispersion -> pyscf not installed` pip-check advisory accepted only under source-tree mode. Require seven `PASS` reports before advancing. With `apply_patch`, atomically replace the single active-document next-profile value: `1/1 -> 4/1 -> 1/4 -> 4/4 -> complete`. Never dispatch a wave whose predecessor is not fully validated.

- [ ] **Step 6: Prove the aggregate gate**

After four waves, aggregate reports must show:

```text
28 unique runs
28 unique artifacts
7 platform/Python combinations
4 profiles per combination
3 exact nodeids per artifact
200 attempts per nodeid per artifact
16,800 records
16,800 pass
0 fail
0 retry
0 missing log/reference
```

Write an index report with #3336 URL/merge, generic and SGX PR URLs/merges,
run URLs, artifact IDs/digests, tested SHA, runtime LibXC values and validator
SHA. Any missing/failed artifact keeps the corresponding nodeid unresolved.

---

### Task 10: Update Issue #3312 and Retire Investigation Pollers

**Files:**
- Update `.agents/active/precision-stability.md`, `.agents/active/upstream-prs.md`.
- Move completed phases to `.agents/completed/` as appropriate.
- Remote: edit/comment on `pyscf/pyscf#3312` only after the final gate.

**Interfaces:**
- Consumes: two merged PRs and the 28-artifact aggregate report.
- Produces: accurate public nodeid status and closed local monitoring lifecycle.

- [ ] **Step 1: Freeze the final public evidence set**

Require exact URLs/SHAs for #3331 merge, SGX merge, post-merge validation head, all 28 runs/artifacts and aggregate report. Independently re-run the aggregate checker. If any of the three nodeids lacks the full gate, keep it unchecked and follow the unresolved path below.

- [ ] **Step 2: Prepare a fail-closed issue-body edit**

Fetch `pyscf/pyscf#3312` body and `updatedAt`. Require each of the three exact nodeid strings occurs exactly once in a Markdown checkbox line. Change only resolved target lines from `- [ ]` to `- [x]`; do not reorder or rewrite unrelated issue content. Write the candidate body to an ignored UTF-8-no-BOM file, show a diff, and re-query `updatedAt` before the remote edit. If it changed, regenerate the candidate from the new body.

```powershell
$ErrorActionPreference = 'Stop'
$Raw = @(gh issue view 3312 --repo pyscf/pyscf --json body,updatedAt,url)
if ($LASTEXITCODE -ne 0) { throw 'Issue read failed' }
$Issue = ConvertFrom-Json -InputObject ($Raw -join "`n") -ErrorAction Stop
$ExpectedUpdatedAt = [string]$Issue.updatedAt
$Body = [string]$Issue.body
$Nodeids = @(
  'pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda',
  'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad',
  'pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_hse03_tda'
)
foreach ($Nodeid in $Nodeids) {
  $Old = '- [ ] `' + $Nodeid + '`'
  $Already = '- [x] `' + $Nodeid + '`'
  $OldCount = [regex]::Matches($Body, [regex]::Escape($Old)).Count
  $AlreadyCount = [regex]::Matches($Body, [regex]::Escape($Already)).Count
  if ($OldCount -eq 1 -and $AlreadyCount -eq 0) {
    $Body = $Body.Replace($Old, $Already)
  }
  elseif ($OldCount -ne 0 -or $AlreadyCount -ne 1) {
    throw "Unexpected checkbox identity for $Nodeid"
  }
}
$CandidateBodyPath = 'D:\workspace\pyscf\.agents\active\precision-ci\issue-3312-body.md'
[IO.File]::WriteAllText(
  $CandidateBodyPath, $Body,
  [Text.UTF8Encoding]::new($false))
$CandidateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $CandidateBodyPath).Hash.ToLowerInvariant()
$LockPath = 'D:\workspace\pyscf\.agents\active\precision-ci\issue-3312-lock.json'
$Lock = [ordered]@{
  updatedAt = $ExpectedUpdatedAt
  candidateBodySha256 = $CandidateHash
}
[IO.File]::WriteAllText(
  $LockPath, (($Lock | ConvertTo-Json) + "`n"),
  [Text.UTF8Encoding]::new($false))
$ConfirmRaw = @(gh issue view 3312 --repo pyscf/pyscf --json updatedAt)
if ($LASTEXITCODE -ne 0) { throw 'Issue optimistic-lock read failed' }
$Confirm = ConvertFrom-Json -InputObject ($ConfirmRaw -join "`n") -ErrorAction Stop
if ([string]$Confirm.updatedAt -ne $ExpectedUpdatedAt) {
  throw 'Issue changed while preparing the edit; regenerate from live body'
}
```

- [ ] **Step 3: Post the evidence comment**

Load the frozen aggregate JSON and require fields `nodeids`,
`libxc_integration_pr`, `libxc_integration_merge`, `generic_pr`, `generic_merge`,
`sgx_pr`, `sgx_merge`, `mechanism_run`, `mechanism_artifact`, `formal_run`,
`formal_artifact`, `matrix_index_url`, `tested_sha`, `records`, and
`runtime_libxc`. Construct the exact comment without placeholder text:

```powershell
$IndexPath = 'D:\workspace\pyscf\.agents\archive\precision-ci\experiments\libxc-3nodeid-post-merge-index.json'
$Index = Get-Content -Raw -Encoding UTF8 -LiteralPath $IndexPath |
  ConvertFrom-Json -ErrorAction Stop
if (@($Index.nodeids).Count -ne 3 -or [long]$Index.records -ne 16800) {
  throw 'Final evidence index is incomplete'
}
$ResolvedLines = @($Index.nodeids | ForEach-Object {
  "- ``$_`` — 5,600/5,600 original-assertion attempts passed"
})
$CommentLines = @(
  'LibXC-related nodeid closure',
  '',
  'Resolved nodeids'
) + $ResolvedLines + @(
  '',
  'Root cause',
  "- Dependency integration: $($Index.libxc_integration_pr) supplied the maintained LibXC $($Index.runtime_libxc) / MAXORDER=3 build path used by all three original tests.",
  '- PBC HSE06/HSE03 required no nodeid-specific algorithm or assertion change; their closure is the released-dependency integration plus the unchanged post-merge matrix.',
  '- SGX additionally exposed a PySCF Extra-cycle convergence asymmetry; LibXC 7.1.2 was the verified runtime, not that numerical defect source.',
  '',
  'Maintained fix',
  "- LibXC release integration: $($Index.libxc_integration_pr), merge ``$($Index.libxc_integration_merge)``.",
  "- Generic rejected-Extra continuation: $($Index.generic_pr), merge ``$($Index.generic_merge)``.",
  "- SGX energy-and-gradient predicate: $($Index.sgx_pr), merge ``$($Index.sgx_merge)``.",
  '',
  'Evidence',
  "- Mechanism: run $($Index.mechanism_run), artifact $($Index.mechanism_artifact), attempt 65.",
  "- Post-fix Windows 3.12 omp4-blas1: run $($Index.formal_run), artifact $($Index.formal_artifact), 200/200.",
  "- Post-merge matrix: $($Index.matrix_index_url), tested SHA ``$($Index.tested_sha)``, 28 artifacts and 16,800/16,800 records."
)
$CommentPath = 'D:\workspace\pyscf\.agents\active\precision-ci\issue-3312-libxc-comment.md'
[IO.File]::WriteAllText(
  $CommentPath, ($CommentLines -join "`n") + "`n",
  [Text.UTF8Encoding]::new($false))
```

- [ ] **Step 4: Apply and verify the remote update**

Present the candidate body diff, exact comment and evidence index to the user;
obtain explicit approval for this external issue write. Then use a fresh shell,
re-establish the paths and recheck the optimistic lock immediately before the
write:

```powershell
$ErrorActionPreference = 'Stop'
$CandidateBodyPath = 'D:\workspace\pyscf\.agents\active\precision-ci\issue-3312-body.md'
$CommentPath = 'D:\workspace\pyscf\.agents\active\precision-ci\issue-3312-libxc-comment.md'
$LockPath = 'D:\workspace\pyscf\.agents\active\precision-ci\issue-3312-lock.json'
if (-not (Test-Path -LiteralPath $CandidateBodyPath -PathType Leaf) -or
    -not (Test-Path -LiteralPath $CommentPath -PathType Leaf) -or
    -not (Test-Path -LiteralPath $LockPath -PathType Leaf)) {
  throw 'Prepared issue update files are missing'
}
$Lock = Get-Content -Raw -Encoding UTF8 -LiteralPath $LockPath |
  ConvertFrom-Json -ErrorAction Stop
$CandidateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $CandidateBodyPath).Hash.ToLowerInvariant()
if ($CandidateHash -ne [string]$Lock.candidateBodySha256) {
  throw 'Candidate issue body changed after approval'
}
$IssueRaw = @(gh issue view 3312 --repo pyscf/pyscf --json updatedAt)
if ($LASTEXITCODE -ne 0) { throw 'Final issue lock query failed' }
$LiveIssue = ConvertFrom-Json -InputObject ($IssueRaw -join "`n") -ErrorAction Stop
if ([string]$LiveIssue.updatedAt -ne [string]$Lock.updatedAt) {
  throw 'Issue changed after approval; regenerate and reapprove the update'
}
gh issue edit 3312 --repo pyscf/pyscf --body-file $CandidateBodyPath
if ($LASTEXITCODE -ne 0) { throw 'Issue body update failed' }
gh issue comment 3312 --repo pyscf/pyscf --body-file $CommentPath
if ($LASTEXITCODE -ne 0) { throw 'Issue comment failed' }
```

Read back the issue body and new comment URL. Require each resolved checkbox and every cited link is present. Do not close the issue unless its broader owner explicitly requests closure.

- [ ] **Step 5: Route unresolved results instead of claiming completion**

If any nodeid failed the final matrix, do not mark it complete. Preserve its first valid failure artifact, add an issue comment stating `unresolved` with exact environment/signature, create a new isolated investigation branch from current upstream master, and return to a new approved RED/root-cause design. Do not alter the passed nodeids' evidence.

- [ ] **Step 6: Retire monitoring and complete the goal**

Verify no target CI is queued/in-progress, no native heartbeat is active for this thread, no matching PS1 process survives, and no dispatch latch can trigger a duplicate run. Archive completed active phases, record remaining unrelated work, then mark the Goal complete only if all three nodeids and issue #3312 update satisfy the approved spec.

---

## Plan Completion Checklist

- [ ] Generic and SGX production commits remain independently reviewable.
- [ ] Every production change has an observed RED and fresh GREEN.
- [ ] Original SGX finite-difference test is byte-identical to live upstream.
- [ ] No diagnostic/CI asset appears in either production PR.
- [ ] Windows witness and SGX 200-repeat are strict installed-wheel PASS.
- [ ] #3331 and SGX upstream integration are accepted before final closure.
- [ ] Final matrix contains exactly 28 artifacts and 16,800 passing records.
- [ ] Issue #3312 is updated per nodeid with public evidence.
- [ ] All heartbeat/poller state is removed only after the full goal completes.
