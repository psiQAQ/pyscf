# CMS-PDFT numerical diagnostic

This workflow is confined to `ci/cms-pdft-repro-20261110`. It does not change
the scientific source, test assertions, grids, or spin penalty. Original
test executions retain all optimizer parameters. Diagnostic and tested
source commits are recorded separately.

The `repeat` phase runs the original H2 nodeid in 200 separate pytest
processes. Each uses two xdist workers with `loadfile`; only one worker
executes the single nodeid. Three uninstrumented controls follow. If all
200 instrumented runs pass and all three stages report convergence, 20
whole-file runs and one original multithreaded CI subset follow.

The `matrix` phase runs the baseline and original failing revision with
OpenMP 1/2 threads and no xdist/two workers, five times per combination.
It downloads the native-library archive from run `42846911445`, attempt 1,
and extracts that same archive into both source trees. Python packages are
installed at the pinned versions on the remote runner only. System library
packages and loaded paths are recorded; the historical runner image cannot
be reconstructed by this workflow.

The matrix now explicitly selects `OPENBLAS_CORETYPE=Haswell` to match the
dispatch observed in the original 200-run capture. The first matrix run
(`42850220899`) used automatic dispatch and reported SkylakeX instead;
those results are retained separately. The repeat phase remains unchanged.
This selects an OpenBLAS kernel, not its thread count; see the
[OpenBLAS runtime-variable documentation](https://www.openmathlib.org/OpenBLAS/docs/runtime_variables/).

After each source matrix, `replay.py` restores the captured CMS entry orbitals
and CI vectors for every failed sample and one successful sample. It calls
the existing CMS and PDFT methods with the original nudge and a diagnostic
`nudge_tol=1e-3` override. This is a causal comparison, not a source fix or a
replacement for fresh end-to-end regression runs. Initial objective,
gradient and Hessian differences against the capture are reported.

Pushes affecting this directory or its workflow currently select `matrix`.
The workflow also defines a `phase` dispatch input, defaulting to `repeat`;
GitHub requires a workflow definition on the default branch before manual
dispatch is available. This diagnostic does not modify the default branch.

Each invocation saves its PID, command, exit code, pytest/JUnit logs and
stage traces. Arrays contain the observed orbitals and CI vectors. CMS
objective, gradient, Hessian and rotation values come from the optimizer's
existing evaluations. Additional initial-density and first-FCI observations
are enabled in the matrix phase's diagnostic revision. Large integration
grids are retained for the first sample and failures. Worker trace names
include the worker identifier and PID.

`summary.json` records each independent calculation. Three failing state
subtests still count as one calculation. A numerical failure does not stop
the remaining runs, and a successful upload does not change the failed job
status. Missing instrumentation stops that phase because it cannot provide
the required evidence. The repeat controller has a 120-minute deadline and
an outer per-invocation timeout; the job reserves time for artifact upload.

Artifacts retain evidence and native libraries for 14 days. Download them
before expiry. Native archives are diagnostic inputs, not a PySCF package
or a promise of portability across arbitrary Linux systems.
