# UHF #3410 final implementation verification

This fork-only workflow tests source baseline
`ab749b4fd00f95a08ad00997356c9f6f77fc8674` (B), which contains merge
`fd6b6898a3d06fa0628f9d8544476a856dc711a8` of final head
`e7d2001bc49df99b65cd182fc3cb70ea9948724b`. Scientific sources and existing
assertions are unchanged. Earlier `ce71ff65` evidence is not counted here.

The dedicated workflow runs only on the UHF verification branch. Each platform
builds a wheel from B, verifies Python payload bytes against the checkout, installs
outside the checkout, and stages only the original test files. The baseline
Windows build script is reused unchanged. The old precision wrapper is not used:
the current Windows verifier does not accept its `Precision*` parameters.

The full workflow is explicitly triggered by creating or updating
`start-full-run.txt` in this directory. The separate Linux resume workflow
reuses the wheel from run 42281471449, installs the existing native Linux
dependencies on each fresh runner, and gates each 100-attempt shard with a
full-node preflight. The first formal Linux run omitted those native packages:
all attempts stopped at import with missing `libblas.so.3`, before pytest ran.
Those failures remain preserved; Windows's independent evidence is retained.
The runtime manifest records both the wheel builder's tool SHA and the current
verification tool SHA when an existing wheel is reused.

Both platform preflights must pass the entire explicit node
`pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing` (both Fe2 stages),
with one collected/executed/passed test, no skip/deselection, two SCF stage
records, native thread metadata and per-attempt logs. Nine nearby existing
molecular/PBC smearing nodes are also run. The existing skipped ROHF/fix_spin
test is not counted, and no full suite is requested.

Only after preflight and regressions pass do formal shards run: Linux Python
3.12, 10 x 100 fresh processes; Windows Python 3.13, 2 x 100. The requested
OMP/BLAS profile is 4/4. A serial BLAS build may actually use one thread;
`probe.py` records the loaded libraries, hashes, API-reported thread counts,
OpenBLAS build/configuration and PySCF's OpenMP count without changing limits.
Every shard uses its platform's preflight wheel hash and pinned dependency
versions. All failed attempts are retained; no retries substitute for failures.

`sys.setprofile` observes the existing convergence-hook and hf.kernel return
frames, recording dF/dE, gradient, thresholds, energy, entropy and convergence
without replacing scientific methods or changing test inputs. This telemetry
adds Python overhead. The underlying pytest method, module setup/teardown, both
stages and every assertion still execute unchanged.

Evidence binds source SHA, tool SHA, wheel SHA-256, Python micro version,
packages, runner image, actual thread counts, process IDs, exact nodes,
per-attempt logs/JUnit/results and executed counts. Temp variables and caches
are private to each task runner/process. Evidence is retained for 90 days and
should also be downloaded to the task's local evidence directory.

## Notes

OpenAI Codex assisted with source review, validation tooling, execution and
evidence preparation. These diagnostic tools belong only on the personal fork's
verification branch. Any upstream code or issue update requires human review
and submission under AI_POLICY.md; this workflow does not publish either.
