#!/usr/bin/env bash

set -uo pipefail

export OMP_NUM_THREADS=4
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
ulimit -s 20000

mkdir -p pyscftmpdir
printf '%s\n' \
  'pbc_tools_pbc_fft_engine = "NUMPY+BLAS"' \
  "dftd3_DFTD3PATH = './pyscf/lib/deps/lib'" \
  'scf_hf_SCF_mute_chkfile = True' \
  'TMPDIR = "./pyscftmpdir"' > .pyscf_conf.py

tests=(
  'pyscf/adc/test/test_radc/test_ee_df_N2.py::KnownValues::test_ee_adc2'
  'pyscf/gw/test/test_gw.py::KnownValues::test_gwac_pade_frozen'
  'pyscf/grad/test/test_mcpdft.py::KnownValues::test_scanner'
  'pyscf/grad/test/test_mcpdft.py::KnownValues::test_gradients'
  'pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_ipccsd'
  'pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_eaccsd'
  'pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_casci_multistate'
  'pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_decomposition_hybrid_sa'
  'pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_decomposition_sa'
  'pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_energy_tot'
  'pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_kernel_steps_casscf'
  'pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_state_average'
  'pyscf/mcpdft/test/test_mcpdft.py::KnownValues::test_tpbe0'
  'pyscf/grad/test/test_pdft_diatomic_gradients.py::KnownValues::test_grad_h2_cms3ftlda22_sto3g_slow'
  'pyscf/mcpdft/test/test_diatomic_energies.py::KnownValues::test_h2_cms3ftlda22_sto3g'
  'pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_tdhf'
  'pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda'
  'pyscf/tdscf/test/test_tduks.py::KnownValues::test_analyze'
  'pyscf/tdscf/test/test_tduks.py::KnownValues::test_tddft_camb3lyp'
  'pyscf/mcscf/test/test_umc1step.py::KnownValues::test_ucasscf'
  'pyscf/mcscf/test/test_h2o.py::KnownValues::test_nosymm_sa4_newton'
  'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad'
  'pyscf/fci/test/test_spin_op.py::KnownValues::test_contract_ss'
  'pyscf/dft/test/test_gks.py::KnownValues::test_collinear_gks_lda'
  'pyscf/adc/test/test_uadc/test_ip_cvs_P.py::KnownValues::test_ip_adc2x'
  'pyscf/mcscf/test/test_casci.py::KnownValues::test_with_x2c_scanner'
  'pyscf/tdscf/test/test_tdrks_vv10.py::KnownValues::test_wb97xv_tda_triplet'
  'pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_hse03_tda'
  # This test is known to fail on Windows CI.
  'pyscf/cc/test/test_uccsdt_highm.py::KnownValues::test_zero_beta_electrons'
)

repeats=10
results_dir='tmp/precision-results'
mkdir -p "$results_dir/logs" "$results_dir/environment"
python -m pip freeze --all > "$results_dir/environment/pip-freeze.txt"
python -m pip list --format=json > "$results_dir/environment/pip-list.json"
if ! python -m pip check > "$results_dir/environment/pip-check.txt" 2>&1; then
    printf 'pip check failed; see pip-check.txt\n' >> "$results_dir/environment/pip-check.txt"
fi
python .github/workflows/collect_precision_environment.py "$results_dir/environment/runtime.json"
printf 'repeat_count=%s\n' "$repeats" > "$results_dir/environment/runner-config.txt"
printf 'test_id,attempt,exit_code,result,log_file\n' > "$results_dir/attempts.csv"
printf 'test_id,attempts,passes,failures\n' > "$results_dir/summary.csv"

total_failures=0
for test_id in "${tests[@]}"; do
    passes=0
    failures=0
    log_name="${test_id//\//_}"
    log_name="${log_name//:/_}"

    for ((attempt=1; attempt<=repeats; attempt++)); do
        log_file="$results_dir/logs/${log_name}.attempt-${attempt}.log"
        if pytest -q -rA -s -c pytest.ini "$test_id" > "$log_file" 2>&1; then
            exit_code=0
            result='pass'
            passes=$((passes + 1))
        else
            exit_code=$?
            result='fail'
            failures=$((failures + 1))
            total_failures=$((total_failures + 1))
        fi
        printf '%s,%s,%s,%s,%s\n' "$test_id" "$attempt" "$exit_code" "$result" "$log_file" >> "$results_dir/attempts.csv"
        printf '%s attempt %s/%s: %s\n' "$test_id" "$attempt" "$repeats" "$result"
    done

    printf '%s,%s,%s,%s\n' "$test_id" "$repeats" "$passes" "$failures" >> "$results_dir/summary.csv"
done

{
    printf '## Precision test summary\n\n'
    printf '| Test ID | Attempts | Passes | Failures |\n'
    printf '| --- | ---: | ---: | ---: |\n'
    while IFS=, read -r test_id attempts passes failures; do
        if [ "$test_id" != 'test_id' ]; then
            printf '| `%s` | %s | %s | %s |\n' "$test_id" "$attempts" "$passes" "$failures"
        fi
    done < "$results_dir/summary.csv"
} > "$results_dir/summary.md"

cat "$results_dir/summary.md"

if [ "$total_failures" -ne 0 ]; then
    exit 1
fi
