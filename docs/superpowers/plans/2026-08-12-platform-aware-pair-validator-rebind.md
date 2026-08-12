# Platform-aware pair validator rebind implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mechanically derive and review a Windows/Linux pair contract bound to
the approved platform-aware production validator, then start exactly one
20-repeat pair and hand its two run IDs to the existing direct-handle heartbeat.

**Architecture:** Treat the already reviewed execution-r1 addendum and
transport as immutable inputs. A standard-library Python helper performs only
counted byte replacements: four old validator hashes in the addendum, then the
addendum filename/hash and five fence hashes in the transport. Production
dispatch remains inside the derived, hash-bound PowerShell fences; no command
is copied or re-authored by hand.

**Tech Stack:** Python 3.13 standard library, Windows PowerShell 5.1, SHA-256,
GitHub CLI, existing direct-handle supervisor and Goal bridge.

## Global Constraints

- Evidence head is exactly `2a2237bc323b8473d19979aaa56a0e8ff88cee04`.
- Old validator SHA-256 is exactly
  `d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c`;
  new reviewed SHA-256 is exactly
  `3c0afb898b7b051096fe4dae33fce3a33e2c3a6974f628e0e102512039be1e35`.
- Immutable execution-r1 addendum SHA-256 is
  `b11afae6bf6c729cbd18a300944479b67d16126b85d001a288bd1e830df87bd4`;
  immutable execution-r1 transport SHA-256 is
  `c32cba464c4d21658f82cc81a4d24a027e9cf8a8b1a93f62d1eaeef741d78ee6`.
- The macOS witness gate must remain plain `PASS`, exact artifact
  `9133834443`, tested SHA equal to EvidenceHead, and explicitly
  transport/provenance only.
- Never modify the execution-r1 addendum/transport, attempt-0001,
  attempt-0002, old pair state, scientific source, nodeids, workflow,
  dependencies, remotes, PRs, issues, or the 26 untracked DLL fixtures.
- Do not execute a production fence until the derived files receive independent
  `Execution Contract: APPROVED` and `Transport Contract: APPROVED` verdicts.
- Pair inputs remain Windows `windows-latest`/Python `3.12`/`4/4`/20 and Linux
  `ubuntu-latest`/Python `3.12`/`4/4`/20, exact UHF singleton nodeid.
- After the unique heartbeat owns both IDs and Goal is exactly `paused`, stop
  all manual GitHub polling. A later terminal acceptance must use the new
  validator; the old Task-6 acceptance command is forbidden.

---

### Task 1: TDD the counted byte rebind helper

**Files:**
- Create ignored: `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/derive-platform-aware-pair-r2.py`
- Create ignored: `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/test-derive-platform-aware-pair-r2.py`
- Create ignored: `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-policy-correction-2a2237bc323b8473d19979aaa56a0e8ff88cee04-execution-r2-validator-3c0afb898b7b051096fe4dae33fce3a33e2c3a6974f628e0e102512039be1e35.md`
- Create ignored: `.superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/task-7-phase-b-transport-execution-2a2237bc323b8473d19979aaa56a0e8ff88cee04-execution-r2-validator-3c0afb898b7b051096fe4dae33fce3a33e2c3a6974f628e0e102512039be1e35.md`

**Interfaces:**
- Consumes: two exact immutable r1 documents and the old/new validator hashes.
- Produces: `derive_bytes(addendum: bytes, transport: bytes) -> dict[str, object]`
  plus CreateNew-or-existing-exact CLI output as `key=value` lines.

- [ ] **Step 1: Write the missing-helper RED test**

Create a `unittest` that loads `derive-platform-aware-pair-r2.py` by path and
asserts all of these values from `derive_bytes`:

```python
self.assertEqual(result['old_validator_count'], 4)
self.assertEqual(result['old_addendum_name_count'], 7)
self.assertEqual(result['old_addendum_sha_count'], 7)
self.assertEqual(result['old_fence_hash_counts'], [4, 4, 4, 4, 4])
self.assertEqual(result['addendum_old_validator_remaining'], 0)
self.assertEqual(result['addendum_new_validator_count'], 4)
self.assertEqual(result['addendum_fence_count'], 5)
self.assertEqual(result['transport_fence_count'], 6)
```

It must also assert strict UTF-8/no-BOM/LF/final-LF, output filenames, and that
the addendum byte diff consists only of the four 64-byte hash replacements.

- [ ] **Step 2: Run the RED**

Run:

```powershell
conda run --no-capture-output -n pyscf-win313-test python `
  .superpowers/sdd/2026-08-11-sgx-extra-cycle-convergence-production/test-derive-platform-aware-pair-r2.py
```

Expected: exit `1`, with the helper path missing; no target file is created.

- [ ] **Step 3: Implement the minimal helper**

Use only `hashlib`, `pathlib`, `re`, `sys`, and `os`. Define these exact
operations:

```python
def replace_exact(data: bytes, old: bytes, new: bytes, count: int) -> bytes:
    if data.count(old) != count:
        raise RuntimeError(f'replacement count mismatch: {data.count(old)} != {count}')
    return data.replace(old, new)

def strict(data: bytes) -> None:
    data.decode('utf-8', errors='strict')
    if data.startswith(b'\xef\xbb\xbf') or b'\r' in data or not data.endswith(b'\n'):
        raise RuntimeError('encoding/EOL mismatch')

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def write_new_or_exact(path: pathlib.Path, data: bytes) -> str:
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        if path.read_bytes() != data:
            raise RuntimeError(f'existing output differs: {path}')
        return 'existing-exact'
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return 'created'
```

`derive_bytes` must verify source hashes, replace exactly four validator hashes,
extract exactly five PowerShell fences with
`rb'(?ms)^```powershell\n(.*?)^```$'`, then replace in the transport exactly
seven addendum filenames, seven addendum hashes, and four occurrences of each
old fence hash. It must extract exactly six new transport fences and return all
document/fence hashes and replacement counts. The CLI writes only the two new
named documents and prints deterministic `key=value` lines.

- [ ] **Step 4: Run GREEN twice and static checks**

Run the test, then the helper twice. Require the test to pass, first helper
dispositions `created`, second dispositions `existing-exact`, Python AST clean,
all seven documents/helpers strict UTF-8/no-BOM/LF/final-LF, and zero GitHub,
Goal, heartbeat, archive, active-document, or Git writes.

---

### Task 2: Materialize, harmlessly test, and independently review r2

**Files:**
- Create ignored content-addressed PowerShell files under
  `tmp/task7-phase-b-contract-review-2a2237bc323b8473d19979aaa56a0e8ff88cee04/`
- Create ignored: `.superpowers/sdd/2026-08-12-platform-aware-libxc-linkage-validator/pair-r2-execution-review.md`
- Create ignored: `.superpowers/sdd/2026-08-12-platform-aware-libxc-linkage-validator/pair-r2-transport-review.md`

**Interfaces:**
- Consumes: Task 1's exact document and 5+6 fence hashes.
- Produces: content-addressed fence files, harmless self-test output, and two
  exact independent approvals.

- [ ] **Step 1: Parse and materialize all fences**

In a fresh PowerShell shell, strict-read the r2 addendum and transport, extract
exactly 5 and 6 fences, require every fence to parse with Windows PowerShell
5.1 AST errors `0`, and write each with CreateNew-or-existing-exact semantics to
`addendum-r2-fence-N-$sha.ps1` and `transport-r2-fence-N-$sha.ps1`.

- [ ] **Step 2: Run only harmless transport fences 1 and 2**

Invoke r2 transport fence 1 twice; require its five addendum outputs first
to report ordinals 1–4 as `created` and the byte-identical ordinal 5 as
`existing-exact` (or `existing-exact-after-create-race`); the second invocation
must report all five as existing-exact. Invoke only r2 transport fence 2 and
require `SELF-TEST PASS: 19 cases`. Assert pair state root absent, local
heartbeat poller count `0`, Goal unchanged, and the validation-branch historical
run-ID set remains exactly the five completed runs `31508338082`,
`31535193241`, `31548379750`, `31548408412`, and `31577510832`. Require the
exact-EvidenceHead run-ID set to contain only `31577510832` and require zero
active run.

- [ ] **Step 3: Obtain independent dual review**

The execution reviewer verifies that the only semantic change is four exact
validator-hash replacements and that Windows/Linux provenance remains strict.
The transport reviewer verifies the exact filename/hash/fence-hash replacement
counts and content-addressed invocation. Require exactly:

```text
Execution Contract: APPROVED
Transport Contract: APPROVED
```

Any finding returns to Task 1 with a new RED; production remains forbidden.

---

### Task 3: Freeze r2 in active state and run the four-block pair

**Files:**
- Modify once: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`
- Create only through reviewed blocks:
  `D:\workspace\pyscf\.agents\active\precision-ci\task-7-phase-b-2a2237bc323b8473d19979aaa56a0e8ff88cee04\**`

**Interfaces:**
- Consumes: Task 2 approvals and exact r2 document/fence hashes.
- Produces: one Windows run, one Linux run, one two-entry manifest, one
  launch-ready/handoff pair, one supervisor, one heartbeat, and Goal paused.

- [ ] **Step 1: Replace the 15 active r1 contract keys exactly once**

Use `apply_patch` to replace addendum path/hash, transport path/hash, five
addendum fence hashes, and six transport fence hashes. Preserve supervisor path,
supervisor hash, state root, EvidenceHead, macOS PASS keys, and all historical
r1 documents. Fresh readback requires each r2 value once and every r1 value zero
within those 15 current keys.

- [ ] **Step 2: Run the final live preflight**

Require local and remote validation branch heads equal EvidenceHead; both
worktrees have zero tracked/staged changes and exactly 26 known DLLs; macOS
witness terminal marker proves original handles gone and Goal active; witness
verdict is plain `PASS`; corrected validator and all r2 contract/fence hashes
match; pair state root is absent; heartbeat poller count is zero; no requested,
queued, in-progress, waiting, or pending exact-head pair run exists.

- [ ] **Step 3: Invoke production fences 3 through 6 in four fresh shells**

For ordinal `3`, `4`, `5`, then `6`, bind the exact active transport-fence hash,
locate `transport-r2-fence-$ordinal-$hash.ps1`, rehash it, parse it with
PowerShell 5.1 AST, and invoke it once. Stop on the first nonzero result; never
replay a successful ordinal.

- [ ] **Step 4: Freeze the handoff and pause**

After fence 6, require exactly two distinct bound run IDs in manifest order
Windows then Linux, one supervisor and one heartbeat, exact `1800` seconds and
`300` minutes, handoff Goal status `paused`, independent root Goal readback
`paused`, and durable active/report keys. From that point perform zero manual
GitHub polling.

---

### Task 4: Terminal recovery boundary

**Files:**
- Preserve all Task 3 state and CI evidence.
- Create a separate reviewed acceptance correction after terminal; do not use
  the old Task-6 command containing the old validator hash.

**Interfaces:**
- Consumes: unique heartbeat terminal marker and exact Goal `active`.
- Produces: a resumed task that can write and directly execute the terminal
  acceptance plan without another user approval.

- [ ] **Step 1: Wait only through the unique heartbeat**

The heartbeat queries exactly the two bound run IDs every 1800 seconds, wakes at
terminal or 300 minutes, reconciles Goal active, and exits. No other poller or
scheduled task may query the pair.

- [ ] **Step 2: On resume, write and execute the acceptance correction**

Bind the terminal marker to the original process handles and exact run IDs,
then derive a new terminal acceptance command using validator SHA
`3c0afb898b7b051096fe4dae33fce3a33e2c3a6974f628e0e102512039be1e35`.
Require Windows installed-wheel native count 26 and Linux source-tree native
count 16 plus runner-exit bytes `30 0A`. A valid scientific failure remains
evidence; only structurally valid plain `PASS` for both 20-repeat artifacts
unlocks the later production reviews.

## Verification checklist

- [ ] r1 documents and macOS attempt-0001/attempt-0002 hashes are unchanged.
- [ ] r2 derivation tests and helper repeated execution pass.
- [ ] New documents have 5+6 AST-clean PowerShell fences and exact counted diff.
- [ ] Independent execution and transport verdicts are both APPROVED.
- [ ] Active state contains only r2 current contract hashes.
- [ ] Fences 3-6 each run once in order; no duplicate dispatch or poller exists.
- [ ] Goal is paused only after durable two-run handoff.
- [ ] No old-validator terminal acceptance is executed.
