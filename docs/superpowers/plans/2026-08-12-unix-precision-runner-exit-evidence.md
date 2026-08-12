# Unix Precision Runner Exit Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add byte-exact Unix runner exit evidence, publish one reviewed evidence commit, freeze its remote readback as one literal `EvidenceHead`, prove that exact SHA with an independently monitored macOS witness, and accept a later non-overlapping Windows/Linux UHF pair only when all three frozen-validator reports bind that same SHA.

**Architecture:** Keep the production change at the wrapper boundary: a real Bash wrapper captures the Python runner status, writes `runner-exit-code.txt`, and returns the same status. A real-wrapper/fake-`python` Windows/MSYS contract test supplies the local RED/GREEN proof without scientific execution. After review and an ordinary fast-forward push, a strict macOS one-repeat witness proves the real Unix transport path; only that witness `PASS` unlocks a mechanically head/state-rebound four-block Windows/Linux pair and its single heartbeat.

**Tech Stack:** Bash with `set -euo pipefail`; Python standard library (`unittest`, `subprocess`, `pathlib`, `tempfile`, `hashlib`); Windows PowerShell 5.1 and .NET file APIs; Git/GitHub CLI; the frozen production validator at SHA-256 `d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c`.

## Global Constraints

- The approved requirements source is `docs/superpowers/specs/2026-08-12-unix-precision-runner-exit-evidence-design.md` at SHA-256 `af06fdef54ae177c139e148c083f8162155713db3439e1d01042245bcdc2b3b5`. Stop if either path or hash differs.
- The implementation parent is exactly `2eb90e3f99219e28390570d13bd906cfe6e17012` in `D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration` on `codex/test/sgx-extra-cycle-convergence-validation`.
- The implementation commit changes exactly `.github/workflows/run_unix_precision_tests.sh` and `.github/workflows/test_precision_investigation_contract.py`. Do not modify the Python runner, validator, workflow YAML, science code, parameters, assertions, nodeids, dependencies, archives, or old run metadata.
- Use `apply_patch` for repository and local-document edits. Preserve UTF-8 without BOM, LF-only, final LF, and the existing executable bit of the Bash wrapper. Do not install packages.
- Keep commits separate: this plan commit is documentation only; the later CI evidence commit is one implementation commit. Do not amend or rewrite `2eb90e3f99219e28390570d13bd906cfe6e17012`.
- Task 2 has the user's existing方案 A authority for one ordinary fast-forward push to the same validation branch. Do not force-push, change remotes, create a PR/issue, or push any other branch.
- Old latches, bindings, manifests, launch files, handoffs, runs `31548379750`/`31548408412`, artifacts `9123528060`/`9123362435`, and their archives are immutable. The new head uses a brand-new state namespace.
- Tasks 1–3 must not dispatch workflows, start a heartbeat, or change Goal. Task 3 may execute only the harmless in-memory ordinal-5 self-test; pair production ordinals 1–4 remain unexecuted until Task 5.
- Push before native Linux/macOS local testing is intentional: do not claim either native host test ran. Task 2 freezes the one remote readback as literal `EvidenceHead`; Tasks 3–7 consume that active-document literal and never recalculate, follow, or advance the branch head.
- Task 4's macOS witness is the only pre-pair real Unix execution gate and is not a scientific-stability conclusion. It has its own exact direct-child heartbeat identity and Goal `paused`/terminal child-gone/Goal `active` lifecycle. That heartbeat must exit and the witness must strictly pass before Task 5 may start its distinct pair heartbeat; the two heartbeat lifecycles never overlap.
- Task 5 uses one heartbeat for the two new pair run IDs with `IntervalSeconds=1800` and `WakeAfterMinutes=300`, then leaves Goal exactly `paused`. Do not manually poll GitHub after the handoff and do not replay a dispatch.
- Task 6 begins only after that exact pair heartbeat exits and Goal is independently read back as exactly `active`. Actions success and 20/20 records are advisory until the frozen validator returns `valid=true` and plain `PASS` for each artifact.
- Do not update `pyscf/pyscf#3312`. Task 7 records only the parent Task 7 Step 3 recovery entry.

## File Map

| Path | Operation | Purpose |
| --- | --- | --- |
| `.github/workflows/run_unix_precision_tests.sh` | Modify in Task 1 | Create the output directory, capture the real Python runner status, write its decimal value followed by one LF, and return the same status. |
| `.github/workflows/test_precision_investigation_contract.py` | Modify in Task 1 | Discover real GNU Bash safely and exercise the real wrapper against a fake `python` in four behavior tests. |
| `.agents/active/libxc-712-release-revalidation.md` | Local ignored updates in Tasks 2–7 | Freeze authenticated head, contract hashes, heartbeat lifecycles, run identities, verdicts, and recovery entry. |
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-policy-correction.md` | Immutable input | Double-approved Phase B addendum, SHA-256 `020ea0d6225632b55f37b6167a2e0fd2eed034b87bf6b03946d24243b670a395`. |
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-transport-execution.md` | Immutable input | Approved transport template, SHA-256 `f24d02372adc6b0051fdfe6cf8e1032e5322754ebdeba78298cbe97a4b83304b`. |
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-policy-correction-$EvidenceHead.md` | CreateNew in Task 3 | Mechanically head/state-rebound four-block execution contract using the frozen 40-hex active-document literal. |
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-transport-execution-$EvidenceHead.md` | CreateNew in Task 3 | Hash-bound materialization and fresh-shell invocation contract for the derived addendum. |
| `.agents/active/precision-ci/task-7-phase-b-$EvidenceHead/` | Created only by Task 5 | New pair latches, bindings, manifest, launch-ready, handoff, and terminal state; no old state path is reused. |
| `.agents/active/precision-ci/task-7-unix-wrapper-witness-$EvidenceHead/` | Created only by Task 4 | Immutable macOS witness latch, binding, heartbeat handoff/terminal identity, archive, and strict verdict. |
| `.agents/archive/precision-ci/experiments/$RunId-production-uhf-$PlatformSlug-py312/` | CreateNew in Task 6 | Immutable pair artifact, run metadata, validator copy, and validation report. `$RunId` and `$PlatformSlug` are computed from the frozen manifest entry. |

---

### Task 1: Build the wrapper evidence commit with real-wrapper TDD

**Files:**
- Modify: `.github/workflows/test_precision_investigation_contract.py`
- Modify: `.github/workflows/run_unix_precision_tests.sh`
- Worktree: `D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration`

**Interfaces:**
- Consumes: approved spec SHA-256 `af06fdef54ae177c139e148c083f8162155713db3439e1d01042245bcdc2b3b5`, validation parent `2eb90e3f99219e28390570d13bd906cfe6e17012`, and the existing four-argument Unix wrapper CLI.
- Produces: one reviewed commit whose parent is the validation parent and whose exact tracked diff is the wrapper plus its contract test; the wrapper writes decimal runner status plus LF and returns the same status.

- [ ] **Step 1 (2–5 min): Freeze the implementation baseline and approved spec**

Run in a fresh PowerShell shell:

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$DesignWorktree = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$ExpectedParent = '2eb90e3f99219e28390570d13bd906cfe6e17012'
$ExpectedSpec = 'af06fdef54ae177c139e148c083f8162155713db3439e1d01042245bcdc2b3b5'
Set-Location -LiteralPath $Worktree
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
FAKE_PYTHON = r'''#!/usr/bin/env bash
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
        fake_bytes = fake_python.read_bytes()
        if b'\x00' in fake_bytes:
            raise AssertionError('fake python contains an embedded NUL')
        if b"printf '%s\\0' '__CALL__' \"$@\"" not in fake_bytes:
            raise AssertionError('fake python lost the literal NUL escape')
        if b"printf '%s\\n' 'fake evidence sentinel'" not in fake_bytes:
            raise AssertionError('fake python lost the literal LF escape')
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
Set-Location -LiteralPath $Worktree
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

- [ ] **Step 6 (2–5 min): Normalize the two tracked files deterministically**

Run this one fresh Windows PowerShell shell after both `apply_patch` edits. It accepts only UTF-8 input, removes at most one BOM, converts CRLF/bare CR to LF, requires a final LF, and writes exactly the two approved paths:

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
Set-Location -LiteralPath $Worktree
@'
from pathlib import Path

paths = (
    Path('.github/workflows/run_unix_precision_tests.sh'),
    Path('.github/workflows/test_precision_investigation_contract.py'),
)
for path in paths:
    raw = path.read_bytes()
    text = raw.decode('utf-8')
    if text.startswith('\ufeff'):
        text = text[1:]
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if not text.endswith('\n'):
        text += '\n'
    path.write_bytes(text.encode('utf-8'))
'@ | conda run --no-capture-output -n pyscf-win313-test python -
if ($LASTEXITCODE -ne 0) { throw 'deterministic UTF-8/LF normalization failed' }
```

- [ ] **Step 7 (2–5 min): Run GREEN, full contract, syntax, EOL, and scope checks**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
Set-Location -LiteralPath $Worktree
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

The Windows discovery evidence must resolve `git` to `D:\Program Files\Git\cmd\git.exe`, Bash to `D:\Program Files\Git\bin\bash.exe`, and the probe output to GNU Bash `5.2.15` with `x86_64-pc-msys`. Do not run or claim native Linux/macOS tests before push; Task 4 supplies the real Unix witness after publication.

- [ ] **Step 8 (2–5 min): Commit exactly the two implementation files**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
Set-Location -LiteralPath $Worktree
git -C $Worktree add -- `
  '.github/workflows/run_unix_precision_tests.sh' `
  '.github/workflows/test_precision_investigation_contract.py'
if ($LASTEXITCODE -ne 0) { throw 'git add failed' }
$Staged = @(git -C $Worktree diff --cached --name-only)
if ($LASTEXITCODE -ne 0 -or $Staged.Count -ne 2) { throw 'staged scope mismatch' }
git -C $Worktree commit -m 'ci: record Unix precision runner exit code'
if ($LASTEXITCODE -ne 0) { throw 'implementation commit failed' }
$ReviewedCommit = (git -C $Worktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $ReviewedCommit -notmatch '^[0-9a-f]{40}$' -or $ReviewedCommit -ceq '2eb90e3f99219e28390570d13bd906cfe6e17012') { throw 'new implementation commit invalid' }
$Parent = (git -C $Worktree rev-parse HEAD^).Trim()
if ($LASTEXITCODE -ne 0 -or $Parent -cne '2eb90e3f99219e28390570d13bd906cfe6e17012') { throw 'implementation commit parent mismatch' }
$CommitNames = @(git -C $Worktree diff-tree --no-commit-id --name-only -r $ReviewedCommit)
if ($LASTEXITCODE -ne 0 -or $CommitNames.Count -ne 2) { throw 'commit scope mismatch' }
```

- [ ] **Step 9 (2–5 min): Obtain independent SDD approval before publication**

Give the reviewer the approved spec hash, preserved Windows/MSYS RED output, Windows/MSYS GREEN/full-suite output, Bash/Python static results, deterministic encoding/EOL/mode evidence, exact two-file diff, and commit SHA. Require `Spec Compliance: APPROVED` and `Code Quality: APPROVED` in an ignored review report. A finding returns to the relevant earlier step and creates an ordinary follow-up commit; do not amend a reviewed/public SHA and do not enter Task 2 without both approvals. The report must say native Linux/macOS tests were not run and must not infer them from MSYS.

---

### Task 2: Fast-forward publish the reviewed evidence commit

**Files:**
- Local ignored update: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Remote ref: `origin/codex/test/sgx-extra-cycle-convergence-validation`

**Interfaces:**
- Consumes: Task 1's independently approved two-file commit and exact old remote head `2eb90e3f99219e28390570d13bd906cfe6e17012`.
- Produces: one ordinary fast-forward remote readback frozen as the unique literal `production_unix_exit_evidence_head`; it produces no dispatch, latch, Goal, or heartbeat state.

- [ ] **Step 1 (2–5 min): Recheck review, local ancestry, and exact old remote head**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$ExpectedOld = '2eb90e3f99219e28390570d13bd906cfe6e17012'
Set-Location -LiteralPath $Worktree
$ExpectedEvidenceHead = (git -C $Worktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $ExpectedEvidenceHead -notmatch '^[0-9a-f]{40}$') { throw 'reviewed evidence head unavailable' }
if ((git -C $Worktree branch --show-current).Trim() -cne $Branch -or $LASTEXITCODE -ne 0) { throw 'branch mismatch' }
git -C $Worktree merge-base --is-ancestor $ExpectedOld $ExpectedEvidenceHead
if ($LASTEXITCODE -ne 0) { throw 'new head is not a descendant of the frozen parent' }
$Status = @(git -C $Worktree status --porcelain=v1)
if ($LASTEXITCODE -ne 0) { throw 'git status failed before push' }
if (@($Status | Where-Object { $_ -notmatch '^\?\? .*(?i)\.dll$' }).Count -ne 0) { throw 'tracked or non-DLL worktree change before push' }
$Remote = @(git -C $Worktree ls-remote --heads origin "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $Remote.Count -ne 1) { throw 'old remote head unavailable or ambiguous' }
$RemoteOld = ($Remote[0] -split "`t")[0]
if ($RemoteOld -cne $ExpectedOld) { throw "remote moved: $RemoteOld" }
[pscustomobject]@{expected_evidence_head=$ExpectedEvidenceHead;expected_line="- production_unix_exit_evidence_expected_head: ``$ExpectedEvidenceHead``";review='Spec Compliance APPROVED; Code Quality APPROVED'}|ConvertTo-Json -Compress
```

- [ ] **Step 2 (2–5 min): Freeze the reviewed `ExpectedEvidenceHead` before push**

Use `apply_patch` to add Step 1's printed `expected_line` byte-for-byte exactly once to the active document. Then run this fresh-shell readback:

```powershell
$ErrorActionPreference='Stop'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true))
$M=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_expected_head: `([0-9a-f]{40})`$')
if($M.Count-ne1){throw 'ExpectedEvidenceHead is not uniquely frozen before push'}
[pscustomobject]@{expected_evidence_head=$M[0].Groups[1].Value;source='independently reviewed commit'}|ConvertTo-Json -Compress
```

- [ ] **Step 3 (2–5 min): Push only `ExpectedEvidenceHead`, read it back once, and render `EvidenceHead`**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
Set-Location -LiteralPath $Worktree
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true))
$ExpectedMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_expected_head: `([0-9a-f]{40})`$')
if($ExpectedMatch.Count-ne1){throw 'ExpectedEvidenceHead unavailable before push'}
$ExpectedEvidenceHead=$ExpectedMatch[0].Groups[1].Value
$LocalHead = (git -C $Worktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $LocalHead -cne $ExpectedEvidenceHead) { throw 'local head is not reviewed ExpectedEvidenceHead' }
git -C $Worktree push origin "$ExpectedEvidenceHead`:refs/heads/$Branch"
if ($LASTEXITCODE -ne 0) { throw 'ordinary fast-forward push failed' }
$Readback = @(git -C $Worktree ls-remote --heads origin "refs/heads/$Branch")
if ($LASTEXITCODE -ne 0 -or $Readback.Count -ne 1) { throw 'remote readback unavailable' }
$RemoteHead = ($Readback[0] -split "`t")[0]
if ($RemoteHead -cne $ExpectedEvidenceHead) { throw "remote readback is not ExpectedEvidenceHead: $RemoteHead" }
$EvidenceHead = $ExpectedEvidenceHead
$PlanWorktree = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$PlanCommit = (git -C $PlanWorktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $PlanCommit -notmatch '^[0-9a-f]{40}$') { throw 'plan commit unavailable' }
$PlanPath = Join-Path $PlanWorktree 'docs\superpowers\plans\2026-08-12-unix-precision-runner-exit-evidence.md'
$PlanSha256 = (Get-FileHash -LiteralPath $PlanPath -Algorithm SHA256).Hash.ToLowerInvariant()
$Lines = @(
  '- production_unix_exit_evidence_plan_path: `D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\docs\superpowers\plans\2026-08-12-unix-precision-runner-exit-evidence.md`',
  "- production_unix_exit_evidence_plan_commit: ``$PlanCommit``",
  "- production_unix_exit_evidence_plan_sha256: ``$PlanSha256``",
  '- production_unix_exit_evidence_implementation_parent: `2eb90e3f99219e28390570d13bd906cfe6e17012`',
  "- production_unix_exit_evidence_implementation_commit: ``$EvidenceHead``",
  '- production_unix_exit_evidence_implementation_review: `Spec Compliance APPROVED; Code Quality APPROVED`',
  "- production_unix_exit_evidence_remote_head: ``$EvidenceHead``",
  "- production_unix_exit_evidence_head: ``$EvidenceHead``",
  '- production_unix_exit_evidence_next_step: `derive and independently review the frozen-head Phase B execution and transport contracts; do not dispatch`'
)
[pscustomobject]@{evidence_head=$EvidenceHead; lines=$Lines} | ConvertTo-Json -Depth 3
```

No `--force`, `--force-with-lease`, tag, PR, issue, dispatch, Goal, or heartbeat command belongs to this task. A readback mismatch stops here and never establishes `EvidenceHead`.

- [ ] **Step 4 (2–5 min): Freeze the authenticated `EvidenceHead` with `apply_patch`**

Use `apply_patch` on `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`. Replace the unique `production_validation_head` value with the immediately preceding command's printed literal `evidence_head`, replace `production_unix_exit_evidence_design_status` with `APPROVED`, and replace the existing `production_unix_exit_evidence_next_step` line with its nine printed `lines` entries byte-for-byte. This edit is the freeze point: every later task reads only this immutable literal and must not derive identity from a branch head.

- [ ] **Step 5 (2–5 min): Read back the frozen active-document identity without Git or GitHub**

```powershell
$ErrorActionPreference = 'Stop'
$PlanWorktree = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
Set-Location -LiteralPath $PlanWorktree
$Active = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Text = [IO.File]::ReadAllText($Active, [Text.UTF8Encoding]::new($false, $true))
$Keys = @('production_unix_exit_evidence_expected_head','production_validation_head','production_unix_exit_evidence_implementation_commit','production_unix_exit_evidence_remote_head','production_unix_exit_evidence_head')
$Values = @()
foreach ($Key in $Keys) {
  $M = [regex]::Matches($Text, "(?m)^- $Key`: ``([0-9a-f]{40})``$")
  if ($M.Count -ne 1) { throw "active key cardinality mismatch: $Key" }
  $Values += $M[0].Groups[1].Value
}
if (@($Values | Select-Object -Unique).Count -ne 1) { throw 'frozen active heads differ' }
[pscustomobject]@{evidence_head=$Values[0];source='active-document literal';branch_refresh_after_freeze=$false}|ConvertTo-Json -Compress
```

---

### Task 3: Mechanically derive and review the new head-bound Phase B contract

**Files:**
- Read immutable: `task-7-phase-b-policy-correction.md` and `task-7-phase-b-transport-execution.md`
- Create ignored: `task-7-phase-b-policy-correction-$EvidenceHead.md`
- Create ignored: `task-7-phase-b-transport-execution-$EvidenceHead.md`
- Create ignored helper: `rebind-task7-phase-b.py`

**Interfaces:**
- Consumes: Task 2's unique active-document `EvidenceHead`, immutable addendum SHA-256 `020ea0d6225632b55f37b6167a2e0fd2eed034b87bf6b03946d24243b670a395`, and immutable transport SHA-256 `f24d02372adc6b0051fdfe6cf8e1032e5322754ebdeba78298cbe97a4b83304b`.
- Produces: one head-bound execution document, one head-bound transport document, five addendum hashes, six transport hashes, a new state-root literal, and two independent `APPROVED` verdicts; no production ordinal is invoked.

- [ ] **Step 1 (2–5 min): Author the exact standard-library rebind helper**

Use `apply_patch` to create `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/rebind-task7-phase-b.py` with the complete code below. This helper verifies immutable inputs, exact replacement counts, active-head cardinality, five output fence hashes, and CreateNew-or-byte-exact output semantics. It strips the old transport's stale runtime-evidence tail and replaces it with an explicit review gate.

```python
import hashlib
import os
from pathlib import Path
import re
import sys


DESIGN_WORKTREE = Path(
    r'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
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
OLD_GATE_TAIL = "'(?m)^- production_sgx_formal_verdict: PASS$')"
NEW_GATE_TAIL_TEMPLATE = (
    "'(?m)^- production_sgx_formal_verdict: PASS$',\n"
    "        '(?m)^- production_unix_exit_evidence_expected_head: `{new_head}`$',\n"
    "        '(?m)^- production_unix_exit_evidence_head: `{new_head}`$',\n"
    "        '(?m)^- production_unix_wrapper_witness_verdict: PASS$')"
)
OLD_LOCAL_REFRESH = '''    $LocalHead = (Invoke-NativeText -FilePath 'git' -Label 'git rev-parse' -ArgumentList @(
        '-c', "safe.directory=$Worktree", '-C', $Worktree, 'rev-parse', 'HEAD')).Trim()
    if ($LocalHead -cne $Head) { throw "Local head mismatch: $LocalHead" }
'''
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
            os.fsync(stream.fileno())
    except FileExistsError:
        if path.read_bytes() != data:
            raise RuntimeError(f'existing output differs: {path}')
        return 'existing-exact'
    return 'created'


if len(sys.argv) != 2 or re.fullmatch(r'[0-9a-f]{40}', sys.argv[1]) is None:
    raise SystemExit('usage: rebind-task7-phase-b.py EVIDENCE_HEAD')
new_head = sys.argv[1]
if new_head == OLD_HEAD:
    raise RuntimeError('EvidenceHead still equals the implementation parent')

active_text = ACTIVE.read_bytes().decode('utf-8')
for key in ('production_validation_head', 'production_unix_exit_evidence_head'):
    active_heads = re.findall(
        rf'^- {key}: `([0-9a-f]{{40}})`$', active_text, re.M
    )
    if active_heads != [new_head]:
        raise RuntimeError(f'active {key} is not unique/EvidenceHead')

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
addendum = replace_exact(
    addendum, OLD_GATE_TAIL,
    NEW_GATE_TAIL_TEMPLATE.format(new_head=new_head), 4,
    'addendum frozen-head and macOS witness gates',
)
addendum = replace_exact(
    addendum, OLD_LOCAL_REFRESH, '', 4,
    'addendum prohibited local-head recalculation',
)
if (OLD_HEAD in addendum or OLD_ROOT_ASSIGNMENT in addendum or
        OLD_GATE_TAIL in addendum or OLD_LOCAL_REFRESH in addendum):
    raise RuntimeError('stale head/root/gate/local-head recalculation remains')
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

print('evidence_head=' + new_head)
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
$Design = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
Set-Location -LiteralPath $Design
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$')
if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$EvidenceHead=$HeadMatch[0].Groups[1].Value
$RebindOutput = @(conda run --no-capture-output -n pyscf-win313-test python `
  "$Design\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production\rebind-task7-phase-b.py" `
  $EvidenceHead)
if ($LASTEXITCODE -ne 0) { throw 'mechanical Phase B rebind failed' }
$Rebind = ConvertFrom-StringData ($RebindOutput -join "`n")
$Required = @(
  'evidence_head','state_root','addendum_path','addendum_sha256',
  'addendum_disposition','transport_path','transport_sha256',
  'transport_disposition'
)
foreach ($Key in $Required) {
  if (-not $Rebind.ContainsKey($Key)) { throw "missing rebind output: $Key" }
}
if ($Rebind.evidence_head -cne $EvidenceHead) { throw 'rebind output EvidenceHead mismatch' }
$RebindOutput
```

Retain `$Rebind` in this shell only for verification. Do not write anything under the new production state root in this task.

- [ ] **Step 3 (2–5 min): Parse every derived fence with Windows PowerShell 5.1**

```powershell
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSEdition -cne 'Desktop' -or $PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) { throw 'Windows PowerShell 5.1 required' }
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$Design = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$EvidenceHead=$HeadMatch[0].Groups[1].Value
$ExpectedCounts = [ordered]@{
  (Join-Path $Sdd "task-7-phase-b-policy-correction-$EvidenceHead.md") = 5
  (Join-Path $Sdd "task-7-phase-b-transport-execution-$EvidenceHead.md") = 6
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
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$EvidenceHead=$HeadMatch[0].Groups[1].Value
$Transport = Join-Path $Sdd "task-7-phase-b-transport-execution-$EvidenceHead.md"
$Text = (New-Object Text.UTF8Encoding($false, $true)).GetString([IO.File]::ReadAllBytes($Transport))
$Fences = [regex]::Matches($Text, '(?ms)^```powershell\n(.*?)^```\s*$')
if ($Fences.Count -ne 6) { throw 'transport fence count mismatch' }
$Code = $Fences[0].Groups[1].Value
$Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Code)
$Sha = [BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()
$ReviewDir = Join-Path 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\tmp' "task7-phase-b-contract-review-$EvidenceHead"
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
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$EvidenceHead=$HeadMatch[0].Groups[1].Value
$Transport = Join-Path $Sdd "task-7-phase-b-transport-execution-$EvidenceHead.md"
$Text = (New-Object Text.UTF8Encoding($false, $true)).GetString([IO.File]::ReadAllBytes($Transport))
$Fences = [regex]::Matches($Text, '(?ms)^```powershell\n(.*?)^```\s*$')
if ($Fences.Count -ne 6) { throw 'transport fence count mismatch' }
$Code = $Fences[0].Groups[1].Value
$Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Code)
$Algorithm = [Security.Cryptography.SHA256]::Create()
try { $Sha = [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant() } finally { $Algorithm.Dispose() }
$Path = Join-Path (Join-Path 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\tmp' "task7-phase-b-contract-review-$EvidenceHead") "transport-fence-1-$Sha.ps1"
if (-not (Test-Path -LiteralPath $Path -PathType Leaf) -or (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Sha) { throw 'materializer review file mismatch' }
$Output = @(& $Path)
if (-not $?) { throw 'second derived materializer invocation failed' }
$Json = $Output -join "`n" | ConvertFrom-Json
if ($Json.fence_count -ne 5 -or @($Json.files | Where-Object { $_.disposition -cne 'existing-exact' }).Count -ne 0) { throw 'second materializer was not fully existing-exact' }
```

In a third fresh `shell_command`, materialize transport fences 2–6 as immutable content-addressed files, then invoke only harmless fence 2:

```powershell
$ErrorActionPreference = 'Stop'
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$EvidenceHead=$HeadMatch[0].Groups[1].Value
$Transport = Join-Path $Sdd "task-7-phase-b-transport-execution-$EvidenceHead.md"
$Text = (New-Object Text.UTF8Encoding($false, $true)).GetString([IO.File]::ReadAllBytes($Transport))
$Fences = [regex]::Matches($Text, '(?ms)^```powershell\n(.*?)^```\s*$')
if ($Fences.Count -ne 6) { throw 'transport fence count mismatch' }
$ReviewDir = Join-Path 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\tmp' "task7-phase-b-contract-review-$EvidenceHead"
[void][IO.Directory]::CreateDirectory($ReviewDir)
$Paths = @{}
for ($Ordinal = 2; $Ordinal -le 6; $Ordinal++) {
  $Code = $Fences[$Ordinal - 1].Groups[1].Value
  $Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Code)
  $Algorithm = [Security.Cryptography.SHA256]::Create()
  try { $Sha = [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant() } finally { $Algorithm.Dispose() }
  $Path = Join-Path $ReviewDir "transport-fence-$Ordinal-$Sha.ps1"
  if (-not (Test-Path -LiteralPath $Path)) {
    $Stream = [IO.File]::Open($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $Stream.Write($Bytes,0,$Bytes.Length); $Stream.Flush($true) } finally { $Stream.Dispose() }
  }
  if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Sha) { throw "transport review file $Ordinal mismatch" }
  $Paths[$Ordinal] = $Path
}
$Output = @(& $Paths[2])
if (-not $? -or $Output.Count -ne 1) { throw 'harmless derived self-test failed' }
$Result = $Output[0] | ConvertFrom-Json
if ($Result.output -cne 'SELF-TEST PASS: 19 cases' -or $Result.fence -ne 5) { throw 'harmless self-test result mismatch' }
```

Transport ordinals 3–6 are materialized and AST-reviewed but not invoked here. Addendum ordinals 1–4 are not invoked.

- [ ] **Step 5 (2–5 min): Prove mechanical scope and absence of stale production identity**

```powershell
$ErrorActionPreference = 'Stop'
$Sdd = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$EvidenceHead=$HeadMatch[0].Groups[1].Value
$Addendum = Join-Path $Sdd "task-7-phase-b-policy-correction-$EvidenceHead.md"
$Transport = Join-Path $Sdd "task-7-phase-b-transport-execution-$EvidenceHead.md"
$A = [IO.File]::ReadAllText($Addendum,[Text.UTF8Encoding]::new($false,$true))
$T = [IO.File]::ReadAllText($Transport,[Text.UTF8Encoding]::new($false,$true))
if ($A.Contains('2eb90e3f99219e28390570d13bd906cfe6e17012')) { throw 'old head remains in derived addendum' }
if ([regex]::Matches($A,[regex]::Escape("`$Root = 'D:\workspace\pyscf\.agents\active\precision-ci'")).Count -ne 0) { throw 'old state root assignment remains' }
$ExpectedRoot = "`$Root = 'D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$EvidenceHead'"
if ([regex]::Matches($A,[regex]::Escape($ExpectedRoot)).Count -ne 4) { throw 'new state namespace count mismatch' }
if ($T.Contains('task-7-phase-b-policy-correction.md') -or $T.Contains('task7-phase-b-transport\task7-')) { throw 'transport still points at old namespace' }
if ([regex]::Matches($A,'(?m)^\$Head = ''[0-9a-f]{40}''$').Count -ne 5) { throw 'head binding cardinality mismatch' }
```

- [ ] **Step 6 (2–5 min): Require independent execution-contract and transport review**

Give independent reviewers: immutable input hashes, helper source, exact replacement counts (`old head=10`, root assignment=`4`, authenticated-head/witness gate tail=`4`, prohibited local-head recalculation=`4`, retained exact remote-head equality check=`4`, addendum filename=`7`, addendum SHA=`7`, transport namespace=`6`, each old fence hash=`4`), derived document hashes, five addendum fence hashes, six transport fence hashes, AST results, two materializer results, and the harmless `19 cases` output. Require explicit `Execution Contract: APPROVED` and `Transport Contract: APPROVED`. Review must confirm that all four production blocks require both active-document `ExpectedEvidenceHead` and `EvidenceHead` literals to equal `$Head`; every dispatch preflight requires remote branch equality without reassigning `$Head`; all four blocks require `production_unix_wrapper_witness_verdict: PASS`; initial candidate uniqueness applies only before a binding exists; frozen pairs use exact bound run IDs plus the two-ID allowlist; no third exact-head run is admitted; old state is immutable; and production ordinals were not executed.

After approval, run this complete fresh shell. It derives `EvidenceHead` only from the frozen active-document literal, reruns the helper, checks every required output, and renders five addendum plus six transport hash lines:

```powershell
$ErrorActionPreference='Stop'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$EvidenceHead=$HeadMatch[0].Groups[1].Value
$RebindOutput=@(conda run --no-capture-output -n pyscf-win313-test python "$Design\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production\rebind-task7-phase-b.py" $EvidenceHead);if($LASTEXITCODE-ne0){throw 'approved helper rerun failed'};$Rebind=ConvertFrom-StringData($RebindOutput-join"`n")
foreach($Key in @('evidence_head','state_root','addendum_path','addendum_sha256','addendum_disposition','transport_path','transport_sha256','transport_disposition')){if(-not$Rebind.ContainsKey($Key)){throw "missing rebind output $Key"}}
if($Rebind.evidence_head-cne$EvidenceHead){throw 'approved rebind EvidenceHead mismatch'}
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
foreach($Line in $ContractLines|Where-Object{$_-match'_sha256:'}){if($Line-notmatch'`[0-9a-f]{64}`$'){throw "rendered hash line invalid: $Line"}}
$ContractLines
```

Require every rendered hash value to match `^[0-9a-f]{64}$`, then use `apply_patch` to add the rendered lines byte-for-byte to the active document. Require each key exactly once before Task 4.

---

### Task 4: Prove the real Unix wrapper with a macOS one-repeat witness

**Files:**
- Create ignored state: `D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$EvidenceHead\`
- Create immutable archive: `D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-production-unix-wrapper-witness-macos-py312\`
- Update ignored active/report documents only after strict validation

**Interfaces:**
- Consumes: Task 2's authenticated active-document `EvidenceHead`, frozen validator SHA-256 `d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c`, and the UHF singleton selection.
- Produces: one immutable macOS latch/binding, one exact heartbeat handoff/terminal identity, exact run/artifact archive, strict source-tree/native-16 `PASS`, and unique active key `production_unix_wrapper_witness_verdict: PASS`; it produces no scientific-stability claim.

- [ ] **Step 1 (2–5 min): Dispatch or recover exactly one macOS witness**

Run this complete fresh-shell command. Existing latch without binding is recovery-only; existing binding is verified and returned; no existing state is overwritten:

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'psiQAQ/pyscf'; $Workflow = 'ci-precision-check.yml'
$WorkflowName = 'Precision investigation'; $Branch = 'codex/test/sgx-extra-cycle-convergence-validation'
$Worktree = 'D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration'
$ActiveDoc = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Nodeids = '.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt'
Set-Location -LiteralPath $Worktree
$Active = [IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$Head=$HeadMatch[0].Groups[1].Value
$LocalHead=(git -C $Worktree rev-parse HEAD).Trim();if($LASTEXITCODE-ne0-or$LocalHead-cne$Head){throw 'local checkout differs from EvidenceHead'}
$Remote = @(git ls-remote https://github.com/psiQAQ/pyscf.git "refs/heads/$Branch"); if ($LASTEXITCODE -ne 0 -or $Remote.Count -ne 1 -or ($Remote[0] -split "`t")[0] -cne $Head) { throw 'remote head mismatch' }
foreach($Key in @('production_unix_exit_evidence_expected_head','production_validation_head','production_unix_exit_evidence_head')){if([regex]::Matches($Active,"(?m)^- $Key`: ``$Head``$").Count-ne1){throw "active EvidenceHead gate mismatch: $Key"}}
$Root = "D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$Head"
[void][IO.Directory]::CreateDirectory($Root)
$LatchPath = Join-Path $Root 'macos-latch.json'; $BindingPath = Join-Path $Root 'macos-binding.json'
$Utf8 = [Text.UTF8Encoding]::new($false,$true)
function Read-Json([string]$Path) { return ($Utf8.GetString([IO.File]::ReadAllBytes($Path)) | ConvertFrom-Json) }
function Write-New([string]$Path,[object]$Value) { $B=$Utf8.GetBytes(($Value|ConvertTo-Json -Depth 6 -Compress)+"`n");$S=[IO.File]::Open($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($B,0,$B.Length);$S.Flush($true)}finally{$S.Dispose()} }
$RowsRaw = @(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 100 --json databaseId,headSha,headBranch,event,workflowName,status,url); if ($LASTEXITCODE -ne 0) { throw 'witness baseline query failed' }
$Rows = @((ConvertFrom-Json ($RowsRaw -join "`n")))
if (Test-Path -LiteralPath $BindingPath -PathType Leaf) {
  $Latch=Read-Json $LatchPath; $Binding=Read-Json $BindingPath
  $LatchSha=(Get-FileHash $LatchPath -Algorithm SHA256).Hash.ToLowerInvariant();if($Latch.purpose-cne'unix-wrapper-macos-witness'-or$Latch.repo-cne$Repo-or$Latch.workflow-cne$Workflow-or$Latch.workflow_name-cne$WorkflowName-or$Latch.branch-cne$Branch-or$Latch.head-cne$Head-or$Latch.before_max-lt0-or$Latch.nodeids_file-cne$Nodeids-or$Latch.platform-cne'macos-latest'-or$Latch.python-cne'3.12'-or$Latch.profile-cne'4/4'-or$Latch.repeats-ne1-or$Latch.artifact-cne'precision-macOS-py3.12'-or$Binding.purpose-cne$Latch.purpose-or$Binding.repo-cne$Repo-or$Binding.workflow-cne$Workflow-or$Binding.workflow_name-cne$WorkflowName-or$Binding.branch-cne$Branch-or$Binding.head-cne$Head-or$Binding.run_id-le$Latch.before_max-or$Binding.before_max-ne$Latch.before_max-or$Binding.nodeids_file-cne$Nodeids-or$Binding.platform-cne'macos-latest'-or$Binding.python-cne'3.12'-or$Binding.profile-cne'4/4'-or$Binding.repeats-ne1-or$Binding.artifact-cne'precision-macOS-py3.12'-or$Binding.latch_path-cne$LatchPath-or$Binding.latch_sha256-cne$LatchSha){throw 'existing witness chain mismatch'}
  [pscustomobject]@{run_id=[long]$Binding.run_id; disposition='existing-bound'}|ConvertTo-Json -Compress; exit 0
}
if (Test-Path -LiteralPath $LatchPath) { $Latch=Read-Json $LatchPath }
else {
  $ActiveRows=@($Rows|Where-Object{$_.headSha -ceq $Head -and $_.status -in @('requested','queued','in_progress','waiting','pending')});if($ActiveRows.Count-ne0){throw 'unknown exact-head run active'}
  $Before=0L;if($Rows.Count){$Before=[long](($Rows|Measure-Object databaseId -Maximum).Maximum)}
  $Latch=[ordered]@{purpose='unix-wrapper-macos-witness';repo=$Repo;workflow=$Workflow;workflow_name=$WorkflowName;branch=$Branch;head=$Head;before_max=$Before;nodeids_file=$Nodeids;repeats=1;platform='macos-latest';python='3.12';profile='4/4';artifact='precision-macOS-py3.12'}
  Write-New $LatchPath $Latch
  gh workflow run $Workflow --repo $Repo --ref $Branch -f nodeids_file=$Nodeids -f repeats=1 -f platform=macos-latest -f python_version=3.12 -f profile=4/4
  if($LASTEXITCODE-ne0){throw 'macOS witness dispatch failed'}
}
if($Latch.purpose-cne'unix-wrapper-macos-witness'-or$Latch.repo-cne$Repo-or$Latch.workflow-cne$Workflow-or$Latch.workflow_name-cne$WorkflowName-or$Latch.branch-cne$Branch-or$Latch.head-cne$Head-or$Latch.before_max-lt0-or$Latch.nodeids_file-cne$Nodeids-or$Latch.platform-cne'macos-latest'-or$Latch.python-cne'3.12'-or$Latch.profile-cne'4/4'-or$Latch.repeats-ne1-or$Latch.artifact-cne'precision-macOS-py3.12'){throw 'witness latch readback mismatch'}
$Candidate=$null
for($Attempt=1;$Attempt-le12;$Attempt++){
  $Raw=@(gh run list --repo $Repo --workflow $Workflow --branch $Branch --event workflow_dispatch --limit 100 --json databaseId,headSha,headBranch,event,workflowName,status,url);if($LASTEXITCODE-ne0){throw 'witness binding query failed'}
  $Candidates=@((ConvertFrom-Json($Raw-join"`n"))|Where-Object{[long]$_.databaseId-gt[long]$Latch.before_max-and$_.headSha-ceq$Head-and$_.headBranch-ceq$Branch-and$_.event-ceq'workflow_dispatch'-and$_.workflowName-ceq$WorkflowName})
  if($Candidates.Count-gt1){throw 'ambiguous witness candidates'};if($Candidates.Count-eq1){$Candidate=$Candidates[0];break};Start-Sleep -Seconds 5
}
if($null-eq$Candidate){throw 'witness dispatch not bound; recover latch without redispatch'}
$Binding=[ordered]@{purpose=$Latch.purpose;repo=$Repo;workflow=$Workflow;workflow_name=$WorkflowName;branch=$Branch;head=$Head;run_id=[long]$Candidate.databaseId;before_max=[long]$Latch.before_max;nodeids_file=$Nodeids;repeats=1;platform='macos-latest';python='3.12';profile='4/4';artifact='precision-macOS-py3.12';url=[string]$Candidate.url;latch_path=$LatchPath;latch_sha256=(Get-FileHash $LatchPath -Algorithm SHA256).Hash.ToLowerInvariant()}
Write-New $BindingPath $Binding
$BindingRead=Read-Json $BindingPath;if(($BindingRead|ConvertTo-Json -Depth 6 -Compress)-cne($Binding|ConvertTo-Json -Depth 6 -Compress)){throw 'witness binding atomic readback mismatch'}
[pscustomobject]@{run_id=[long]$BindingRead.run_id;disposition='created-bound'}|ConvertTo-Json -Compress
```

- [ ] **Step 2 (2–5 min): Launch the witness-only heartbeat and freeze exact identity**

```powershell
$ErrorActionPreference='Stop'
$Repo='psiQAQ/pyscf';$Branch='codex/test/sgx-extra-cycle-convergence-validation';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Heartbeat='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';$HeartbeatSha='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639';$PowerShellExe='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe';$GoalThread='019f64bd-77a5-7573-88e9-fd80b1882e70';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'frozen EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value
$Remote=@(git ls-remote https://github.com/psiQAQ/pyscf.git "refs/heads/$Branch");if($LASTEXITCODE-ne0-or$Remote.Count-ne1-or($Remote[0]-split"`t")[0]-cne$Head){throw 'remote no longer equals EvidenceHead; no heartbeat launch'}
if((Get-FileHash $Heartbeat -Algorithm SHA256).Hash.ToLowerInvariant()-cne$HeartbeatSha){throw 'heartbeat hash mismatch'};$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$Head";$BindingPath=Join-Path $Root 'macos-binding.json';$HandoffPath=Join-Path $Root 'macos-heartbeat-handoff.json';if(Test-Path $HandoffPath){throw 'witness heartbeat handoff already exists'}
$Binding=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($BindingPath))|ConvertFrom-Json);$RunId=[long]$Binding.run_id;if($Binding.head-cne$Head-or$Binding.platform-cne'macos-latest'-or$Binding.repeats-ne1){throw 'witness binding mismatch'}
$RunRaw=@(gh run view $RunId --repo $Repo --json databaseId,attempt,event,workflowName,headSha,headBranch,status);if($LASTEXITCODE-ne0){throw 'witness launch identity query failed'};$Run=ConvertFrom-Json($RunRaw-join"`n");if($Run.databaseId-ne$RunId-or$Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.workflowName-cne'Precision investigation'-or$Run.headSha-cne$Head-or$Run.headBranch-cne$Branch){throw 'witness run head/identity mismatch; preserve and STOP without replay'}
$Leaf=[IO.Path]::GetFileName($Heartbeat);$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{$_.CommandLine-and([string]$_.CommandLine).IndexOf($Leaf,[StringComparison]::OrdinalIgnoreCase)-ge0});if($Pollers.Count-ne0){throw 'another heartbeat process exists'};$Schedulers=@(Get-ScheduledTask -ErrorAction Stop|Where-Object{$_.State-cne'Disabled'}|Where-Object{$n="$($_.TaskPath)$($_.TaskName)";$a=($_.Actions|ForEach-Object{"$($_.Execute) $($_.Arguments)"})-join' ';$n-match'(?i)heartbeat|precision-ci'-or$a.IndexOf($Leaf,[StringComparison]::OrdinalIgnoreCase)-ge0});if($Schedulers.Count-ne0){throw 'native heartbeat scheduler exists'}
$Command="& '$Heartbeat' -TargetRunIds @('$RunId') -TargetHeadSha '$Head' -IntervalSeconds 1800 -WakeAfterMinutes 300";$Encoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command));$Monitor=$null;$Owned=$false;$Stream=$null
try{$Monitor=Start-Process -FilePath $PowerShellExe -WindowStyle Hidden -PassThru -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-EncodedCommand',$Encoded);$Pid=[int]$Monitor.Id;$Monitor.Refresh();$StartUtc=$Monitor.StartTime.ToUniversalTime().ToString('o');$Rows=@(Get-CimInstance Win32_Process -Filter "ProcessId=$Pid" -ErrorAction Stop);if($Monitor.HasExited-or$Rows.Count-ne1-or$Rows[0].ExecutablePath-cne$PowerShellExe-or$Rows[0].CommandLine-notmatch([regex]::Escape($Encoded))){throw 'witness direct-child identity mismatch'}
  $GoalRaw=@(& $PowerShellExe -NoProfile -ExecutionPolicy Bypass -File $Heartbeat -SetGoalStatus paused);if($LASTEXITCODE-ne0){throw 'Goal paused reconciliation failed'};$Goal=ConvertFrom-Json($GoalRaw-join"`n");if($Goal.threadId-cne$GoalThread-or$Goal.status-cne'paused'){throw 'Goal paused readback mismatch'}
  $A=[Security.Cryptography.SHA256]::Create();try{$EncodedSha=[BitConverter]::ToString($A.ComputeHash([Text.UTF8Encoding]::new($false).GetBytes($Encoded))).Replace('-','').ToLowerInvariant()}finally{$A.Dispose()};$Payload=[ordered]@{purpose='unix-wrapper-witness-heartbeat-handoff';head=$Head;run_id=$RunId;monitor_pid=$Pid;monitor_start_utc=$StartUtc;monitor_executable=$PowerShellExe;encoded_command_sha256=$EncodedSha;encoded_command=$Encoded;heartbeat_path=$Heartbeat;heartbeat_sha256=$HeartbeatSha;interval_seconds=1800;wake_after_minutes=300;goal_thread_id=$GoalThread;goal_status='paused'};$Bytes=[Text.UTF8Encoding]::new($false).GetBytes(($Payload|ConvertTo-Json -Depth 5 -Compress)+"`n");$Stream=[IO.File]::Open($HandoffPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);$Owned=$true;$Stream.Write($Bytes,0,$Bytes.Length);$Stream.Flush($true);$Stream.Dispose();$Stream=$null;$Read=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($HandoffPath))|ConvertFrom-Json);if($Read.monitor_pid-ne$Pid-or$Read.monitor_start_utc-cne$StartUtc-or$Read.head-cne$Head-or$Read.run_id-ne$RunId-or$Read.goal_status-cne'paused'-or$Read.encoded_command_sha256-cne$EncodedSha){throw 'witness handoff readback mismatch'};[pscustomobject]@{pid=$Pid;start_utc=$StartUtc;run_id=$RunId;goal='paused';handoff=$HandoffPath}|ConvertTo-Json -Compress
}catch{$Failures=@("launch: $($_.Exception.Message)");if($null-ne$Stream){try{$Stream.Dispose()}catch{$Failures+="stream: $($_.Exception.Message)"}};if($Owned-and(Test-Path $HandoffPath)){try{[IO.File]::Delete($HandoffPath)}catch{$Failures+="handoff: $($_.Exception.Message)"}};if($null-ne$Monitor){try{$Monitor.Refresh();if(-not$Monitor.HasExited){Stop-Process -Id $Monitor.Id -Force -ErrorAction Stop};if(-not$Monitor.WaitForExit(30000)){throw 'wait timeout'};$Monitor.Refresh();if(-not$Monitor.HasExited-or@(Get-CimInstance Win32_Process -Filter "ProcessId=$($Monitor.Id)" -ErrorAction Stop).Count-ne0){throw 'direct child remains'}}catch{$Failures+="cleanup: $($_.Exception.Message)"}};try{$G=@(& $PowerShellExe -NoProfile -ExecutionPolicy Bypass -File $Heartbeat -SetGoalStatus active);if($LASTEXITCODE-ne0){throw 'Goal active native failure'};$GO=ConvertFrom-Json($G-join"`n");if($GO.threadId-cne$GoalThread-or$GO.status-cne'active'){throw 'Goal active mismatch'}}catch{$Failures+="goal: $($_.Exception.Message)"};throw ($Failures-join'; ')}finally{if($null-ne$Monitor){$Monitor.Dispose()}}
```

- [ ] **Step 3 (2–5 min): Reconcile terminal child-gone and Goal active**

After the witness heartbeat reports completion, use the approved Goal bridge to require exact `active` and record exactly one active-document line `- production_unix_wrapper_witness_terminal_goal: active` with `apply_patch`. Then run this fresh-shell identity gate:

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Heartbeat='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$HandoffPath="D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$Head\macos-heartbeat-handoff.json";$Handoff=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($HandoffPath))|ConvertFrom-Json)
if($Handoff.head-cne$Head-or$Handoff.monitor_pid-lt1-or$Handoff.monitor_executable-cne'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'-or[datetime]$Handoff.monitor_start_utc-eq[datetime]::MinValue){throw 'witness handoff identity mismatch'};$A=[Security.Cryptography.SHA256]::Create();try{$ES=[BitConverter]::ToString($A.ComputeHash([Text.UTF8Encoding]::new($false).GetBytes([string]$Handoff.encoded_command))).Replace('-','').ToLowerInvariant()}finally{$A.Dispose()};if($ES-cne$Handoff.encoded_command_sha256){throw 'witness command hash mismatch'};$Process=Get-Process -Id ([int]$Handoff.monitor_pid) -ErrorAction SilentlyContinue;if($null-ne$Process){$Process.Refresh();if(-not$Process.HasExited){throw 'witness heartbeat still running'}};$Cim=@(Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$Handoff.monitor_pid)" -ErrorAction Stop);if($Cim.Count-ne0){throw 'witness heartbeat CIM row remains'}
if([regex]::Matches($Active,'(?m)^- production_unix_wrapper_witness_terminal_goal: active$').Count-ne1){throw 'independent Goal active readback missing'};[pscustomobject]@{pid=[int]$Handoff.monitor_pid;has_exited=$true;cim_count=0;goal='active';head=$Head}|ConvertTo-Json -Compress
```

- [ ] **Step 4 (2–5 min): Archive and strictly validate the witness**

```powershell
$ErrorActionPreference='Stop';$Repo='psiQAQ/pyscf';$Branch='codex/test/sgx-extra-cycle-convergence-validation';$Worktree='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Worktree
$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value
$BindingPath="D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$Head\macos-binding.json";$Binding=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($BindingPath))|ConvertFrom-Json);$RunId=[long]$Binding.run_id
$RunRaw=@(gh run view $RunId --repo $Repo --json databaseId,attempt,event,workflowName,headSha,headBranch,status,conclusion,jobs,url);if($LASTEXITCODE-ne0){throw 'witness run view failed'};$Run=ConvertFrom-Json($RunRaw-join"`n")
$ArtRaw=@(gh api "repos/$Repo/actions/runs/$RunId/artifacts?per_page=100");if($LASTEXITCODE-ne0){throw 'witness artifact query failed'};$Arts=@((ConvertFrom-Json($ArtRaw-join"`n")).artifacts);$Jobs=@($Run.jobs|Where-Object{$_.name-ceq'precision'})
if($Run.databaseId-ne$RunId-or$Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.workflowName-cne'Precision investigation'-or$Run.headSha-cne$Head-or$Run.headBranch-cne$Branch-or$Run.status-cne'completed'-or$Run.conclusion-cne'success'-or$Jobs.Count-ne1-or$Jobs[0].conclusion-cne'success'){throw 'witness terminal identity mismatch'}
$ExactArts=@($Arts|Where-Object{$_.name-ceq'precision-macOS-py3.12'-and-not$_.expired});if($ExactArts.Count-ne1-or$Arts.Count-ne1){throw 'witness artifact cardinality mismatch'};$Artifact=$ExactArts[0]
$Archive="D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-production-unix-wrapper-witness-macos-py312";if(Test-Path -LiteralPath $Archive){throw 'witness archive already exists'};[void][IO.Directory]::CreateDirectory($Archive)
gh run download $RunId --repo $Repo --name 'precision-macOS-py3.12' --dir $Archive;if($LASTEXITCODE-ne0){throw 'witness download failed'}
$Utf8=[Text.UTF8Encoding]::new($false);$RunObject=[ordered]@{databaseId=$RunId;attempt=1;event='workflow_dispatch';workflowName='Precision investigation';headSha=$Head;headBranch=$Branch;status='completed';conclusion='success';jobs=@([ordered]@{databaseId=[long]$Jobs[0].databaseId;name='precision';status='completed';conclusion='success'});artifacts=@([ordered]@{id=[long]$Artifact.id;name=[string]$Artifact.name;digest=[string]$Artifact.digest;sizeInBytes=[long]$Artifact.size_in_bytes;expired=[bool]$Artifact.expired})}
$RunBytes=$Utf8.GetBytes(($RunObject|ConvertTo-Json -Depth 6 -Compress)+"`n");$S=[IO.File]::Open((Join-Path $Archive 'run.json'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($RunBytes,0,$RunBytes.Length);$S.Flush($true)}finally{$S.Dispose()}
$RunRead=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Archive 'run.json')))|ConvertFrom-Json);if(($RunRead|ConvertTo-Json -Depth 6 -Compress)-cne($RunObject|ConvertTo-Json -Depth 6 -Compress)){throw 'witness run.json exact readback mismatch'}
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py';if((Get-FileHash $Validator -Algorithm SHA256).Hash.ToLowerInvariant()-cne'd9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c'){throw 'validator hash mismatch'}
$VBytes=[IO.File]::ReadAllBytes($Validator);$VPath=Join-Path $Archive 'validate_precision_production.py';$VS=[IO.File]::Open($VPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$VS.Write($VBytes,0,$VBytes.Length);$VS.Flush($true)}finally{$VS.Dispose()}
$Exit=[IO.File]::ReadAllBytes((Join-Path $Archive 'runner-exit-code.txt'));if(-not[Linq.Enumerable]::SequenceEqual([byte[]]$Exit,[byte[]]@(0x30,0x0A))){throw 'witness runner exit bytes mismatch'}
$Report=Join-Path $Archive 'production-validation.json';if(Test-Path $Report){throw 'witness report path already exists'};conda run --no-capture-output -n pyscf-win313-test python $VPath $Archive --mode source-tree --expected-sha $Head --expected-nodeids-file (Join-Path $Worktree '.github\workflows\precision-uhf-smearing-extra-cycle-nodeids.txt') --expected-profile omp4-blas4 --expected-repeats 1 --expected-platform macos-latest --expected-python 3.12 --expected-native-count 16 --run-metadata (Join-Path $Archive 'run.json') --expected-run-id $RunId --expected-branch $Branch --expected-artifact-name 'precision-macOS-py3.12' --report $Report
if($LASTEXITCODE-ne0){throw 'witness strict validator failed'};$Verdict=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($Report))|ConvertFrom-Json);if($Verdict.valid-ne$true-or$Verdict.verdict-cne'PASS'-or$Verdict.tested_sha-cne$Head-or$Verdict.records-ne1-or$Verdict.pass-ne1-or$Verdict.fail-ne0-or$Verdict.profile-cne'omp4-blas4'){throw 'witness report is not strict same-EvidenceHead 1/1 PASS'}
[pscustomobject]@{active_line='- production_unix_wrapper_witness_verdict: PASS';run_id=$RunId;artifact_id=[long]$Artifact.id;archive=$Archive;report_sha256=(Get-FileHash $Report -Algorithm SHA256).Hash.ToLowerInvariant();claim='Unix wrapper transport witness only; not scientific stability'}|ConvertTo-Json -Compress
```

- [ ] **Step 5 (2–5 min): Freeze the witness PASS gate**

Use `apply_patch` to add the command's exact run/artifact/archive/report values, exact `tested_sha`, the literal line `- production_unix_wrapper_witness_verdict: PASS`, and the literal claim line printed by the prior command. Run this complete fresh-shell readback; do not enter Task 5 unless it succeeds:

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));if([regex]::Matches($Text,'(?m)^- production_unix_wrapper_witness_verdict: PASS$').Count-ne1){throw 'witness PASS key mismatch'};if([regex]::Matches($Text,'(?m)^- production_unix_wrapper_witness_claim: `transport/provenance only; repeats 1 is not scientific stability`$').Count-ne1){throw 'witness claim key mismatch'}
'MACOS WITNESS GATE PASS'
```

---

### Task 5: Execute the reviewed four-block Windows/Linux pair

**Files:**
- Invoke hash-bound transport fences from `tmp\task7-phase-b-contract-review-$EvidenceHead\`
- Create pair state only through the reviewed addendum blocks

**Interfaces:**
- Consumes: Task 4's unique plain witness `PASS`, terminal Goal `active`, proven-gone witness heartbeat, and Task 3's reviewed transport fences 3–6.
- Produces: exact Windows/Linux bindings, top-level manifest object with `.entries`, immutable launch-ready/handoff files, and one heartbeat owning both pair IDs at `1800/300` with Goal exactly `paused`.

The reviewed blocks must retain exactly these configs: Windows then Linux; nodeids file `.github/workflows/precision-uhf-smearing-extra-cycle-nodeids.txt`; repeats `20`; Python `3.12`; profile `4/4`; platforms `windows-latest`/`ubuntu-latest`; artifacts `precision-Windows-py3.12`/`precision-Linux-py3.12`. The four fresh-shell invocations stop at the first nonzero exit and never skip or replay an ordinal.

- [ ] **Step 1 (2–5 min): Invoke transport fence 3 for pair Block 1**

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText('D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md',[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;if([regex]::Matches($Active,'(?m)^- production_unix_wrapper_witness_terminal_goal: active$').Count-ne1-or[regex]::Matches($Active,'(?m)^- production_unix_wrapper_witness_verdict: PASS$').Count-ne1){throw 'witness lifecycle not complete'};$WH=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes("D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$Head\macos-heartbeat-handoff.json"))|ConvertFrom-Json);if(@(Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$WH.monitor_pid)" -ErrorAction Stop).Count-ne0){throw 'witness heartbeat overlaps pair'};$M=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_transport_fence_3_sha256: `([0-9a-f]{64})`$');if($M.Count-ne1){throw 'transport hash gate 3'};$P=Join-Path "$Design\tmp\task7-phase-b-contract-review-$Head" "transport-fence-3-$($M[0].Groups[1].Value).ps1";if((Get-FileHash $P -Algorithm SHA256).Hash.ToLowerInvariant()-cne$M[0].Groups[1].Value){throw 'transport fence 3 mismatch'};& $P;if(-not$?){throw 'pair Block 1 failed'}
```

- [ ] **Step 2 (2–5 min): Invoke transport fence 4 for pair Block 2**

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText('D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md',[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$M=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_transport_fence_4_sha256: `([0-9a-f]{64})`$');if($M.Count-ne1){throw 'transport hash gate 4'};$P=Join-Path "$Design\tmp\task7-phase-b-contract-review-$Head" "transport-fence-4-$($M[0].Groups[1].Value).ps1";if((Get-FileHash $P -Algorithm SHA256).Hash.ToLowerInvariant()-cne$M[0].Groups[1].Value){throw 'transport fence 4 mismatch'};& $P;if(-not$?){throw 'pair Block 2 failed'}
```

- [ ] **Step 3 (2–5 min): Invoke transport fence 5 for pair Block 3**

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText('D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md',[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$M=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_transport_fence_5_sha256: `([0-9a-f]{64})`$');if($M.Count-ne1){throw 'transport hash gate 5'};$P=Join-Path "$Design\tmp\task7-phase-b-contract-review-$Head" "transport-fence-5-$($M[0].Groups[1].Value).ps1";if((Get-FileHash $P -Algorithm SHA256).Hash.ToLowerInvariant()-cne$M[0].Groups[1].Value){throw 'transport fence 5 mismatch'};& $P;if(-not$?){throw 'pair Block 3 failed'}
```

- [ ] **Step 4 (2–5 min): Invoke transport fence 6 for pair Block 4**

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText('D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md',[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$M=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_transport_fence_6_sha256: `([0-9a-f]{64})`$');if($M.Count-ne1){throw 'transport hash gate 6'};$P=Join-Path "$Design\tmp\task7-phase-b-contract-review-$Head" "transport-fence-6-$($M[0].Groups[1].Value).ps1";if((Get-FileHash $P -Algorithm SHA256).Hash.ToLowerInvariant()-cne$M[0].Groups[1].Value){throw 'transport fence 6 mismatch'};& $P;if(-not$?){throw 'pair Block 4 failed'}
```

- [ ] **Step 5 (2–5 min): Verify the object manifest and enter no-poll waiting**

```powershell
$ErrorActionPreference='Stop';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Integration;$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value
$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$Head";$Manifest=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-runs.json')))|ConvertFrom-Json);$Entries=@($Manifest.entries)
if($Manifest.purpose-cne'production-uhf-pair'-or$Manifest.head-cne$Head-or$Entries.Count-ne2-or$Entries[0].platform-cne'windows-latest'-or$Entries[1].platform-cne'ubuntu-latest'){throw 'pair manifest object/entries mismatch'}
foreach($Name in @('production-uhf-launch-ready.json','production-uhf-heartbeat-handoff.json')){if(-not(Test-Path -LiteralPath (Join-Path $Root $Name) -PathType Leaf)){throw "missing $Name"}}
$Ready=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-launch-ready.json')))|ConvertFrom-Json);$Handoff=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-heartbeat-handoff.json')))|ConvertFrom-Json);if($Ready.head-cne$Head-or$Handoff.head-cne$Head-or$Ready.windows_run_id-ne$Entries[0].run_id-or$Ready.linux_run_id-ne$Entries[1].run_id-or$Handoff.windows_run_id-ne$Entries[0].run_id-or$Handoff.linux_run_id-ne$Entries[1].run_id-or$Handoff.goal_status-cne'paused'-or$Handoff.monitor_pid-lt1){throw 'launch-ready/handoff exact identity mismatch'}
[pscustomobject]@{windows_run_id=[long]$Entries[0].run_id;linux_run_id=[long]$Entries[1].run_id;manifest_sha256=(Get-FileHash (Join-Path $Root 'production-uhf-runs.json') -Algorithm SHA256).Hash.ToLowerInvariant();launch_ready_sha256=(Get-FileHash (Join-Path $Root 'production-uhf-launch-ready.json') -Algorithm SHA256).Hash.ToLowerInvariant();handoff_sha256=(Get-FileHash (Join-Path $Root 'production-uhf-heartbeat-handoff.json') -Algorithm SHA256).Hash.ToLowerInvariant();goal_expected='paused';manual_polling='forbidden'}|ConvertTo-Json -Compress
```

Freeze these exact values with `apply_patch`, independently require Goal exactly `paused`, and make no GitHub query until the single heartbeat exits.

---

### Task 6: Archive and strictly validate the terminal Windows/Linux pair

**Files:**
- Read pair manifest `.entries`, handoff, and exact bindings
- Create two immutable archives and reports in fixed Windows-then-Linux order

**Interfaces:**
- Consumes: Task 5's exact heartbeat exit/Goal `active` gate and top-level manifest object.
- Produces: two immutable strict reports for the same new SHA: Windows installed-wheel/native-26 and Linux source-tree/native-16 with exact runner exit bytes.

- [ ] **Step 1 (2–5 min): Gate on heartbeat exit and rebind all acceptance variables**

First use the approved App Server Goal bridge to read the current task Goal; require exact `active`, then use `apply_patch` to add exactly one literal line `- production_uhf_pair_terminal_goal: active` to the active document. Run this complete fresh shell to bind the handoff identity, prove the process/CIM is gone, and recheck that independent Goal result:

```powershell
$ErrorActionPreference='Stop';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Integration
$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$Head";$Handoff=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-heartbeat-handoff.json')))|ConvertFrom-Json)
if($Handoff.head-cne$Head-or$Handoff.monitor_pid-lt1-or$Handoff.monitor_executable-cne'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'-or[datetime]$Handoff.monitor_start_utc-eq[datetime]::MinValue){throw 'handoff identity incomplete'}
$Process=Get-Process -Id ([int]$Handoff.monitor_pid) -ErrorAction SilentlyContinue;if($null-ne$Process){$Process.Refresh();if(-not$Process.HasExited){throw 'pair heartbeat still running'}}
$Cim=@(Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$Handoff.monitor_pid)" -ErrorAction Stop);if($Cim.Count-ne0){throw 'pair heartbeat CIM identity still exists'}
$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));if([regex]::Matches($Active,'(?m)^- production_uhf_pair_terminal_goal: active$').Count-ne1){throw 'independent Goal active gate missing'}
[pscustomobject]@{pid=[int]$Handoff.monitor_pid;has_exited=$true;cim_count=$Cim.Count;goal='active';head=$Head}|ConvertTo-Json -Compress
```

Then run the single fresh-shell archive/validation command in Step 2; it defines every later variable itself.

- [ ] **Step 2 (2–5 min): Run the fixed Windows-to-Linux archive loop**

```powershell
$ErrorActionPreference='Stop';$Repo='psiQAQ/pyscf';$Branch='codex/test/sgx-extra-cycle-convergence-validation';$Worktree='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';Set-Location -LiteralPath $Worktree
$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$Head"
$ManifestObject=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-runs.json')))|ConvertFrom-Json);$Entries=@($ManifestObject.entries)
if($ManifestObject.head-cne$Head-or$Entries.Count-ne2-or$Entries[0].platform-cne'windows-latest'-or$Entries[1].platform-cne'ubuntu-latest'){throw 'manifest .entries order mismatch'}
$ValidatorSource='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py';$ValidatorSha='d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c';if((Get-FileHash $ValidatorSource -Algorithm SHA256).Hash.ToLowerInvariant()-cne$ValidatorSha){throw 'validator hash mismatch'}
$Results=@();$Utf8=[Text.UTF8Encoding]::new($false)
for($Index=0;$Index-lt2;$Index++){
  $Entry=$Entries[$Index];$RunId=[long]$Entry.run_id;$IsWindows=$Index-eq0;$ExpectedPlatform=if($IsWindows){'windows-latest'}else{'ubuntu-latest'};$ExpectedArtifact=if($IsWindows){'precision-Windows-py3.12'}else{'precision-Linux-py3.12'};$Mode=if($IsWindows){'installed-wheel'}else{'source-tree'};$Native=if($IsWindows){26}else{16};$Suffix=if($IsWindows){'production-uhf-windows-py312'}else{'production-uhf-linux-py312'}
  if($Entry.platform-cne$ExpectedPlatform-or$Entry.artifact-cne$ExpectedArtifact-or$Entry.repeats-ne20-or$Entry.python-cne'3.12'-or$Entry.profile-cne'4/4'-or$Entry.head-cne$Head){throw "manifest entry mismatch index=$Index"}
  $Raw=@(gh run view $RunId --repo $Repo --json databaseId,attempt,event,workflowName,headSha,headBranch,status,conclusion,jobs,url);if($LASTEXITCODE-ne0){throw "run view failed $RunId"};$Run=ConvertFrom-Json($Raw-join"`n");$ARaw=@(gh api "repos/$Repo/actions/runs/$RunId/artifacts?per_page=100");if($LASTEXITCODE-ne0){throw "artifact query failed $RunId"};$Arts=@((ConvertFrom-Json($ARaw-join"`n")).artifacts);$Jobs=@($Run.jobs|Where-Object{$_.name-ceq'precision'});$Exact=@($Arts|Where-Object{$_.name-ceq$ExpectedArtifact-and-not$_.expired})
  if($Run.databaseId-ne$RunId-or$Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.workflowName-cne'Precision investigation'-or$Run.headSha-cne$Head-or$Run.headBranch-cne$Branch-or$Run.status-cne'completed'-or$Run.conclusion-cne'success'-or$Jobs.Count-ne1-or$Jobs[0].conclusion-cne'success'-or$Exact.Count-ne1-or$Arts.Count-ne1){throw "terminal identity mismatch $RunId"};$Artifact=$Exact[0]
  $Archive="D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-$Suffix";if(Test-Path -LiteralPath $Archive){throw "archive exists $Archive"};[void][IO.Directory]::CreateDirectory($Archive);gh run download $RunId --repo $Repo --name $ExpectedArtifact --dir $Archive;if($LASTEXITCODE-ne0){throw "download failed $RunId"}
  $RunObject=[ordered]@{databaseId=$RunId;attempt=1;event='workflow_dispatch';workflowName='Precision investigation';headSha=$Head;headBranch=$Branch;status='completed';conclusion='success';jobs=@([ordered]@{databaseId=[long]$Jobs[0].databaseId;name='precision';status='completed';conclusion='success'});artifacts=@([ordered]@{id=[long]$Artifact.id;name=[string]$Artifact.name;digest=[string]$Artifact.digest;sizeInBytes=[long]$Artifact.size_in_bytes;expired=[bool]$Artifact.expired})};$RB=$Utf8.GetBytes(($RunObject|ConvertTo-Json -Depth 6 -Compress)+"`n");$RunPath=Join-Path $Archive 'run.json';$RS=[IO.File]::Open($RunPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$RS.Write($RB,0,$RB.Length);$RS.Flush($true)}finally{$RS.Dispose()};$RunRead=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($RunPath))|ConvertFrom-Json);if(($RunRead|ConvertTo-Json -Depth 6 -Compress)-cne($RunObject|ConvertTo-Json -Depth 6 -Compress)){throw "run.json exact readback mismatch $RunId"}
  $VB=[IO.File]::ReadAllBytes($ValidatorSource);$VP=Join-Path $Archive 'validate_precision_production.py';$VS=[IO.File]::Open($VP,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$VS.Write($VB,0,$VB.Length);$VS.Flush($true)}finally{$VS.Dispose()};if((Get-FileHash $VP -Algorithm SHA256).Hash.ToLowerInvariant()-cne$ValidatorSha){throw 'archive validator mismatch'}
  if(-not$IsWindows){$EB=[IO.File]::ReadAllBytes((Join-Path $Archive 'runner-exit-code.txt'));if(-not[Linq.Enumerable]::SequenceEqual([byte[]]$EB,[byte[]]@(0x30,0x0A))){throw 'Linux runner exit bytes mismatch'}}
  $Report=Join-Path $Archive 'production-validation.json';if(Test-Path $Report){throw "report exists $RunId"};conda run --no-capture-output -n pyscf-win313-test python $VP $Archive --mode $Mode --expected-sha $Head --expected-nodeids-file (Join-Path $Worktree '.github\workflows\precision-uhf-smearing-extra-cycle-nodeids.txt') --expected-profile omp4-blas4 --expected-repeats 20 --expected-platform $ExpectedPlatform --expected-python 3.12 --expected-native-count $Native --run-metadata (Join-Path $Archive 'run.json') --expected-run-id $RunId --expected-branch $Branch --expected-artifact-name $ExpectedArtifact --report $Report;if($LASTEXITCODE-ne0){throw "validator failed $RunId"};$V=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($Report))|ConvertFrom-Json);if($V.valid-ne$true-or$V.verdict-cne'PASS'-or$V.tested_sha-cne$Head-or$V.records-ne20-or$V.pass-ne20-or$V.fail-ne0-or$V.profile-cne'omp4-blas4'){throw "report not same-EvidenceHead 20/20 PASS $RunId"}
  $Results+=[pscustomobject]@{platform=$ExpectedPlatform;run_id=$RunId;artifact_id=[long]$Artifact.id;archive=$Archive;report_sha256=(Get-FileHash $Report -Algorithm SHA256).Hash.ToLowerInvariant();tested_sha=[string]$V.tested_sha;valid=$true;verdict='PASS';native_count=$Native}
}
if($Results.Count-ne2-or$Results[0].platform-cne'windows-latest'-or$Results[1].platform-cne'ubuntu-latest'){throw 'fixed archive loop result mismatch'};$Results|ConvertTo-Json -Depth 4
```

- [ ] **Step 3 (2–5 min): Freeze the exact two-report conjunction**

Use `apply_patch` to record both loop results, validator SHA, exact Linux exit-file SHA, and `- production_unix_exit_evidence_terminal_status: `PASS``. Any command failure preserves the archive and records `STOP`; it does not replay a dispatch or unlock Task 7. Run this complete fresh-shell readback:

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));if([regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_terminal_status: `PASS`$').Count-ne1){throw 'two-report terminal PASS key mismatch'}
'WINDOWS LINUX PAIR STRICT PASS'
```

---

### Task 7: Record the parent Task 7 Step 3 recovery entry

**Files:**
- Update ignored active and Task 7 report documents
- Do not modify tracked source or `pyscf/pyscf#3312`

**Interfaces:**
- Consumes: macOS witness `PASS` plus the exact Windows/Linux two-report `PASS` conjunction.
- Produces: one narrow, read-back-verified recovery key for parent Task 7 Step 3; it performs no review, Task 8 action, or issue update.

- [ ] **Step 1 (2–5 min): Record exact terminal evidence**

Use `apply_patch` to append the three new run/artifact/archive/report identities without altering the historical Windows `PASS` or Linux `INVALID` entries.

- [ ] **Step 2 (2–5 min): Freeze and verify the recovery key**

Use `apply_patch` to set exactly one `production_unix_exit_evidence_next_step` line to `Task 7 Step 3 only; independently review the three production commits and stacked integration using the new macOS transport witness plus same-SHA Windows/Linux frozen-validator PASS reports; do not redispatch, start Task 8, or update pyscf/pyscf#3312`. Run this complete fresh-shell readback:

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'EvidenceHead cardinality mismatch'};$Head=$HeadMatch[0].Groups[1].Value
$Next='- production_unix_exit_evidence_next_step: `Task 7 Step 3 only; independently review the three production commits and stacked integration using the new macOS transport witness plus same-SHA Windows/Linux frozen-validator PASS reports; do not redispatch, start Task 8, or update pyscf/pyscf#3312`';if([regex]::Matches($Text,'(?m)^'+[regex]::Escape($Next)+'$').Count-ne1){throw 'recovery key mismatch'};if([regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_terminal_status: `PASS`$').Count-ne1){throw 'terminal PASS mismatch'}
$Tested=@([regex]::Matches($Text,'(?m)^- production_(?:unix_wrapper_witness|uhf_windows|uhf_linux)_tested_sha: `([0-9a-f]{40})`$')|ForEach-Object{$_.Groups[1].Value});if($Tested.Count-ne3-or@($Tested|Where-Object{$_-cne$Head}).Count-ne0){throw 'three tested_sha values do not equal EvidenceHead'};'TASK 7 STEP 3 RECOVERY READY'
```

## Plan Self-Review Checklist

- [ ] Every approved-spec requirement maps to Task 1 implementation proof, Task 2 authenticated publication, Task 3 mechanical derivation, Task 4 macOS witness, Task 5 pair execution, Task 6 strict pair acceptance, or Task 7 recovery.
- [ ] The plan contains one Bash implementation snippet, four behavior-test methods, one `resolve_bash`, and one mechanical rebind helper; no alternative implementation remains.
- [ ] All paths are absolute where host identity matters and repository-relative where MSYS argv conversion matters; post-push identities derive only from the authenticated 40-hex active-document `EvidenceHead`.
- [ ] Every `gh`, `git`, `conda`, and Bash native command that affects a gate has an immediate exit check.
- [ ] The derived addendum has exactly five PowerShell fences and the derived transport has exactly six; every fence has Windows PowerShell 5.1 AST errors `0` before approval.
- [ ] Task 3 runs only materialization and the harmless 19-case fence; Task 4 owns the non-overlapping macOS witness heartbeat; Task 5 starts the pair heartbeat only after witness child-gone/Goal `active` and invokes pair ordinals 1–4 in four fresh `shell_command` processes.
- [ ] The old addendum, transport, state, archives, runs, and artifacts remain immutable; no replay, force push, second poller, early Step 3, Task 8, or issue `#3312` update is permitted.
