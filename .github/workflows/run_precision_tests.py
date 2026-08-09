#!/usr/bin/env python
"""Run an explicit nodeid list repeatedly and emit reviewable evidence."""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path


PROFILES = {
    '1/1': ('1', '1', 'omp1-blas1'),
    '4/1': ('4', '1', 'omp4-blas1'),
    '1/4': ('1', '4', 'omp1-blas4'),
    '4/4': ('4', '4', 'omp4-blas4'),
}
RECORD_FIELDS = (
    'tested_sha',
    'nodeid',
    'attempt',
    'profile',
    'status',
    'duration_seconds',
    'pytest_summary',
    'log_file',
    'environment_file',
    'nodeids_file',
)


def load_nodeids(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f'Nodeid file does not exist: {path}')
    nodeids = [
        line.strip() for line in path.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.lstrip().startswith('#')
    ]
    if not nodeids:
        raise ValueError('Nodeid file must contain at least one nodeid')
    seen = set()
    for nodeid in nodeids:
        if nodeid in seen:
            raise ValueError(f'Duplicate nodeid: {nodeid}')
        seen.add(nodeid)
    return nodeids


def parse_profile(value):
    try:
        return PROFILES[value]
    except KeyError as error:
        allowed = ', '.join(PROFILES)
        raise ValueError(f'Unsupported profile {value!r}; expected one of {allowed}') from error


def validate_repeats(value):
    if value < 1:
        raise ValueError('Repeats must be a positive integer')
    return value


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nodeids-file', required=True, type=Path)
    parser.add_argument('--repeats', required=True, type=int)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--tested-sha')
    parser.add_argument('--working-directory', type=Path, default=Path.cwd())
    parser.add_argument('--rootdir', type=Path, default=Path.cwd())
    parser.add_argument('--pytest-config', type=Path, default=Path('pytest.ini'))
    parser.add_argument(
        '--collector',
        type=Path,
        default=Path(__file__).with_name('collect_precision_environment.py'),
    )
    parser.add_argument('--validate-only', action='store_true')
    return parser.parse_args()


def resolve_tested_sha(explicit, working_directory):
    if explicit:
        return explicit
    if os.environ.get('GITHUB_SHA'):
        return os.environ['GITHUB_SHA']
    result = subprocess.run(
        ('git', 'rev-parse', 'HEAD'),
        cwd=working_directory,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError('Unable to determine tested SHA; pass --tested-sha')
    return result.stdout.strip()


def profile_environment(omp_threads, blas_threads):
    environment = os.environ.copy()
    environment.update({
        'OMP_NUM_THREADS': omp_threads,
        'OPENBLAS_NUM_THREADS': blas_threads,
        'MKL_NUM_THREADS': blas_threads,
        'BLIS_NUM_THREADS': blas_threads,
        'VECLIB_MAXIMUM_THREADS': blas_threads,
        'NUMEXPR_NUM_THREADS': blas_threads,
    })
    return environment


def pytest_summary(output, returncode):
    patterns = (
        re.compile(r'=+ .*\b(?:passed|failed|error|errors|skipped|deselected)\b.* =+$'),
        re.compile(r'.*\b(?:passed|failed|error|errors|skipped|deselected)\b.*'),
    )
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for pattern in patterns:
        for line in reversed(lines):
            if pattern.fullmatch(line):
                return line
    return f'pytest exited with code {returncode}; inspect the attempt log'


def relative_evidence_path(path, output_dir):
    return path.relative_to(output_dir).as_posix()


def append_record(path, record):
    with path.open('a', encoding='utf-8') as handle:
        json.dump(record, handle, sort_keys=True)
        handle.write('\n')


def write_summary(output_dir, records):
    csv_path = output_dir / 'summary.csv'
    with csv_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=RECORD_FIELDS)
        writer.writeheader()
        writer.writerows(records)
    statuses = Counter(record['status'] for record in records)
    lines = [
        '# Precision investigation summary',
        '',
        f'- Tested SHA: `{records[0]["tested_sha"]}`',
        f'- Profile: `{records[0]["profile"]}`',
        f'- Records: {len(records)}',
        '',
        '## Status counts',
        '',
        *(f'- `{status}`: {count}' for status, count in sorted(statuses.items())),
    ]
    (output_dir / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def collect_environment(collector, output_dir, working_directory, environment):
    environment_dir = output_dir / 'environment'
    command = [sys.executable, str(collector), '--snapshot-dir', str(environment_dir)]
    collector_environment = environment.copy()
    existing_pythonpath = collector_environment.get('PYTHONPATH')
    collector_environment['PYTHONPATH'] = os.pathsep.join(
        value for value in (str(working_directory), existing_pythonpath) if value
    )
    result = subprocess.run(
        command,
        cwd=working_directory,
        env=collector_environment,
        capture_output=True,
        text=True,
        check=False,
    )
    (environment_dir / 'collector.log').write_text(
        result.stdout + result.stderr, encoding='utf-8'
    )
    if result.returncode:
        raise RuntimeError(
            f'Environment capture failed with code {result.returncode}; '
            f'inspect {environment_dir / "collector.log"}'
        )
    return environment_dir / 'runtime.json'


def main():
    args = parse_args()
    try:
        nodeids = load_nodeids(args.nodeids_file)
        repeats = validate_repeats(args.repeats)
        omp_threads, blas_threads, profile = parse_profile(args.profile)
        working_directory = args.working_directory.resolve(strict=True)
        rootdir = args.rootdir.resolve(strict=True)
        pytest_config = args.pytest_config.resolve(strict=True)
        collector = args.collector.resolve(strict=True)
        tested_sha = resolve_tested_sha(args.tested_sha, working_directory)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error

    if args.validate_only:
        print(json.dumps({
            'nodeids': nodeids,
            'repeats': repeats,
            'profile': profile,
            'tested_sha': tested_sha,
        }, indent=2))
        return
    if args.output_dir is None:
        raise SystemExit('--output-dir is required unless --validate-only is used')

    output_dir = args.output_dir.resolve()
    logs_dir = output_dir / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    selected_path = output_dir / 'selected-nodeids.txt'
    selected_path.write_text('\n'.join(nodeids) + '\n', encoding='utf-8')
    environment = profile_environment(omp_threads, blas_threads)
    environment['PRECISION_TESTED_SHA'] = tested_sha
    try:
        environment_path = collect_environment(
            collector, output_dir, working_directory, environment
        )
    except RuntimeError as error:
        raise SystemExit(str(error)) from error

    records_path = output_dir / 'records.jsonl'
    records_path.unlink(missing_ok=True)
    records = []
    for node_index, nodeid in enumerate(nodeids, 1):
        for attempt in range(1, repeats + 1):
            log_path = logs_dir / f'node-{node_index:03d}-attempt-{attempt:04d}.log'
            command = [
                sys.executable,
                '-m',
                'pytest',
                nodeid,
                '-s',
                '-c',
                str(pytest_config),
                '--rootdir',
                str(rootdir),
                '--import-mode=prepend',
                '--durations=10',
            ]
            started = time.monotonic()
            result = subprocess.run(
                command,
                cwd=working_directory,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            duration = round(time.monotonic() - started, 6)
            output = result.stdout + result.stderr
            log_path.write_text(output, encoding='utf-8')
            sys.stdout.write(output)
            record = {
                'tested_sha': tested_sha,
                'nodeid': nodeid,
                'attempt': attempt,
                'profile': profile,
                'status': 'pass' if result.returncode == 0 else 'fail',
                'duration_seconds': duration,
                'pytest_summary': pytest_summary(output, result.returncode),
                'log_file': relative_evidence_path(log_path, output_dir),
                'environment_file': relative_evidence_path(environment_path, output_dir),
                'nodeids_file': relative_evidence_path(selected_path, output_dir),
            }
            append_record(records_path, record)
            records.append(record)

    write_summary(output_dir, records)
    if any(record['status'] != 'pass' for record in records):
        raise SystemExit('One or more precision attempts failed; evidence is complete')


if __name__ == '__main__':
    main()
