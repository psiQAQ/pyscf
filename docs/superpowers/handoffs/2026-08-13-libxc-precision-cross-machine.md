# LibXC precision cross-machine handoff

## Final objective

从 `precision-investigation-template@7d3d241` 创建隔离的 LibXC 7.1.2 调查工程，构建并验证 Windows installed wheel，按原断言复验 PBC HSE06 TDA、SGX finite-difference gradient、PBC HSE03 TDA，必要时开展重复稳定性与根因实验；若稳定通过则关闭依赖门禁，若可复现失败则形成最小且可上游维护的 RED/GREEN 修复方案；验证完成后更新 `pyscf/pyscf#3312`，对已解决的相关 nodeid 标记完成并附上 CI、根因和最终解决方式等证据；若仍未解决，则继续在隔离调查分支中定位、实验并推进，直至这三个 nodeid 均获得可由上游长期维护的最终解决方案。

最终收口还包括：UHF/smearing 与 SGX 两个上游修复合入实时 `pyscf/pyscf:master` 后，针对三个目标 nodeid 完成 7 个 platform/Python 组合 × 4 个 OMP/BLAS profile 的正式矩阵；每份 artifact 为 3 nodeids × 200 attempts，共 28 artifacts、16,800 records，要求 0 fail/retry/missing，并据此更新和关闭 `pyscf/pyscf#3312`。

## Repository and exact refs

- fork: `https://github.com/psiQAQ/pyscf.git`
- upstream: `https://github.com/pyscf/pyscf.git`
- investigation: `codex/investigate/libxc-712-release-revalidation` (this document's commit is the continuation entry)
- GKS base comparison: `codex/investigate/pr3331-gks-linux38-base@c62a96f0fc026d46d0bfe0af5ce74ee73423280f`
- GKS head comparison: `codex/investigate/pr3331-gks-linux38-head@3753ef8ec1ca477c6e06fb35c11973418bf6c137`
- UHF historical PR content: `codex/fix/uhf-smearing-convergence-v2@860430ff9da7f4a7557fd7e405e3dbbe65015002`
- UHF rebuilt on live master: `codex/fix/uhf-smearing-convergence-v3@d57d6de09734ca32f2a1dc3223a19c47735e0aa6`
- SGX fix: `codex/fix/sgx-extra-cycle-convergence@13e8b529b0656b332fe296cdf45fd8700b79622d`
- SGX validation: `codex/test/sgx-extra-cycle-convergence-validation@2a2237bc323b8473d19979aaa56a0e8ff88cee04`
- telemetry: `codex/investigate/libxc-712-sgx-extra-cycle-telemetry@2133114d93af1c7cb18f1acdc5693e871d8632db`

All refs above were read back equal between local and `origin` immediately before this handoff, except this handoff commit itself, which must be pushed after creation.

## Current evidence

The targeted Linux 3.8 GKS comparison used only
`pyscf/dft/test/test_gks.py::KnownValues::test_collinear_gks_lda`, profile 4/4, 200 repeats per branch:

- base run `31666195355`, artifact `9168147496`: 197/200 pass; failures 45, 48, 119.
- head run `31666197628`, artifact `9168142469`: 199/200 pass; failure 186.
- all four failures are the same original `test_gks.py:98` six-place assertion, delta about `7.451251e-07`.
- Fisher exact two-sided p-value `0.6231131986`; risk difference head-base `-0.01`.
- verdict: `PRE_EXISTING_FLAKE_CONFIRMED`. The observed failure predates #3331; there is no evidence that #3331 increases its rate, and this does not prove that #3331 fixes GKS.

Local ignored evidence (not transported by Git) is under `.agents/archive/precision-ci/experiments/`; the comparison report SHA-256 is `402fca6f2cc99032a2eb9d40007f4038feb1fb76e7d7668842f0c296f7ddab77`. Re-download artifacts by run ID on another machine when raw evidence is needed.

The UHF v3 rebuild is based on live upstream master `14fb93158ec9c97ae1d67462ea47b5b27ce63aca`. Range-diff against the prior two-commit PR series is exact (`=`), and the three scientific file blobs match the reviewed PR head. Local Windows scientific tests are currently invalid because both old and new worktrees fail native DLL loading with `0xc06d007f`; do not treat that environment failure as a scientific regression.

## Critical PR boundary

PR `pyscf/pyscf#3331` is open/draft. Its fork branch `codex/fix/uhf-smearing-convergence` was externally force-pushed back to `2f1be97e3b522333d9f5aa4dd50d96421a275abe` after previously pointing at `860430ff...`. Do not overwrite it blindly. First inspect the live PR/timeline and confirm whether that reset was intentional. Only then, if appropriate, update it from the reviewed v3 branch using an exact `--force-with-lease` expectation bound to the live old SHA.

The recently added explanatory comment on #3331 was deleted; comment ID `5270808179` must remain absent unless new evidence warrants a replacement.

## Safe continuation order

1. Fetch `origin` and live upstream `master`; verify every SHA above and current PR #3331 head/body/checks.
2. Resolve the intentionality of the #3331 branch reset before any PR ref mutation. Re-run narrow checks, then update the PR only with exact lease protection and current evidence.
3. After #3331 merges, create the SGX PR from then-live upstream master and transplant only the minimal two-file fix from `13e8b529...`; keep the original scientific assertion unchanged.
4. After both fixes merge, run the frozen 28-artifact formal matrix for the three target nodeids and independently validate all 16,800 records.
5. Update `pyscf/pyscf#3312`: mark only genuinely solved nodeids, attach run/job/artifact links, root causes, final fixes and merge SHAs. Continue investigation for any unresolved nodeid; do not label non-reproduction as a fix.

On a new machine, read `AGENTS.md` first. Local `.agents/` state is ignored and may be absent, so use this tracked file as the recovery entry, then verify every dynamic GitHub/CI fact live before acting.
