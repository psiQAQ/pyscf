# LibXC precision investigation - wrap-up handoff (2026-08-26)

Status at pause: **11 of 13 checklist entries in pyscf/pyscf#3312 are checked (7 closed by this campaign), five upstream PRs merged, two entries remain.** All dynamic facts below are snapshots - re-query GitHub live before acting.

## Merged this campaign

- #3404 `ad1d9d278fed` - EOM-GCCSD degenerate-cluster star-contraction biorthonormalization (+ swap-gauge regressions)
- #3405 `622e4424a752` - X2C linear-dependency eigh driver fallback `_eigh_with_fallback` (+ fault-injection regression)
- #3406 `3ddb2d59ba8c` - CIAH initial-trial-vector normalization (solver deadlock root cause behind #3319)
- #3407 `85206a8c4905` - rccsd update_amps fingerprint assertion 7->6 places (portability boundary, maintainer-approved)
- #3409 `b1f8c79feb2a` - sa4 newton conv_tol=1e-9 (tolerance/assertion margin, 1000/1000 verified)
- dependency: LibXC MR !806 via #3336 (`7ab7344`); HSE06/HSE03 closed on a released-path 28-artifact matrix, 11,200/11,200, independently validated.

## Remaining entries

1. `test_uhf_smearing` - carrier is **#3410** (jeanwsr, e_free convergence criterion; supersedes our closed #3331). Review in progress at pause: sunqm wants e_free-only via overloaded `check_convergence` (objects to a separate `check_extra_convergence` API) and questions dF-OR-|g|; jeanwsr updated assertions (e_free 8 places / e_tot 4-5) and the main criterion; AND/OR undecided. Our independent cross-validation of head `ce71ff65`: Linux 1000/1000 (run 32223176764), Windows wheel 200/200 (run 32224026926); RED baselines 1/200 (31689528256) and 3/1000 (31772613521). If the final version differs materially from `ce71ff65`, re-run the validation. After merge: master revalidation (molecular + pbc test_uhf_smearing, Linux + Windows) -> check the entry.
2. `test_finite_diff_grad` (SGX) - rework after #3410 settles. Frozen pre-implementation on `codex/fix/sgx-extra-convergence-hook` (based on pr3410-head; `_SGXHF.check_extra_convergence`, AND predicate + unit regression). If the hook API is dropped per sunqm, switch to overriding `check_convergence` (cf. the original candidate `13e8b529`, installed-wheel 200/200 run 31535193241). Then GREEN -> PR -> merge -> revalidation -> check. Finally close #3312.

## Operational rules distilled (do not regress)

- Read maintainer comments in full via `gh api .../comments/<id> --jq .body`; monitor summaries truncate.
- PR monitoring must cover issue comments AND `pulls/<n>/reviews` AND `pulls/<n>/comments` (inline) - review threads are invisible to the issues API.
- Lease pushes only, bound to a live `git ls-remote` value.
- When a fix lands within one order of magnitude of an assertion, 200 attempts cannot confirm it - use 1000+.
- Windows verification branches need the infra quartet: `.gitattributes`, `pyscf/lib/CMakeLists.txt` (M_PI/BUILD_TESTING/UPDATE_DISCONNECTED/patch-hard-fail), `MANIFEST.in` excludes, `pyscf/lib/misc.py` DLL fallback (plus `.github`).
- Entries are checked only after post-merge revalidation; NOT_REPRODUCED is never "fixed".
- Archive rule: once an entry closes, tag its verification branches `archive/<name>` and delete them; keep open-PR heads and referenced evidence branches.

## Environment

WSL Ubuntu-24.04, repo `/home/zywang/workspace/pyscf` (this branch is the recovery entry), worktree `/home/zywang/tmp/uhf-wt`. gh authenticated as psiQAQ. Global git author fixed to `psiQAQ <49629985+psiQAQ@users.noreply.github.com>`. Fork `ci.yml` stays disabled; all verification via `ci-precision-check.yml` workflow_dispatch. Run artifacts expire ~90 days after their run dates - run IDs above are authoritative.

The Windows-side companion docs (CLAUDE/HANDOFF/GOALS/PLAN/research) live in the workstation scratch repo and are not readable from WSL; this file is self-contained for recovery.
