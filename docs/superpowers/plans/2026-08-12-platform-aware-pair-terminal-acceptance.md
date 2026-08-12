# Platform-aware pair terminal acceptance implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strictly archive and validate the completed Windows/Linux 20-repeat
pair with the approved platform-aware validator, without rerun or redispatch.

**Architecture:** One ignored Windows PowerShell 5.1 script consumes the
immutable manifest and direct-handle terminal marker. It queries each exact run
and sole artifact, creates one immutable archive attempt, runs the already
reviewed validator, adds only platform-specific exit/provenance checks, and
writes a completion marker only for plain `PASS`.

**Tech Stack:** Windows PowerShell 5.1, .NET file APIs, GitHub CLI, existing
conda Python 3.13 environment, reviewed Python validator.

## Global constraints

- EvidenceHead: `2a2237bc323b8473d19979aaa56a0e8ff88cee04`.
- Validator SHA-256:
  `3c0afb898b7b051096fe4dae33fce3a33e2c3a6974f628e0e102512039be1e35`.
- Windows run/job/artifact: `31595536823` / `94110014568` / `9141180986`,
  `precision-Windows-py3.12`, digest
  `sha256:6f22ec4cc4a79e8b87b76b1078b94da405a2de52c4255291222f74745471399c`,
  size `81853`.
- Linux run/job/artifact: `31595587864` / `94110176681` / `9140967528`,
  `precision-Linux-py3.12`, digest
  `sha256:43506d0a63444bf3ff3367015da7ab150c3c5485712b189f4c18c75e87a8b4a6`,
  size `19491`.
- Windows mode/native count: `installed-wheel` / `26`; Linux:
  `source-tree` / `16` with runner-exit bytes `30 0A` and SHA-256
  `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`.
- Both artifacts must contain the exact singleton UHF nodeid, profile
  `omp4-blas4`, Python `3.12`, repeats `20`, runtime LibXC `7.1.2`, and plain
  validator `PASS 20/20/0`.
- Preserve all prior archives, attempts, latches, bindings, manifests,
  terminal evidence, 26 DLL fixtures, source, dependencies, remotes, PRs and
  issues. Never rerun, redispatch or use the old d9b559 validator.

---

### Task 1: Author and harmlessly verify the acceptance script

**Files:**
- Create ignored: `.superpowers/sdd/2026-08-12-platform-aware-libxc-linkage-validator/validate-platform-aware-pair-r2.ps1`
- Modify once: `D:\workspace\pyscf\.agents\active\libxc-712-release-revalidation.md`

**Interfaces:**
- Consumes: manifest SHA `d7a8b17a...`, handoff SHA `85d29b...`, terminal SHA
  `97e1b4ed...`, exact Goal-active key, and the reviewed validator.
- Produces: `-SelfTest` result `SELF-TEST PASS: 2 cases` and one production
  JSON summary.

- [ ] **Step 1: Write the script with a side-effect-free self-test**

Use strict JSON readers, `FileMode.CreateNew` + `Flush(true)` writers, native
exit-code checks, exact two-entry configuration order, and an early
`-SelfTest` branch. The self-test verifies Windows/Linux mode, native count,
run/artifact IDs, and requires zero GitHub/Goal/archive calls.

- [ ] **Step 2: Run static and harmless checks**

Require Windows PowerShell 5.1 AST errors `0`, UTF-8 without BOM, LF-only,
final LF, exact script SHA, and `SELF-TEST PASS: 2 cases`. Confirm both target
archive roots are absent and no heartbeat/supervisor survives.

- [ ] **Step 3: Freeze exact Goal active in the active document**

Use one `apply_patch` to add exactly one
`production_uhf_pair_r2_terminal_goal: active` line after independent
`get_goal` readback. The script must require this line and the terminal marker's
original-handle proof before any archive write.

---

### Task 2: Execute strict two-artifact acceptance

**Files:**
- Create: `.agents/archive/precision-ci/experiments/31595536823-production-uhf-pair-r2-windows-py312/**`
- Create: `.agents/archive/precision-ci/experiments/31595587864-production-uhf-pair-r2-linux-py312/**`
- Modify once after PASS: `.agents/active/libxc-712-release-revalidation.md`
- Modify: `.superpowers/sdd/2026-08-12-platform-aware-libxc-linkage-validator/pair-r2-execution-report.md`

**Interfaces:**
- Consumes: Task 1 script and exact live run/artifact identities.
- Produces: two immutable archive identities, attempts, validator reports and
  completion markers, or retained incomplete attempts on any failure.

- [ ] **Step 1: Run the script exactly once**

The script must process Windows then Linux. Each run must be attempt 1,
`workflow_dispatch`, completed success, exact workflow/head/branch, and contain
one completed-success `precision` job plus one exact nonexpired artifact.

- [ ] **Step 2: Require validator and platform evidence**

For each attempt require validator exit `0`, `valid=true`, plain `PASS`, records
`20`, pass `20`, fail `0`, exact head/profile/nodeid/validator hash, runtime
LibXC `7.1.2`, and exact mode/native count. Linux additionally reopens the
ordinary runner-exit file and verifies its bytes and hash.

- [ ] **Step 3: Durably complete and update active evidence**

Write each completion marker only after report durability/readback. Use one
`apply_patch` to add unique Windows/Linux run, job, artifact, report, completion,
tested-SHA and verdict keys plus overall pair verdict `PASS`. Preserve the old
Windows PASS/Linux INVALID historical evidence and label this result as a
20-repeat UHF transport gate, not the three-nodeid final result.

---

### Task 3: Independent evidence review and continuation

**Files:**
- Create ignored: `.superpowers/sdd/2026-08-12-platform-aware-libxc-linkage-validator/pair-r2-terminal-review.md`

- [ ] **Step 1: Obtain independent read-only review**

The reviewer re-queries run/job/artifact identities, re-runs the frozen
validator, cross-checks all 20 records/logs/summary/runtime/linkage/exit hashes,
and returns exactly `Pair Terminal Acceptance: APPROVED` or a finding.

- [ ] **Step 2: Continue the full objective**

Only dual platform `PASS` plus independent approval closes this UHF Unix
transport gate. Then return to the full three-nodeid matrix/root-cause plan;
do not update issue `#3312` until nodeid-specific evidence supports the claim.

## Verification checklist

- [ ] Terminal/handoff/Goal active are exact and original processes are gone.
- [ ] Script AST/encoding/self-test pass and target archives start absent.
- [ ] Live run/job/artifact identity matches all frozen values.
- [ ] Windows is installed-wheel 26-native PASS 20/20.
- [ ] Linux is source-tree 16-native PASS 20/20 with exit bytes `30 0A`.
- [ ] Completion markers and active keys bind exact report hashes.
- [ ] Independent terminal review is APPROVED.
- [ ] No rerun, redispatch, retry, dependency, source, remote, PR/issue or DLL mutation occurs.
