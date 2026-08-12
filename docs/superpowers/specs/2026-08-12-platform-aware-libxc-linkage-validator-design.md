# Platform-aware LibXC linkage validator correction

**Date:** 2026-08-12
**Status:** Approved design awaiting written-spec review
**Scope:** Local ignored production-evidence validator and its evidence workflow only

## Context

The macOS one-repeat Unix-wrapper witness is bound to run `31577510832`, job
`94052864840`, artifact `9133834443`, and tested commit
`2a2237bc323b8473d19979aaa56a0e8ff88cee04`. The workflow completed
successfully. Its artifact contains one passing record, runtime LibXC `7.1.2`,
and an ordinary `runner-exit-code.txt` with bytes `0x30 0x0A` and SHA-256
`9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`.

The frozen validator at SHA-256
`d9b559e7259ea768c866add619e648419b7ac9d3b2d6c4bb2f4f69da38d4292c`
classified the artifact `INVALID` with `Native inventory lacks LibXC
libraries`. That result is retained and is not a scientific failure.

The failure is a validator-contract defect. The validator first requires both
`libxc_itrf.<suffix>` and `libxc.<suffix>` to appear in the collected
`pyscf/lib` inventory. Real Unix source-tree artifacts contain 16 PySCF
interface libraries, including `libxc_itrf`, while LibXC itself is a linked
dependency outside that inventory:

- macOS: `libxc_itrf.dylib` links exactly one `@rpath/libxc.15.dylib`;
- Linux: `libxc_itrf.so` resolves `libxc.so` to
  `<imported-pyscf>/lib/deps/lib/libxc.so`.

Windows installed-wheel artifacts are different: the 26-DLL wheel inventory
contains both `libxc_itrf.dll` and wheel-local `libxc.dll`.

## Goal

Make the validator prove the platform's real LibXC loading contract without
weakening runtime version, native inventory, path containment, linkage return
code, record, thread-profile, package-import, artifact-identity, or exit-code
checks.

This correction is evidence infrastructure. It does not modify PySCF, rerun a
scientific calculation, change a scientific assertion, or by itself establish
stability or a fix for any nodeid.

## Platform contracts

### Windows installed wheel

Keep the existing contract unchanged:

1. `libxc_itrf.dll` and `libxc.dll` must both be present in the exact native
   inventory.
2. `libxc_itrf.dll` linkage must contain exactly one `libxc.dll` target.
3. That target must resolve to the imported wheel's own
   `site-packages/pyscf/lib/libxc.dll`, accepting the already-supported native
   Windows or equivalent Cygwin spelling only.
4. The installed-wheel mode, package path, native count `26`, pip check, and
   all existing provenance gates remain strict.

### macOS source tree

Use the real source-tree contract:

1. `libxc_itrf.dylib` must be present in the exact 16-library inventory.
2. A separate inventory entry named `libxc.dylib` is neither required nor
   synthesized.
3. The `otool -L` output for `libxc_itrf.dylib` must contain exactly one
   dependency line for `@rpath/libxc.15.dylib`.
4. The linkage command must have return code `0`; the imported PySCF path,
   runtime LibXC `7.1.2`, source-tree mode, native count `16`, and all other
   gates remain strict.

### Linux source tree

Use the real source-tree contract:

1. `libxc_itrf.so` must be present in the exact 16-library inventory.
2. A separate inventory entry named `libxc.so` is neither required nor
   synthesized.
3. The `ldd` output for `libxc_itrf.so` must contain exactly one `libxc.so`
   resolution target.
4. The normalized target must equal
   `<imported-pyscf>/lib/deps/lib/libxc.so`; a system library, another checkout,
   an unresolved entry, or an additional target is invalid.
5. The linkage command must have return code `0`; the imported PySCF path,
   runtime LibXC `7.1.2`, source-tree mode, native count `16`, and all other
   gates remain strict.

## Implementation boundary

Change only the local ignored production validator and its local tests/reports.
The minimal production change belongs in `_check_libxc_linkage`:

1. require `libxc_itrf.<suffix>` for every platform;
2. branch by platform before deciding whether a separate `libxc.<suffix>`
   inventory entry is required;
3. keep that second inventory requirement only for Windows;
4. validate the Darwin rpath or Linux `deps/lib` target as specified above.

Do not add a general linker parser, a new dependency, workflow changes, PySCF
source changes, retries, tolerance changes, or compatibility fallbacks.

## TDD and verification

The change must follow RED/GREEN:

1. Add a real-shaped macOS source-tree fixture with 16 native libraries,
   `libxc_itrf.dylib`, no `libxc.dylib`, and one exact
   `@rpath/libxc.15.dylib` dependency. Confirm the current validator fails with
   `Native inventory lacks LibXC libraries`.
2. Add a real-shaped Linux source-tree fixture with 16 native libraries,
   `libxc_itrf.so`, no inventory `libxc.so`, and one exact
   `<imported-pyscf>/lib/deps/lib/libxc.so` resolution. Confirm the current
   validator fails for the same contract defect.
3. Apply the minimal platform-aware implementation and require both fixtures to
   pass.
4. Add or retain negative coverage proving that macOS rejects a missing,
   duplicate, or wrong-version rpath; Linux rejects external, duplicate,
   unresolved, or wrong-path LibXC targets; and Windows still rejects a missing
   wheel-local `libxc.dll`.
5. Run the validator self-test suite, `py_compile`, strict UTF-8/no-BOM/LF
   checks, and hash/readback checks. No package installation is required.
6. Obtain an independent specification and code-quality review before the new
   validator hash becomes authoritative.

## Evidence recovery and gates

Preserve the existing macOS archive attempt containing the original frozen
validator and its `INVALID` report. Do not edit or reinterpret that report.

After review:

1. freeze the corrected validator under a new SHA-256 and update its active
   provenance key;
2. re-download or otherwise byte-bind the same artifact `9133834443` into a new
   archive attempt, preserving run, job, artifact, digest, size, head, and
   branch identity;
3. run only the corrected frozen validator against that new attempt;
4. require the existing runner-exit bytes/SHA, one passing record, LibXC
   `7.1.2`, profile `omp4-blas4`, Python `3.12`, macOS source-tree mode, 16
   native entries, and the exact rpath contract;
5. create the archive completion marker and seven witness PASS keys only if the
   new report is `valid=true` and `verdict=PASS`;
6. label the result exactly as transport/provenance evidence with repeats `1`,
   not scientific stability.

No CI rerun is needed for this validator defect. The Windows+Ubuntu 20-repeat
pair remains forbidden until the recovered macOS witness gate is strictly
`PASS`. Any unrelated validator failure stops the workflow and requires a new
diagnosis rather than another dispatch.

## Success criteria

The correction is complete only when all of the following are true:

- real-shaped Darwin and Linux fixtures demonstrate the original RED and the
  corrected GREEN;
- Windows installed-wheel LibXC containment remains unchanged and covered;
- the full validator self-test suite and static checks pass;
- an independent review approves the exact corrected validator;
- the preserved macOS artifact validates under the corrected frozen hash with
  `valid=true`, `verdict=PASS`, and exact runtime/linkage/exit provenance;
- the original `INVALID` attempt remains intact;
- no new CI run, pair dispatch, scientific claim, PR/issue update, dependency
  change, or unrelated tracked modification occurs during the correction.
