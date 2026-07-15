"""Summarize precision diagnostic records without scientific interpretation."""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path


FIELDS = (
    'nodeid',
    'experiment',
    'mode',
    'status',
    'attempt',
    'artifact',
    'profile',
    'omp_num_threads',
    'openblas_num_threads',
    'mkl_num_threads',
    'veclib_maximum_threads',
    'log_file',
    'snapshot_or_checkpoint',
    'records_file',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-root', required=True, type=Path)
    parser.add_argument('--output-md', required=True, type=Path)
    parser.add_argument('--output-csv', required=True, type=Path)
    parser.add_argument('--nodeid')
    return parser.parse_args()


def read_records(root: Path, nodeid: str | None = None) -> list[dict[str, object]]:
    paths = sorted(root.rglob('records.jsonl'))
    if not paths:
        raise SystemExit(f'No records.jsonl files found under {root}')
    rows = []
    for path in paths:
        relative_path = path.relative_to(root)
        artifact = relative_path.parts[0] if len(relative_path.parts) > 2 else '.'
        for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise SystemExit(f'{path}:{lineno}: {error}') from error
            if nodeid and record.get('nodeid') != nodeid:
                continue
            details = record.get('details') or {}
            threads = record.get('thread_environment') or {}
            reference = details.get('snapshot_file') or details.get('checkpoint_file') or ''
            rows.append({
                'nodeid': record.get('nodeid', ''),
                'experiment': record.get('experiment', ''),
                'mode': record.get('mode', ''),
                'status': record.get('status', ''),
                'attempt': record.get('attempt', ''),
                'artifact': artifact,
                'profile': path.parent.name,
                'omp_num_threads': threads.get('OMP_NUM_THREADS', ''),
                'openblas_num_threads': threads.get('OPENBLAS_NUM_THREADS', ''),
                'mkl_num_threads': threads.get('MKL_NUM_THREADS', ''),
                'veclib_maximum_threads': threads.get('VECLIB_MAXIMUM_THREADS', ''),
                'log_file': str(details.get('log_file', '')).replace('\\', '/'),
                'snapshot_or_checkpoint': str(reference).replace('\\', '/'),
                'records_file': relative_path.as_posix(),
            })
    if nodeid and not rows:
        raise SystemExit(f'No records matched nodeid {nodeid!r}')
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, root: Path, rows: list[dict[str, object]]) -> None:
    statuses = Counter(str(row['status']) for row in rows)
    groups = Counter(
        (
            str(row['artifact']),
            str(row['nodeid']),
            str(row['profile']),
            str(row['status']),
        )
        for row in rows
    )
    references = sorted({
        str(row['snapshot_or_checkpoint'])
        for row in rows
        if row['snapshot_or_checkpoint']
    })
    lines = [
        '# Precision artifact report',
        '',
        f'- Artifact root: `{root}`',
        f'- Records: {len(rows)}',
        '',
        '## Status counts',
        '',
        *(f'- `{status}`: {count}' for status, count in sorted(statuses.items())),
        '',
        '## Nodeid and profile counts',
        '',
        '| artifact | nodeid | profile | status | count |',
        '| --- | --- | --- | --- | ---: |',
        *(
            f'| `{artifact}` | `{nodeid}` | `{profile}` | `{status}` | {count} |'
            for (artifact, nodeid, profile, status), count in sorted(groups.items())
        ),
        '',
        '## Snapshot and checkpoint references',
        '',
        *(f'- `{reference}`' for reference in references),
    ]
    if not references:
        lines.append('- None')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> None:
    args = parse_args()
    root = args.artifact_root.resolve()
    rows = read_records(root, args.nodeid)
    for name in ('paired-runs.json', 'summary.csv'):
        if not any(root.rglob(name)):
            print(f'WARNING: no {name} found under {root}', file=sys.stderr)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, root, rows)


if __name__ == '__main__':
    main()
