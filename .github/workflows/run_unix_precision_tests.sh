#!/usr/bin/env bash

set -euo pipefail

nodeids_file=${1:?nodeids file is required}
repeats=${2:?repeats is required}
profile=${3:?profile is required}
output_dir=${4:-tmp/precision-results}
repo_root=$(cd "$(dirname "$0")/../.." && pwd)

python "$repo_root/.github/workflows/run_precision_tests.py" \
  --nodeids-file "$nodeids_file" \
  --repeats "$repeats" \
  --profile "$profile" \
  --output-dir "$output_dir" \
  --tested-sha "${GITHUB_SHA:-$(git -C "$repo_root" rev-parse HEAD)}" \
  --working-directory "$repo_root" \
  --rootdir "$repo_root" \
  --pytest-config "$repo_root/pytest.ini" \
  --environment-mode source-tree \
  --collector "$repo_root/.github/workflows/collect_precision_environment.py"
