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
- Tasks 1–3 must not dispatch workflows, start a heartbeat, or change Goal. Task 3 may execute only the supervisor's harmless `-SelfTest` and the harmless in-memory ordinal-5 self-test; pair production ordinals 1–4 remain unexecuted until Task 5.
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
| `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/heartbeat-direct-handle-supervisor.ps1` | Create and independently review in Task 3 | Non-polling local supervisor that retains the original heartbeat `Process` handle through terminal proof and writes durable handoff/terminal markers. |
| `.agents/active/precision-ci/task-7-phase-b-$EvidenceHead/` | Created only by Task 5 | New pair latches, bindings, manifest, launch-ready, handoff, and terminal state; no old state path is reused. |
| `.agents/active/precision-ci/task-7-unix-wrapper-witness-$EvidenceHead/` | Created only by Task 4 | Immutable macOS witness latch, binding, heartbeat handoff/terminal identity, archive, and strict verdict. |
| `.agents/archive/precision-ci/experiments/$RunId-production-uhf-$PlatformSlug-py312/` | Durable staged completion in Task 6 | Immutable identity and completion markers plus append-only `attempt-NNNN` directories; an incomplete attempt is retained and the same frozen run resumes without redispatch. |

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

Run this one fresh Windows PowerShell shell after both `apply_patch` edits. It accepts strict UTF-8 only, rejects a BOM and every lone CR, converts only well-formed CRLF pairs to LF, requires a final LF, and writes exactly the two approved paths:

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
    if raw.startswith(b'\xef\xbb\xbf'):
        raise RuntimeError(f'UTF-8 BOM is forbidden: {path}')
    text = raw.decode('utf-8', errors='strict')
    if '\r' in text.replace('\r\n', ''):
        raise RuntimeError(f'lone CR is forbidden: {path}')
    text = text.replace('\r\n', '\n')
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
git -C $Worktree commit -m 'ci: record Unix precision runner exit code [skip ci]'
if ($LASTEXITCODE -ne 0) { throw 'implementation commit failed' }
$ReviewedCommit = (git -C $Worktree rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $ReviewedCommit -notmatch '^[0-9a-f]{40}$' -or $ReviewedCommit -ceq '2eb90e3f99219e28390570d13bd906cfe6e17012') { throw 'new implementation commit invalid' }
$Parent = (git -C $Worktree rev-parse HEAD^).Trim()
if ($LASTEXITCODE -ne 0 -or $Parent -cne '2eb90e3f99219e28390570d13bd906cfe6e17012') { throw 'implementation commit parent mismatch' }
$CommitNames = @(git -C $Worktree diff-tree --no-commit-id --name-only -r $ReviewedCommit)
if ($LASTEXITCODE -ne 0 -or $CommitNames.Count -ne 2) { throw 'commit scope mismatch' }
```

- [ ] **Step 9 (2–5 min): Obtain independent SDD approval before publication**

Give the reviewer the approved spec hash, preserved Windows/MSYS RED output, Windows/MSYS GREEN/full-suite output, Bash/Python static results, deterministic encoding/EOL/mode evidence, exact two-file diff, and commit SHA. The ignored report path is `D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production\unix-exit-evidence-implementation-review.json`; it is strict UTF-8 no-BOM/LF and has exactly this top-level schema: `purpose`, `reviewed_commit`, `reviewed_parent`, `reviewed_paths`, `spec_sha256`, `spec_compliance`, `code_quality`, `native_linux_test`, `native_macos_test`, `reviewed_utc`. Require one `Spec Compliance: APPROVED` and one `Code Quality: APPROVED`, encoded as exact JSON values `APPROVED`; both native-host fields are exact `NOT_RUN`.

If review requests a change, do not stack a follow-up commit. Create a new isolated worktree from exact parent `2eb90e3f99219e28390570d13bd906cfe6e17012`, apply only the final two-file bytes with `apply_patch`, rerun Steps 4–7, create one new `[skip ci]` commit, and obtain a new complete review report bound to that exact candidate. Delete no prior worktree or commit. Task 2 accepts only a candidate whose parent is exact and whose `diff-tree` contains exactly two paths, so a multi-commit implementation range cannot be published.

---

### Task 2: Fast-forward publish the reviewed evidence commit

**Files:**
- Local ignored update: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Read ignored implementation review: `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/unix-exit-evidence-implementation-review.json`
- Read ignored plan review: `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/unix-exit-evidence-plan-review.json`
- Remote ref: `origin/codex/test/sgx-extra-cycle-convergence-validation`

**Interfaces:**
- Consumes: two strict independent review reports, Task 1's exact single implementation commit, this plan's exact reviewed commit/blob/content SHA, and old remote head `2eb90e3f99219e28390570d13bd906cfe6e17012`.
- Produces: active-document report paths/hashes and reviewed identities frozen before push, then one ordinary fast-forward readback frozen as `EvidenceHead`; it produces no dispatch, latch, Goal, or heartbeat state.

- [ ] **Step 1 (2–5 min): Authenticate both independent review reports before any active edit**

```powershell
$ErrorActionPreference = 'Stop'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';Set-Location -LiteralPath $Design
$Sdd=Join-Path $Design '.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production';$ImplReviewPath=Join-Path $Sdd 'unix-exit-evidence-implementation-review.json';$PlanReviewPath=Join-Path $Sdd 'unix-exit-evidence-plan-review.json';$PlanPath=Join-Path $Design 'docs\superpowers\plans\2026-08-12-unix-precision-runner-exit-evidence.md';$PlanRel='docs/superpowers/plans/2026-08-12-unix-precision-runner-exit-evidence.md';$SpecSha='af06fdef54ae177c139e148c083f8162155713db3439e1d01042245bcdc2b3b5';$Parent='2eb90e3f99219e28390570d13bd906cfe6e17012'
function Read-Review([string]$Path,[string[]]$Keys){$B=[IO.File]::ReadAllBytes($Path);if($B.Length-lt2-or($B.Length-ge3-and$B[0]-eq239-and$B[1]-eq187-and$B[2]-eq191)-or$B[-1]-ne10-or@($B|Where-Object{$_-eq13}).Count-ne0){throw "review encoding/EOL mismatch: $Path"};$J=([Text.UTF8Encoding]::new($false,$true).GetString($B)|ConvertFrom-Json);$Actual=@($J.PSObject.Properties.Name);if($Actual.Count-ne$Keys.Count-or@($Actual|Where-Object{$_-notin$Keys}).Count-ne0){throw "review schema mismatch: $Path"};return [pscustomobject]@{json=$J;sha=(Get-FileHash $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
$IR=Read-Review $ImplReviewPath @('purpose','reviewed_commit','reviewed_parent','reviewed_paths','spec_sha256','spec_compliance','code_quality','native_linux_test','native_macos_test','reviewed_utc');$I=$IR.json
if($I.purpose-cne'unix-exit-evidence-implementation-review'-or$I.reviewed_commit-notmatch'^[0-9a-f]{40}$'-or$I.reviewed_parent-cne$Parent-or@($I.reviewed_paths).Count-ne2-or$I.reviewed_paths[0]-cne'.github/workflows/run_unix_precision_tests.sh'-or$I.reviewed_paths[1]-cne'.github/workflows/test_precision_investigation_contract.py'-or$I.spec_sha256-cne$SpecSha-or$I.spec_compliance-cne'APPROVED'-or$I.code_quality-cne'APPROVED'-or$I.native_linux_test-cne'NOT_RUN'-or$I.native_macos_test-cne'NOT_RUN'){throw 'implementation review verdict/identity mismatch'}
$ExpectedEvidenceHead=[string]$I.reviewed_commit;$Local=(git -C $Integration rev-parse HEAD).Trim();if($LASTEXITCODE-ne0-or$Local-cne$ExpectedEvidenceHead){throw 'implementation checkout is not reviewed commit'};$ImplParent=(git -C $Integration rev-parse "$ExpectedEvidenceHead^").Trim();if($LASTEXITCODE-ne0-or$ImplParent-cne$Parent){throw 'reviewed implementation is not one exact commit over parent'};$Names=@(git -C $Integration diff-tree --no-commit-id --name-only -r $ExpectedEvidenceHead);if($LASTEXITCODE-ne0-or$Names.Count-ne2-or$Names[0]-cne'.github/workflows/run_unix_precision_tests.sh'-or$Names[1]-cne'.github/workflows/test_precision_investigation_contract.py'){throw 'reviewed implementation commit scope mismatch'};$Subject=(git -C $Integration show -s --format=%s $ExpectedEvidenceHead).Trim();if($LASTEXITCODE-ne0-or$Subject-cne'ci: record Unix precision runner exit code [skip ci]'){throw 'reviewed implementation subject mismatch'}
$PR=Read-Review $PlanReviewPath @('purpose','plan_path','plan_commit','plan_sha256','spec_sha256','spec_compliance','plan_quality','reviewed_utc');$P=$PR.json
if($P.purpose-cne'unix-exit-evidence-plan-review'-or$P.plan_path-cne$PlanRel-or$P.plan_commit-notmatch'^[0-9a-f]{40}$'-or$P.plan_sha256-notmatch'^[0-9a-f]{64}$'-or$P.spec_sha256-cne$SpecSha-or$P.spec_compliance-cne'APPROVED'-or$P.plan_quality-cne'APPROVED'){throw 'plan review verdict/identity mismatch'}
$PlanBlob=(git -C $Design rev-parse "$($P.plan_commit)`:$PlanRel").Trim();if($LASTEXITCODE-ne0-or$PlanBlob-notmatch'^[0-9a-f]{40}$'){throw 'reviewed plan commit/blob unavailable'};$LiveBlob=(git -C $Design hash-object -- $PlanPath).Trim();if($LASTEXITCODE-ne0-or$LiveBlob-cne$PlanBlob-or(Get-FileHash $PlanPath -Algorithm SHA256).Hash.ToLowerInvariant()-cne$P.plan_sha256){throw 'live plan bytes are not reviewed plan bytes'}
$Lines=@("- production_unix_exit_evidence_expected_head: ``$ExpectedEvidenceHead``","- production_unix_exit_evidence_implementation_review_path: ``$ImplReviewPath``","- production_unix_exit_evidence_implementation_review_sha256: ``$($IR.sha)``","- production_unix_exit_evidence_plan_path: ``$PlanPath``","- production_unix_exit_evidence_plan_commit: ``$($P.plan_commit)``","- production_unix_exit_evidence_plan_sha256: ``$($P.plan_sha256)``","- production_unix_exit_evidence_plan_review_path: ``$PlanReviewPath``","- production_unix_exit_evidence_plan_review_sha256: ``$($PR.sha)``")
[pscustomobject]@{expected_evidence_head=$ExpectedEvidenceHead;implementation_review_sha256=$IR.sha;plan_review_sha256=$PR.sha;lines=$Lines}|ConvertTo-Json -Depth 3
```

- [ ] **Step 2 (2–5 min): Freeze only the authenticated review output before push**

Use `apply_patch` to add the preceding command's eight printed `lines` byte-for-byte exactly once to the active document. Do not type an `APPROVED` value or derive a commit/hash manually. Then run this fresh-shell readback:

```powershell
$ErrorActionPreference='Stop'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true))
$HeadMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_expected_head: `([0-9a-f]{40})`$');$IRPathMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_implementation_review_path: `(.+)`$');$IRShaMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_implementation_review_sha256: `([0-9a-f]{64})`$');$PRPathMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_plan_review_path: `(.+)`$');$PRShaMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_plan_review_sha256: `([0-9a-f]{64})`$')
if($HeadMatch.Count-ne1-or$IRPathMatch.Count-ne1-or$IRShaMatch.Count-ne1-or$PRPathMatch.Count-ne1-or$PRShaMatch.Count-ne1){throw 'frozen review key cardinality mismatch'};if((Get-FileHash $IRPathMatch[0].Groups[1].Value -Algorithm SHA256).Hash.ToLowerInvariant()-cne$IRShaMatch[0].Groups[1].Value-or(Get-FileHash $PRPathMatch[0].Groups[1].Value -Algorithm SHA256).Hash.ToLowerInvariant()-cne$PRShaMatch[0].Groups[1].Value){throw 'frozen review hash mismatch'}
[pscustomobject]@{expected_evidence_head=$HeadMatch[0].Groups[1].Value;implementation_review_sha256=$IRShaMatch[0].Groups[1].Value;plan_review_sha256=$PRShaMatch[0].Groups[1].Value}|ConvertTo-Json -Compress
```

- [ ] **Step 3 (2–5 min): Reauthenticate the frozen implementation report and old remote head**

```powershell
$ErrorActionPreference = 'Stop'
$Worktree='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Branch='codex/test/sgx-extra-cycle-convergence-validation';$Parent='2eb90e3f99219e28390570d13bd906cfe6e17012';Set-Location -LiteralPath $Worktree
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true))
$HM=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_expected_head: `([0-9a-f]{40})`$');$RPM=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_implementation_review_path: `(.+)`$');$RSM=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_implementation_review_sha256: `([0-9a-f]{64})`$');if($HM.Count-ne1-or$RPM.Count-ne1-or$RSM.Count-ne1){throw 'frozen implementation review keys missing'};$ExpectedEvidenceHead=$HM[0].Groups[1].Value;$ReviewPath=$RPM[0].Groups[1].Value;if((Get-FileHash $ReviewPath -Algorithm SHA256).Hash.ToLowerInvariant()-cne$RSM[0].Groups[1].Value){throw 'implementation review changed after freeze'};$Review=([Text.UTF8Encoding]::new($false,$true).GetString([IO.File]::ReadAllBytes($ReviewPath))|ConvertFrom-Json);if($Review.reviewed_commit-cne$ExpectedEvidenceHead-or$Review.reviewed_parent-cne$Parent-or$Review.spec_compliance-cne'APPROVED'-or$Review.code_quality-cne'APPROVED'){throw 'implementation review no longer authenticates ExpectedEvidenceHead'}
$Local=(git -C $Worktree rev-parse HEAD).Trim();if($LASTEXITCODE-ne0-or$Local-cne$ExpectedEvidenceHead){throw 'local implementation head changed'};$Remote=@(git -C $Worktree ls-remote --heads origin "refs/heads/$Branch");if($LASTEXITCODE-ne0-or$Remote.Count-ne1-or($Remote[0]-split"`t")[0]-cne$Parent){throw 'old remote head changed'}
[pscustomobject]@{expected_evidence_head=$ExpectedEvidenceHead;old_remote_head=$Parent;push_ready=$true}|ConvertTo-Json -Compress
```

- [ ] **Step 4 (2–5 min): Push only the authenticated commit and freeze exact remote readback**

```powershell
$ErrorActionPreference='Stop';$Worktree='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Branch='codex/test/sgx-extra-cycle-convergence-validation';Set-Location -LiteralPath $Worktree
$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_expected_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'ExpectedEvidenceHead unavailable'};$ExpectedEvidenceHead=$HM[0].Groups[1].Value
git -C $Worktree push origin "$ExpectedEvidenceHead`:refs/heads/$Branch";if($LASTEXITCODE-ne0){throw 'ordinary fast-forward push failed'};$Readback=@(git -C $Worktree ls-remote --heads origin "refs/heads/$Branch");if($LASTEXITCODE-ne0-or$Readback.Count-ne1){throw 'remote readback unavailable'};$RemoteHead=($Readback[0]-split"`t")[0];if($RemoteHead-cne$ExpectedEvidenceHead){throw 'remote readback is not ExpectedEvidenceHead; no EvidenceHead'}
$Lines=@("- production_validation_head: ``$ExpectedEvidenceHead``",'- production_unix_exit_evidence_implementation_parent: `2eb90e3f99219e28390570d13bd906cfe6e17012`',"- production_unix_exit_evidence_implementation_commit: ``$ExpectedEvidenceHead``",'- production_unix_exit_evidence_implementation_review: `Spec Compliance APPROVED; Code Quality APPROVED`',"- production_unix_exit_evidence_remote_head: ``$ExpectedEvidenceHead``","- production_unix_exit_evidence_head: ``$ExpectedEvidenceHead``",'- production_unix_exit_evidence_next_step: `derive and independently review the frozen-head Phase B execution and transport contracts; do not dispatch`');[pscustomobject]@{evidence_head=$ExpectedEvidenceHead;lines=$Lines}|ConvertTo-Json -Depth 3
```

Use `apply_patch` to replace the unique existing `production_validation_head` and `production_unix_exit_evidence_next_step` lines with the seven printed lines byte-for-byte. A remote mismatch writes nothing and authorizes no dispatch.

- [ ] **Step 5 (2–5 min): Read back all frozen provenance without a dynamic design HEAD**

```powershell
$ErrorActionPreference = 'Stop'
$PlanWorktree='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';Set-Location -LiteralPath $PlanWorktree
$Active = 'D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md'
$Text = [IO.File]::ReadAllText($Active, [Text.UTF8Encoding]::new($false, $true))
$Keys=@('production_unix_exit_evidence_expected_head','production_validation_head','production_unix_exit_evidence_implementation_commit','production_unix_exit_evidence_remote_head','production_unix_exit_evidence_head')
$Values = @()
foreach ($Key in $Keys) {
  $M = [regex]::Matches($Text, "(?m)^- $Key`: ``([0-9a-f]{40})``$")
  if ($M.Count -ne 1) { throw "active key cardinality mismatch: $Key" }
  $Values += $M[0].Groups[1].Value
}
if (@($Values | Select-Object -Unique).Count -ne 1) { throw 'frozen active heads differ' }
$PlanPathMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_plan_path: `(.+)`$');$PlanCommitMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_plan_commit: `([0-9a-f]{40})`$');$PlanShaMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_plan_sha256: `([0-9a-f]{64})`$');$PlanReviewPathMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_plan_review_path: `(.+)`$');$PlanReviewShaMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_plan_review_sha256: `([0-9a-f]{64})`$');if($PlanPathMatch.Count-ne1-or$PlanCommitMatch.Count-ne1-or$PlanShaMatch.Count-ne1-or$PlanReviewPathMatch.Count-ne1-or$PlanReviewShaMatch.Count-ne1){throw 'frozen plan provenance key mismatch'}
if((Get-FileHash $PlanPathMatch[0].Groups[1].Value -Algorithm SHA256).Hash.ToLowerInvariant()-cne$PlanShaMatch[0].Groups[1].Value-or(Get-FileHash $PlanReviewPathMatch[0].Groups[1].Value -Algorithm SHA256).Hash.ToLowerInvariant()-cne$PlanReviewShaMatch[0].Groups[1].Value){throw 'frozen plan/report bytes changed'}
[pscustomobject]@{evidence_head=$Values[0];plan_commit=$PlanCommitMatch[0].Groups[1].Value;plan_sha256=$PlanShaMatch[0].Groups[1].Value;source='independent review reports';branch_refresh_after_freeze=$false}|ConvertTo-Json -Compress
```

No force option, tag, PR, issue, dispatch, Goal, or heartbeat command belongs to this task.

---

### Task 3: Mechanically derive and review the new head-bound Phase B contract

**Files:**
- Read immutable: `task-7-phase-b-policy-correction.md` and `task-7-phase-b-transport-execution.md`
- Create ignored: `task-7-phase-b-policy-correction-$EvidenceHead.md`
- Create ignored: `task-7-phase-b-transport-execution-$EvidenceHead.md`
- Create ignored helper: `rebind-task7-phase-b.py`
- Create ignored helper: `heartbeat-direct-handle-supervisor.ps1`

**Interfaces:**
- Consumes: Task 2's unique active-document `EvidenceHead`, immutable addendum SHA-256 `020ea0d6225632b55f37b6167a2e0fd2eed034b87bf6b03946d24243b670a395`, and immutable transport SHA-256 `f24d02372adc6b0051fdfe6cf8e1032e5322754ebdeba78298cbe97a4b83304b`.
- Produces: one head-bound execution document, one head-bound transport document, one hash-bound non-polling direct-handle supervisor, five addendum hashes, six transport hashes, a new state-root literal, and two independent `APPROVED` verdicts; no production ordinal is invoked.

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
SUPERVISOR = SDD / 'heartbeat-direct-handle-supervisor.ps1'
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
SUPERVISED_LAUNCH_MARKER = "$WindowsRunId = [long]$WindowsChain.binding.run_id\n"
SUPERVISED_LAUNCH_TAIL = r'''$WindowsRunId = [long]$WindowsChain.binding.run_id
$LinuxRunId = [long]$LinuxChain.binding.run_id
$SupervisorPath = 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production\heartbeat-direct-handle-supervisor.ps1'
$SupervisorMatches = [regex]::Matches($ActiveText,'(?m)^- production_uhf_phase_b_supervisor_sha256: `([0-9a-f]{64})`$')
if($SupervisorMatches.Count-ne1){throw 'supervisor active hash gate mismatch'}
Assert-FileHash $SupervisorPath $SupervisorMatches[0].Groups[1].Value
$HandoffPath = Join-Path $Root 'production-uhf-heartbeat-handoff.json'
$TerminalPath = Join-Path $Root 'production-uhf-heartbeat-terminal.json'
if((Test-Path $HandoffPath)-or(Test-Path $TerminalPath)){throw 'pair supervisor state already exists'}
$Args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$SupervisorPath,'-TargetRunIds',$WindowsRunId,$LinuxRunId,'-TargetHeadSha',$Head,'-HandoffPath',$HandoffPath,'-TerminalPath',$TerminalPath,'-Purpose','production-uhf-pair-heartbeat','-LaunchReadyPath',$LaunchReadyPath,'-LaunchReadySha256',$LaunchReadySha256,'-IntervalSeconds','1800','-WakeAfterMinutes','300')
$Supervisor = Start-Process -FilePath $PowerShellExe -WindowStyle Hidden -PassThru -ArgumentList $Args
$Supervisor.Refresh();$SupervisorId=[int]$Supervisor.Id;$SupervisorStart=$Supervisor.StartTime.ToUniversalTime().ToString('o')
for($I=0;$I-lt60-and-not(Test-Path $HandoffPath)-and-not(Test-Path $TerminalPath);$I++){Start-Sleep -Milliseconds 500}
if((Test-Path $TerminalPath)-and-not(Test-Path $HandoffPath)){throw 'pair supervisor stopped before durable handoff; do not replay'}
if(-not(Test-Path $HandoffPath)){throw 'pair supervisor owns unresolved launch without handoff; do not replay'}
$Handoff=Read-StrictJson $HandoffPath 'pair supervisor handoff'
if($Handoff.purpose-cne'production-uhf-pair-heartbeat'-or$Handoff.head-cne$Head-or@($Handoff.run_ids).Count-ne2-or[long]$Handoff.run_ids[0]-ne$WindowsRunId-or[long]$Handoff.run_ids[1]-ne$LinuxRunId-or$Handoff.supervisor_pid-ne$SupervisorId-or$Handoff.supervisor_start_utc-cne$SupervisorStart-or$Handoff.goal_status-cne'paused'){throw 'pair supervisor handoff identity mismatch'}
$Supervisor.Refresh();if($Supervisor.HasExited){throw 'pair supervisor exited during handoff verification'}
[pscustomobject]@{handoff_path=$HandoffPath;handoff_sha256=Get-Sha256 $HandoffPath;terminal_path=$TerminalPath;supervisor_pid=$SupervisorId;supervisor_start_utc=$SupervisorStart;heartbeat_pid=[int]$Handoff.heartbeat_pid;heartbeat_start_utc=[string]$Handoff.heartbeat_start_utc;windows_run_id=$WindowsRunId;linux_run_id=$LinuxRunId;launch_ready_sha256=$LaunchReadySha256;goal_status='paused'}|ConvertTo-Json -Compress
$Supervisor.Dispose()
'''


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
supervisor_bytes=SUPERVISOR.read_bytes()
if(supervisor_bytes.startswith(b'\xef\xbb\xbf') or b'\r' in supervisor_bytes or
        not supervisor_bytes.endswith(b'\n')):
    raise RuntimeError('supervisor encoding/EOL mismatch')
supervisor_sha=sha256(supervisor_bytes)

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
fence_matches = list(FENCE_RE.finditer(addendum))
if len(fence_matches) != 5:
    raise RuntimeError(f'pre-supervisor addendum fence count {len(fence_matches)}')
launch_code = fence_matches[3].group(1)
if launch_code.count(SUPERVISED_LAUNCH_MARKER) != 1:
    raise RuntimeError('pair launch-tail marker mismatch')
launch_code = launch_code.split(SUPERVISED_LAUNCH_MARKER,1)[0] + SUPERVISED_LAUNCH_TAIL
start,end=fence_matches[3].span(1)
addendum=addendum[:start]+launch_code+addendum[end:]
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
print(f'supervisor_path={SUPERVISOR}')
print(f'supervisor_sha256={supervisor_sha}')
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

- [ ] **Step 2 (2–5 min): Create the non-polling direct-handle supervisor**

Use `apply_patch` to create `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/heartbeat-direct-handle-supervisor.ps1` with this complete Windows PowerShell 5.1 script:

```powershell
param(
    [string[]]$TargetRunIds,
    [string]$TargetHeadSha,
    [string]$HandoffPath,
    [string]$TerminalPath,
    [string]$Purpose,
    [string]$LaunchReadyPath,
    [string]$LaunchReadySha256,
    [int]$IntervalSeconds = 1800,
    [int]$WakeAfterMinutes = 300,
    [switch]$SelfTest)
$ErrorActionPreference='Stop'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';Set-Location -LiteralPath $Design
$Heartbeat='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';$HeartbeatSha256='4198340e5e56caa9a103f37a133bd9cb5ab37d839771f5aae832c280b0e2f639';$PowerShellExe='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe';$GoalThreadId='019f64bd-77a5-7573-88e9-fd80b1882e70';$Utf8=[Text.UTF8Encoding]::new($false);$Strict=[Text.UTF8Encoding]::new($false,$true)
function Get-TextSha([string]$Text){$A=[Security.Cryptography.SHA256]::Create();try{return [BitConverter]::ToString($A.ComputeHash($Utf8.GetBytes($Text))).Replace('-','').ToLowerInvariant()}finally{$A.Dispose()}}
function Write-NewJson([string]$Path,[object]$Value){$B=$Utf8.GetBytes(($Value|ConvertTo-Json -Depth 8 -Compress)+"`n");$S=[IO.File]::Open($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($B,0,$B.Length);$S.Flush($true)}finally{$S.Dispose()};$R=$Strict.GetString([IO.File]::ReadAllBytes($Path))|ConvertFrom-Json;return $R}
function Get-Cim([int]$Id){return @(Get-CimInstance Win32_Process -Filter "ProcessId=$Id" -ErrorAction Stop)}
function Set-Goal([string]$Status){$Raw=@(& $PowerShellExe -NoProfile -ExecutionPolicy Bypass -File $Heartbeat -SetGoalStatus $Status);if($LASTEXITCODE-ne0){throw "Goal $Status native failure"};$G=ConvertFrom-Json($Raw-join"`n");if($G.threadId-cne$GoalThreadId-or$G.status-cne$Status){throw "Goal $Status readback mismatch"};return $G}
if($SelfTest){$P=Start-Process -FilePath $PowerShellExe -WindowStyle Hidden -PassThru -ArgumentList @('-NoProfile','-Command','exit 0');$Id=[int]$P.Id;$Start=$P.StartTime.ToUniversalTime().ToString('o');if(-not$P.WaitForExit(30000)){throw 'self-test child timeout'};$P.Refresh();for($I=0;$I-lt20-and@(Get-Cim $Id).Count-ne0;$I++){Start-Sleep -Milliseconds 250};$Gone=@(Get-Cim $Id);$Result=[ordered]@{pid=$Id;start_utc=$Start;wait_completed=$true;direct_handle_has_exited=[bool]$P.HasExited;exit_code=[int]$P.ExitCode;cim_count=$Gone.Count};$P.Dispose();if(-not$Result.direct_handle_has_exited-or$Result.exit_code-ne0-or$Result.cim_count-ne0){throw 'direct-handle self-test failed'};$Result|ConvertTo-Json -Compress;exit 0}
if($TargetHeadSha-notmatch'^[0-9a-f]{40}$'-or@($TargetRunIds).Count-lt1-or@($TargetRunIds).Count-gt2-or@($TargetRunIds|Select-Object -Unique).Count-ne@($TargetRunIds).Count-or[string]::IsNullOrWhiteSpace($Purpose)-or$LaunchReadySha256-notmatch'^[0-9a-f]{64}$'){throw 'supervisor arguments invalid'}
if((Get-FileHash $Heartbeat -Algorithm SHA256).Hash.ToLowerInvariant()-cne$HeartbeatSha256){throw 'heartbeat hash mismatch'};if(-not(Test-Path $LaunchReadyPath -PathType Leaf)-or(Get-FileHash $LaunchReadyPath -Algorithm SHA256).Hash.ToLowerInvariant()-cne$LaunchReadySha256){throw 'launch-ready hash mismatch'};if((Test-Path $HandoffPath)-or(Test-Path $TerminalPath)){throw 'supervisor state path already exists'}
$SupervisorSelf=Get-Process -Id $PID -ErrorAction Stop;$SupervisorStart=$SupervisorSelf.StartTime.ToUniversalTime().ToString('o');$HeartbeatProcess=$null;$HeartbeatId=0;$HeartbeatStart=$null;$Command=$null;$Encoded=$null;$HandoffWritten=$false;$Failures=New-Object 'System.Collections.Generic.List[string]'
try{$Command="& '$Heartbeat' -TargetRunIds @('$([string]::Join("','",$TargetRunIds))') -TargetHeadSha '$TargetHeadSha' -IntervalSeconds $IntervalSeconds -WakeAfterMinutes $WakeAfterMinutes";$Encoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command));$HeartbeatProcess=Start-Process -FilePath $PowerShellExe -WindowStyle Hidden -PassThru -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-EncodedCommand',$Encoded);$HeartbeatId=[int]$HeartbeatProcess.Id;$HeartbeatProcess.Refresh();$HeartbeatStart=$HeartbeatProcess.StartTime.ToUniversalTime().ToString('o');$Rows=@(Get-Cim $HeartbeatId);if($HeartbeatProcess.HasExited-or$Rows.Count-ne1-or$Rows[0].ExecutablePath-cne$PowerShellExe-or$Rows[0].CommandLine-notmatch([regex]::Escape($Encoded))){throw 'original heartbeat direct-child identity mismatch'};$Goal=Set-Goal 'paused'
  $Handoff=[ordered]@{purpose=$Purpose;head=$TargetHeadSha;run_ids=@($TargetRunIds);supervisor_pid=[int]$PID;supervisor_start_utc=$SupervisorStart;supervisor_executable=$PowerShellExe;heartbeat_pid=$HeartbeatId;heartbeat_start_utc=$HeartbeatStart;heartbeat_executable=$PowerShellExe;encoded_command_sha256=Get-TextSha $Encoded;heartbeat_path=$Heartbeat;heartbeat_sha256=$HeartbeatSha256;launch_ready_path=$LaunchReadyPath;launch_ready_sha256=$LaunchReadySha256;interval_seconds=$IntervalSeconds;wake_after_minutes=$WakeAfterMinutes;goal_thread_id=$GoalThreadId;goal_status='paused'};$HR=Write-NewJson $HandoffPath $Handoff;if($HR.heartbeat_pid-ne$HeartbeatId-or$HR.supervisor_pid-ne$PID-or$HR.supervisor_start_utc-cne$SupervisorStart-or$HR.head-cne$TargetHeadSha){throw 'handoff durable readback mismatch'};$HandoffWritten=$true
  $HeartbeatProcess.WaitForExit();$HeartbeatProcess.Refresh();$DirectHasExited=[bool]$HeartbeatProcess.HasExited;$ExitCode=[int]$HeartbeatProcess.ExitCode;if(-not$DirectHasExited-or$HeartbeatProcess.Id-ne$HeartbeatId-or$HeartbeatProcess.StartTime.ToUniversalTime().ToString('o')-cne$HeartbeatStart){throw 'original direct handle terminal proof failed'};for($I=0;$I-lt20-and@(Get-Cim $HeartbeatId).Count-ne0;$I++){Start-Sleep -Milliseconds 250};$Cim=@(Get-Cim $HeartbeatId);if($Cim.Count-ne0){throw 'heartbeat CIM row remains after direct handle exit'};$ActiveGoal=Set-Goal 'active';if($ExitCode-ne0){throw "heartbeat exit code $ExitCode"}
  $Terminal=[ordered]@{purpose=$Purpose;head=$TargetHeadSha;run_ids=@($TargetRunIds);handoff_path=$HandoffPath;handoff_sha256=(Get-FileHash $HandoffPath -Algorithm SHA256).Hash.ToLowerInvariant();supervisor_pid=[int]$PID;supervisor_start_utc=$SupervisorStart;supervisor_executable=$PowerShellExe;heartbeat_pid=$HeartbeatId;heartbeat_start_utc=$HeartbeatStart;heartbeat_executable=$PowerShellExe;encoded_command_sha256=Get-TextSha $Encoded;wait_completed=$true;direct_handle_has_exited=$DirectHasExited;heartbeat_exit_code=$ExitCode;cim_count=$Cim.Count;goal_thread_id=$GoalThreadId;goal_status=[string]$ActiveGoal.status;terminal_status='PASS';completed_utc=[DateTimeOffset]::UtcNow.ToString('o')};$TR=Write-NewJson $TerminalPath $Terminal;if($TR.supervisor_start_utc-cne$SupervisorStart-or$TR.direct_handle_has_exited-ne$true-or$TR.terminal_status-cne'PASS'){throw 'terminal marker durable readback mismatch'}
}catch{[void]$Failures.Add($_.Exception.Message);if($null-ne$HeartbeatProcess){try{$HeartbeatProcess.Refresh();if(-not$HeartbeatProcess.HasExited){if($HeartbeatProcess.Id-ne$HeartbeatId-or$HeartbeatProcess.StartTime.ToUniversalTime().ToString('o')-cne$HeartbeatStart){throw 'cleanup direct-handle identity changed'};Stop-Process -Id $HeartbeatId -Force -ErrorAction Stop};if(-not$HeartbeatProcess.WaitForExit(30000)){throw 'cleanup wait timeout'};$HeartbeatProcess.Refresh();if(-not$HeartbeatProcess.HasExited-or@(Get-Cim $HeartbeatId).Count-ne0){throw 'cleanup terminal proof failed'}}catch{[void]$Failures.Add("cleanup: $($_.Exception.Message)")}};try{[void](Set-Goal 'active')}catch{[void]$Failures.Add("Goal active: $($_.Exception.Message)")};if(-not(Test-Path $TerminalPath)){try{$Stop=[ordered]@{purpose=$Purpose;head=$TargetHeadSha;run_ids=@($TargetRunIds);handoff_written=$HandoffWritten;supervisor_pid=[int]$PID;supervisor_start_utc=$SupervisorStart;supervisor_executable=$PowerShellExe;heartbeat_pid=$HeartbeatId;heartbeat_start_utc=$HeartbeatStart;wait_completed=if($null-ne$HeartbeatProcess){[bool]$HeartbeatProcess.HasExited}else{$false};direct_handle_has_exited=if($null-ne$HeartbeatProcess){[bool]$HeartbeatProcess.HasExited}else{$false};terminal_status='STOP';errors=@($Failures);completed_utc=[DateTimeOffset]::UtcNow.ToString('o')};[void](Write-NewJson $TerminalPath $Stop)}catch{[void]$Failures.Add("STOP marker: $($_.Exception.Message)")}};throw [InvalidOperationException]::new([string]::Join('; ',$Failures))
}finally{if($null-ne$HeartbeatProcess){$HeartbeatProcess.Dispose()}}
```

Normalize it with the same strict UTF-8/no-BOM/LF policy used for the tracked files. In a fresh shell run the exact harmless command `Set-Location -LiteralPath 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'; & 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production\heartbeat-direct-handle-supervisor.ps1' -SelfTest; if (-not $?) { throw 'supervisor self-test failed' }`; require one JSON object with `wait_completed=true`, `direct_handle_has_exited=true`, `exit_code=0`, and `cim_count=0`. Production arguments remain forbidden.

- [ ] **Step 3 (2–5 min): Derive the two new ignored contracts without dispatch**

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
  'evidence_head','supervisor_path','supervisor_sha256','state_root','addendum_path','addendum_sha256',
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

- [ ] **Step 4 (2–5 min): Parse every derived fence with Windows PowerShell 5.1**

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

- [ ] **Step 5 (2–5 min): Run the derived materializer twice, then the harmless self-test once**

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

- [ ] **Step 6 (2–5 min): Prove mechanical scope and absence of stale production identity**

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

- [ ] **Step 7 (2–5 min): Require independent execution-contract and transport review**

Give independent reviewers: immutable input hashes, rebind helper and supervisor source, supervisor harmless direct-handle self-test output, exact replacement counts (`old head=10`, root assignment=`4`, authenticated-head/witness gate tail=`4`, prohibited local-head recalculation=`4`, retained exact remote-head equality check=`4`, supervised Block-4 tail=`1`, addendum filename=`7`, addendum SHA=`7`, transport namespace=`6`, each old fence hash=`4`), derived document hashes, five addendum fence hashes, six transport fence hashes, AST results, two materializer results, and the harmless `19 cases` output. Require explicit `Execution Contract: APPROVED` and `Transport Contract: APPROVED`. Review must confirm that all four production blocks require both active-document `ExpectedEvidenceHead` and `EvidenceHead` literals to equal `$Head`; every dispatch preflight requires remote branch equality without reassigning `$Head`; Block 4 launches only the reviewed non-polling supervisor; all four blocks require `production_unix_wrapper_witness_verdict: PASS`; initial candidate uniqueness applies only before a binding exists; frozen pairs use exact bound run IDs plus the two-ID allowlist; no third exact-head run is admitted; old state is immutable; and production ordinals were not executed.

After approval, run this complete fresh shell. It derives `EvidenceHead` only from the frozen active-document literal, reruns the helper, checks every required output, and renders five addendum plus six transport hash lines:

```powershell
$ErrorActionPreference='Stop'
$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$ActiveText=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($ActiveText,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'frozen EvidenceHead unavailable'};$EvidenceHead=$HeadMatch[0].Groups[1].Value
$RebindOutput=@(conda run --no-capture-output -n pyscf-win313-test python "$Design\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production\rebind-task7-phase-b.py" $EvidenceHead);if($LASTEXITCODE-ne0){throw 'approved helper rerun failed'};$Rebind=ConvertFrom-StringData($RebindOutput-join"`n")
foreach($Key in @('evidence_head','supervisor_path','supervisor_sha256','state_root','addendum_path','addendum_sha256','addendum_disposition','transport_path','transport_sha256','transport_disposition')){if(-not$Rebind.ContainsKey($Key)){throw "missing rebind output $Key"}}
if($Rebind.evidence_head-cne$EvidenceHead){throw 'approved rebind EvidenceHead mismatch'}
$ContractLines = @(
  "- production_uhf_phase_b_supervisor_path: ``$($Rebind.supervisor_path)``",
  "- production_uhf_phase_b_supervisor_sha256: ``$($Rebind.supervisor_sha256)``",
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
- Produces: one immutable macOS latch/binding, one supervisor-owned original-handle heartbeat proof, one durable staged archive completion, strict source-tree/native-16 `PASS`, and exact active evidence keys; it produces no scientific-stability claim.

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

- [ ] **Step 2 (2–5 min): Launch or recover the witness supervisor and freeze its durable handoff**

```powershell
$ErrorActionPreference='Stop'
$Repo='psiQAQ/pyscf';$Branch='codex/test/sgx-extra-cycle-convergence-validation';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Heartbeat='D:\workspace\pyscf\.agents\active\libxc-712-ci-heartbeat.ps1';$PowerShellExe='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'frozen EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value
$Remote=@(git ls-remote https://github.com/psiQAQ/pyscf.git "refs/heads/$Branch");if($LASTEXITCODE-ne0-or$Remote.Count-ne1-or($Remote[0]-split"`t")[0]-cne$Head){throw 'remote no longer equals EvidenceHead; no heartbeat launch'}
$SM=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_supervisor_path: `([^`]+)`$');$SH=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_supervisor_sha256: `([0-9a-f]{64})`$');if($SM.Count-ne1-or$SH.Count-ne1){throw 'supervisor provenance unavailable'};$SupervisorPath=$SM[0].Groups[1].Value;$SupervisorSha=$SH[0].Groups[1].Value;if((Get-FileHash $SupervisorPath -Algorithm SHA256).Hash.ToLowerInvariant()-cne$SupervisorSha){throw 'supervisor hash mismatch'};$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$Head";$BindingPath=Join-Path $Root 'macos-binding.json';$ReadyPath=Join-Path $Root 'macos-launch-ready.json';$HandoffPath=Join-Path $Root 'macos-heartbeat-handoff.json';$TerminalPath=Join-Path $Root 'macos-heartbeat-terminal.json'
$Binding=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($BindingPath))|ConvertFrom-Json);$RunId=[long]$Binding.run_id;if($Binding.head-cne$Head-or$Binding.platform-cne'macos-latest'-or$Binding.repeats-ne1){throw 'witness binding mismatch'}
$RunRaw=@(gh run view $RunId --repo $Repo --json databaseId,attempt,event,workflowName,headSha,headBranch,status);if($LASTEXITCODE-ne0){throw 'witness launch identity query failed'};$Run=ConvertFrom-Json($RunRaw-join"`n");if($Run.databaseId-ne$RunId-or$Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.workflowName-cne'Precision investigation'-or$Run.headSha-cne$Head-or$Run.headBranch-cne$Branch){throw 'witness run head/identity mismatch; preserve and STOP without replay'}
$Leaf=[IO.Path]::GetFileName($Heartbeat);$Pollers=@(Get-CimInstance Win32_Process -ErrorAction Stop|Where-Object{[int]$_.ProcessId-ne$PID-and$_.CommandLine-and([string]$_.CommandLine).IndexOf($Leaf,[StringComparison]::OrdinalIgnoreCase)-ge0});if($Pollers.Count-ne0){throw 'another heartbeat process exists'};$Schedulers=@(Get-ScheduledTask -ErrorAction Stop|Where-Object{$_.State-cne'Disabled'}|Where-Object{$n="$($_.TaskPath)$($_.TaskName)";$a=($_.Actions|ForEach-Object{"$($_.Execute) $($_.Arguments)"})-join' ';$n-match'(?i)heartbeat|precision-ci'-or$a.IndexOf($Leaf,[StringComparison]::OrdinalIgnoreCase)-ge0});if($Schedulers.Count-ne0){throw 'native heartbeat scheduler exists'}
$Utf8=[Text.UTF8Encoding]::new($false,$true);function Read-J([string]$P){$Utf8.GetString([IO.File]::ReadAllBytes($P))|ConvertFrom-Json};function Write-New([string]$P,[object]$O){$B=[Text.UTF8Encoding]::new($false).GetBytes(($O|ConvertTo-Json -Depth 8 -Compress)+"`n");$S=[IO.File]::Open($P,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($B,0,$B.Length);$S.Flush($true)}finally{$S.Dispose()};Read-J $P};$ReadyObject=[ordered]@{purpose='unix-wrapper-witness-launch-ready';head=$Head;run_ids=@($RunId);run_id=$RunId;binding_path=$BindingPath;binding_sha256=(Get-FileHash $BindingPath -Algorithm SHA256).Hash.ToLowerInvariant();supervisor_path=$SupervisorPath;supervisor_sha256=$SupervisorSha;interval_seconds=1800;wake_after_minutes=300};if(Test-Path $ReadyPath){$Ready=Read-J $ReadyPath}else{$Ready=Write-New $ReadyPath $ReadyObject};if(($Ready|ConvertTo-Json -Depth 8 -Compress)-cne($ReadyObject|ConvertTo-Json -Depth 8 -Compress)){throw 'witness launch-ready mismatch'};$ReadySha=(Get-FileHash $ReadyPath -Algorithm SHA256).Hash.ToLowerInvariant()
if(Test-Path $TerminalPath){$T=Read-J $TerminalPath;if($T.purpose-cne'unix-wrapper-witness-heartbeat'-or$T.head-cne$Head-or@($T.run_ids).Count-ne1-or[long]$T.run_ids[0]-ne$RunId){throw 'existing terminal mismatch'};[pscustomobject]@{disposition='existing-terminal';status=[string]$T.terminal_status;run_id=$RunId}|ConvertTo-Json -Compress;exit 0};if(Test-Path $HandoffPath){$H=Read-J $HandoffPath;if($H.purpose-cne'unix-wrapper-witness-heartbeat'-or$H.head-cne$Head-or@($H.run_ids).Count-ne1-or[long]$H.run_ids[0]-ne$RunId-or$H.launch_ready_sha256-cne$ReadySha){throw 'existing handoff mismatch'};[pscustomobject]@{disposition='existing-handoff';supervisor_pid=[int]$H.supervisor_pid;heartbeat_pid=[int]$H.heartbeat_pid;goal='paused'}|ConvertTo-Json -Compress;exit 0}
$Args=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$SupervisorPath,'-TargetRunIds',$RunId,'-TargetHeadSha',$Head,'-HandoffPath',$HandoffPath,'-TerminalPath',$TerminalPath,'-Purpose','unix-wrapper-witness-heartbeat','-LaunchReadyPath',$ReadyPath,'-LaunchReadySha256',$ReadySha,'-IntervalSeconds','1800','-WakeAfterMinutes','300');$Supervisor=Start-Process -FilePath $PowerShellExe -WindowStyle Hidden -PassThru -ArgumentList $Args;$SupervisorId=[int]$Supervisor.Id;$Supervisor.Refresh();$SupervisorStart=$Supervisor.StartTime.ToUniversalTime().ToString('o');$Rows=@(Get-CimInstance Win32_Process -Filter "ProcessId=$SupervisorId" -ErrorAction Stop);if($Supervisor.HasExited-or$Rows.Count-ne1-or$Rows[0].ExecutablePath-cne$PowerShellExe-or$Rows[0].CommandLine.IndexOf($SupervisorPath,[StringComparison]::OrdinalIgnoreCase)-lt0){throw 'supervisor launch identity mismatch'}
for($I=0;$I-lt60-and-not(Test-Path $HandoffPath)-and-not(Test-Path $TerminalPath);$I++){Start-Sleep -Milliseconds 500};if(Test-Path $TerminalPath){$T=Read-J $TerminalPath;throw "supervisor stopped before handoff: $($T.terminal_status)"};if(-not(Test-Path $HandoffPath)){throw 'supervisor handoff timeout'};$H=Read-J $HandoffPath;if($H.purpose-cne'unix-wrapper-witness-heartbeat'-or$H.head-cne$Head-or@($H.run_ids).Count-ne1-or[long]$H.run_ids[0]-ne$RunId-or$H.supervisor_pid-ne$SupervisorId-or$H.supervisor_start_utc-cne$SupervisorStart-or$H.launch_ready_sha256-cne$ReadySha-or$H.goal_status-cne'paused'){throw 'supervisor handoff exact readback mismatch'};$Supervisor.Refresh();if($Supervisor.HasExited){throw 'supervisor exited during handoff verification'};[pscustomobject]@{disposition='launched';supervisor_pid=$SupervisorId;heartbeat_pid=[int]$H.heartbeat_pid;run_id=$RunId;handoff_sha256=(Get-FileHash $HandoffPath -Algorithm SHA256).Hash.ToLowerInvariant();goal='paused'}|ConvertTo-Json -Compress
```

- [ ] **Step 3 (2–5 min): Verify the original-handle terminal proof and Goal reconciliation**

After terminal state appears, use the approved Goal bridge to require exact `active` and record exactly one active-document line `- production_unix_wrapper_witness_terminal_goal: active` with `apply_patch`. This gate consumes the supervisor's persistent proof emitted while it still owned the original direct-child handle; it never synthesizes `HasExited` from a later handle:

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design;$Utf8=[Text.UTF8Encoding]::new($false,$true)
$Active=[IO.File]::ReadAllText($ActiveDoc,$Utf8);$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$Head";$HP=Join-Path $Root 'macos-heartbeat-handoff.json';$TP=Join-Path $Root 'macos-heartbeat-terminal.json';$H=($Utf8.GetString([IO.File]::ReadAllBytes($HP))|ConvertFrom-Json);$T=($Utf8.GetString([IO.File]::ReadAllBytes($TP))|ConvertFrom-Json);$HandoffSha=(Get-FileHash $HP -Algorithm SHA256).Hash.ToLowerInvariant()
if($T.purpose-cne'unix-wrapper-witness-heartbeat'-or$T.head-cne$Head-or$T.handoff_path-cne$HP-or$T.handoff_sha256-cne$HandoffSha-or$T.supervisor_pid-ne$H.supervisor_pid-or$T.supervisor_start_utc-cne$H.supervisor_start_utc-or$T.supervisor_executable-cne$H.supervisor_executable-or$T.heartbeat_pid-ne$H.heartbeat_pid-or$T.heartbeat_start_utc-cne$H.heartbeat_start_utc-or$T.encoded_command_sha256-cne$H.encoded_command_sha256-or$T.wait_completed-ne$true-or$T.direct_handle_has_exited-ne$true-or$T.heartbeat_exit_code-ne0-or$T.cim_count-ne0-or$T.goal_status-cne'active'-or$T.terminal_status-cne'PASS'){throw 'witness original-handle terminal proof mismatch'}
for($I=0;$I-lt20-and@(Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$T.supervisor_pid)" -ErrorAction Stop).Count-ne0;$I++){Start-Sleep -Milliseconds 250};if(@(Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$T.supervisor_pid)" -ErrorAction Stop).Count-ne0){throw 'witness supervisor remains'};if([regex]::Matches($Active,'(?m)^- production_unix_wrapper_witness_terminal_goal: active$').Count-ne1){throw 'independent Goal active readback missing'};[pscustomobject]@{heartbeat_pid=[int]$T.heartbeat_pid;direct_handle_has_exited=$true;heartbeat_cim_count=0;supervisor_cim_count=0;goal='active';terminal_sha256=(Get-FileHash $TP -Algorithm SHA256).Hash.ToLowerInvariant()}|ConvertTo-Json -Compress
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
$Archive="D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-production-unix-wrapper-witness-macos-py312";[void][IO.Directory]::CreateDirectory($Archive);$Utf8=[Text.UTF8Encoding]::new($false);$Strict=[Text.UTF8Encoding]::new($false,$true);function Read-J([string]$P){$Strict.GetString([IO.File]::ReadAllBytes($P))|ConvertFrom-Json};function Write-New([string]$P,[object]$O){$B=$Utf8.GetBytes(($O|ConvertTo-Json -Depth 9 -Compress)+"`n");$S=[IO.File]::Open($P,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($B,0,$B.Length);$S.Flush($true)}finally{$S.Dispose()};Read-J $P}
$Identity=[ordered]@{purpose='unix-wrapper-witness-archive';head=$Head;run_id=$RunId;artifact_id=[long]$Artifact.id;artifact_name=[string]$Artifact.name;artifact_digest=[string]$Artifact.digest;artifact_size=[long]$Artifact.size_in_bytes;branch=$Branch;validator_sha256='d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c'};$IdentityPath=Join-Path $Archive 'archive-identity.json';if(Test-Path $IdentityPath){$IR=Read-J $IdentityPath}else{$IR=Write-New $IdentityPath $Identity};if(($IR|ConvertTo-Json -Depth 9 -Compress)-cne($Identity|ConvertTo-Json -Depth 9 -Compress)){throw 'witness archive identity mismatch'};$CompletePath=Join-Path $Archive 'archive-complete.json';if(Test-Path $CompletePath){$C=Read-J $CompletePath;$CA=[string]$C.attempt_dir;$CRP=Join-Path $CA 'production-validation.json';$CRun=Join-Path $CA 'run.json';$CV=Join-Path $CA 'validate_precision_production.py';if($C.head-cne$Head-or$C.run_id-ne$RunId-or$C.artifact_id-ne[long]$Artifact.id-or$C.tested_sha-cne$Head-or$C.verdict-cne'PASS'-or$C.runner_exit_sha256-cne'9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa'-or$C.identity_sha256-cne(Get-FileHash $IdentityPath -Algorithm SHA256).Hash.ToLowerInvariant()-or-not(Test-Path $CRP -PathType Leaf)-or(Get-FileHash $CRP -Algorithm SHA256).Hash.ToLowerInvariant()-cne$C.report_sha256-or(Get-FileHash $CRun -Algorithm SHA256).Hash.ToLowerInvariant()-cne$C.run_sha256-or(Get-FileHash $CV -Algorithm SHA256).Hash.ToLowerInvariant()-cne$C.validator_sha256){throw 'witness completion mismatch'};$Lines=@("- production_unix_wrapper_witness_run_id: ``$RunId``","- production_unix_wrapper_witness_artifact_id: ``$([long]$Artifact.id)``","- production_unix_wrapper_witness_report_sha256: ``$([string]$C.report_sha256)``","- production_unix_wrapper_witness_runner_exit_sha256: ``$([string]$C.runner_exit_sha256)``","- production_unix_wrapper_witness_tested_sha: ``$Head``",'- production_unix_wrapper_witness_verdict: PASS','- production_unix_wrapper_witness_claim: `transport/provenance only; repeats=1 is not scientific stability`');[pscustomobject]@{active_lines=$Lines;archive=$Archive;attempt_dir=$CA}|ConvertTo-Json -Depth 4;exit 0}
$Numbers=@(Get-ChildItem -LiteralPath $Archive -Directory -Filter 'attempt-*'|ForEach-Object{if($_.Name-match'^attempt-([0-9]{4})$'){[int]$Matches[1]}});$Next=if($Numbers.Count){([Linq.Enumerable]::Max([int[]]$Numbers))+1}else{1};$AttemptDir=Join-Path $Archive ('attempt-{0:d4}'-f$Next);[void][IO.Directory]::CreateDirectory($AttemptDir);gh run download $RunId --repo $Repo --name 'precision-macOS-py3.12' --dir $AttemptDir;if($LASTEXITCODE-ne0){throw 'witness download failed; keep attempt for same-run recovery'}
$RunObject=[ordered]@{databaseId=$RunId;attempt=1;event='workflow_dispatch';workflowName='Precision investigation';headSha=$Head;headBranch=$Branch;status='completed';conclusion='success';jobs=@([ordered]@{databaseId=[long]$Jobs[0].databaseId;name='precision';status='completed';conclusion='success'});artifacts=@([ordered]@{id=[long]$Artifact.id;name=[string]$Artifact.name;digest=[string]$Artifact.digest;sizeInBytes=[long]$Artifact.size_in_bytes;expired=[bool]$Artifact.expired})}
$RunBytes=$Utf8.GetBytes(($RunObject|ConvertTo-Json -Depth 6 -Compress)+"`n");$S=[IO.File]::Open((Join-Path $AttemptDir 'run.json'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($RunBytes,0,$RunBytes.Length);$S.Flush($true)}finally{$S.Dispose()}
$RunRead=Read-J (Join-Path $AttemptDir 'run.json');if(($RunRead|ConvertTo-Json -Depth 6 -Compress)-cne($RunObject|ConvertTo-Json -Depth 6 -Compress)){throw 'witness run.json exact readback mismatch'}
$Validator='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py';if((Get-FileHash $Validator -Algorithm SHA256).Hash.ToLowerInvariant()-cne'd9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c'){throw 'validator hash mismatch'}
$VBytes=[IO.File]::ReadAllBytes($Validator);$VPath=Join-Path $AttemptDir 'validate_precision_production.py';$VS=[IO.File]::Open($VPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$VS.Write($VBytes,0,$VBytes.Length);$VS.Flush($true)}finally{$VS.Dispose()}
$ExitPath=Join-Path $AttemptDir 'runner-exit-code.txt';$Exit=[IO.File]::ReadAllBytes($ExitPath);if(-not[Linq.Enumerable]::SequenceEqual([byte[]]$Exit,[byte[]]@(0x30,0x0A))){throw 'witness runner exit bytes mismatch'};$ExitSha=(Get-FileHash $ExitPath -Algorithm SHA256).Hash.ToLowerInvariant();if($ExitSha-cne'9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa'){throw 'witness runner exit SHA mismatch'}
$Report=Join-Path $AttemptDir 'production-validation.json';if(Test-Path $Report){throw 'witness report path already exists'};conda run --no-capture-output -n pyscf-win313-test python $VPath $AttemptDir --mode source-tree --expected-sha $Head --expected-nodeids-file (Join-Path $Worktree '.github\workflows\precision-uhf-smearing-extra-cycle-nodeids.txt') --expected-profile omp4-blas4 --expected-repeats 1 --expected-platform macos-latest --expected-python 3.12 --expected-native-count 16 --run-metadata (Join-Path $AttemptDir 'run.json') --expected-run-id $RunId --expected-branch $Branch --expected-artifact-name 'precision-macOS-py3.12' --report $Report
if($LASTEXITCODE-ne0){throw 'witness strict validator failed'};$Before=[IO.File]::ReadAllBytes($Report);$RS=[IO.File]::Open($Report,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None);try{$RS.Flush($true)}finally{$RS.Dispose()};$After=[IO.File]::ReadAllBytes($Report);if(-not[Linq.Enumerable]::SequenceEqual([byte[]]$Before,[byte[]]$After)){throw 'validator report bytes changed during durability gate'};$Verdict=Read-J $Report;if($Verdict.valid-ne$true-or$Verdict.verdict-cne'PASS'-or$Verdict.tested_sha-cne$Head-or$Verdict.records-ne1-or$Verdict.pass-ne1-or$Verdict.fail-ne0-or$Verdict.profile-cne'omp4-blas4'){throw 'witness report is not strict same-EvidenceHead 1/1 PASS'};$ReportSha=(Get-FileHash $Report -Algorithm SHA256).Hash.ToLowerInvariant()
$Complete=[ordered]@{purpose='unix-wrapper-witness-archive-complete';head=$Head;run_id=$RunId;artifact_id=[long]$Artifact.id;artifact_name=[string]$Artifact.name;attempt_dir=$AttemptDir;identity_sha256=(Get-FileHash $IdentityPath -Algorithm SHA256).Hash.ToLowerInvariant();run_sha256=(Get-FileHash (Join-Path $AttemptDir 'run.json') -Algorithm SHA256).Hash.ToLowerInvariant();validator_sha256='d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c';report_sha256=$ReportSha;runner_exit_sha256=$ExitSha;tested_sha=$Head;verdict='PASS'};$CR=Write-New $CompletePath $Complete;if(($CR|ConvertTo-Json -Depth 9 -Compress)-cne($Complete|ConvertTo-Json -Depth 9 -Compress)){throw 'witness completion readback mismatch'};$Lines=@("- production_unix_wrapper_witness_run_id: ``$RunId``","- production_unix_wrapper_witness_artifact_id: ``$([long]$Artifact.id)``","- production_unix_wrapper_witness_report_sha256: ``$ReportSha``","- production_unix_wrapper_witness_runner_exit_sha256: ``$ExitSha``","- production_unix_wrapper_witness_tested_sha: ``$Head``",'- production_unix_wrapper_witness_verdict: PASS','- production_unix_wrapper_witness_claim: `transport/provenance only; repeats=1 is not scientific stability`');[pscustomobject]@{active_lines=$Lines;archive=$Archive;attempt_dir=$AttemptDir}|ConvertTo-Json -Depth 4
```

- [ ] **Step 5 (2–5 min): Freeze the witness PASS gate**

Copy the prior command's seven `active_lines` byte-for-byte into one `apply_patch` update to the active document; no hand rendering is allowed. Run this complete fresh-shell readback; do not enter Task 5 unless it succeeds:

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;foreach($P in @('(?m)^- production_unix_wrapper_witness_run_id: `[0-9]+`$','(?m)^- production_unix_wrapper_witness_artifact_id: `[0-9]+`$','(?m)^- production_unix_wrapper_witness_report_sha256: `[0-9a-f]{64}`$','(?m)^- production_unix_wrapper_witness_runner_exit_sha256: `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`$','(?m)^- production_unix_wrapper_witness_tested_sha: `'+$Head+'`$','(?m)^- production_unix_wrapper_witness_verdict: PASS$','(?m)^- production_unix_wrapper_witness_claim: `transport/provenance only; repeats=1 is not scientific stability`$')){if([regex]::Matches($Text,$P).Count-ne1){throw "witness active evidence mismatch: $P"}}
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
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText('D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md',[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;if([regex]::Matches($Active,'(?m)^- production_unix_wrapper_witness_terminal_goal: active$').Count-ne1-or[regex]::Matches($Active,'(?m)^- production_unix_wrapper_witness_verdict: PASS$').Count-ne1){throw 'witness lifecycle not complete'};$WT="D:\workspace\pyscf\.agents\active\precision-ci\task-7-unix-wrapper-witness-$Head\macos-heartbeat-terminal.json";$W=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes($WT))|ConvertFrom-Json);if($W.head-cne$Head-or$W.terminal_status-cne'PASS'-or$W.direct_handle_has_exited-ne$true-or$W.cim_count-ne0-or$W.goal_status-cne'active'-or@(Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$W.supervisor_pid)" -ErrorAction Stop).Count-ne0){throw 'witness terminal proof incomplete or overlaps pair'};$M=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_transport_fence_3_sha256: `([0-9a-f]{64})`$');if($M.Count-ne1){throw 'transport hash gate 3'};$P=Join-Path "$Design\tmp\task7-phase-b-contract-review-$Head" "transport-fence-3-$($M[0].Groups[1].Value).ps1";if((Get-FileHash $P -Algorithm SHA256).Hash.ToLowerInvariant()-cne$M[0].Groups[1].Value){throw 'transport fence 3 mismatch'};& $P;if(-not$?){throw 'pair Block 1 failed'}
```

- [ ] **Step 2 (2–5 min): Invoke transport fence 4 for pair Block 2**

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText('D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md',[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$M=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_transport_fence_4_sha256: `([0-9a-f]{64})`$');if($M.Count-ne1){throw 'transport hash gate 4'};$P=Join-Path "$Design\tmp\task7-phase-b-contract-review-$Head" "transport-fence-4-$($M[0].Groups[1].Value).ps1";if((Get-FileHash $P -Algorithm SHA256).Hash.ToLowerInvariant()-cne$M[0].Groups[1].Value){throw 'transport fence 4 mismatch'};& $P;if(-not$?){throw 'pair Block 2 failed'}
```

- [ ] **Step 3 (2–5 min): Invoke transport fence 5 for pair Block 3**

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText('D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md',[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$M=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_transport_fence_5_sha256: `([0-9a-f]{64})`$');if($M.Count-ne1){throw 'transport hash gate 5'};$P=Join-Path "$Design\tmp\task7-phase-b-contract-review-$Head" "transport-fence-5-$($M[0].Groups[1].Value).ps1";if((Get-FileHash $P -Algorithm SHA256).Hash.ToLowerInvariant()-cne$M[0].Groups[1].Value){throw 'transport fence 5 mismatch'};& $P;if(-not$?){throw 'pair Block 3 failed'}
```

- [ ] **Step 4 (2–5 min): Invoke transport fence 6 for pair Block 4**

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';Set-Location -LiteralPath $Design
$Active=[IO.File]::ReadAllText('D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md',[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$M=[regex]::Matches($Active,'(?m)^- production_uhf_phase_b_transport_fence_6_sha256: `([0-9a-f]{64})`$');if($M.Count-ne1){throw 'transport hash gate 6'};$P=Join-Path "$Design\tmp\task7-phase-b-contract-review-$Head" "transport-fence-6-$($M[0].Groups[1].Value).ps1";if((Get-FileHash $P -Algorithm SHA256).Hash.ToLowerInvariant()-cne$M[0].Groups[1].Value){throw 'transport fence 6 mismatch'};& $P;if(-not$?){throw 'pair Block 4 failed'}
```

- [ ] **Step 5 (2–5 min): Verify the object manifest and enter no-poll waiting**

```powershell
$ErrorActionPreference='Stop';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Integration;$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value
$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$Head";$Manifest=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-runs.json')))|ConvertFrom-Json);$Entries=@($Manifest.entries)
if($Manifest.purpose-cne'production-uhf-pair'-or$Manifest.head-cne$Head-or$Entries.Count-ne2-or$Entries[0].platform-cne'windows-latest'-or$Entries[1].platform-cne'ubuntu-latest'){throw 'pair manifest object/entries mismatch'}
foreach($Name in @('production-uhf-launch-ready.json','production-uhf-heartbeat-handoff.json')){if(-not(Test-Path -LiteralPath (Join-Path $Root $Name) -PathType Leaf)){throw "missing $Name"}}
$Ready=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-launch-ready.json')))|ConvertFrom-Json);$Handoff=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-heartbeat-handoff.json')))|ConvertFrom-Json);if($Ready.head-cne$Head-or$Handoff.head-cne$Head-or$Ready.windows_run_id-ne$Entries[0].run_id-or$Ready.linux_run_id-ne$Entries[1].run_id-or@($Handoff.run_ids).Count-ne2-or$Handoff.run_ids[0]-ne$Entries[0].run_id-or$Handoff.run_ids[1]-ne$Entries[1].run_id-or$Handoff.goal_status-cne'paused'-or$Handoff.supervisor_pid-lt1-or$Handoff.heartbeat_pid-lt1){throw 'launch-ready/supervisor handoff exact identity mismatch'}
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

First use the approved App Server Goal bridge to read the current task Goal; require exact `active`, then use `apply_patch` to add exactly one literal line `- production_uhf_pair_terminal_goal: active` to the active document. Run this complete fresh shell to bind the supervisor handoff to its terminal marker and consume the persisted original-handle proof:

```powershell
$ErrorActionPreference='Stop';$Integration='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Integration
$Utf8=[Text.UTF8Encoding]::new($false,$true);$Active=[IO.File]::ReadAllText($ActiveDoc,$Utf8);$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$Head";$HP=Join-Path $Root 'production-uhf-heartbeat-handoff.json';$TP=Join-Path $Root 'production-uhf-heartbeat-terminal.json';$Handoff=($Utf8.GetString([IO.File]::ReadAllBytes($HP))|ConvertFrom-Json);$Terminal=($Utf8.GetString([IO.File]::ReadAllBytes($TP))|ConvertFrom-Json);$HSha=(Get-FileHash $HP -Algorithm SHA256).Hash.ToLowerInvariant()
if($Handoff.head-cne$Head-or$Terminal.head-cne$Head-or$Terminal.handoff_path-cne$HP-or$Terminal.handoff_sha256-cne$HSha-or$Terminal.supervisor_pid-ne$Handoff.supervisor_pid-or$Terminal.supervisor_start_utc-cne$Handoff.supervisor_start_utc-or$Terminal.supervisor_executable-cne$Handoff.supervisor_executable-or$Terminal.heartbeat_pid-ne$Handoff.heartbeat_pid-or$Terminal.heartbeat_start_utc-cne$Handoff.heartbeat_start_utc-or$Terminal.encoded_command_sha256-cne$Handoff.encoded_command_sha256-or$Terminal.wait_completed-ne$true-or$Terminal.direct_handle_has_exited-ne$true-or$Terminal.heartbeat_exit_code-ne0-or$Terminal.cim_count-ne0-or$Terminal.goal_status-cne'active'-or$Terminal.terminal_status-cne'PASS'){throw 'pair original-handle terminal proof mismatch'}
for($I=0;$I-lt20-and@(Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$Terminal.supervisor_pid)" -ErrorAction Stop).Count-ne0;$I++){Start-Sleep -Milliseconds 250};if(@(Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$Terminal.supervisor_pid)" -ErrorAction Stop).Count-ne0){throw 'pair supervisor remains'};if([regex]::Matches($Active,'(?m)^- production_uhf_pair_terminal_goal: active$').Count-ne1){throw 'independent Goal active gate missing'}
[pscustomobject]@{heartbeat_pid=[int]$Terminal.heartbeat_pid;direct_handle_has_exited=$true;heartbeat_cim_count=0;supervisor_cim_count=0;goal='active';head=$Head;terminal_sha256=(Get-FileHash $TP -Algorithm SHA256).Hash.ToLowerInvariant()}|ConvertTo-Json -Compress
```

Then run the single fresh-shell archive/validation command in Step 2; it defines every later variable itself.

- [ ] **Step 2 (2–5 min): Run the fixed Windows-to-Linux archive loop**

```powershell
$ErrorActionPreference='Stop';$Repo='psiQAQ/pyscf';$Branch='codex/test/sgx-extra-cycle-convergence-validation';$Worktree='D:\workspace\pyscf\.worktrees\sgx-extra-cycle-integration';Set-Location -LiteralPath $Worktree
$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Active=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Active,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;$Root="D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-$Head"
$ManifestObject=((New-Object Text.UTF8Encoding($false,$true)).GetString([IO.File]::ReadAllBytes((Join-Path $Root 'production-uhf-runs.json')))|ConvertFrom-Json);$Entries=@($ManifestObject.entries)
if($ManifestObject.head-cne$Head-or$Entries.Count-ne2-or$Entries[0].platform-cne'windows-latest'-or$Entries[1].platform-cne'ubuntu-latest'){throw 'manifest .entries order mismatch'}
$ValidatorSource='D:\workspace\pyscf\.agents\active\precision-ci\scripts\validate_precision_production.py';$ValidatorSha='d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c';if((Get-FileHash $ValidatorSource -Algorithm SHA256).Hash.ToLowerInvariant()-cne$ValidatorSha){throw 'validator hash mismatch'}
$Results=@();$Utf8=[Text.UTF8Encoding]::new($false);$Strict=[Text.UTF8Encoding]::new($false,$true);function Read-J([string]$P){$Strict.GetString([IO.File]::ReadAllBytes($P))|ConvertFrom-Json};function Write-New([string]$P,[object]$O){$B=$Utf8.GetBytes(($O|ConvertTo-Json -Depth 9 -Compress)+"`n");$S=[IO.File]::Open($P,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$S.Write($B,0,$B.Length);$S.Flush($true)}finally{$S.Dispose()};Read-J $P}
for($Index=0;$Index-lt2;$Index++){
  $Entry=$Entries[$Index];$RunId=[long]$Entry.run_id;$IsWindows=$Index-eq0;$ExpectedPlatform=if($IsWindows){'windows-latest'}else{'ubuntu-latest'};$ExpectedArtifact=if($IsWindows){'precision-Windows-py3.12'}else{'precision-Linux-py3.12'};$Mode=if($IsWindows){'installed-wheel'}else{'source-tree'};$Native=if($IsWindows){26}else{16};$Suffix=if($IsWindows){'production-uhf-windows-py312'}else{'production-uhf-linux-py312'}
  if($Entry.platform-cne$ExpectedPlatform-or$Entry.artifact-cne$ExpectedArtifact-or$Entry.repeats-ne20-or$Entry.python-cne'3.12'-or$Entry.profile-cne'4/4'-or$Entry.head-cne$Head){throw "manifest entry mismatch index=$Index"}
  $Raw=@(gh run view $RunId --repo $Repo --json databaseId,attempt,event,workflowName,headSha,headBranch,status,conclusion,jobs,url);if($LASTEXITCODE-ne0){throw "run view failed $RunId"};$Run=ConvertFrom-Json($Raw-join"`n");$ARaw=@(gh api "repos/$Repo/actions/runs/$RunId/artifacts?per_page=100");if($LASTEXITCODE-ne0){throw "artifact query failed $RunId"};$Arts=@((ConvertFrom-Json($ARaw-join"`n")).artifacts);$Jobs=@($Run.jobs|Where-Object{$_.name-ceq'precision'});$Exact=@($Arts|Where-Object{$_.name-ceq$ExpectedArtifact-and-not$_.expired})
  if($Run.databaseId-ne$RunId-or$Run.attempt-ne1-or$Run.event-cne'workflow_dispatch'-or$Run.workflowName-cne'Precision investigation'-or$Run.headSha-cne$Head-or$Run.headBranch-cne$Branch-or$Run.status-cne'completed'-or$Run.conclusion-cne'success'-or$Jobs.Count-ne1-or$Jobs[0].conclusion-cne'success'-or$Exact.Count-ne1-or$Arts.Count-ne1){throw "terminal identity mismatch $RunId"};$Artifact=$Exact[0]
  $Archive="D:\workspace\pyscf\.agents\archive\precision-ci\experiments\$RunId-$Suffix";[void][IO.Directory]::CreateDirectory($Archive);$Identity=[ordered]@{purpose='production-uhf-archive';head=$Head;run_id=$RunId;platform=$ExpectedPlatform;artifact_id=[long]$Artifact.id;artifact_name=[string]$Artifact.name;artifact_digest=[string]$Artifact.digest;artifact_size=[long]$Artifact.size_in_bytes;branch=$Branch;validator_sha256=$ValidatorSha};$IP=Join-Path $Archive 'archive-identity.json';if(Test-Path $IP){$IR=Read-J $IP}else{$IR=Write-New $IP $Identity};if(($IR|ConvertTo-Json -Depth 9 -Compress)-cne($Identity|ConvertTo-Json -Depth 9 -Compress)){throw "archive identity mismatch $RunId"};$CP=Join-Path $Archive 'archive-complete.json';if(Test-Path $CP){$C=Read-J $CP;$CA=[string]$C.attempt_dir;$CRP=Join-Path $CA 'production-validation.json';$CRun=Join-Path $CA 'run.json';$CV=Join-Path $CA 'validate_precision_production.py';if($C.head-cne$Head-or$C.run_id-ne$RunId-or$C.platform-cne$ExpectedPlatform-or$C.artifact_id-ne[long]$Artifact.id-or$C.tested_sha-cne$Head-or$C.verdict-cne'PASS'-or$C.native_count-ne$Native-or$C.identity_sha256-cne(Get-FileHash $IP -Algorithm SHA256).Hash.ToLowerInvariant()-or-not(Test-Path $CRP -PathType Leaf)-or(Get-FileHash $CRP -Algorithm SHA256).Hash.ToLowerInvariant()-cne$C.report_sha256-or(Get-FileHash $CRun -Algorithm SHA256).Hash.ToLowerInvariant()-cne$C.run_sha256-or(Get-FileHash $CV -Algorithm SHA256).Hash.ToLowerInvariant()-cne$C.validator_sha256-or(-not$IsWindows-and$C.runner_exit_sha256-cne'9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa')){throw "archive completion mismatch $RunId"};$Results+=[pscustomobject]@{platform=$ExpectedPlatform;run_id=$RunId;artifact_id=[long]$Artifact.id;archive=$Archive;attempt_dir=$CA;report_sha256=[string]$C.report_sha256;tested_sha=$Head;runner_exit_sha256=[string]$C.runner_exit_sha256;valid=$true;verdict='PASS';native_count=$Native;disposition='recovered-complete'};continue};$Nums=@(Get-ChildItem -LiteralPath $Archive -Directory -Filter 'attempt-*'|ForEach-Object{if($_.Name-match'^attempt-([0-9]{4})$'){[int]$Matches[1]}});$Next=if($Nums.Count){([Linq.Enumerable]::Max([int[]]$Nums))+1}else{1};$AttemptDir=Join-Path $Archive ('attempt-{0:d4}'-f$Next);[void][IO.Directory]::CreateDirectory($AttemptDir);gh run download $RunId --repo $Repo --name $ExpectedArtifact --dir $AttemptDir;if($LASTEXITCODE-ne0){throw "download failed; retain same-run attempt $RunId"}
  $RunObject=[ordered]@{databaseId=$RunId;attempt=1;event='workflow_dispatch';workflowName='Precision investigation';headSha=$Head;headBranch=$Branch;status='completed';conclusion='success';jobs=@([ordered]@{databaseId=[long]$Jobs[0].databaseId;name='precision';status='completed';conclusion='success'});artifacts=@([ordered]@{id=[long]$Artifact.id;name=[string]$Artifact.name;digest=[string]$Artifact.digest;sizeInBytes=[long]$Artifact.size_in_bytes;expired=[bool]$Artifact.expired})};$RB=$Utf8.GetBytes(($RunObject|ConvertTo-Json -Depth 6 -Compress)+"`n");$RunPath=Join-Path $AttemptDir 'run.json';$RS=[IO.File]::Open($RunPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$RS.Write($RB,0,$RB.Length);$RS.Flush($true)}finally{$RS.Dispose()};$RunRead=Read-J $RunPath;if(($RunRead|ConvertTo-Json -Depth 6 -Compress)-cne($RunObject|ConvertTo-Json -Depth 6 -Compress)){throw "run.json exact readback mismatch $RunId"}
  $VB=[IO.File]::ReadAllBytes($ValidatorSource);$VP=Join-Path $AttemptDir 'validate_precision_production.py';$VS=[IO.File]::Open($VP,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None);try{$VS.Write($VB,0,$VB.Length);$VS.Flush($true)}finally{$VS.Dispose()};if((Get-FileHash $VP -Algorithm SHA256).Hash.ToLowerInvariant()-cne$ValidatorSha){throw 'archive validator mismatch'}
  $ExitSha=$null;if(-not$IsWindows){$EP=Join-Path $AttemptDir 'runner-exit-code.txt';$EB=[IO.File]::ReadAllBytes($EP);if(-not[Linq.Enumerable]::SequenceEqual([byte[]]$EB,[byte[]]@(0x30,0x0A))){throw 'Linux runner exit bytes mismatch'};$ExitSha=(Get-FileHash $EP -Algorithm SHA256).Hash.ToLowerInvariant();if($ExitSha-cne'9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa'){throw 'Linux runner exit SHA mismatch'}}
  $Report=Join-Path $AttemptDir 'production-validation.json';if(Test-Path $Report){throw "new attempt report exists $RunId"};conda run --no-capture-output -n pyscf-win313-test python $VP $AttemptDir --mode $Mode --expected-sha $Head --expected-nodeids-file (Join-Path $Worktree '.github\workflows\precision-uhf-smearing-extra-cycle-nodeids.txt') --expected-profile omp4-blas4 --expected-repeats 20 --expected-platform $ExpectedPlatform --expected-python 3.12 --expected-native-count $Native --run-metadata $RunPath --expected-run-id $RunId --expected-branch $Branch --expected-artifact-name $ExpectedArtifact --report $Report;if($LASTEXITCODE-ne0){throw "validator failed; retain same-run attempt $RunId"};$Before=[IO.File]::ReadAllBytes($Report);$FS=[IO.File]::Open($Report,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None);try{$FS.Flush($true)}finally{$FS.Dispose()};$After=[IO.File]::ReadAllBytes($Report);if(-not[Linq.Enumerable]::SequenceEqual([byte[]]$Before,[byte[]]$After)){throw "report durability changed bytes $RunId"};$V=Read-J $Report;if($V.valid-ne$true-or$V.verdict-cne'PASS'-or$V.tested_sha-cne$Head-or$V.records-ne20-or$V.pass-ne20-or$V.fail-ne0-or$V.profile-cne'omp4-blas4'){throw "report not same-EvidenceHead 20/20 PASS $RunId"};$ReportSha=(Get-FileHash $Report -Algorithm SHA256).Hash.ToLowerInvariant()
  $Complete=[ordered]@{purpose='production-uhf-archive-complete';head=$Head;run_id=$RunId;platform=$ExpectedPlatform;artifact_id=[long]$Artifact.id;artifact_name=$ExpectedArtifact;attempt_dir=$AttemptDir;identity_sha256=(Get-FileHash $IP -Algorithm SHA256).Hash.ToLowerInvariant();run_sha256=(Get-FileHash $RunPath -Algorithm SHA256).Hash.ToLowerInvariant();validator_sha256=$ValidatorSha;report_sha256=$ReportSha;runner_exit_sha256=$ExitSha;tested_sha=$Head;verdict='PASS';native_count=$Native};$CR=Write-New $CP $Complete;if(($CR|ConvertTo-Json -Depth 9 -Compress)-cne($Complete|ConvertTo-Json -Depth 9 -Compress)){throw "completion readback mismatch $RunId"};$Results+=[pscustomobject]@{platform=$ExpectedPlatform;run_id=$RunId;artifact_id=[long]$Artifact.id;archive=$Archive;attempt_dir=$AttemptDir;report_sha256=$ReportSha;tested_sha=$Head;runner_exit_sha256=$ExitSha;valid=$true;verdict='PASS';native_count=$Native;disposition='completed'}
}
if($Results.Count-ne2-or$Results[0].platform-cne'windows-latest'-or$Results[1].platform-cne'ubuntu-latest'-or$Results[0].tested_sha-cne$Head-or$Results[1].tested_sha-cne$Head-or$Results[1].runner_exit_sha256-cne'9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa'){throw 'fixed archive loop result mismatch'};$Lines=@("- production_uhf_windows_run_id: ``$($Results[0].run_id)``","- production_uhf_windows_artifact_id: ``$($Results[0].artifact_id)``","- production_uhf_windows_report_sha256: ``$($Results[0].report_sha256)``","- production_uhf_windows_tested_sha: ``$Head``","- production_uhf_linux_run_id: ``$($Results[1].run_id)``","- production_uhf_linux_artifact_id: ``$($Results[1].artifact_id)``","- production_uhf_linux_report_sha256: ``$($Results[1].report_sha256)``","- production_uhf_linux_runner_exit_sha256: ``$($Results[1].runner_exit_sha256)``","- production_uhf_linux_tested_sha: ``$Head``",'- production_unix_exit_evidence_terminal_status: `PASS`');[pscustomobject]@{results=$Results;active_lines=$Lines}|ConvertTo-Json -Depth 6
```

- [ ] **Step 3 (2–5 min): Freeze the exact two-report conjunction**

Copy the prior command's ten `active_lines` byte-for-byte into one `apply_patch` update. Any command failure retains incomplete attempts without a completion marker and records `STOP`; rerunning resumes the same frozen run IDs, reuses any exact completion, never redispatches, and does not unlock Task 7. Run this complete fresh-shell readback:

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HM=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HM.Count-ne1){throw 'EvidenceHead unavailable'};$Head=$HM[0].Groups[1].Value;foreach($P in @('(?m)^- production_uhf_windows_run_id: `[0-9]+`$','(?m)^- production_uhf_windows_artifact_id: `[0-9]+`$','(?m)^- production_uhf_windows_report_sha256: `[0-9a-f]{64}`$','(?m)^- production_uhf_windows_tested_sha: `'+$Head+'`$','(?m)^- production_uhf_linux_run_id: `[0-9]+`$','(?m)^- production_uhf_linux_artifact_id: `[0-9]+`$','(?m)^- production_uhf_linux_report_sha256: `[0-9a-f]{64}`$','(?m)^- production_uhf_linux_runner_exit_sha256: `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`$','(?m)^- production_uhf_linux_tested_sha: `'+$Head+'`$','(?m)^- production_unix_exit_evidence_terminal_status: `PASS`$')){if([regex]::Matches($Text,$P).Count-ne1){throw "pair active evidence mismatch: $P"}}
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

Run this fresh shell to render the exact terminal evidence lines from the already read-back active keys. Copy its `report_lines` byte-for-byte in one `apply_patch` update to the ignored Task 7 report; do not alter historical Windows `PASS` or Linux `INVALID` entries. Then rerun the command with `$ReportUpdated=$true` to require each line exactly once.

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';$Report='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation\.superpowers\sdd\2026-08-11-sgx-extra-cycle-convergence-production\task-7-report.md';$ReportUpdated=$false;Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));function One([string]$Pattern){$M=[regex]::Matches($Text,$Pattern);if($M.Count-ne1){throw "active key mismatch: $Pattern"};$M[0].Groups[1].Value};$Head=One '(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$';$WR=One '(?m)^- production_unix_wrapper_witness_run_id: `([0-9]+)`$';$WA=One '(?m)^- production_unix_wrapper_witness_artifact_id: `([0-9]+)`$';$WH=One '(?m)^- production_unix_wrapper_witness_report_sha256: `([0-9a-f]{64})`$';$WW=One '(?m)^- production_uhf_windows_run_id: `([0-9]+)`$';$WHA=One '(?m)^- production_uhf_windows_artifact_id: `([0-9]+)`$';$WHP=One '(?m)^- production_uhf_windows_report_sha256: `([0-9a-f]{64})`$';$LR=One '(?m)^- production_uhf_linux_run_id: `([0-9]+)`$';$LA=One '(?m)^- production_uhf_linux_artifact_id: `([0-9]+)`$';$LH=One '(?m)^- production_uhf_linux_report_sha256: `([0-9a-f]{64})`$';$LE=One '(?m)^- production_uhf_linux_runner_exit_sha256: `([0-9a-f]{64})`$';$Lines=@("- macOS wrapper witness: run ``$WR``, artifact ``$WA``, report SHA-256 ``$WH``, tested SHA ``$Head``, strict PASS; transport/provenance only.","- Windows paired evidence: run ``$WW``, artifact ``$WHA``, report SHA-256 ``$WHP``, tested SHA ``$Head``, strict PASS.","- Linux paired evidence: run ``$LR``, artifact ``$LA``, report SHA-256 ``$LH``, runner-exit SHA-256 ``$LE``, tested SHA ``$Head``, strict PASS.");if($ReportUpdated){$RT=[IO.File]::ReadAllText($Report,[Text.UTF8Encoding]::new($false,$true));foreach($L in $Lines){if([regex]::Matches($RT,'(?m)^'+[regex]::Escape($L)+'$').Count-ne1){throw "report line mismatch: $L"}}};[pscustomobject]@{report_lines=$Lines;verified=$ReportUpdated}|ConvertTo-Json -Depth 4
```

- [ ] **Step 2 (2–5 min): Freeze and verify the recovery key**

Use `apply_patch` to set exactly one `production_unix_exit_evidence_next_step` line to `Task 7 Step 3 only; independently review the three production commits and stacked integration using the new macOS transport witness plus same-SHA Windows/Linux frozen-validator PASS reports; do not redispatch, start Task 8, or update pyscf/pyscf#3312`. Run this complete fresh-shell readback:

```powershell
$ErrorActionPreference='Stop';$Design='D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$ActiveDoc='D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md';Set-Location -LiteralPath $Design
$Text=[IO.File]::ReadAllText($ActiveDoc,[Text.UTF8Encoding]::new($false,$true));$HeadMatch=[regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_head: `([0-9a-f]{40})`$');if($HeadMatch.Count-ne1){throw 'EvidenceHead cardinality mismatch'};$Head=$HeadMatch[0].Groups[1].Value
$Next='- production_unix_exit_evidence_next_step: `Task 7 Step 3 only; independently review the three production commits and stacked integration using the new macOS transport witness plus same-SHA Windows/Linux frozen-validator PASS reports; do not redispatch, start Task 8, or update pyscf/pyscf#3312`';if([regex]::Matches($Text,'(?m)^'+[regex]::Escape($Next)+'$').Count-ne1){throw 'recovery key mismatch'};if([regex]::Matches($Text,'(?m)^- production_unix_exit_evidence_terminal_status: `PASS`$').Count-ne1){throw 'terminal PASS mismatch'}
$Tested=@([regex]::Matches($Text,'(?m)^- production_(?:unix_wrapper_witness|uhf_windows|uhf_linux)_tested_sha: `([0-9a-f]{40})`$')|ForEach-Object{$_.Groups[1].Value});if($Tested.Count-ne3-or@($Tested|Where-Object{$_-cne$Head}).Count-ne0){throw 'three tested_sha values do not equal EvidenceHead'};if([regex]::Matches($Text,'(?m)^- production_unix_wrapper_witness_claim: `transport/provenance only; repeats=1 is not scientific stability`$').Count-ne1-or[regex]::Matches($Text,'(?m)^- production_(?:unix_wrapper_witness|uhf_linux)_runner_exit_sha256: `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`$').Count-ne2){throw 'claim or runner-exit evidence mismatch'};'TASK 7 STEP 3 RECOVERY READY'
```

## Plan Self-Review Checklist

Before approval, run both harmless probes. They do not read or write production state, call GitHub, or touch Goal state.

```powershell
$ErrorActionPreference='Stop';Set-Location -LiteralPath 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation'
function Decide([object]$Expected,[object]$Identity,[object]$Complete){if($null-eq$Identity){return 'initialize'};if(($Identity|ConvertTo-Json -Compress)-cne($Expected|ConvertTo-Json -Compress)){throw 'identity mismatch'};if($null-eq$Complete){return 'resume'};if($Complete.identity-cne$Expected.identity-or$Complete.verdict-cne'PASS'){throw 'completion mismatch'};'complete'}
$Expected=[ordered]@{identity='run-101-artifact-201'};if((Decide $Expected $null $null)-cne'initialize'){throw 'initial RED'};if((Decide $Expected $Expected $null)-cne'resume'){throw 'partial RED'};if((Decide $Expected $Expected ([ordered]@{identity=$Expected.identity;verdict='PASS'}))-cne'complete'){throw 'complete RED'}
$Caught=0;try{[void](Decide $Expected ([ordered]@{identity='unknown'}) $null)}catch{$Caught++};try{[void](Decide $Expected $Expected ([ordered]@{identity='unknown';verdict='PASS'}))}catch{$Caught++};if($Caught-ne2){throw 'mismatch fail-closed RED'}
$Order=@('windows','linux');$State=@{windows=[ordered]@{identity='win';verdict='PASS'};linux=$null};$Actions=@();foreach($P in $Order){$E=[ordered]@{identity=if($P-ceq'windows'){'win'}else{'linux'}};$I=if($P-ceq'windows'){$E}else{$E};$D=Decide $E $I $State[$P];$Actions+="$P`:$D"};if(($Actions-join',')-cne'windows:complete,linux:resume'){throw 'Windows-complete/Linux-partial continuation RED'}
[pscustomobject]@{initial='initialize';partial='resume';mismatch_failures=$Caught;fixed_order=$Actions}|ConvertTo-Json -Compress
```

```powershell
$ErrorActionPreference='Stop';Set-Location -LiteralPath 'D:\workspace\pyscf\.worktrees\libxc-712-release-revalidation';$PowerShellExe='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe';$P=Start-Process -FilePath $PowerShellExe -WindowStyle Hidden -PassThru -ArgumentList @('-NoProfile','-Command','exit 0');$Id=[int]$P.Id;$Start=$P.StartTime.ToUniversalTime().ToString('o');if(-not$P.WaitForExit(30000)){throw 'harmless direct-child timeout'};$P.Refresh();for($I=0;$I-lt20-and@(Get-CimInstance Win32_Process -Filter "ProcessId=$Id" -ErrorAction Stop).Count-ne0;$I++){Start-Sleep -Milliseconds 250};$Cim=@(Get-CimInstance Win32_Process -Filter "ProcessId=$Id" -ErrorAction Stop);$Proof=[ordered]@{same_process_handle=$true;pid=$Id;start_utc=$Start;wait_completed=$true;direct_handle_has_exited=[bool]$P.HasExited;exit_code=[int]$P.ExitCode;cim_count=$Cim.Count};$P.Dispose();if(-not$Proof.direct_handle_has_exited-or$Proof.exit_code-ne0-or$Proof.cim_count-ne0){throw 'original direct-handle harmless proof failed'};$Proof|ConvertTo-Json -Compress
```

- [ ] Every approved-spec requirement maps to Task 1 implementation proof, Task 2 authenticated publication, Task 3 mechanical derivation, Task 4 macOS witness, Task 5 pair execution, Task 6 strict pair acceptance, or Task 7 recovery.
- [ ] The plan contains one Bash implementation snippet, four behavior-test methods, one `resolve_bash`, and one mechanical rebind helper; no alternative implementation remains.
- [ ] All paths are absolute where host identity matters and repository-relative where MSYS argv conversion matters; post-push identities derive only from the authenticated 40-hex active-document `EvidenceHead`.
- [ ] Every `gh`, `git`, `conda`, and Bash native command that affects a gate has an immediate exit check.
- [ ] The derived addendum has exactly five PowerShell fences and the derived transport has exactly six; every fence has Windows PowerShell 5.1 AST errors `0` before approval.
- [ ] Task 3 runs only materialization, the supervisor's harmless `-SelfTest`, and the harmless 19-case fence; Task 4 owns the non-overlapping macOS witness heartbeat; Task 5 starts the pair heartbeat only after witness child-gone/Goal `active` and invokes pair ordinals 1–4 in four fresh `shell_command` processes.
- [ ] The old addendum, transport, state, archives, runs, and artifacts remain immutable; no replay, force push, second poller, early Step 3, Task 8, or issue `#3312` update is permitted.
- [ ] The archive recovery probe returns `windows:complete,linux:resume`; validator reports pass byte-preserving `Flush(true)` durability before any completion marker; all completion readbacks rehash their identity, run, validator, and report files.
- [ ] The direct-handle harmless probe and supervisor `-SelfTest` prove `WaitForExit` plus `Refresh` plus original-handle `HasExited`, exit code, and CIM disappearance without a GitHub query or Goal mutation.
