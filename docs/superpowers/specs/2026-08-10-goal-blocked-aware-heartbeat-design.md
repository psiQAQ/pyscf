# Goal Blocked-Aware Heartbeat Design

## Status

Approved approach A; written-spec review pending.

## Context

The Stage 2 formal precision run uses one reviewed PowerShell heartbeat to poll
one exact GitHub Actions run every 1,800 seconds. The heartbeat pauses the
existing Codex Goal while CI is nonterminal and restores that same Goal to
`active` after a terminal, diagnostic, or 300-minute wake condition.

In this Codex App session, setting the Goal to `paused` has been followed by at
least seven immediate Goal-engine continuations that change it back to
`active`. Repeating the setter creates empty turns and does not establish a
stable wait. The frozen heartbeat intentionally rejects a current Goal status
of `blocked`, so marking the real scheduler fault as blocked would otherwise
prevent terminal recovery.

## Decision

Keep the frozen, reviewed GoalBridge file unchanged. Create one local ignored
runtime copy and make exactly one behavioral change in that copy:

- `Get-TerminalActivationAction` returns `set` for a Goal whose current status
  is `blocked`, in addition to its existing `paused` behavior.

The `blocked` state is used only after the same Goal-engine scheduler fault has
recurred at least three consecutive turns. It records a real operational
blocker; it is not a synonym for ordinary CI waiting.

## Runtime Handoff

1. Add a pure self-test proving `blocked` selects the existing `set active`
   path. Observe the test fail against the copied frozen behavior.
2. Add the single `blocked` branch and rerun the complete heartbeat self-test
   plus Windows PowerShell 5.1 AST, encoding, and hash checks.
3. Verify the old monitor by exact PID, executable path, script path, run ID,
   head SHA, interval, and wake threshold.
4. Stop only that exact old process and verify it is gone.
5. Start one runtime-copy monitor with the same exact run ID, head SHA,
   `IntervalSeconds=1800`, and `WakeAfterMinutes=300`.
6. Verify exactly one matching monitor, then set the existing Goal to
   `blocked` through the Goal API.
7. Record the runtime-copy path/hash, new PID/command line, blocker evidence,
   and recovery command in the active task document.

The swap must not dispatch, cancel, rerun, or query a different workflow run.

## State Semantics

- Nonterminal CI: the monitor sleeps normally; the Goal remains `blocked`
  because the scheduler fault prevents stable `paused` operation.
- Terminal/diagnostic/300-minute wake: the monitor reads the exact Goal. For
  `blocked` or `paused`, it calls the existing exact set-and-read-back path for
  `active`, then exits.
- Already `active`: the monitor exits without a duplicate setter.
- Any other Goal status, identity mismatch, transport ambiguity, run/head
  mismatch, or malformed GitHub state remains fail-closed under the existing
  logic.

## Evidence Boundaries

This is local control-plane handling only. It does not change:

- the scientific branch, selector, pytest assertions, LibXC build, wheel, or
  GitHub Actions workflow;
- the frozen validator or artifact acceptance rules;
- the frozen reviewed GoalBridge file and its recorded SHA;
- the formal run ID, head SHA, repeats, profile, or timeout/cancel gate.

The runtime copy is never committed to an upstream PySCF branch. Formal
artifact validation continues to use the original frozen helper and validator
hashes. The active document separately records the runtime copy provenance.

## Verification

- RED: copied heartbeat self-test fails because `blocked` is rejected during
  terminal activation.
- GREEN: complete self-test passes with the new pure case; Windows PowerShell
  5.1 AST reports zero errors; file is UTF-8 without BOM and LF-only.
- Mutation: temporarily removing the `blocked` branch makes the new self-test
  fail for the expected reason, then the mutation is removed.
- Process handoff: old exact PID is gone; one and only one new exact monitor is
  alive; no unrelated process is stopped.
- Goal handoff: independent Goal readback reports the exact thread/objective
  unchanged and status `blocked`; terminal handling later proves exact
  `active` and monitor exit.

## Stop Conditions

Stop and restore the Goal to `active` if the runtime copy fails self-test, AST,
identity validation, exact child cleanup, or Goal readback. Do not create a
second monitor, modify the frozen helper, or weaken any scientific or artifact
gate.
