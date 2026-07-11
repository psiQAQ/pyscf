#!/usr/bin/env bash

set -uo pipefail

export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
ulimit -s 20000

node_id_source='.github/workflows/precision-selected-nodeids.txt'
repeats=1
results_dir='tmp/precision-results'
test_environment_dir="$results_dir/environment/test"

if [[ ! -s "$node_id_source" ]]; then
    printf 'Missing precision node-ID file: %s\n' "$node_id_source" >&2
    exit 2
fi
mapfile -t tests < <(sed -e '/^[[:space:]]*$/d' -e '/^[[:space:]]*#/d' "$node_id_source")
if (( ${#tests[@]} == 0 )); then
    printf 'Precision node-ID file is empty: %s\n' "$node_id_source" >&2
    exit 2
fi

mkdir -p pyscftmpdir "$results_dir/logs" "$test_environment_dir"
cp "$node_id_source" "$results_dir/selected-nodeids.txt"
printf '%s\n' \
  'pbc_tools_pbc_fft_engine = "NUMPY+BLAS"' \
  "dftd3_DFTD3PATH = './pyscf/lib/deps/lib'" \
  'scf_hf_SCF_mute_chkfile = True' \
  'TMPDIR = "./pyscftmpdir"' > .pyscf_conf.py

python .github/workflows/collect_precision_environment.py --snapshot-dir "$test_environment_dir"
printf 'repeat_count=%s\nOMP_NUM_THREADS=%s\nOPENBLAS_NUM_THREADS=%s\nMKL_NUM_THREADS=%s\n' \
  "$repeats" "$OMP_NUM_THREADS" "$OPENBLAS_NUM_THREADS" "$MKL_NUM_THREADS" \
  > "$test_environment_dir/runner-config.txt"

write_csv_row() {
    local first=1 value escaped
    for value in "$@"; do
        escaped=${value//\"/\"\"}
        if (( first )); then
            first=0
        else
            printf ','
        fi
        printf '"%s"' "$escaped"
    done
    printf '\n'
}

printf 'test_id,attempt,status,duration_seconds,pytest_summary,relative_log_path\n' > "$results_dir/attempts.csv"
printf 'test_id,attempts,passes,failures,average_seconds,first_failure_log\n' > "$results_dir/summary.csv"
{
    printf '## Precision test summary\n\n'
    printf '| Test ID | Attempts | Passes | Failures | Average Seconds | First Failure Log |\n'
    printf '| --- | ---: | ---: | ---: | ---: | --- |\n'
} > "$results_dir/summary.md"

total_failures=0
for test_id in "${tests[@]}"; do
    passes=0
    failures=0
    duration_total=0
    first_failure_log=''
    log_name="${test_id//\//_}"
    log_name="${log_name//:/_}"

    for ((attempt=1; attempt<=repeats; attempt++)); do
        log_file="$results_dir/logs/${log_name}.attempt-${attempt}.log"
        started_ns=$(date +%s%N)
        if pytest -q -rA -s -c pytest.ini "$test_id" > "$log_file" 2>&1; then
            result='passed'
            passes=$((passes + 1))
        else
            result='failed'
            failures=$((failures + 1))
            total_failures=$((total_failures + 1))
            if [[ -z "$first_failure_log" ]]; then
                first_failure_log="$log_file"
            fi
        fi
        finished_ns=$(date +%s%N)
        duration_seconds=$(awk -v start="$started_ns" -v end="$finished_ns" 'BEGIN {printf "%.3f", (end - start) / 1000000000}')
        duration_total=$(awk -v total="$duration_total" -v duration="$duration_seconds" 'BEGIN {printf "%.3f", total + duration}')
        pytest_summary=$(grep -E '(subtests passed|subtests failed|[0-9]+ (passed|failed|error|errors|skipped|warning|warnings|xfailed|xpassed))' "$log_file" | tail -n 1 | tr '\r\n' ' ')
        write_csv_row "$test_id" "$attempt" "$result" "$duration_seconds" "$pytest_summary" "$log_file" >> "$results_dir/attempts.csv"
        printf '%s attempt %s/%s: %s\n' "$test_id" "$attempt" "$repeats" "$result"
    done

    average_seconds=$(awk -v total="$duration_total" -v count="$repeats" 'BEGIN {printf "%.3f", total / count}')
    write_csv_row "$test_id" "$repeats" "$passes" "$failures" "$average_seconds" "$first_failure_log" >> "$results_dir/summary.csv"
    printf '| `%s` | %s | %s | %s | %s | %s |\n' \
        "$test_id" "$repeats" "$passes" "$failures" "$average_seconds" "$first_failure_log" >> "$results_dir/summary.md"
done

cat "$results_dir/summary.md"

if (( total_failures != 0 )); then
    exit 1
fi
