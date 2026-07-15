import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name('report_precision_artifacts.py')


def write_records(root, records, artifact=None, profile='omp1-blas1'):
    directory = root / profile if artifact is None else root / artifact / profile
    directory.mkdir(parents=True)
    (directory / 'records.jsonl').write_text(
        ''.join(json.dumps(record) + '\n' for record in records),
        encoding='utf-8',
    )
    return directory


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
    def test_cli_summarizes_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact = 'precision-thread-paired-sgx-windows-py3.13'
            records = [
                {
                    'attempt': 1,
                    'experiment': 'sgx',
                    'mode': 'settings-2',
                    'nodeid': 'pyscf/test.py::KnownValues::test_case',
                    'status': 'pass',
                    'thread_environment': {
                        'OMP_NUM_THREADS': '4',
                        'OPENBLAS_NUM_THREADS': '4',
                    },
                    'details': {'log_file': 'logs/pass.log'},
                },
                {
                    'attempt': 2,
                    'experiment': 'sgx',
                    'mode': 'settings-2',
                    'nodeid': 'pyscf/test.py::KnownValues::test_case',
                    'status': 'reference_mismatch',
                    'thread_environment': {
                        'OMP_NUM_THREADS': '4',
                        'OPENBLAS_NUM_THREADS': '4',
                    },
                    'details': {
                        'log_file': 'logs/fail.log',
                        'snapshot_file': 'snapshots/first-failure.npz',
                    },
                },
            ]
            profile = write_records(root, records, artifact, 'omp4-blas4')
            snapshot = profile / 'snapshots' / 'first-failure.npz'
            snapshot.parent.mkdir()
            snapshot.touch()
            (root / 'paired-runs.json').write_text('{}', encoding='utf-8')
            (profile / 'summary.csv').write_text('status,count\npass,1\n', encoding='utf-8')

            result, output_md, output_csv = run_cli(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            with output_csv.open(encoding='utf-8', newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[1]['artifact'], artifact)
            self.assertEqual(rows[1]['profile'], 'omp4-blas4')
            self.assertEqual(rows[1]['omp_num_threads'], '4')
            self.assertEqual(
                rows[1]['snapshot_or_checkpoint'],
                'snapshots/first-failure.npz',
            )
            report = output_md.read_text(encoding='utf-8')
            self.assertIn('`pass`: 1', report)
            self.assertIn('`reference_mismatch`: 1', report)

    def test_cli_filters_nodeid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_records(root, [
                {'nodeid': 'pyscf/test.py::test_keep', 'status': 'pass', 'details': {}},
                {'nodeid': 'pyscf/test.py::test_drop', 'status': 'pass', 'details': {}},
            ])

            result, _, output_csv = run_cli(
                root, '--nodeid', 'pyscf/test.py::test_keep'
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            with output_csv.open(encoding='utf-8', newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row['nodeid'] for row in rows], ['pyscf/test.py::test_keep'])

    def test_cli_fails_without_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result, _, _ = run_cli(Path(tmpdir))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('No records.jsonl files found', result.stderr)

    def test_cli_reports_invalid_json_location(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            directory = root / 'omp1-blas1'
            directory.mkdir()
            (directory / 'records.jsonl').write_text('{bad json}\n', encoding='utf-8')

            result, _, _ = run_cli(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('records.jsonl:1:', result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_cli_warns_when_optional_summaries_are_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_records(root, [
                {'nodeid': 'pyscf/test.py::test_case', 'status': 'pass', 'details': {}},
            ])

            result, _, _ = run_cli(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('WARNING: no paired-runs.json found', result.stderr)
            self.assertIn('WARNING: no summary.csv found', result.stderr)

    def test_cli_fails_when_nodeid_does_not_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_records(root, [
                {'nodeid': 'pyscf/test.py::test_present', 'status': 'pass', 'details': {}},
            ])

            result, _, _ = run_cli(
                root, '--nodeid', 'pyscf/test.py::test_missing'
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('No records matched nodeid', result.stderr)


if __name__ == '__main__':
    unittest.main()
