# Unified Precision CI Artifacts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all precision runs consume one node-ID file and emit comparable build/test artifacts while normal Windows check remains a single-pass installed-wheel gate.

**Architecture:** A canonical text file supplies node IDs to Bash and PowerShell. The existing Python environment collector becomes the shared snapshot writer for `environment/build/` and `environment/test/`. Windows keeps its Conda/MSYS2 and staged installed-wheel test flow; workflows only stage outputs under the common artifact root.

**Tech Stack:** GitHub Actions YAML, Bash, PowerShell, Python standard library.

## Global Constraints

- No dependency installation or Python-environment mutation in the local checkout.
- Normal Windows `check` repeats each selected node exactly once.
- Manual precision triage keeps ten repeats.
- Normal Windows `full` remains disabled.
- No normal Windows artifact includes `dist/*.whl`.

---

### Task 1: Define and validate the shared node-ID contract

**Files:**
- Create: `.github/workflows/precision-selected-nodeids.txt`
- Modify: `.github/workflows/run_linux_precision_tests.sh`
- Modify: `.github/workflows/run_windows_precision_tests.ps1`
- Modify: `.github/workflows/ci_windows/verify_installed_wheel_ci.ps1`
- Test: `tmp/test_precision_artifact_contract.ps1`

- [ ] Write a static guard that reads the canonical file, rejects duplicates and blank node IDs, and asserts both runners reference `precision-selected-nodeids.txt`.
- [ ] Run the guard before changes and confirm it fails because the canonical file is absent.
- [ ] Move the existing 29 IDs into the text file; have Bash and PowerShell copy that file to `tmp/precision-results/selected-nodeids.txt` and parse it.
- [ ] Make Windows check resolve the canonical file by default, while accepting the copied artifact file from precision triage.
- [ ] Re-run the guard and parser checks for both PowerShell scripts.

### Task 2: Produce common build and test environment snapshots

**Files:**
- Modify: `.github/workflows/collect_precision_environment.py`
- Modify: `.github/workflows/ci-linux-precision.yml`
- Modify: `.github/workflows/run_linux_precision_tests.sh`
- Modify: `.github/workflows/run_windows_precision_tests.ps1`
- Modify: `.github/workflows/run_ci_windows.ps1`
- Modify: `.github/workflows/ci_windows/run_tests.ps1`
- Test: `tmp/test_precision_artifact_contract.ps1`

- [ ] Extend the existing collector so an output directory receives `runtime.json`, `pip-freeze.txt`, `pip-list.json`, and `pip-check.txt`; retain its current runtime fields.
- [ ] Capture Linux/macOS build metadata immediately after the existing build command and test metadata immediately before the test loop.
- [ ] Capture Windows build metadata from the build Conda environment after wheel creation and test metadata from the test Conda environment after installed-wheel verification, even when pytest failed.
- [ ] Update all runner configuration files to include repeat count and all three thread settings.
- [ ] Extend the static guard to require both `environment/build` and `environment/test` and run it.

### Task 3: Standardize attempts, summaries, and normal Windows artifacts

**Files:**
- Modify: `.github/workflows/run_linux_precision_tests.sh`
- Modify: `.github/workflows/ci-windows.yml`
- Modify: `.github/workflows/run_ci_windows.ps1`
- Test: `tmp/test_precision_artifact_contract.ps1`

- [ ] Add elapsed seconds, pytest summary, relative log path, average seconds, and first failure log to the Bash CSV output so it matches the Windows schema.
- [ ] Make normal Windows check pass the shared node-ID file and `tmp/precision-results` report directory to the existing installed-wheel verifier.
- [ ] Stage Windows build logs and `wheel-metadata.json` below `tmp/precision-results`; do not copy the wheel binary.
- [ ] Set `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, and `MKL_NUM_THREADS` to `4` for normal Windows verification.
- [ ] Run the guard and inspect the generated YAML/runner references.

### Task 4: Update workflow upload policy and disable full validation

**Files:**
- Modify: `.github/workflows/ci-windows.yml`
- Test: `tmp/test_precision_artifact_contract.ps1`

- [ ] Disable `windows-build-full` with `if: ${{ false }}` while preserving its definition for later restoration.
- [ ] Change both upload steps to `actions/upload-artifact@v7` and upload only `tmp/precision-results`.
- [ ] Ensure check artifact naming remains `windows-build-check-artifacts` and that `if: always()` plus `if-no-files-found: warn` are preserved.
- [ ] Run the static guard, `git diff --check`, Bash syntax check, and PowerShell parser checks.
- [ ] Commit the implementation as one focused CI change after fresh verification.
