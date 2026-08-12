# Unix Precision Runner Exit Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add byte-exact Unix runner exit evidence, publish one reviewed evidence commit on the existing validation branch, mechanically rebind the already-approved Task 7 Phase B state machine to that new commit, and accept a new Windows/Linux UHF pair only when both frozen-validator reports are `PASS` for the same new SHA.

**Architecture:** Keep the production change at the wrapper boundary: a real Bash wrapper captures the Python runner status, writes `runner-exit-code.txt`, and returns the same status. A real-wrapper/fake-`python` contract test supplies the RED/GREEN proof without scientific execution. Deployment preserves the existing validation branch and derives a new head-bound Phase B execution/transport contract from the immutable approved addendum; four hash-bound fresh-shell production blocks own dispatch and the single heartbeat, while terminal acceptance remains a separate frozen-validator gate.

**Tech Stack:** Bash with `set -euo pipefail`; Python standard library (`unittest`, `subprocess`, `pathlib`, `tempfile`, `hashlib`); Windows PowerShell 5.1 and .NET file APIs; Git/GitHub CLI; the frozen production validator at SHA-256 `d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c`.

## Global Constraints

- The approved requirements source is `docs/superpowers/specs/2026-08-12-unix-precision-runner-exit-evidence-design.md` at SHA-256 `ac39e9768aa1475ace3a0a30e2d14f843e363e264f536ab23f8453521cedc7b6`. Stop if either path or hash differs.
- The implementation parent is exactly `2eb90e3f99219e28390570d13bd906cfe6e17012` in `D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration` on `codex/test/sgx-extra-cycle-convergence-validation`.
- The implementation commit changes exactly `.github/workflows/run_unix_precision_tests.sh` and `.github/workflows/test_precision_investigation_contract.py`. Do not modify the Python runner, validator, workflow YAML, science code, parameters, assertions, nodeids, dependencies, archives, or old run metadata.
- Use `apply_patch` for repository and local-document edits. Preserve UTF-8 without BOM, LF-only, final LF, and the existing executable bit of the Bash wrapper. Do not install packages.
- Keep commits separate: this plan commit is documentation only; the later CI evidence commit is one implementation commit. Do not amend or rewrite `2eb90e3f99219e28390570d13bd906cfe6e17012`.
- Task 2 has the user's existing方案 A authority for one ordinary fast-forward push to the same validation branch. Do not force-push, change remotes, create a PR/issue, or push any other branch.
- Old latches, bindings, manifests, launch files, handoffs, runs `31548379750`/`31548408412`, artifacts `9123528060`/`9123362435`, and their archives are immutable. The new head uses a brand-new state namespace.
- Tasks 1–3 must not dispatch workflows, start a heartbeat, or change Goal. Task 3 may execute only the harmless in-memory ordinal-5 self-test; production ordinals 1–4 remain unexecuted until Task 4.
- Task 4 uses one heartbeat for both new run IDs with `IntervalSeconds=1800` and `WakeAfterMinutes=300`, then leaves Goal exactly `paused`. Do not manually poll GitHub after the handoff and do not replay a dispatch.
- Task 5 begins only after that exact heartbeat exits and Goal is independently read back as exactly `active`. Actions success and 20/20 records are advisory until the frozen validator returns `valid=true` and plain `PASS` for each artifact.
- Do not update `pyscf/pyscf#3312`. Task 6 records only the parent Task 7 Step 3 recovery entry.

## File Map

| Path | Operation | Purpose |
| --- | --- | --- |
| `.github/workflows/run_unix_precision_tests.sh` | Modify in Task 1 | Create the output directory, capture the real Python runner status, write its decimal value followed by one LF, and return the same status. |
| `.github/workflows/test_precision_investigation_contract.py` | Modify in Task 1 | Discover real GNU Bash safely and exercise the real wrapper against a fake `python` in four behavior tests. |
| `.agents/active/libxc-712-release-revalidation.md` | Local ignored updates in Tasks 2, 3, 5, 6 | Freeze the implementation head, derived-contract hashes, run identities, verdicts, and Step 3 recovery entry. |
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-policy-correction.md` | Immutable input | Double-approved Phase B addendum, SHA-256 `020ea0d6225632b55f37b6167a2e0fd2eed034b87bf6b03946d24243b670a395`. |
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-transport-execution.md` | Immutable input | Approved transport template, SHA-256 `f24d02372adc6b0051fdfe6cf8e1032e5322754ebdeba78298cbe97a4b83304b`. |
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-policy-correction-$NewHead.md` | CreateNew in Task 3 | Mechanically head/state-rebound four-block execution contract. `$NewHead` is the exact 40-hex implementation commit read at runtime. |
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-transport-execution-$NewHead.md` | CreateNew in Task 3 | Hash-bound materialization and fresh-shell invocation contract for the derived addendum. |
| `.agents/active/precision-ci/task-7-phase-b-$NewHead/` | Created only by Tasks 4–5 | New latches, bindings, manifest, launch-ready, handoff, and terminal state; no old state path is reused. |
| `.agents/archive/precision-ci/experiments/$RunId-production-uhf-$PlatformSlug-py312/` | CreateNew in Task 5 | Immutable new artifact, run metadata, validator copy, and validation report. `$RunId` and `$PlatformSlug` are computed from the frozen manifest entry. |

---

### Task 1: Build the wrapper evidence commit with real-wrapper TDD

**Files:**
- Modify: `.github/workflows/test_precision_investigation_contract.py`
- Modify: `.github/workflows/run_unix_precision_tests.sh`
- Worktree: `D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration`

- [ ] **Step 1 (2–5 min): Freeze the implementation baseline and approved spec**

Run in a fresh PowerShell shell:

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$DesignWorktree = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$ExpectedParent = '2eb90e3f99219e28390570d13bd906cfe6e17012'
$ExpectedSpec = 'ac39e9768aa1475ace3a0a30e2d14f843e363e264f536ab23f8453521cedc7b6'
if ((git -C $Worktree rev-parse HEAD).Trim() -cne $ExpectedParent -or $LASTEXITCODE -ne 0) { throw 'implementation parent mismatch' }
if ((git -C $Worktree branch --show-current).Trim() -cne 'codex/test/sgx-extra-cycle-convergence-validation' -or $LASTEXITCODE -ne 0) { throw 'validation branch mismatch' }
$Status = @(git -C $Worktree status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) { throw 'git status failed' }
$Tracked = @($Status | Where-Object { $_ -notmatch '^\?\? ' })
$Dll = @($Status | Where-Object { $_ -match '^\?\? .*(?i)\.dll$' })
$Other = @($Status | Where-Object { $_ -match '^\?\? ' -and $_ -notmatch '(?i)\.dll$' })
if ($Tracked.Count -ne 0 -or $Dll.Count -ne 26 -or $Other.Count -ne 0) { throw 'worktree is not tracked-clean with exactly 26 DLL fixtures' }
$Spec = Join-Path $DesignWorktree 'docs\superpowers\specs\2026-08-12-unix-precision-runner-exit-evidence-design.md'
if ((Get-FileHash -LiteralPath $Spec -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedSpec) { throw 'approved spec hash mismatch' }
```

Expected: exact parent/branch, zero tracked changes, 26 untracked DLLs, no other untracked path, and no exception.

- [ ] **Step 2 (2–5 min): Add the real Bash discovery and fake-runner harness**

Use `apply_patch`. Add imports `contextlib`, `os`, `shutil`, and `stat`, then add the following complete helpers after `ROOT` and before `read`:

```python
FAKE_PYTHON = '''#!/usr/bin/env bash
set -euo pipefail
: "${FAKE_INVOCATION_RECORD:?}"
: "${FAKE_PYTHON_EXIT:?}"
printf '%s\0' '__CALL__' "$@" >> "$FAKE_INVOCATION_RECORD"
output_count=0
output_dir=
while (($#)); do
  if [[ "$1" == '--output-dir' ]]; then
    output_count=$((output_count + 1))
    shift
    (($#)) || exit 96
    output_dir=$1
  fi
  shift
done
((output_count == 1)) || exit 96
[[ -d "$output_dir" ]] || exit 97
printf '%s\n' 'fake evidence sentinel' > "$output_dir/fake-evidence.txt"
exit "$FAKE_PYTHON_EXIT"
'''


def _is_within(path, parent):
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _probe_bash(candidate, require_msys):
    candidate = Path(candidate).resolve(strict=True)
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        raise RuntimeError(f'Bash is not an executable file: {candidate}')
    result = subprocess.run(
        [str(candidate), '--version'], capture_output=True, text=True,
        shell=False,
    )
    version = (result.stdout + result.stderr).casefold()
    if result.returncode != 0 or 'gnu bash' not in version:
        raise RuntimeError(f'GNU Bash probe failed: {candidate}')
    if require_msys and 'msys' not in version:
        raise RuntimeError(f'MSYS Bash is required on Windows: {candidate}')
    return candidate


def resolve_bash():
    if sys.platform == 'win32':
        discovered_git = shutil.which('git')
        if discovered_git is None:
            raise RuntimeError('git.exe is required to locate MSYS Bash')
        git_path = Path(discovered_git).resolve(strict=True)
        if git_path.name.casefold() != 'git.exe':
            raise RuntimeError(f'Expected git.exe, got {git_path}')
        if not git_path.is_file() or not os.access(git_path, os.X_OK):
            raise RuntimeError(f'git.exe is not executable: {git_path}')
        if git_path.parent.name.casefold() not in ('cmd', 'bin'):
            raise RuntimeError(f'Unexpected Git installation layout: {git_path}')
        system_root = Path(os.environ['SystemRoot']).resolve(strict=True)
        system32 = (system_root / 'System32').resolve(strict=True)
        if _is_within(git_path, system32):
            raise RuntimeError('System32 git.exe is forbidden')
        bash_path = (git_path.parent.parent / 'bin/bash.exe').resolve(strict=True)
        if _is_within(bash_path, system32):
            raise RuntimeError('System32/WSL Bash compatibility shim is forbidden')
        return _probe_bash(bash_path, require_msys=True)
    if sys.platform not in ('linux', 'darwin'):
        raise RuntimeError(f'Unsupported contract-test platform: {sys.platform}')
    discovered_bash = shutil.which('bash')
    if discovered_bash is None:
        raise RuntimeError('GNU Bash is required')
    return _probe_bash(discovered_bash, require_msys=False)


@contextlib.contextmanager
def unix_wrapper_case(fake_exit, output_kind, exit_path_directory=False):
    tmp_parent = ROOT / 'tmp'
    tmp_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=tmp_parent) as tmpdir:
        case_root = Path(tmpdir)
        case_rel = case_root.relative_to(ROOT).as_posix()
        bin_dir = case_root / 'bin'
        bin_dir.mkdir()
        fake_python = bin_dir / 'python'
        fake_python.write_bytes(FAKE_PYTHON.encode('utf-8'))
        fake_python.chmod(
            fake_python.stat().st_mode
            | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        nodeids = case_root / 'nodeids.txt'
        nodeids.write_bytes(
            b'pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing\n'
        )
        output = case_root / 'output'
        if output_kind == 'directory':
            output.mkdir()
        elif output_kind == 'file':
            output.write_bytes(b'not a directory\n')
        elif output_kind != 'missing':
            raise AssertionError(f'unknown output kind: {output_kind}')
        if exit_path_directory:
            if not output.is_dir():
                raise AssertionError(
                    'exit-path directory needs an output directory'
                )
            (output / 'runner-exit-code.txt').mkdir()
        invocation_record = case_root / 'invocations.bin'
        env = os.environ.copy()
        env['PATH'] = str(bin_dir) + os.pathsep + env['PATH']
        env['GITHUB_SHA'] = 'a' * 40
        env['FAKE_PYTHON_EXIT'] = str(fake_exit)
        env['FAKE_INVOCATION_RECORD'] = (
            f'{case_rel}/invocations.bin'
        )
        command = [
            str(resolve_bash()),
            '.github/workflows/run_unix_precision_tests.sh',
            f'{case_rel}/nodeids.txt',
            '1',
            '4/4',
            f'{case_rel}/output',
        ]
        result = subprocess.run(
            command, cwd=ROOT, env=env, capture_output=True, text=True,
            shell=False,
        )
        raw = invocation_record.read_bytes() if invocation_record.exists() else b''
        fields = raw.split(b'\0')
        if fields and fields[-1] == b'':
            fields.pop()
        calls = fields.count(b'__CALL__')
        argv = [field.decode('utf-8') for field in fields[1:]] if calls == 1 else []
        yield SimpleNamespace(
            result=result, calls=calls, argv=argv, output=output,
            exit_path=output / 'runner-exit-code.txt',
            sentinel=output / 'fake-evidence.txt',
            nodeids=f'{case_rel}/nodeids.txt',
            output_arg=f'{case_rel}/output',
        )


def assert_exact_fake_argv(test_case, case):
    test_case.assertEqual(case.calls, 1)
    test_case.assertEqual(case.argv.count('--output-dir'), 1)
    pairs = dict(zip(case.argv[1::2], case.argv[2::2]))
    test_case.assertTrue(
        case.argv[0].replace('\\', '/').endswith(
            '/.github/workflows/run_precision_tests.py'
        )
    )
    test_case.assertEqual(pairs['--nodeids-file'], case.nodeids)
    test_case.assertEqual(pairs['--repeats'], '1')
    test_case.assertEqual(pairs['--profile'], '4/4')
    test_case.assertEqual(pairs['--output-dir'], case.output_arg)
    test_case.assertEqual(pairs['--tested-sha'], 'a' * 40)
    test_case.assertEqual(pairs['--working-directory'], pairs['--rootdir'])
    root = pairs['--rootdir'].replace('\\', '/').rstrip('/')
    test_case.assertEqual(
        case.argv[0].replace('\\', '/'),
        root + '/.github/workflows/run_precision_tests.py',
    )
    test_case.assertEqual(
        pairs['--pytest-config'].replace('\\', '/'), root + '/pytest.ini'
    )
    test_case.assertEqual(pairs['--environment-mode'], 'source-tree')
    test_case.assertEqual(
        pairs['--collector'].replace('\\', '/'),
        root + '/.github/workflows/collect_precision_environment.py',
    )
```

The fake writes its invocation marker before checking the output directory, never creates that directory, and writes its sentinel only after the wrapper has supplied a real directory. `PATH` uses host `os.pathsep`; all paths consumed as fake arguments or environment-record paths are repository-relative POSIX paths.

- [ ] **Step 3 (2–5 min): Add exactly four behavior tests**

Add these methods to `PrecisionInvestigationContractTest` immediately after the existing workflow-contract test:

```python
    def test_unix_wrapper_creates_output_directory(self):
        with unix_wrapper_case(0, 'missing') as case:
            assert_exact_fake_argv(self, case)
            self.assertEqual(case.result.returncode, 0, case.result.stderr)
            self.assertEqual(case.sentinel.read_bytes(), b'fake evidence sentinel\n')
            self.assertEqual(case.exit_path.read_bytes(), b'0\n')

    def test_unix_wrapper_records_zero_and_nonzero_runner_exit(self):
        for runner_exit, expected_bytes in ((0, b'0\n'), (23, b'23\n')):
            with self.subTest(runner_exit=runner_exit):
                with unix_wrapper_case(runner_exit, 'directory') as case:
                    assert_exact_fake_argv(self, case)
                    self.assertEqual(case.sentinel.read_bytes(), b'fake evidence sentinel\n')
                    self.assertTrue(case.exit_path.is_file())
                    self.assertEqual(case.exit_path.read_bytes(), expected_bytes)
                    self.assertEqual(case.result.returncode, runner_exit)

    def test_unix_wrapper_rejects_output_file_before_runner(self):
        with unix_wrapper_case(0, 'file') as case:
            self.assertNotEqual(case.result.returncode, 0)
            self.assertEqual(case.calls, 0)
            self.assertTrue(case.output.is_file())

    def test_unix_wrapper_fails_closed_when_exit_path_is_directory(self):
        with unix_wrapper_case(
                0, 'directory', exit_path_directory=True
        ) as case:
            assert_exact_fake_argv(self, case)
            self.assertEqual(case.sentinel.read_bytes(), b'fake evidence sentinel\n')
            self.assertNotEqual(case.result.returncode, 0)
            self.assertTrue(case.exit_path.is_dir())
            self.assertFalse(case.exit_path.is_file())
```

- [ ] **Step 4 (2–5 min): Run the four-test RED and inspect each failure boundary**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Tests = @(
  'PrecisionInvestigationContractTest.test_unix_wrapper_creates_output_directory',
  'PrecisionInvestigationContractTest.test_unix_wrapper_records_zero_and_nonzero_runner_exit',
  'PrecisionInvestigationContractTest.test_unix_wrapper_rejects_output_file_before_runner',
  'PrecisionInvestigationContractTest.test_unix_wrapper_fails_closed_when_exit_path_is_directory'
)
conda run --no-capture-output -n pyscf-win313-test python `
  '.github/workflows/test_precision_investigation_contract.py' @Tests -v
if ($LASTEXITCODE -eq 0) { throw 'RED unexpectedly passed' }
```

Required RED classification before implementation:

- Missing output: fake call count is `1`, fake returns harness status `97`, wrapper does not create the directory.
- Precreated output with runner `0` and `23`: fake call/argv/sentinel and wrapper status already match; the first failing assertion in each subtest is the absent ordinary `runner-exit-code.txt`.
- Ordinary output file: current wrapper incorrectly calls fake once; the `calls == 0` assertion fails.
- Exit path directory: fake is called once and sentinel remains, but the current wrapper incorrectly returns `0` because it never redirects the exit file.

If Bash discovery, MSYS path conversion, fake lookup, or argv parsing fails first, repair only the harness and repeat RED; do not edit the wrapper until these exact boundaries are observed.

- [ ] **Step 5 (2–5 min): Apply the minimal wrapper implementation**

Use `apply_patch` to replace the existing direct Python-command tail with this single implementation snippet; no second variant is allowed:

```bash
mkdir -p "$output_dir"
runner_exit=0
if python "$repo_root/.github/workflows/run_precision_tests.py" \
  --nodeids-file "$nodeids_file" \
  --repeats "$repeats" \
  --profile "$profile" \
  --output-dir "$output_dir" \
  --tested-sha "${GITHUB_SHA:-$(git -C "$repo_root" rev-parse HEAD)}" \
  --working-directory "$repo_root" \
  --rootdir "$repo_root" \
  --pytest-config "$repo_root/pytest.ini" \
  --environment-mode source-tree \
  --collector "$repo_root/.github/workflows/collect_precision_environment.py"; then
  runner_exit=0
else
  runner_exit=$?
fi
printf '%s\n' "$runner_exit" > "$output_dir/runner-exit-code.txt"
exit "$runner_exit"
```

- [ ] **Step 6 (2–5 min): Run GREEN, full contract, syntax, EOL, and scope checks**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Tests = @(
  'PrecisionInvestigationContractTest.test_unix_wrapper_creates_output_directory',
  'PrecisionInvestigationContractTest.test_unix_wrapper_records_zero_and_nonzero_runner_exit',
  'PrecisionInvestigationContractTest.test_unix_wrapper_rejects_output_file_before_runner',
  'PrecisionInvestigationContractTest.test_unix_wrapper_fails_closed_when_exit_path_is_directory'
)
conda run --no-capture-output -n pyscf-win313-test python `
  '.github/workflows/test_precision_investigation_contract.py' @Tests -v
if ($LASTEXITCODE -ne 0) { throw 'focused GREEN failed' }
conda run --no-capture-output -n pyscf-win313-test python `
  '.github/workflows/test_precision_investigation_contract.py' -v
if ($LASTEXITCODE -ne 0) { throw 'full contract suite failed' }
& 'D:\Program Files\Git\bin\bash.exe' -n '.github/workflows/run_unix_precision_tests.sh'
if ($LASTEXITCODE -ne 0) { throw 'bash -n failed' }
git -C $Worktree diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff --check failed' }
$Names = @(git -C $Worktree diff --name-only)
if ($LASTEXITCODE -ne 0 -or $Names.Count -ne 2 -or
    $Names -notcontains '.github/workflows/run_unix_precision_tests.sh' -or
    $Names -notcontains '.github/workflows/test_precision_investigation_contract.py') { throw 'implementation scope mismatch' }
$Eol = @(git -C $Worktree ls-files --eol -- `
  '.github/workflows/run_unix_precision_tests.sh' `
  '.github/workflows/test_precision_investigation_contract.py')
if ($LASTEXITCODE -ne 0 -or @($Eol | Where-Object { $_ -notmatch 'i/lf\s+w/lf\s+' }).Count -ne 0) { throw 'LF gate failed' }
$Summary = @(git -C $Worktree diff --summary)
if ($LASTEXITCODE -ne 0 -or @($Summary | Where-Object { $_ -match 'mode change' }).Count -ne 0) { throw 'wrapper executable mode changed' }
```

The Windows discovery evidence must resolve `git` to `D:\Program Files\Git\cmd\git.exe`, Bash to `D:\Program Files\Git\bin\bash.exe`, and the probe output to GNU Bash `5.2.15` with `x86_64-pc-msys`. On a native Linux host and a native macOS host, run the same focused and full Python commands with the host Python and require all tests green; `resolve_bash()` must probe the host GNU Bash rather than skip. If either host is unavailable, record `Not Run` and stop before Task 2 rather than claiming cross-platform acceptance.

- [ ] **Step 7 (2–5 min): Commit exactly the two implementation files**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
git -C $Worktree add -- `
  '.github/workflows/run_unix_precision_tests.sh' `
  '.github/workflows/test_precision_investigation_contract.py'
if ($LASTEXITCODE -ne 0) { throw 'git add failed' }
$Staged = @(git -C $Worktree diff --cached --name-only)
if ($LASTEXITCODE -ne 0 -or $Staged.Count -ne 2) { throw 'staged scope mismatch' }
git -C $Worktree commit -m 'ci: record Unix precision runner exit code'
if ($LASTEXITCODE -ne 0) { throw 'implementation commit failed' }
$NewHead = (git -C $Worktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$' -or $NewHead -ceq '2eb90e3f99219e28390570d13bd906cfe6e17012') { throw 'new implementation head invalid' }
$Parent = (git -C $Worktree rev-parse HEAD^).Trim()
if ($LASTEXITCODE -ne 0 -or $Parent -cne '2eb90e3f99219e28390570d13bd906cfe6e17012') { throw 'implementation commit parent mismatch' }
$CommitNames = @(git -C $Worktree diff-tree --no-commit-id --name-only -r $NewHead)
if ($LASTEXITCODE -ne 0 -or $CommitNames.Count -ne 2) { throw 'commit scope mismatch' }
```

- [ ] **Step 8 (2–5 min): Obtain independent SDD approval before publication**

Give the reviewer the approved spec hash, the preserved RED output, the GREEN/full-suite outputs, both host-boundary results, `git show --stat --oneline HEAD`, `git diff HEAD^..HEAD`, EOL/mode evidence, and the exact commit SHA. Require two explicit verdicts in an ignored review report: `Spec Compliance: APPROVED` and `Code Quality: APPROVED`. A finding sends the change back to Step 2 or Step 5 and creates a new ordinary follow-up commit; do not amend a reviewed/public SHA and do not enter Task 2 without both approvals.

---

### Task 2: Fast-forward publish the reviewed evidence commit

**Files:**
- Local ignored update: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Remote ref: `origin/codex/test/sgx-extra-cycle-convergence-validation`

- [ ] **Step 1 (2–5 min): Recheck review, local ancestry, and exact old remote head**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$ExpectedOld = '2eb90e3f99219e28390570d13bd906cfe6e17012'
$NewHead = (git -C $Worktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'local new head unavailable' }
if ((git -C $Worktree branch --show-current).Trim() -cne $Branch -or $LASTEXITCODE -ne 0) { throw 'branch mismatch' }
git -C $Worktree merge-base --is-ancestor $ExpectedOld $NewHead
if ($LASTEXITCODE -ne 0) { throw 'new head is not a descendant of the frozen parent' }
$Status = @(git -C $Worktree status --porcelain=v1)
if ($LASTEXITCODE -ne 0) { throw 'git status failed before push' }
if (@($Status | Where-Object { $_ -notmatch '^\?\? .*(?i)\.dll$' }).Count -ne 0) { throw 'tracked or non-DLL worktree change before push' }
$Remote = @(git -C $Worktree ls-remote --heads origin "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $Remote.Count -ne 1) { throw 'old remote head unavailable or ambiguous' }
$RemoteOld = ($Remote[0] -split "`t")[0]
if ($RemoteOld -cne $ExpectedOld) { throw "remote moved: $RemoteOld" }
```

- [ ] **Step 2 (2–5 min): Perform one ordinary push and exact readback**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$NewHead = (git -C $Worktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'new head unavailable before push' }
git -C $Worktree push origin "$NewHead`:refs/heads/$Branch"
if ($LASTEXITCODE -ne 0) { throw 'ordinary fast-forward push failed' }
$Readback = @(git -C $Worktree ls-remote --heads origin "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $Readback.Count -ne 1) { throw 'remote readback unavailable' }
$RemoteHead = ($Readback[0] -split "`t")[0]
if ($RemoteHead -cne $NewHead) { throw "remote readback mismatch: $RemoteHead" }
```

No `--force`, `--force-with-lease`, tag, PR, issue, dispatch, Goal, or heartbeat command belongs to this task.

- [ ] **Step 3 (2–5 min): Freeze the new active-document keys with `apply_patch`**

First compute and record these exact runtime values:

```powershell
$ErrorActionPreference = 'Stop'
$PlanWorktree = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$ImplementationWorktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$NewHead = (git -C $ImplementationWorktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'implementation head unavailable' }
$PlanCommit = (git -C $PlanWorktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $PlanCommit -notmatch '^[0-9a-f]{40}$') { throw 'plan commit unavailable' }
$PlanPath = Join-Path $PlanWorktree 'docs\superpowers\plans\2026-08-12-unix-precision-runner-exit-evidence.md'
$PlanSha256 = (Get-FileHash -LiteralPath $PlanPath -Algorithm SHA256).Hash.ToLowerInvariant()
[pscustomobject]@{new_head=$NewHead; plan_commit=$PlanCommit; plan_sha256=$PlanSha256} | ConvertTo-Json -Compress
```

Render the exact active-document lines from those values:

```powershell
$Lines = @(
  '- production_unix_exit_evidence_plan_path: `D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\docs\superpowers\plans\2026-08-12-unix-precision-runner-exit-evidence.md`',
  "- production_unix_exit_evidence_plan_commit: ``$PlanCommit``",
  "- production_unix_exit_evidence_plan_sha256: ``$PlanSha256``",
  '- production_unix_exit_evidence_implementation_parent: `2eb90e3f99219e28390570d13bd906cfe6e17012`',
  "- production_unix_exit_evidence_implementation_commit: ``$NewHead``",
  '- production_unix_exit_evidence_implementation_review: `Spec Compliance APPROVED; Code Quality APPROVED`',
  "- production_unix_exit_evidence_remote_head: ``$NewHead``",
  '- production_unix_exit_evidence_next_step: `derive and independently review the new head-bound Phase B execution and transport contracts; do not dispatch`'
)
$Lines
```

Use `apply_patch` on `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md` to replace the unique `production_validation_head` value with the printed `$NewHead`, replace `production_unix_exit_evidence_design_status` with `APPROVED`, and replace the existing `production_unix_exit_evidence_next_step` line with the eight rendered lines byte-for-byte. After `apply_patch`, require each key exactly once and require the three head values to be byte-identical:

```powershell
$ErrorActionPreference = 'Stop'
$Active = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Text = [IO.File]::ReadAllText($Active, [Text.UTF8Encoding]::new($false, $true))
$Keys = @('production_validation_head','production_unix_exit_evidence_implementation_commit','production_unix_exit_evidence_remote_head')
$Values = @()
foreach ($Key in $Keys) {
  $M = [regex]::Matches($Text, "(?m)^- $Key`: ``([0-9a-f]{40})``$")
  if ($M.Count -ne 1) { throw "active key cardinality mismatch: $Key" }
  $Values += $M[0].Groups[1].Value
}
if (@($Values | Select-Object -Unique).Count -ne 1) { throw 'active heads differ' }
```

---

### Task 3: Mechanically derive and review the new head-bound Phase B contract

**Files:**
- Read immutable: `task-7-phase-b-policy-correction.md` and `task-7-phase-b-transport-execution.md`
- Create ignored: `task-7-phase-b-policy-correction-$NewHead.md`
- Create ignored: `task-7-phase-b-transport-execution-$NewHead.md`
- Create ignored helper: `rebind-task7-phase-b.py`

- [ ] **Step 1 (2–5 min): Author the exact standard-library rebind helper**

Use `apply_patch` to create `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/rebind-task7-phase-b.py` with the complete code below. This helper verifies immutable inputs, exact replacement counts, active-head cardinality, five output fence hashes, and CreateNew-or-byte-exact output semantics. It strips the old transport's stale runtime-evidence tail and replaces it with an explicit review gate.

```python
import hashlib
from pathlib import Path
import re
import subprocess
import sys


DESIGN_WORKTREE = Path(
    r'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
)
INTEGRATION_WORKTREE = Path(
    r'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
)
SDD = DESIGN_WORKTREE / (
    '.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production'
)
ACTIVE = Path(
    r'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
)
SOURCE_ADDENDUM = SDD / 'task-7-phase-b-policy-correction.md'
SOURCE_TRANSPORT = SDD / 'task-7-phase-b-transport-execution.md'
OLD_HEAD = '2eb90e3f99219e28390570d13bd906cfe6e17012'
SOURCE_ADDENDUM_SHA = (
    '020ea0d6225632b55f37b6167a2e0fd2eed034b87bf6b03946d24243b670a395'
)
SOURCE_TRANSPORT_SHA = (
    'f24d02372adc6b0051fdfe6cf8e1032e5322754ebdeba78298cbe97a4b83304b'
)
OLD_ROOT_ASSIGNMENT = (
    "$Root = 'D:\\workspace\\pyscf\\.agents\\active\\precision-ci'"
)
OLD_FENCE_HASHES = (
    'a7a4fbd66353f71c5a2eb547ea6c4990965f82faf6c1a6d4ec7daf9a951e90be',
    '159d3f422f56d75badc6a0ecc5d414d9d4ca2db1c574123a4360947e9829ceda',
    'fc46f9e649ae4be3fa5a8ee24486a8ab65c3160f6761397cf1064eb3548b3ac3',
    '6cffda581fdf5aecbfd81a928e9709cc7238b8701b5344810513b2b158b76a9e',
    'f09f835ea66a44362ad57e3837df6382423841730e4054f84fab7f5d5ddec79a',
)
FENCE_RE = re.compile(r'^```powershell\n(.*?)^```\s*$', re.M | re.S)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_contract(path, expected_sha):
    data = path.read_bytes()
    if sha256(data) != expected_sha:
        raise RuntimeError(f'input SHA mismatch: {path}')
    if data.startswith(b'\xef\xbb\xbf') or b'\r' in data or not data.endswith(b'\n'):
        raise RuntimeError(f'input encoding/EOL mismatch: {path}')
    return data.decode('utf-8')


def replace_exact(text, old, new, count, label):
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f'{label} count {actual}, expected {count}')
    return text.replace(old, new)


def write_new_or_exact(path, data):
    try:
        with path.open('xb') as stream:
            stream.write(data)
            stream.flush()
    except FileExistsError:
        if path.read_bytes() != data:
            raise RuntimeError(f'existing output differs: {path}')
        return 'existing-exact'
    return 'created'


if len(sys.argv) != 2 or re.fullmatch(r'[0-9a-f]{40}', sys.argv[1]) is None:
    raise SystemExit('usage: rebind-task7-phase-b.py NEW_HEAD')
new_head = sys.argv[1]
live_head = subprocess.run(
    ['git', '-C', str(INTEGRATION_WORKTREE), 'rev-parse', 'HEAD'],
    check=True, capture_output=True, text=True,
).stdout.strip()
if live_head != new_head or new_head == OLD_HEAD:
    raise RuntimeError('new head does not match the integration worktree')

active_text = ACTIVE.read_bytes().decode('utf-8')
active_heads = re.findall(
    r'^- production_validation_head: `([0-9a-f]{40})`$', active_text, re.M
)
if active_heads != [new_head]:
    raise RuntimeError('active production_validation_head is not unique/new')

source_addendum = read_contract(SOURCE_ADDENDUM, SOURCE_ADDENDUM_SHA)
new_root = (
    "$Root = 'D:\\workspace\\pyscf\\.agents\\active\\precision-ci\\"
    f"task-7-phase-b-{new_head}'"
)
addendum = replace_exact(
    source_addendum, OLD_HEAD, new_head, 10, 'addendum old-head'
)
addendum = replace_exact(
    addendum, OLD_ROOT_ASSIGNMENT, new_root, 4,
    'addendum state-root assignment',
)
if OLD_HEAD in addendum or OLD_ROOT_ASSIGNMENT in addendum:
    raise RuntimeError('stale head or old state-root assignment remains')
addendum_bytes = addendum.encode('utf-8')
addendum_fences = [
    match.group(1).encode('utf-8') for match in FENCE_RE.finditer(addendum)
]
if len(addendum_fences) != 5:
    raise RuntimeError(f'new addendum fence count {len(addendum_fences)}')
new_fence_hashes = tuple(sha256(code) for code in addendum_fences)
new_addendum_name = f'task-7-phase-b-policy-correction-{new_head}.md'
new_addendum_path = SDD / new_addendum_name
addendum_disposition = write_new_or_exact(new_addendum_path, addendum_bytes)
new_addendum_sha = sha256(addendum_bytes)

source_transport = read_contract(SOURCE_TRANSPORT, SOURCE_TRANSPORT_SHA)
transport = replace_exact(
    source_transport, 'task-7-phase-b-policy-correction.md',
    new_addendum_name, 7, 'transport addendum path',
)
transport = replace_exact(
    transport, SOURCE_ADDENDUM_SHA, new_addendum_sha, 7,
    'transport addendum SHA',
)
transport = replace_exact(
    transport, 'task7-phase-b-transport',
    f'task7-phase-b-transport-{new_head}', 6,
    'transport output namespace',
)
for ordinal, (old_hash, new_hash) in enumerate(
        zip(OLD_FENCE_HASHES, new_fence_hashes), start=1):
    transport = replace_exact(
        transport, old_hash, new_hash, 4,
        f'transport fence {ordinal} SHA',
    )
evidence_marker = '## Harmless review evidence\n'
if transport.count(evidence_marker) != 1:
    raise RuntimeError('transport review-evidence marker mismatch')
transport = transport.split(evidence_marker, 1)[0] + '''## Review gates before production

- Run the materializer twice: first result may be `created` or
  `existing-exact`; second result must be `existing-exact` for all five files.
- In a separate fresh shell, invoke only ordinal 5 and require exactly
  `SELF-TEST PASS: 19 cases`.
- Independently review the derived addendum diff, the exact replacement-count
  report, all five fence hashes, all six transport-fence hashes, PowerShell 5.1
  AST results, new state namespace, and absence of the old head/state root.
- Production ordinals 1-4 remain forbidden until both independent reviews say
  `APPROVED` and Task 4 begins.
'''
transport_bytes = transport.encode('utf-8')
if transport_bytes.startswith(b'\xef\xbb\xbf') or b'\r' in transport_bytes or not transport_bytes.endswith(b'\n'):
    raise RuntimeError('new transport encoding/EOL mismatch')
transport_fences = [
    match.group(1).encode('utf-8') for match in FENCE_RE.finditer(transport)
]
if len(transport_fences) != 6:
    raise RuntimeError(f'new transport fence count {len(transport_fences)}')
new_transport_path = SDD / (
    f'task-7-phase-b-transport-execution-{new_head}.md'
)
transport_disposition = write_new_or_exact(new_transport_path, transport_bytes)

print('new_head=' + new_head)
print('state_root=' + str(Path(
    r'D:\workspace\pyscf\.agents\active\precision-ci'
) / f'task-7-phase-b-{new_head}'))
print(f'addendum_path={new_addendum_path}')
print(f'addendum_sha256={new_addendum_sha}')
print(f'addendum_disposition={addendum_disposition}')
for ordinal, digest in enumerate(new_fence_hashes, start=1):
    print(f'addendum_fence_{ordinal}_sha256={digest}')
print(f'transport_path={new_transport_path}')
print(f'transport_sha256={sha256(transport_bytes)}')
print(f'transport_disposition={transport_disposition}')
for ordinal, code in enumerate(transport_fences, start=1):
    print(f'transport_fence_{ordinal}_sha256={sha256(code)}')
```

- [ ] **Step 2 (2–5 min): Derive the two new ignored contracts without dispatch**

```powershell
$ErrorActionPreference = 'Stop'
$Integration = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Design = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$NewHead = (git -C $Integration rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'new head unavailable' }
$RebindOutput = @(conda run --no-capture-output -n pyscf-win313-test python `
  "$Design\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production\rebind-task7-phase-b.py" `
  $NewHead)
if ($LASTEXITCODE -ne 0) { throw 'mechanical Phase B rebind failed' }
$Rebind = ConvertFrom-StringData ($RebindOutput -join "`n")
$Required = @(
  'new_head','state_root','addendum_path','addendum_sha256',
  'addendum_disposition','transport_path','transport_sha256',
  'transport_disposition'
)
foreach ($Key in $Required) {
  if (-not $Rebind.ContainsKey($Key)) { throw "missing rebind output: $Key" }
}
if ($Rebind.new_head -cne $NewHead) { throw 'rebind output head mismatch' }
$RebindOutput
```

Retain `$Rebind` in this shell only for verification. Do not write anything under the new production state root in this task.

- [ ] **Step 3 (2–5 min): Parse every derived fence with Windows PowerShell 5.1**

```powershell
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSEdition -cne 'Desktop' -or $PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) { throw 'Windows PowerShell 5.1 required' }
$Integration = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$NewHead = (git -C $Integration rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'git rev-parse failed' }
$ExpectedCounts = [ordered]@{
  (Join-Path $Sdd "task-7-phase-b-policy-correction-$NewHead.md") = 5
  (Join-Path $Sdd "task-7-phase-b-transport-execution-$NewHead.md") = 6
}
$StrictUtf8 = New-Object Text.UTF8Encoding($false, $true)
foreach ($Entry in $ExpectedCounts.GetEnumerator()) {
  $Bytes = [IO.File]::ReadAllBytes($Entry.Key)
  if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) { throw "BOM: $($Entry.Key)" }
  $Text = $StrictUtf8.GetString($Bytes)
  if ($Text.Contains("`r") -or -not $Text.EndsWith("`n")) { throw "EOL: $($Entry.Key)" }
  $Fences = [regex]::Matches($Text, '(?ms)^```powershell\n(.*?)^```\s*$')
  if ($Fences.Count -ne $Entry.Value) { throw "fence count: $($Entry.Key)" }
  for ($I = 0; $I -lt $Fences.Count; $I++) {
    $Tokens = $null; $Errors = $null
    [void][Management.Automation.Language.Parser]::ParseInput($Fences[$I].Groups[1].Value, [ref]$Tokens, [ref]$Errors)
    if ($Errors.Count -ne 0) { throw "$($Entry.Key) fence $($I + 1) has $($Errors.Count) AST errors" }
  }
  [pscustomobject]@{path=$Entry.Key; fences=$Fences.Count; ast_errors=0; sha256=(Get-FileHash -LiteralPath $Entry.Key -Algorithm SHA256).Hash.ToLowerInvariant()}
}
```

- [ ] **Step 4 (2–5 min): Run the derived materializer twice, then the harmless self-test once**

In one fresh `shell_command`, extract transport ordinal 1 to a content-addressed file, verify AST, and call it in the current PowerShell 5.1 shell:

```powershell
$ErrorActionPreference = 'Stop'
$Integration = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$NewHead = (git -C $Integration rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'new head unavailable' }
$Transport = Join-Path $Sdd "task-7-phase-b-transport-execution-$NewHead.md"
$Text = (New-Object Text.UTF8Encoding($false, $true)).GetString([IO.File]::ReadAllBytes($Transport))
$Fences = [regex]::Matches($Text, '(?ms)^```powershell\n(.*?)^```\s*$')
if ($Fences.Count -ne 6) { throw 'transport fence count mismatch' }
$Code = $Fences[0].Groups[1].Value
$Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Code)
$Sha = [BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()
$ReviewDir = Join-Path 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\tmp' "task7-phase-b-contract-review-$NewHead"
[void][IO.Directory]::CreateDirectory($ReviewDir)
$Path = Join-Path $ReviewDir "transport-fence-1-$Sha.ps1"
if (-not (Test-Path -LiteralPath $Path)) {
  $Stream = [IO.File]::Open($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  try { $Stream.Write($Bytes,0,$Bytes.Length); $Stream.Flush($true) } finally { $Stream.Dispose() }
}
if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Sha) { throw 'review materializer hash mismatch' }
& $Path
if (-not $?) { throw 'derived materializer failed' }
```

In a second fresh `shell_command`, perform the complete second materializer invocation and require all five dispositions to be `existing-exact`:

```powershell
$ErrorActionPreference = 'Stop'
$Integration = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$NewHead = (git -C $Integration rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'new head unavailable' }
$Transport = Join-Path $Sdd "task-7-phase-b-transport-execution-$NewHead.md"
$Text = (New-Object Text.UTF8Encoding($false, $true)).GetString([IO.File]::ReadAllBytes($Transport))
$Fences = [regex]::Matches($Text, '(?ms)^```powershell\n(.*?)^```\s*$')
if ($Fences.Count -ne 6) { throw 'transport fence count mismatch' }
$Code = $Fences[0].Groups[1].Value
$Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Code)
$Algorithm = [Security.Cryptography.SHA256]::Create()
try { $Sha = [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant() } finally { $Algorithm.Dispose() }
$Path = Join-Path (Join-Path 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\tmp' "task7-phase-b-contract-review-$NewHead") "transport-fence-1-$Sha.ps1"
if (-not (Test-Path -LiteralPath $Path -PathType Leaf) -or (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Sha) { throw 'materializer review file mismatch' }
$Output = @(& $Path)
if (-not $?) { throw 'second derived materializer invocation failed' }
$Json = $Output -join "`n" | ConvertFrom-Json
if ($Json.fence_count -ne 5 -or @($Json.files | Where-Object { $_.disposition -cne 'existing-exact' }).Count -ne 0) { throw 'second materializer was not fully existing-exact' }
```

In a third fresh `shell_command`, perform the complete harmless self-test invocation:

```powershell
$ErrorActionPreference = 'Stop'
$Integration = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$NewHead = (git -C $Integration rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'new head unavailable' }
$Transport = Join-Path $Sdd "task-7-phase-b-transport-execution-$NewHead.md"
$Text = (New-Object Text.UTF8Encoding($false, $true)).GetString([IO.File]::ReadAllBytes($Transport))
$Fences = [regex]::Matches($Text, '(?ms)^```powershell\n(.*?)^```\s*$')
if ($Fences.Count -ne 6) { throw 'transport fence count mismatch' }
$Code = $Fences[1].Groups[1].Value
$Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Code)
$Algorithm = [Security.Cryptography.SHA256]::Create()
try { $Sha = [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant() } finally { $Algorithm.Dispose() }
$ReviewDir = Join-Path 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\tmp' "task7-phase-b-contract-review-$NewHead"
[void][IO.Directory]::CreateDirectory($ReviewDir)
$Path = Join-Path $ReviewDir "transport-fence-2-$Sha.ps1"
if (-not (Test-Path -LiteralPath $Path)) {
  $Stream = [IO.File]::Open($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  try { $Stream.Write($Bytes,0,$Bytes.Length); $Stream.Flush($true) } finally { $Stream.Dispose() }
}
if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Sha) { throw 'harmless review file mismatch' }
$Output = @(& $Path)
if (-not $? -or $Output.Count -ne 1) { throw 'harmless derived self-test failed' }
$Result = $Output[0] | ConvertFrom-Json
if ($Result.output -cne 'SELF-TEST PASS: 19 cases' -or $Result.fence -ne 5) { throw 'harmless self-test result mismatch' }
```

Do not extract or invoke transport ordinals 3–6 and do not invoke addendum ordinals 1–4.

- [ ] **Step 5 (2–5 min): Prove mechanical scope and absence of stale production identity**

```powershell
$ErrorActionPreference = 'Stop'
$Integration = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$NewHead = (git -C $Integration rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'new head unavailable' }
$Addendum = Join-Path $Sdd "task-7-phase-b-policy-correction-$NewHead.md"
$Transport = Join-Path $Sdd "task-7-phase-b-transport-execution-$NewHead.md"
$A = [IO.File]::ReadAllText($Addendum,[Text.UTF8Encoding]::new($false,$true))
$T = [IO.File]::ReadAllText($Transport,[Text.UTF8Encoding]::new($false,$true))
if ($A.Contains('2eb90e3f99219e28390570d13bd906cfe6e17012')) { throw 'old head remains in derived addendum' }
if ([regex]::Matches($A,[regex]::Escape("`$Root = 'D:\workspace\pyscf\.agents\active\precision-ci'")).Count -ne 0) { throw 'old state root assignment remains' }
$ExpectedRoot = "`$Root = 'D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$NewHead'"
if ([regex]::Matches($A,[regex]::Escape($ExpectedRoot)).Count -ne 4) { throw 'new state namespace count mismatch' }
if ($T.Contains('task-7-phase-b-policy-correction.md') -or $T.Contains('task7-phase-b-transport\task7-')) { throw 'transport still points at old namespace' }
if ([regex]::Matches($A,'(?m)^\$Head = ''[0-9a-f]{40}''$').Count -ne 5) { throw 'head binding cardinality mismatch' }
```

- [ ] **Step 6 (2–5 min): Require independent execution-contract and transport review**

Give independent reviewers: immutable input hashes, helper source, exact replacement counts (`old head=10`, root assignment=`4`, addendum filename=`7`, addendum SHA=`7`, transport namespace=`6`, each old fence hash=`4`), derived document hashes, five addendum fence hashes, six transport fence hashes, AST results, two materializer results, and the harmless `19 cases` output. Require explicit `Execution Contract: APPROVED` and `Transport Contract: APPROVED`. Review must confirm that initial candidate uniqueness applies only before a binding exists; frozen pairs use exact bound run IDs plus the two-ID allowlist; no third exact-head run is admitted; old state is immutable; and production ordinals were not executed.

After approval, rerun the helper and capture `$RebindOutput`/`$Rebind` exactly as in Step 2. Render the following active lines; the two loops produce five and six hash lines respectively:

```powershell
$ContractLines = @(
  "- production_uhf_phase_b_state_root: ``$($Rebind.state_root)``",
  "- production_uhf_phase_b_addendum_path: ``$($Rebind.addendum_path)``",
  "- production_uhf_phase_b_addendum_sha256: ``$($Rebind.addendum_sha256)``",
  "- production_uhf_phase_b_transport_path: ``$($Rebind.transport_path)``",
  "- production_uhf_phase_b_transport_sha256: ``$($Rebind.transport_sha256)``"
)
for ($Ordinal = 1; $Ordinal -le 5; $Ordinal++) {
  $Key = "addendum_fence_$($Ordinal)_sha256"
  $ContractLines += "- production_uhf_phase_b_addendum_fence_$($Ordinal)_sha256: ``$($Rebind[$Key])``"
}
for ($Ordinal = 1; $Ordinal -le 6; $Ordinal++) {
  $Key = "transport_fence_$($Ordinal)_sha256"
  $ContractLines += "- production_uhf_phase_b_transport_fence_$($Ordinal)_sha256: ``$($Rebind[$Key])``"
}
$ContractLines += '- production_uhf_phase_b_contract_review: `Execution Contract APPROVED; Transport Contract APPROVED`'
$ContractLines
```

Require every rendered hash value to match `^[0-9a-f]{64}$`, then use `apply_patch` to add the rendered lines byte-for-byte to the active document. Require each key exactly once before Task 4.

---

### Task 4: Execute the reviewed four-block Phase B dispatch and heartbeat handoff

**Files:**
- Read reviewed: `task-7-phase-b-policy-correction-$NewHead.md`
- Read reviewed: `task-7-phase-b-transport-execution-$NewHead.md`
- Create through approved blocks only: new head-bound latch/binding/manifest/launch-ready/handoff files

The derived blocks retain these two exact configurations and no others:

| Ordinal | `nodeids_file` | `repeats` | `platform` | `python_version` | `profile` | artifact |
| --- | --- | --- | --- | --- | --- | --- |
| Windows | `.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt` | `20` | `windows-latest` | `3.12` | `4/4` | `precision-Windows-py3.12` |
| Linux | `.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt` | `20` | `ubuntu-latest` | `3.12` | `4/4` | `precision-Linux-py3.12` |

- [ ] **Step 1 (2–5 min): Revalidate the frozen contract and classify the new namespace**

In a read-only fresh shell, require local and remote validation heads equal `$NewHead`, active keys and reviewed addendum/transport hashes each match exactly once, old state files remain byte-identical, no matching heartbeat process exists, no active native scheduler exists, and the heartbeat source hash/self-test match the derived addendum's frozen values. On first entry the new state root must be absent. On recovery entry, every existing new-namespace file must belong to the exact lowest incomplete ordinal and is admitted only through that ordinal's approved strict recovery path; never delete, overwrite, or skip it. Do not query runs outside the approved Block 1 logic and do not create the state root during this precheck.

- [ ] **Step 2 (2–5 min): Submit reviewed production ordinal 1 in its own fresh shell**

Copy the complete `Production ordinal 1` PowerShell fence from the reviewed head-bound transport document as the entire `shell_command` payload. It must recheck PS5.1, the derived addendum hash, exact materialized Block 1 file hash and AST, then invoke only `& $FencePath`. Require tool exit `0` before proceeding. This dispatches or strictly recovers only the Windows UHF run and atomically freezes its binding.

- [ ] **Step 3 (2–5 min): Submit reviewed production ordinal 2 in a second fresh shell**

Only after ordinal 1 exit `0`, submit the complete `Production ordinal 2` transport fence in a new `shell_command`. Require exit `0`. It re-runs the full preflight, validates the frozen Windows ID, admits only that ID while binding Linux, dispatches or strictly recovers only Linux, and writes/revalidates the exact ordered two-run manifest. Do not reuse the ordinal-1 shell.

- [ ] **Step 4 (2–5 min): Submit reviewed production ordinal 3 in a third fresh shell**

Only after ordinal 2 exit `0`, submit the complete `Production ordinal 3` transport fence in a new `shell_command`. Require exit `0`. This is the only Block 3 write: an immutable, atomic, hash-bound launch-ready JSON. It must not dispatch, launch a process, or change Goal.

- [ ] **Step 5 (2–5 min): Submit reviewed production ordinal 4 in a fourth fresh shell**

Only after ordinal 3 exit `0`, submit the complete `Production ordinal 4` transport fence in a new `shell_command`. Require exit `0`. Its internal minimal `Start-Process` launches exactly one heartbeat for the two frozen IDs with `1800/300`, verifies direct handle/PID/start time and exact CIM identity, sets and independently reads Goal exactly `paused`, then atomically freezes the handoff JSON. If it fails, accept only the addendum's direct-handle cleanup, CIM-gone check, aggregate error, and exact Goal `active` reconciliation; do not rerun an earlier ordinal.

- [ ] **Step 6 (2–5 min): Freeze the handoff and enter no-poll waiting**

Read back the manifest, launch-ready, and handoff hashes and exact two run IDs from the new state namespace, add them to the active document with `apply_patch`, and verify Goal exactly `paused`. From this point, do not call `gh run list`, `gh run view`, `gh api`, or start any second poller. The sole heartbeat owns both IDs until it exits and wakes the task.

---

### Task 5: Perform terminal identity, artifact, and frozen-validator acceptance

**Files:**
- Read: new head-bound handoff/manifest/bindings
- Create: two new immutable archive directories and their validator reports
- Update ignored active/report documents only after exact readback

- [ ] **Step 1 (2–5 min): Gate on exact heartbeat exit and Goal active**

Use the handoff's PID/start time/executable identity to require `Refresh(); HasExited=$true` and CIM absence. Independently read Goal through the approved App Server bridge and require exactly `active`. If the process still exists or Goal is not exact `active`, stop; do not manually poll GitHub and do not dispatch.

- [ ] **Step 2 (2–5 min): Fetch and freeze exact terminal run/job/artifact identities**

Start one fresh acceptance shell by loading the exact head-bound state and manifest:

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'psiQAQ/pyscf'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$Integration = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$NewHead = (git -C $Integration rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'acceptance head unavailable' }
$StateRoot = "D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$NewHead"
$ManifestPath = Join-Path $StateRoot 'production-uhf-runs.json'
$Manifest = @((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($ManifestPath)) | ConvertFrom-Json)
if ($Manifest.Count -ne 2) { throw 'terminal manifest must have exactly two entries' }
$WindowsEntry = @($Manifest | Where-Object { $_.platform -ceq 'windows-latest' })
$LinuxEntry = @($Manifest | Where-Object { $_.platform -ceq 'ubuntu-latest' })
if ($WindowsEntry.Count -ne 1 -or $LinuxEntry.Count -ne 1) { throw 'terminal platform mapping mismatch' }
$Entries = @($WindowsEntry[0],$LinuxEntry[0])
$FrozenIds = [long[]]@($Entries | ForEach-Object { [long]$_.run_id })
if (@($FrozenIds | Select-Object -Unique).Count -ne 2) { throw 'terminal run IDs are not unique' }
```

For each entry in `$Entries`, in the fixed Windows-then-Linux order, set `$RunId=[long]$Entry.run_id` and `$ArtifactName=[string]$Entry.artifact`, then run native `gh` commands and check `$LASTEXITCODE` immediately:

```powershell
$RunRaw = @(gh run view $RunId --repo 'psiQAQ/pyscf' --json databaseId,attempt,event,workflowName,headSha,headBranch,status,conclusion,jobs,url)
if ($LASTEXITCODE -ne 0) { throw "gh run view failed for $RunId" }
$Run = ConvertFrom-Json ($RunRaw -join "`n")
$ArtifactRaw = @(gh api "repos/psiQAQ/pyscf/actions/runs/$RunId/artifacts?per_page=100")
if ($LASTEXITCODE -ne 0) { throw "gh artifact query failed for $RunId" }
$Artifacts = @((ConvertFrom-Json ($ArtifactRaw -join "`n")).artifacts)
```

Require: exact bound `databaseId`; `attempt=1`; `event=workflow_dispatch`; workflow `Precision investigation`; branch `codex/test/sgx-extra-cycle-convergence-validation`; head `$NewHead`; terminal `completed/success`; exactly one `precision` job with `completed/success`; exactly one non-expired artifact with the manifest's exact name. After both exact identities are frozen, perform one `gh run list --repo $Repo --workflow ci-precision-check.yml --branch $Branch --event workflow_dispatch --limit 100 --json databaseId,headSha,headBranch,event,workflowName,status` call with an immediate native exit check. Among exact-head rows whose `databaseId` is strictly greater than the manifest's frozen Windows `before_max` floor, require every `databaseId` belongs to `$FrozenIds`; among active exact-head rows above that same floor, require the same allowlist. Any third row or identity mismatch stops acceptance and does not replay.

- [ ] **Step 3 (2–5 min): Create each immutable archive and download its sole artifact**

For Windows use suffix `production-uhf-windows-py312`; for Linux use `production-uhf-linux-py312`. Compute `$Archive = Join-Path 'D:\workspace\pyscf\.agents\archive\precision-ci\experiments' "$RunId-$Suffix"`, refuse any existing path, and create the directory exactly once with `[IO.Directory]::CreateDirectory($Archive)`. Then:

```powershell
gh run download $RunId --repo 'psiQAQ/pyscf' --name $ArtifactName --dir $Archive
if ($LASTEXITCODE -ne 0) { throw "gh run download failed for $RunId" }
```

Construct compact `run.json` with the exact fields shown in Step 2 plus the sole artifact identity, and freeze the validator through the same CreateNew/Flush path:

```powershell
$ErrorActionPreference = 'Stop'
$SoleJobs = @($Run.jobs | ForEach-Object {
  [ordered]@{
    databaseId = [long]$_.databaseId
    name = [string]$_.name
    status = [string]$_.status
    conclusion = [string]$_.conclusion
  }
})
$RunPayload = [ordered]@{
  databaseId = [long]$Run.databaseId
  attempt = [int]$Run.attempt
  event = [string]$Run.event
  workflowName = [string]$Run.workflowName
  headSha = [string]$Run.headSha
  headBranch = [string]$Run.headBranch
  status = [string]$Run.status
  conclusion = [string]$Run.conclusion
  jobs = $SoleJobs
  artifacts = @([ordered]@{
    id = [long]$Artifact.id
    name = [string]$Artifact.name
    digest = [string]$Artifact.digest
    sizeInBytes = [long]$Artifact.size_in_bytes
    expired = [bool]$Artifact.expired
  })
}
$Utf8 = [Text.UTF8Encoding]::new($false)
$RunBytes = $Utf8.GetBytes(($RunPayload | ConvertTo-Json -Depth 6 -Compress) + "`n")
$RunPath = Join-Path $Archive 'run.json'
$RunStream = [IO.File]::Open($RunPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try { $RunStream.Write($RunBytes,0,$RunBytes.Length); $RunStream.Flush($true) } finally { $RunStream.Dispose() }
$ValidatorSource = 'D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py'
$ValidatorBytes = [IO.File]::ReadAllBytes($ValidatorSource)
$ValidatorPath = Join-Path $Archive 'validate_precision_production.py'
$ValidatorStream = [IO.File]::Open($ValidatorPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try { $ValidatorStream.Write($ValidatorBytes,0,$ValidatorBytes.Length); $ValidatorStream.Flush($true) } finally { $ValidatorStream.Dispose() }
if ((Get-FileHash -LiteralPath $ValidatorPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne 'd9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c') { throw 'frozen validator hash mismatch' }
```

- [ ] **Step 4 (2–5 min): Validate Windows installed-wheel/native-26 evidence**

```powershell
$ErrorActionPreference = 'Stop'
conda run --no-capture-output -n pyscf-win313-test python `
  "$WindowsArchive\validate_precision_production.py" $WindowsArchive `
  --mode installed-wheel `
  --expected-sha $NewHead `
  --expected-nodeids-file 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration\.github\workflows\precision-uhf-smearing-extra-cycle-nodeids.txt' `
  --expected-profile omp4-blas4 `
  --expected-repeats 20 `
  --expected-platform windows-latest `
  --expected-python 3.12 `
  --expected-native-count 26 `
  --run-metadata "$WindowsArchive\run.json" `
  --expected-run-id $WindowsRunId `
  --expected-branch 'codex/test/sgx-extra-cycle-convergence-validation' `
  --expected-artifact-name 'precision-Windows-py3.12' `
  --report "$WindowsArchive\production-validation.json"
if ($LASTEXITCODE -ne 0) { throw 'Windows frozen validator failed' }
```

Read the JSON back strictly and require `valid -eq $true`, `verdict -ceq 'PASS'`, `records=20`, `pass=20`, `fail=0`, exact SHA/nodeid/profile/run metadata, LibXC `7.1.2`, installed-wheel mode, and 26 native libraries.

- [ ] **Step 5 (2–5 min): Validate Linux source-tree/native-16 evidence including direct runner exit**

Before invoking the validator, require `$LinuxArchive\runner-exit-code.txt` is an ordinary file with bytes exactly `0x30,0x0A`; absence, directory type, BOM, CR, or trailing bytes is `INVALID`.

```powershell
$ErrorActionPreference = 'Stop'
$ExitBytes = [IO.File]::ReadAllBytes("$LinuxArchive\runner-exit-code.txt")
if (-not [Linq.Enumerable]::SequenceEqual([byte[]]$ExitBytes,[byte[]]@(0x30,0x0A))) { throw 'Linux runner-exit-code.txt is not exact 0 LF' }
conda run --no-capture-output -n pyscf-win313-test python `
  "$LinuxArchive\validate_precision_production.py" $LinuxArchive `
  --mode source-tree `
  --expected-sha $NewHead `
  --expected-nodeids-file 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration\.github\workflows\precision-uhf-smearing-extra-cycle-nodeids.txt' `
  --expected-profile omp4-blas4 `
  --expected-repeats 20 `
  --expected-platform ubuntu-latest `
  --expected-python 3.12 `
  --expected-native-count 16 `
  --run-metadata "$LinuxArchive\run.json" `
  --expected-run-id $LinuxRunId `
  --expected-branch 'codex/test/sgx-extra-cycle-convergence-validation' `
  --expected-artifact-name 'precision-Linux-py3.12' `
  --report "$LinuxArchive\production-validation.json"
if ($LASTEXITCODE -ne 0) { throw 'Linux frozen validator failed' }
```

Read back the same strict report fields and require source-tree mode, native count 16, and the same `$NewHead` as Windows. Do not infer validity from the 20 records or job conclusion.

- [ ] **Step 6 (2–5 min): Unlock only on an exact two-report PASS conjunction**

Read both report bytes and SHA-256 values. Require each JSON has `valid=true`, plain `PASS`, 20/20/0, its exact run/artifact identity, and identical tested SHA equal to `$NewHead`. If either side fails, record `production_uhf_terminal_status: STOP` with the exact validator error and preserve both archives; do not update Step 3, do not dispatch, and do not reinterpret old evidence. Only the conjunction may set `production_unix_exit_evidence_terminal_status: PASS` in the active document.

---

### Task 6: Record the parent Task 7 Step 3 recovery entry

**Files:**
- Update ignored: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Update ignored: `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-report.md`
- Do not modify tracked source or any GitHub issue

- [ ] **Step 1 (2–5 min): Record immutable terminal evidence with `apply_patch`**

Add exact new head, two run IDs, two artifact IDs/digests/sizes, archive paths, validator SHA, report SHA values, record counts, environment modes, native counts, runner-exit file SHA, and the two plain `PASS` verdicts. Preserve the old Linux `INVALID` and old Windows `PASS` entries as historical evidence; do not overwrite them.

- [ ] **Step 2 (2–5 min): Replace the next-step key with a narrow Step 3 recovery instruction**

Set the unique next-step entry to:

```text
- production_unix_exit_evidence_next_step: `Task 7 Step 3 only: read docs/superpowers/plans/2026-08-11-sgx-extra-cycle-convergence-production.md lines 1562-1571; independently review the three production commits plus stacked integration using the two new frozen-validator PASS reports; do not repeat dispatch, update issue 3312, or start Task 8`
```

This records the recovery point; it does not perform Step 3.

- [ ] **Step 3 (2–5 min): Run final state, scope, encoding, and contradiction checks**

```powershell
$ErrorActionPreference = 'Stop'
$Design = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$Integration = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Active = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Plan = Join-Path $Design 'docs\superpowers\plans\2026-08-12-unix-precision-runner-exit-evidence.md'
$NewHead = (git -C $Integration rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $NewHead -notmatch '^[0-9a-f]{40}$') { throw 'final new head unavailable' }
$Remote = @(git -C $Integration ls-remote --heads origin 'refs/heads/codex/test/sgx-extra-cycle-convergence-validation')
if ($LASTEXITCODE -ne 0 -or $Remote.Count -ne 1 -or ($Remote[0] -split "`t")[0] -cne $NewHead) { throw 'final local/remote head mismatch' }
git -C $Integration diff --check '2eb90e3f99219e28390570d13bd906cfe6e17012..HEAD'
if ($LASTEXITCODE -ne 0) { throw 'implementation diff-check failed' }
$FinalNames = @(git -C $Integration diff --name-only '2eb90e3f99219e28390570d13bd906cfe6e17012..HEAD')
if ($LASTEXITCODE -ne 0 -or $FinalNames.Count -ne 2) { throw 'implementation scope changed' }
$Text = [IO.File]::ReadAllText($Active,[Text.UTF8Encoding]::new($false,$true))
foreach ($Key in @('production_validation_head','production_unix_exit_evidence_implementation_commit','production_unix_exit_evidence_terminal_status','production_unix_exit_evidence_next_step')) {
  if ([regex]::Matches($Text,"(?m)^- $Key`:").Count -ne 1) { throw "active key cardinality mismatch: $Key" }
}
if ($Text -notmatch '(?m)^- production_unix_exit_evidence_terminal_status: `PASS`$') { throw 'two-platform PASS gate absent' }
$PlanText = [IO.File]::ReadAllText($Plan,[Text.UTF8Encoding]::new($false,$true))
if ($PlanText -match '(?i)(TO'+'DO|T'+'BD|FIX'+'ME)') { throw 'unfinished authoring token remains in plan' }
```

Also run `git diff --check` in the design worktree and `git status --short` in both worktrees. At this terminal point the integration branch contains exactly one new two-file implementation commit over `2eb90e3f99219e28390570d13bd906cfe6e17012`; the design branch contains only this plan commit; ignored execution/report/state files do not enter either tracked diff.

## Plan Self-Review Checklist

- [ ] Every approved-spec requirement maps to Task 1 tests/implementation, Task 2 publication, Tasks 3–4 dispatch safety, Task 5 strict evidence acceptance, or Task 6 recovery.
- [ ] The plan contains one Bash implementation snippet, four behavior-test methods, one `resolve_bash`, and one mechanical rebind helper; no alternative implementation remains.
- [ ] All paths are absolute where host identity matters and repository-relative where MSYS argv conversion matters; all dynamic identities are derived from a verified 40-hex `$NewHead`.
- [ ] Every `gh`, `git`, `conda`, and Bash native command that affects a gate has an immediate exit check.
- [ ] The derived addendum has exactly five PowerShell fences and the derived transport has exactly six; every fence has Windows PowerShell 5.1 AST errors `0` before approval.
- [ ] Task 3 runs only materialization and the harmless 19-case fence; Task 4 alone invokes production ordinals 1–4 in four fresh `shell_command` processes.
- [ ] The old addendum, transport, state, archives, runs, and artifacts remain immutable; no replay, force push, second poller, early Step 3, Task 8, or issue `#3312` update is permitted.
