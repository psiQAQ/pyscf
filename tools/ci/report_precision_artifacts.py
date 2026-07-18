"""Validate and summarize generic precision-investigation records."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


REQUIRED_FIELDS = (
    'tested_sha', 'nodeid', 'attempt', 'profile', 'status',
    'duration_seconds', 'pytest_summary', 'log_file',
    'environment_file', 'nodeids_file',
)
FIELDS = ('artifact', *REQUIRED_FIELDS, 'records_file')
REFERENCE_FIELDS = ('log_file', 'environment_file', 'nodeids_file')


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-root', required=True, type=Path)
    parser.add_argument('--output-md', required=True, type=Path)
    parser.add_argument('--output-csv', required=True, type=Path)
    parser.add_argument('--nodeid')
    return parser.parse_args()


def fail(message):
    raise SystemExit(message)


def validate_reference(records_path, field, value):
    reference = Path(str(value))
    if reference.is_absolute() or '..' in reference.parts:
        fail(f'{records_path}: invalid relative evidence path in {field}: {value}')
    path = records_path.parent / reference
    if not path.is_file():
        fail(f'{records_path}: missing evidence file for {field}: {value}')


def read_records(root, nodeid=None):
    paths = sorted(root.rglob('records.jsonl'))
    if not paths:
        fail(f'No records.jsonl files found under {root}')
    rows = []
    for path in paths:
        relative_path = path.relative_to(root)
        artifact = relative_path.parts[0] if len(relative_path.parts) > 1 else '.'
        for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                fail(f'{path}:{lineno}: {error}')
            for field in REQUIRED_FIELDS:
                if field not in record or record[field] in (None, ''):
                    fail(f'{path}:{lineno}: missing required field {field}')
            for field in REFERENCE_FIELDS:
                validate_reference(path, field, record[field])
            if nodeid and record['nodeid'] != nodeid:
                continue
            rows.append({
                'artifact': artifact,
                **{field: record[field] for field in REQUIRED_FIELDS},
                'records_file': relative_path.as_posix(),
            })
    if nodeid and not rows:
        fail(f'No records matched nodeid {nodeid!r}')
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path, root, rows):
    statuses = Counter(str(row['status']) for row in rows)
    groups = Counter(
        (str(row['artifact']), str(row['nodeid']), str(row['profile']), str(row['status']))
        for row in rows
    )
    reference_count = len(rows) * len(REFERENCE_FIELDS)
    lines = [
        '# Precision artifact report',
        '',
        f'- Artifact root: `{root}`',
        f'- Records: {len(rows)}',
        f'- Evidence references: {reference_count}/{reference_count} present',
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
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    args = parse_args()
    root = args.artifact_root.resolve()
    rows = read_records(root, args.nodeid)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, root, rows)


if __name__ == '__main__':
    main()
