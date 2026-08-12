# Platform-aware LibXC Linkage Validator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the local production-evidence validator so real 16-library macOS and Linux source-tree artifacts prove LibXC through their platform linkage, then revalidate the already-frozen macOS witness without rerunning CI.

**Architecture:** Keep the change inside the existing single-file ignored validator. Make its test fixture reflect the real Unix inventory, branch `_check_libxc_linkage` by platform, preserve the Windows wheel-local DLL contract, freeze the reviewed validator under a new hash, and validate the same immutable GitHub artifact in a new archive attempt. The existing invalid attempt remains immutable; the existing pair transport remains intentionally unusable because it is bound to the old validator hash.

**Tech Stack:** Python 3.13 standard library (`unittest`, `pathlib`, `json`), Windows PowerShell 5.1, `gh` CLI, Git.

## Global Constraints

- Approved design: `docs/superpowers/specs/2026-08-12-platform-aware-libxc-linkage-validator-design.md` at commit `82cea527c8a73674d2ca91e93491f16558120d8e` and file SHA-256 `5ca28bd5b12489019c9be8cfc51a0cbf55786f694311d9fb63997003c6510ca1`.
- Original validator SHA-256: `d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c`.
- Original macOS evidence: run `31577510832`, job `94052864840`, artifact `9133834443`, artifact digest `sha256:73f108d3545bf365ffc72374f0e3e5b7831bc94d64e0de0bf3f0108813ba5300`, size `7400`, head `2a2237bc323b8473d19979aaa56a0e8ff88cee04`.
- Preserve `attempt-0001`, validator/report SHA bindings, and its `INVALID` verdict byte-for-byte.
- Do not rerun or dispatch CI, enter the Windows/Linux pair, update a PR/issue, change dependencies, modify PySCF source, relax scientific assertions, or stage/delete the 26 known DLLs.
- The corrected witness proves transport/provenance only; repeats `1` is not scientific stability.
- Use `conda run --no-capture-output -n pyscf-win313-test python` without installing packages.
- All edited ignored Python/Markdown/JSON files are strict UTF-8 without BOM, LF-only, and final-LF.
- Existing pair addendum/transport files remain immutable and bound to the old validator hash; a later reviewed mechanical rebind is required before pair execution.

---

### Task 1: Reproduce the Unix inventory defect and make the positive path pass

**Files:**
- Modify: `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py`
- Create: `D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-12-platform-aware-libxc-linkage-validator\task-1-report.md`

**Interfaces:**
- Consumes: frozen validator SHA `d9b559e...4292c` and its current `ProductionSelfTest` fixture.
- Produces: real-shaped 16-library Unix fixtures and a first platform-aware `_check_libxc_linkage` implementation.

- [ ] **Step 1: Freeze the baseline before editing**

Run:

```powershell
$ErrorActionPreference='Stop'
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py'
if((Get-FileHash $Validator -Algorithm SHA256).Hash.ToLowerInvariant() -cne
  'd9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c') {
    throw 'baseline validator drift'
}
conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test
if($LASTEXITCODE -ne 0) { throw 'baseline self-test failed' }
```

Expected: `Ran 50 tests` and `OK`.

- [ ] **Step 2: Write the real-shaped Unix fixture RED**

Replace only the fixture's native-name/count construction with:

```python
    suffix = '.dll' if platform_name == 'windows-latest' else (
        '.dylib' if platform_name == 'macos-latest' else '.so')
    if platform_name == 'windows-latest':
        names = [f'lib{i:02d}{suffix}' for i in range(24)] + [
            f'libxc{suffix}', f'libxc_itrf{suffix}']
        expected_native_count = 26
    else:
        names = [name + suffix for name in (
            'libagf2', 'libao2mo', 'libcc', 'libccsdt', 'libcgto',
            'libcvhf', 'libdft', 'libfci', 'libmcscf', 'libmp',
            'libnp_helper', 'libpbc', 'libpdft', 'libri',
            'libxc_itrf', 'libxcfun_itrf')]
        expected_native_count = 16
```

For `libxc_itrf`, generate real linkage shapes:

```python
        if name == f'libxc_itrf{suffix}':
            if suffix == '.dylib':
                output = '@rpath/libxc.15.dylib (compatibility version 15.0.0)'
            elif suffix == '.so':
                output = f'libxc.so => {lib_root / "deps" / "lib" / "libxc.so"} (0x1)'
            else:
                output = f'libxc.dll => {lib_root / "libxc.dll"} (0x1)'
```

Set the fixture option field to `expected_native_count=expected_native_count` instead of the old unconditional `26`. Do not edit `_check_libxc_linkage` yet.

- [ ] **Step 3: Run the RED and inspect the boundary**

Run the full self-test once:

```powershell
conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test
if($LASTEXITCODE -eq 0) { throw 'Unix real-inventory RED did not fail' }
```

Expected: only `test_macos_source_tree_singleton_pass` and `test_linux_source_tree_three_nodeids_200_repeats_pass` fail, both because `Native inventory lacks LibXC libraries`; Windows tests remain green.

- [ ] **Step 4: Implement the smallest positive platform branch**

Replace `_check_libxc_linkage` with this deliberately positive-path-only version:

```python
def _check_libxc_linkage(by_name, package_lib, platform_name, path_kind):
    suffix = '.dll' if platform_name == 'Windows' else (
        '.dylib' if platform_name == 'Darwin' else '.so')
    itrf = 'libxc_itrf' + suffix
    libxc = 'libxc' + suffix
    _require(itrf in by_name, 'Native inventory lacks LibXC interface library')
    output = by_name[itrf]['linkage']['output']
    if platform_name == 'Darwin':
        deps = [line for line in output.splitlines()
                if '@rpath/libxc.15.dylib' in line]
        _require(len(deps) == 1,
                 'libxc_itrf.dylib must list exactly one LibXC rpath dependency')
        return
    if path_kind == 'windows':
        _require(libxc in by_name,
                 'Native inventory lacks wheel-local LibXC library')
        native = pathlib.PureWindowsPath(str(package_lib / libxc))
        cygwin = pathlib.PurePosixPath(
            '/' + native.drive[0].casefold(), *native.parts[1:]).as_posix().casefold()
        targets = []
        for line in output.splitlines():
            pieces = line.strip().split('=>')
            if len(pieces) == 2 and pieces[0].strip().casefold() == 'libxc.dll':
                targets.append(pieces[1].strip().rsplit(' (', 1)[0].casefold())
        _require(len(targets) == 1 and targets[0] in
                 (str(native).casefold(), cygwin),
                 'libxc_itrf.dll does not resolve local libxc.dll')
        return
    expected = str(package_lib / 'deps' / 'lib' / libxc)
    targets = []
    for line in output.splitlines():
        pieces = line.strip().split('=>')
        if len(pieces) == 2 and pieces[0].strip() == 'libxc.so':
            targets.append(pieces[1].strip().rsplit(' (', 1)[0])
    _require(expected in targets,
             'libxc_itrf.so does not resolve checkout deps/lib/libxc.so')
```

- [ ] **Step 5: Run the positive GREEN**

Run:

```powershell
conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test
if($LASTEXITCODE -ne 0) { throw 'positive platform linkage GREEN failed' }
```

Expected: all existing 50 tests pass with the real-shaped Unix fixtures.

---

### Task 2: Make each platform linkage parser fail closed

**Files:**
- Modify: `D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py`
- Modify: `D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-12-platform-aware-libxc-linkage-validator\task-1-report.md`

**Interfaces:**
- Consumes: Task 1's real-shaped fixture and positive-path implementation.
- Produces: exact Darwin/Linux candidate parsing, unchanged strict Windows containment, and 58 passing self-tests.

- [ ] **Step 1: Add a test-only linkage mutation helper**

Add inside `ProductionSelfTest`:

```python
    def _set_libxc_itrf_output(self, options, suffix, output):
        runtime_path = options.evidence_dir / 'environment' / 'runtime.json'
        runtime = load_json_strict(runtime_path)
        item = next(entry for entry in runtime['native_libraries']
                    if entry['path'].endswith('libxc_itrf' + suffix))
        item['linkage']['output'] = output
        _write_json(runtime_path, runtime)
```

- [ ] **Step 2: Write Darwin and Linux strictness RED tests plus the Windows regression test**

Add these tests:

```python
    def test_macos_rejects_missing_libxc_rpath(self):
        options = self._case('source-tree', 'macos-latest', self.nodeids, 1)
        self._set_libxc_itrf_output(options, '.dylib', '')
        with self.assertRaises(InvalidEvidence):
            validate_evidence(options)

    def test_macos_rejects_duplicate_libxc_rpath(self):
        options = self._case('source-tree', 'macos-latest', self.nodeids, 1)
        line = '@rpath/libxc.15.dylib (compatibility version 15.0.0)'
        self._set_libxc_itrf_output(options, '.dylib', line + '\n' + line)
        with self.assertRaises(InvalidEvidence):
            validate_evidence(options)

    def test_macos_rejects_additional_wrong_version_libxc_rpath(self):
        options = self._case('source-tree', 'macos-latest', self.nodeids, 1)
        self._set_libxc_itrf_output(
            options, '.dylib',
            '@rpath/libxc.15.dylib (compatibility version 15.0.0)\n'
            '@rpath/libxc.14.dylib (compatibility version 14.0.0)')
        with self.assertRaises(InvalidEvidence):
            validate_evidence(options)

    def test_linux_rejects_external_libxc_before_checkout_target(self):
        options = self._case('source-tree', 'ubuntu-latest', self.nodeids, 1)
        expected = '/home/runner/work/pyscf/pyscf/pyscf/lib/deps/lib/libxc.so'
        self._set_libxc_itrf_output(
            options, '.so',
            f'libxc.so => /usr/lib/libxc.so (0x1)\nlibxc.so => {expected} (0x2)')
        with self.assertRaises(InvalidEvidence):
            validate_evidence(options)

    def test_linux_rejects_duplicate_checkout_libxc_targets(self):
        options = self._case('source-tree', 'ubuntu-latest', self.nodeids, 1)
        expected = '/home/runner/work/pyscf/pyscf/pyscf/lib/deps/lib/libxc.so'
        self._set_libxc_itrf_output(
            options, '.so',
            f'libxc.so => {expected} (0x1)\nlibxc.so => {expected} (0x2)')
        with self.assertRaises(InvalidEvidence):
            validate_evidence(options)

    def test_linux_rejects_unresolved_libxc(self):
        options = self._case('source-tree', 'ubuntu-latest', self.nodeids, 1)
        self._set_libxc_itrf_output(options, '.so', 'libxc.so => not found')
        with self.assertRaises(InvalidEvidence):
            validate_evidence(options)

    def test_linux_rejects_wrong_checkout_libxc_path(self):
        options = self._case('source-tree', 'ubuntu-latest', self.nodeids, 1)
        self._set_libxc_itrf_output(
            options, '.so',
            'libxc.so => /home/runner/work/other/pyscf/lib/deps/lib/libxc.so (0x1)')
        with self.assertRaises(InvalidEvidence):
            validate_evidence(options)

    def test_windows_still_requires_wheel_local_libxc_inventory_entry(self):
        options = self._case('installed-wheel', 'windows-latest', self.nodeids, 1)
        runtime_path = options.evidence_dir / 'environment' / 'runtime.json'
        runtime = load_json_strict(runtime_path)
        runtime['native_libraries'] = [
            item for item in runtime['native_libraries']
            if not item['path'].endswith('libxc.dll')]
        options.expected_native_count -= 1
        _write_json(runtime_path, runtime)
        with self.assertRaises(InvalidEvidence):
            validate_evidence(options)
```

- [ ] **Step 3: Run the parser RED**

Run the full self-test once. Expected: at least
`test_macos_rejects_additional_wrong_version_libxc_rpath`,
`test_linux_rejects_external_libxc_before_checkout_target`, and
`test_linux_rejects_duplicate_checkout_libxc_targets` fail because the
positive-only parser accepts extra candidates. The missing/unresolved/wrong
path and Windows characterization tests may already pass and are retained as
regression coverage.

- [ ] **Step 4: Tighten only the two Unix candidate lists**

Replace the Darwin branch with:

```python
    if platform_name == 'Darwin':
        tokens = [line.strip().split(' ', 1)[0]
                  for line in output.splitlines() if line.strip()]
        deps = [token for token in tokens
                if token.startswith('@rpath/libxc.')
                and token.endswith('.dylib')]
        _require(deps == ['@rpath/libxc.15.dylib'],
                 'libxc_itrf.dylib must resolve exactly one '
                 '@rpath/libxc.15.dylib dependency')
        return
```

Replace the Linux final requirement with:

```python
    expected = str(package_lib / 'deps' / 'lib' / libxc)
    targets = []
    for line in output.splitlines():
        pieces = line.strip().split('=>')
        if len(pieces) == 2 and pieces[0].strip() == 'libxc.so':
            targets.append(pieces[1].strip().rsplit(' (', 1)[0])
    _require(targets == [expected],
             'libxc_itrf.so must resolve exactly one checkout '
             'deps/lib/libxc.so')
```

Do not change the Windows branch.

- [ ] **Step 5: Run final GREEN and static checks**

Run:

```powershell
conda run --no-capture-output -n pyscf-win313-test python $Validator --self-test
if($LASTEXITCODE -ne 0) { throw 'full corrected self-test failed' }
conda run --no-capture-output -n pyscf-win313-test python -m py_compile $Validator
if($LASTEXITCODE -ne 0) { throw 'validator py_compile failed' }
$Bytes=[IO.File]::ReadAllBytes($Validator)
if($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) {
    throw 'validator has UTF-8 BOM'
}
if(@($Bytes | Where-Object { $_ -eq 13 }).Count -ne 0 -or $Bytes[-1] -ne 10) {
    throw 'validator is not LF-only with final LF'
}
```

Expected: `Ran 58 tests`, `OK`, and `py_compile` exit `0`.

- [ ] **Step 6: Write and read back the implementation report**

Use `apply_patch` to create `task-1-report.md` containing:

- original validator SHA and `50/50` baseline;
- exact positive RED failure names/messages;
- exact parser RED failure names/messages;
- final `58/58` output;
- `py_compile`, encoding, scope, and corrected validator SHA;
- explicit statement that no CI, Goal, heartbeat, pair, dependency, issue, or PySCF source operation occurred.

Re-read the report with strict UTF-8 and record its SHA-256.

---

### Task 3: Review and freeze the corrected validator

**Files:**
- Read: approved spec, this plan, corrected validator, Task 1 report, original and real macOS/Linux runtime evidence.
- Modify after approval only: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Create: `D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-12-platform-aware-libxc-linkage-validator\task-2-review.md`

**Interfaces:**
- Consumes: corrected validator SHA and Task 1 RED/GREEN evidence.
- Produces: independent `Specification Compliance: APPROVED` and `Code Quality: APPROVED`, plus one authoritative corrected validator hash.

- [ ] **Step 1: Request an independent scoped review**

Use `superpowers:requesting-code-review`. Require the reviewer to verify:

- exact 16-library Darwin/Linux fixture shape;
- Darwin candidate list is exactly one `@rpath/libxc.15.dylib`;
- Linux target list is exactly one imported-checkout `deps/lib/libxc.so`;
- Windows still requires wheel-local inventory `libxc.dll` and exact target;
- all unrelated trust-boundary checks are unchanged;
- original artifact facts match the new contract;
- fresh `58/58`, `py_compile`, UTF-8/LF, and no-side-effect evidence.

The reviewer writes `task-2-review.md` and returns the two exact verdicts.

- [ ] **Step 2: Resolve review findings before freezing**

For any actionable finding, return to Task 2 TDD: add a failing test, observe
the intended RED, make the smallest correction, rerun all 58+ tests, and obtain
a fresh review. Do not suppress or waive a provenance finding.

- [ ] **Step 3: Freeze the authoritative validator hash**

After both verdicts are `APPROVED`, run:

```powershell
$CorrectedValidatorSha=(Get-FileHash $Validator -Algorithm SHA256).Hash.ToLowerInvariant()
if($CorrectedValidatorSha -ceq
  'd9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c') {
    throw 'corrected validator hash did not change'
}
```

Use `apply_patch` to replace exactly one current
`production_validator_sha256` active key with this reviewed hash and append
exactly one `production_unix_wrapper_witness_validator_sha256` key. Preserve
all historical evidence-specific old-validator keys.

- [ ] **Step 4: Prove old pair contracts fail closed under the new hash**

Read the exact execution-r1 addendum and require its four literal
`$ValidatorSha256` values to remain the old hash. Do not edit or invoke those
blocks. Record that the active validator now differs, so the existing pair
preflight cannot pass until a later reviewed mechanical rebind.

---

### Task 4: Revalidate the same macOS artifact in a new attempt

**Files:**
- Preserve: `D:\workspace\pyscf\.agents\archive\precision-ci\experiments\31577510832-production-unix-wrapper-witness-macos-py312\attempt-0001\**`
- Create: `...\archive-identity-platform-aware.json`
- Create: `...\attempt-0002\**`
- Create on strict PASS only: `...\archive-complete.json`
- Modify: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Modify: `D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-12-unix-precision-runner-exit-evidence\task-4-report.md`

**Interfaces:**
- Consumes: reviewed corrected validator, immutable run/job/artifact identity, and original `attempt-0001` hashes.
- Produces: one durable same-artifact `PASS` completion and the macOS witness gate; no new CI run.

- [ ] **Step 1: Verify immutable original evidence and live identity**

Require before any write:

```powershell
$ErrorActionPreference='Stop'
$Repo='psiQAQ/pyscf'
$RunId=31577510832L
$JobId=94052864840L
$ArtifactId=9133834443L
$Head='2a2237bc323b8473d19979aaa56a0e8ff88cee04'
$Branch='codex/test/sgx-extra-cycle-convergence-validation'
$Archive="D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-production-unix-wrapper-witness-macos-py312"
$OldAttempt=Join-Path $Archive 'attempt-0001'
if((Get-FileHash (Join-Path $OldAttempt 'validate_precision_production.py') -Algorithm SHA256).Hash.ToLowerInvariant() -cne
  'd9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c') { throw 'old validator changed' }
if((Get-FileHash (Join-Path $OldAttempt 'production-validation.json') -Algorithm SHA256).Hash.ToLowerInvariant() -cne
  'b188bdd6beed7f435009553fb3b9e1c9550cc2076f3acc4201a8130c023be684') { throw 'old INVALID report changed' }
$Run=(gh run view $RunId --repo $Repo --json databaseId,attempt,event,workflowName,headSha,headBranch,status,conclusion,jobs,url | ConvertFrom-Json -ErrorAction Stop)
if($LASTEXITCODE -ne 0) { throw 'run query failed' }
$Api=(gh api "repos/$Repo/actions/runs/$RunId/artifacts?per_page=100" | ConvertFrom-Json -ErrorAction Stop)
if($LASTEXITCODE -ne 0) { throw 'artifact query failed' }
$Jobs=@($Run.jobs | Where-Object { $_.name -ceq 'precision' })
$Arts=@($Api.artifacts)
if($Run.databaseId -ne $RunId -or $Run.attempt -ne 1 -or
   $Run.event -cne 'workflow_dispatch' -or
   $Run.workflowName -cne 'Precision investigation' -or
   $Run.headSha -cne $Head -or $Run.headBranch -cne $Branch -or
   $Run.status -cne 'completed' -or $Run.conclusion -cne 'success' -or
   $Jobs.Count -ne 1 -or $Jobs[0].databaseId -ne $JobId -or
   $Jobs[0].status -cne 'completed' -or $Jobs[0].conclusion -cne 'success') {
    throw 'run/job identity mismatch'
}
if($Arts.Count -ne 1 -or $Arts[0].id -ne $ArtifactId -or
   $Arts[0].name -cne 'precision-macOS-py3.12' -or $Arts[0].expired -ne $false -or
   $Arts[0].digest -cne 'sha256:73f108d3545bf365ffc72374f0e3e5b7831bc94d64e0de0bf3f0108813ba5300' -or
   $Arts[0].size_in_bytes -ne 7400) { throw 'artifact identity mismatch' }
```

- [ ] **Step 2: Create the new identity and attempt without touching attempt-0001**

Using `System.IO.FileMode.CreateNew` plus `Flush(true)`, construct
`archive-identity-platform-aware.json` from this ordered object:

```powershell
$CorrectedValidatorSha=(Get-FileHash $Validator -Algorithm SHA256).Hash.ToLowerInvariant()
$Identity=[ordered]@{
    purpose='unix-wrapper-witness-platform-aware-revalidation'
    head=$Head
    run_id=$RunId
    job_id=$JobId
    artifact_id=$ArtifactId
    artifact_name='precision-macOS-py3.12'
    artifact_digest='sha256:73f108d3545bf365ffc72374f0e3e5b7831bc94d64e0de0bf3f0108813ba5300'
    artifact_size=7400L
    branch=$Branch
    validator_sha256=$CorrectedValidatorSha
}
```

Serialize and read back this exact object. Create `attempt-0002` with
`New-Item -ItemType Directory`; fail if
it already contains any entry unless it is an exact recoverable same-identity
attempt.

- [ ] **Step 3: Download and byte-bind the same artifact**

Run exactly once:

```powershell
gh run download $RunId --repo $Repo --name 'precision-macOS-py3.12' --dir $AttemptDir
if($LASTEXITCODE -ne 0) { throw 'same-run artifact download failed' }
Copy-Item -LiteralPath (Join-Path $OldAttempt 'run.json') -Destination (Join-Path $AttemptDir 'run.json')
Copy-Item -LiteralPath $Validator -Destination (Join-Path $AttemptDir 'validate_precision_production.py')
```

Require both the original and copied `run.json` hashes to equal
`e1b8b4022700e2a387705586f898d3c5dfd440ee035bee8e7d03bb0b139d9cc1`.
Require the copied validator hash to equal `$CorrectedValidatorSha`.

- [ ] **Step 4: Validate the new attempt**

Run:

```powershell
$VPath=Join-Path $AttemptDir 'validate_precision_production.py'
$Report=Join-Path $AttemptDir 'production-validation.json'
conda run --no-capture-output -n pyscf-win313-test python $VPath $AttemptDir `
  --mode source-tree `
  --expected-sha $Head `
  --expected-nodeids-file 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration\.github\workflows\precision-uhf-smearing-extra-cycle-nodeids.txt' `
  --expected-profile omp4-blas4 `
  --expected-repeats 1 `
  --expected-platform macos-latest `
  --expected-python 3.12 `
  --expected-native-count 16 `
  --run-metadata (Join-Path $AttemptDir 'run.json') `
  --expected-run-id $RunId `
  --expected-branch $Branch `
  --expected-artifact-name 'precision-macOS-py3.12' `
  --report $Report
if($LASTEXITCODE -ne 0) { throw 'corrected witness validation failed' }
```

Require strict report fields: `valid=true`, `verdict=PASS`, `records=1`,
`pass=1`, `fail=0`, exact head/profile/nodeid; runtime LibXC `7.1.2`; Python
`3.12`; source-tree mode; native count `16`; one `libxc_itrf.dylib`; exact
`@rpath/libxc.15.dylib`; and `runner-exit-code.txt` bytes `30 0A` with SHA
`9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`.

- [ ] **Step 5: Durably complete and update the active witness gate**

Flush and rehash the report without changing its bytes. Create
`archive-complete.json` with `FileMode.CreateNew`, including exact head,
run/job/artifact IDs, attempt path, corrected validator SHA, new identity SHA,
run SHA, report SHA, runner-exit SHA, `tested_sha`, and `verdict=PASS`.

Use one `apply_patch` to:

- change `production_unix_wrapper_witness_wait_status` to strict recovered PASS;
- append exactly one artifact ID, report SHA, runner-exit SHA, tested SHA,
  verdict `PASS`, and claim `transport/provenance only; repeats=1 is not scientific stability`;
- append the corrected validator SHA if Task 3 did not already add it;
- preserve the original `attempt-0001 INVALID` and stop lines.

Freshly require each active key exactly once and print `MACOS WITNESS GATE PASS`.
Do not invoke any pair transport fence.

- [ ] **Step 6: Update Task 4 report and verify final scope**

Append a recovery section to Task 4 report with both old INVALID and new PASS
hashes, exact run/job/artifact, validator hash, runner-exit proof, active hash,
and the statement that no CI rerun or pair execution occurred. Verify both Git
worktrees have no tracked/staged changes and exactly the known 26 untracked DLLs.

---

## Final Verification Checklist

- [ ] Approved spec commit/hash and plan commit/hash are exact.
- [ ] Baseline was `50/50`; positive RED and strict-parser RED were observed for the intended reasons.
- [ ] Corrected validator is `58/58`, `py_compile` clean, UTF-8 no-BOM/LF/final-LF.
- [ ] Independent review gives both exact `APPROVED` verdicts with no actionable finding.
- [ ] Windows wheel-local `libxc.dll` contract is unchanged.
- [ ] Original `attempt-0001` validator/report hashes are unchanged.
- [ ] New `attempt-0002` uses the same run/job/artifact/head/digest and corrected validator.
- [ ] New report is strict `PASS` 1/1 with LibXC `7.1.2`, native 16, exact Darwin rpath, and exit bytes/SHA.
- [ ] Active witness gate is unique, exact, and explicitly transport/provenance only.
- [ ] Existing pair transport remains old-hash-bound and was not invoked.
- [ ] No CI dispatch/rerun, dependency install, issue/PR update, PySCF source change, or DLL staging/deletion occurred.
