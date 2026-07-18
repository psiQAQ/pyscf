import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name('report_precision_artifacts.py')
REQUIRED = {
    'tested_sha': 'abc123',
    'nodeid': 'pyscf/test.py::test_case',
    'attempt': 1,
    'profile': 'omp1-blas1',
    'status': 'pass',
    'duration_seconds': 1.25,
    'pytest_summary': '1 passed in 1.25s',
    'log_file': 'logs/attempt-0001.log',
    'environment_file': 'environment/runtime.json',
    'nodeids_file': 'selected-nodeids.txt',
}


def write_artifact(root, records):
    artifact = root / 'precision-windows-py3.13-omp1-blas1'
    (artifact / 'logs').mkdir(parents=True)
    (artifact / 'environment').mkdir()
    (artifact / 'logs/attempt-0001.log').write_text('ok\n', encoding='utf-8')
    (artifact / 'environment/runtime.json').write_text('{}\n', encoding='utf-8')
    (artifact / 'selected-nodeids.txt').write_text(
        'pyscf/test.py::test_case\n', encoding='utf-8'
    )
    (artifact / 'records.jsonl').write_text(
        ''.join(json.dumps(record) + '\n' for record in records),
        encoding='utf-8',
    )
    return artifact


def run_cli(root, *extra):
    output_md = root / 'report.md'
    output_csv = root / 'records.csv'
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            '--artifact-root',
            str(root),
            '--output-md',
            str(output_md),
            '--output-csv',
            str(output_csv),
            *extra,
        ],
        capture_output=True,
        text=True,
    )
    return result, output_md, output_csv


class ReportPrecisionArtifactsTests(unittest.TestCase):
    def test_cli_validates_and_summarizes_complete_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_artifact(root, [REQUIRED])

            result, output_md, output_csv = run_cli(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            with output_csv.open(encoding='utf-8', newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['tested_sha'], 'abc123')
            self.assertEqual(rows[0]['artifact'], 'precision-windows-py3.13-omp1-blas1')
            report = output_md.read_text(encoding='utf-8')
            self.assertIn('`pass`: 1', report)
            self.assertIn('Evidence references: 3/3 present', report)

    def test_cli_filters_nodeid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            other = dict(REQUIRED, nodeid='pyscf/test.py::test_other', attempt=2)
            write_artifact(root, [REQUIRED, other])

            result, _, output_csv = run_cli(
                root, '--nodeid', 'pyscf/test.py::test_case'
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            with output_csv.open(encoding='utf-8', newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row['nodeid'] for row in rows], [REQUIRED['nodeid']])

    def test_cli_fails_without_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result, _, _ = run_cli(Path(tmpdir))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('No records.jsonl files found', result.stderr)

    def test_cli_rejects_missing_required_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            record = dict(REQUIRED)
            del record['tested_sha']
            write_artifact(root, [record])

            result, _, _ = run_cli(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('missing required field', result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_cli_rejects_missing_evidence_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact = write_artifact(root, [REQUIRED])
            (artifact / 'logs/attempt-0001.log').unlink()

            result, _, _ = run_cli(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('missing evidence file', result.stderr)

    def test_cli_reports_invalid_json_location(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact = root / 'artifact'
            artifact.mkdir()
            (artifact / 'records.jsonl').write_text('{bad json}\n', encoding='utf-8')

            result, _, _ = run_cli(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('records.jsonl:1:', result.stderr)
            self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
