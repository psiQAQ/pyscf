# Unified Precision CI Artifact Design

## Goal

Make the Windows PR check use the same selected precision node IDs as the Linux/macOS precision workflow, while keeping Windows installed-wheel validation intact and making all three platforms emit one comparable artifact layout.

## Scope

- Add one tracked node-ID text file under `.github/workflows/`; Bash and PowerShell read it directly.
- Run every selected node once in this batch, including the normal Windows `check` and manual precision workflow.
- Disable the normal Windows `full` job temporarily with a job-level false condition.
- Standardize artifacts at `tmp/precision-results/`: `selected-nodeids.txt`, `attempts.csv`, `summary.csv`, `summary.md`, `logs/`, and `environment/build/` plus `environment/test/`.
- Upgrade both normal Windows artifact uploads to `actions/upload-artifact@v7`; stage logs and reports under the shared root and upload wheel metadata, not `dist/*.whl`.
- Capture Linux/macOS build metadata immediately after the existing build step and test metadata immediately before the test loop. These are two timestamps of the same environment, not a build/test environment refactor.
- Capture Windows build and test Conda environments separately.

## Non-goals

- Do not change Conda/MSYS2 setup, DLL packaging, source-vs-installed-wheel validation, test selection semantics, or Linux/macOS build scripts.
- Do not upload wheel binaries from normal Windows CI.
- Do not increase any selected-test repeat count beyond one in this batch.

## Data Flow

1. Each runner copies the canonical node-ID file into `tmp/precision-results/selected-nodeids.txt`.
2. Every runner executes each selected node once.
3. Each runner writes the same attempts and summary CSV schemas and per-attempt logs.
4. The workflow publishes `environment/build/` after building and `environment/test/` before testing. Windows uses its distinct Conda environments; Linux/macOS use two snapshots around the existing test boundary.
5. Normal Windows stages legacy build logs/reports plus `wheel-metadata.json` under `tmp/precision-results/` and uploads that one directory with v7.

## Verification

- Static guardrails assert that all runners reference the shared file, normal Windows check repeats once, normal Windows full is disabled, and all uploads use v7 without `dist/*.whl`.
- Shell and PowerShell parser checks validate modified runners.
- The next manually triggered CI run verifies artifact schemas and all platform environment folders.
