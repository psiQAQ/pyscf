import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding='utf-8')


def load_runner():
    path = ROOT / '.github/workflows/run_precision_tests.py'
    spec = importlib.util.spec_from_file_location('run_precision_tests', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PrecisionInvestigationContractTest(unittest.TestCase):
    def test_template_selection_is_empty_and_case_neutral(self):
        selection = read('.github/workflows/precision-selected-nodeids.txt')
        active = [
            line.strip() for line in selection.splitlines()
            if line.strip() and not line.lstrip().startswith('#')
        ]
        self.assertEqual(active, [])
        for historical_case in (
            'test_nosymm_sa4_newton',
            'test_uhf_smearing',
            'test_finite_diff_grad',
            'test_update_amps',
            'test_lindep_xbasis',
        ):
            self.assertNotIn(historical_case, selection)

    def test_workflow_requires_explicit_generic_inputs_and_always_uploads(self):
        workflow = read('.github/workflows/ci-precision-check.yml')
        for value in (
            'workflow_dispatch:',
            'nodeids_file:',
            'repeats:',
            'platform:',
            'python_version:',
            'profile:',
            '1/1',
            '4/1',
            '1/4',
            '4/4',
            'if: always()',
            'actions/upload-artifact@v7',
        ):
            self.assertIn(value, workflow)
        self.assertNotIn('matrix:', workflow)
        self.assertNotIn('shard', workflow.lower())

    def test_windows_precision_reuses_formal_installed_wheel_path(self):
        runner = read('.github/workflows/run_windows_precision_tests.ps1')
        self.assertIn('ci_windows\\build_wheel.ps1', runner)
        self.assertIn('ci_windows\\verify_installed_wheel.ps1', runner)
        for obsolete in (
            'verify_installed_wheel_ci.ps1',
            'create_build_env.ps1',
            'build_pyscf.ps1',
            'tools/windows',
        ):
            self.assertNotIn(obsolete, runner)

    def test_formal_windows_default_has_no_precision_exceptions(self):
        workflow = read('.github/workflows/ci-windows.yml')
        verify = read('.github/workflows/ci_windows/verify_installed_wheel.ps1')
        self.assertIn('verify_installed_wheel.ps1', workflow)
        self.assertNotIn('precision-selected-nodeids', workflow)
        for forbidden in ('--deselect', 'retry'):
            self.assertNotIn(forbidden, workflow.lower())
            self.assertNotIn(forbidden, verify.lower())

    def test_selection_validation_rejects_empty_duplicates_and_bad_values(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'nodeids.txt'
            path.write_text('# fill this in a child branch\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'at least one nodeid'):
                runner.load_nodeids(path)
            path.write_text('a.py::test_x\na.py::test_x\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Duplicate nodeid'):
                runner.load_nodeids(path)
        with self.assertRaisesRegex(ValueError, 'profile'):
            runner.parse_profile('2/2')
        with self.assertRaisesRegex(ValueError, 'positive integer'):
            runner.validate_repeats(0)

    def test_runner_records_required_evidence_without_retry_or_deselect(self):
        runner = read('.github/workflows/run_precision_tests.py')
        for field in (
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
        ):
            self.assertIn(field, runner)
        self.assertNotIn('--deselect', runner)
        self.assertNotIn('retry', runner.lower())

    def test_failed_attempt_keeps_complete_evidence_and_exits_nonzero(self):
        runner = ROOT / '.github/workflows/run_precision_tests.py'
        collector = ROOT / '.github/workflows/collect_precision_environment.py'
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / 'test_sample.py').write_text(
                'def test_failure():\n    assert False\n', encoding='utf-8'
            )
            nodeids = root / 'nodeids.txt'
            nodeids.write_text(
                'test_sample.py::test_failure\n', encoding='utf-8'
            )
            config = root / 'pytest.ini'
            config.write_text('[pytest]\n', encoding='utf-8')
            output = root / 'evidence'

            result = subprocess.run(
                [
                    sys.executable,
                    str(runner),
                    '--nodeids-file',
                    str(nodeids),
                    '--repeats',
                    '1',
                    '--profile',
                    '1/1',
                    '--output-dir',
                    str(output),
                    '--tested-sha',
                    'test-sha',
                    '--working-directory',
                    str(root),
                    '--rootdir',
                    str(root),
                    '--pytest-config',
                    str(config),
                    '--collector',
                    str(collector),
                ],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            records = [
                json.loads(line)
                for line in (output / 'records.jsonl').read_text(
                    encoding='utf-8'
                ).splitlines()
            ]
            self.assertEqual(records[0]['status'], 'fail')
            for field in (
                'log_file', 'environment_file', 'nodeids_file'
            ):
                self.assertTrue((output / records[0][field]).is_file())
            self.assertTrue((output / 'summary.csv').is_file())
            self.assertTrue((output / 'summary.md').is_file())


if __name__ == '__main__':
    unittest.main()
