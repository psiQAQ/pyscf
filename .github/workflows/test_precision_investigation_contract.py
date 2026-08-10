import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SGX_HSE06_TELEMETRY_PREFIX = 'PYSCF_SGX_HSE06_TELEMETRY_V1 '


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding='utf-8')


def load_runner():
    path = ROOT / '.github/workflows/run_precision_tests.py'
    spec = importlib.util.spec_from_file_location('run_precision_tests', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_collector():
    path = ROOT / '.github/workflows/collect_precision_environment.py'
    spec = importlib.util.spec_from_file_location(
        'collect_precision_environment', path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_runtime_snapshot(
        output_dir, *, mode, returncode, pyscf_path, error=None):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'pip-check.txt').write_text(
        'test pip check output\n', encoding='utf-8'
    )
    runtime_path = output_dir / 'runtime.json'
    runtime_path.write_text(json.dumps({
        'schema_version': 2,
        'python': {'executable': sys.executable},
        'key_modules': {
            'pyscf': {'path': str(pyscf_path), 'version': 'test-version'},
        },
        'pip_check': {
            'mode': mode,
            'command': [sys.executable, '-m', 'pip', 'check'],
            'returncode': returncode,
            'error': error,
            'output_file': 'pip-check.txt',
        },
    }), encoding='utf-8')
    return runtime_path


class PrecisionInvestigationContractTest(unittest.TestCase):
    def test_sgx_hse06_telemetry_selection(self):
        runner = load_runner()
        selection = (
            ROOT / '.github/workflows/'
            'precision-libxc-712-sgx-hse06-telemetry-nodeids.txt'
        )
        self.assertEqual(runner.load_nodeids(selection), [
            'pyscf/sgx/grad/test/test_rks.py::KnownValues::'
            'test_finite_diff_grad_settings2_hse06_telemetry',
        ])

    def test_template_selection_is_empty_and_catalogs_unresolved_families(self):
        selection = read('.github/workflows/precision-selected-nodeids.txt')
        active = [
            line.strip() for line in selection.splitlines()
            if line.strip() and not line.lstrip().startswith('#')
        ]
        self.assertEqual(active, [])
        catalog = [
            line.removeprefix('# ') for line in selection.splitlines()
            if line.startswith('# pyscf/')
        ]
        self.assertEqual(len([
            line for line in selection.splitlines() if line.startswith('# Family: ')
        ]), 6)
        self.assertEqual(catalog, [
            'pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_ipccsd',
            'pyscf/cc/test/test_eom_gccsd.py::KnownValues::test_eaccsd',
            'pyscf/mcscf/test/test_h2o.py::KnownValues::test_nosymm_sa4_newton',
            'pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing',
            'pyscf/cc/test/test_rccsd.py::KnownValues::test_update_amps',
            'pyscf/x2c/test/test_x2c.py::KnownValues::test_lindep_xbasis',
            'pyscf/pbc/tdscf/test/test_rks.py::Diamond::test_hse06_tda',
            'pyscf/sgx/grad/test/test_rks.py::KnownValues::test_finite_diff_grad',
            'pyscf/pbc/tdscf/test/test_uks.py::DiamondM06::test_hse03_tda',
        ])

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
        unix_runner = read('.github/workflows/run_unix_precision_tests.sh')
        self.assertIn('--environment-mode source-tree', unix_runner)

    def test_windows_precision_reuses_formal_installed_wheel_path(self):
        runner = read('.github/workflows/run_windows_precision_tests.ps1')
        verify = read('.github/workflows/ci_windows/verify_installed_wheel.ps1')
        self.assertIn('ci_windows\\build_wheel.ps1', runner)
        self.assertIn('ci_windows\\verify_installed_wheel.ps1', runner)
        self.assertIn('--environment-mode installed-wheel', verify)
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

    def test_collector_imports_pyscf_from_working_directory(self):
        runner = load_runner()
        collector = ROOT / '.github/workflows/collect_precision_environment.py'
        with tempfile.TemporaryDirectory() as tmpdir:
            working_directory = Path(tmpdir)
            package = working_directory / 'pyscf'
            package.mkdir()
            existing_pythonpath = working_directory / 'existing-pythonpath'
            existing_pythonpath.mkdir()
            (existing_pythonpath / '_precision_test_support.py').write_text(
                "VERSION = 'source-tree'\n", encoding='utf-8'
            )
            package_init = package / '__init__.py'
            package_init.write_text(
                'from _precision_test_support import VERSION\n'
                '__version__ = VERSION\n',
                encoding='utf-8',
            )
            environment = runner.profile_environment('1', '1')
            environment['PYTHONPATH'] = str(existing_pythonpath)

            runtime_path = runner.collect_environment(
                collector,
                working_directory / 'evidence',
                working_directory,
                environment,
                'source-tree',
            )

            self.assertEqual(environment['PYTHONPATH'], str(existing_pythonpath))
            runtime = json.loads(runtime_path.read_text(encoding='utf-8'))
            self.assertEqual(runtime['schema_version'], 2)
            self.assertEqual(runtime['pip_check']['mode'], 'source-tree')
            self.assertNotIn('pyscf_import_error', runtime)
            self.assertEqual(runtime['key_modules']['pyscf']['version'], 'source-tree')
            self.assertEqual(
                Path(runtime['key_modules']['pyscf']['path']).resolve(),
                package_init.resolve(),
            )

    def test_macos_native_library_linkage_uses_otool_l(self):
        collector = load_collector()
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / 'pyscf'
            libdir = package / 'lib'
            libdir.mkdir(parents=True)
            package_init = package / '__init__.py'
            package_init.write_text('', encoding='utf-8')
            library = libdir / 'libxc_itrf.dylib'
            library.write_bytes(b'test-dylib')

            with mock.patch.object(
                    collector.platform, 'system', return_value='Darwin'
            ), mock.patch.object(
                    collector, 'run_command', return_value={
                        'returncode': 0, 'output': ''
                    }
            ) as run_command:
                collector.native_libraries(
                    SimpleNamespace(__file__=str(package_init))
                )

            run_command.assert_called_once_with(
                ('otool', '-L', str(library.resolve()))
            )

    def test_mode_aware_snapshot_records_pip_check_once(self):
        collector = load_collector()
        commands = []

        def run_command(command):
            command = tuple(command)
            commands.append(command)
            if command == (sys.executable, '-m', 'pip', 'check'):
                return {
                    'returncode': 1,
                    'output': 'broken source-tree metadata\n',
                }
            return {'returncode': 0, 'output': ''}

        with tempfile.TemporaryDirectory() as tmpdir, mock.patch.object(
                collector, 'run_command', side_effect=run_command
        ), mock.patch.object(
                collector, 'capture_show_config', return_value={'output': ''}
        ):
            output_dir = Path(tmpdir)
            collector.write_snapshot(output_dir, 'source-tree')
            runtime = json.loads(
                (output_dir / 'runtime.json').read_text(encoding='utf-8')
            )

            self.assertEqual(runtime['schema_version'], 2)
            self.assertEqual(runtime['pip_check'], {
                'mode': 'source-tree',
                'command': [sys.executable, '-m', 'pip', 'check'],
                'returncode': 1,
                'error': None,
                'output_file': 'pip-check.txt',
            })
            self.assertEqual(
                (output_dir / 'pip-check.txt').read_text(encoding='utf-8'),
                'broken source-tree metadata\n',
            )
            self.assertEqual(
                commands.count((sys.executable, '-m', 'pip', 'check')), 1
            )

    def test_legacy_collect_keeps_schema_version_one(self):
        collector = load_collector()
        with tempfile.TemporaryDirectory() as tmpdir, mock.patch.object(
                collector, 'run_command', return_value={
                    'returncode': 0, 'output': ''
                }
        ), mock.patch.object(
                collector, 'capture_show_config', return_value={'output': ''}
        ):
            runtime_path = Path(tmpdir) / 'runtime.json'
            collector.collect(runtime_path)
            runtime = json.loads(runtime_path.read_text(encoding='utf-8'))

        self.assertEqual(runtime['schema_version'], 1)
        self.assertNotIn('pip_check', runtime)

    def test_source_tree_pip_check_is_advisory(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as tmpdir:
            working_directory = Path(tmpdir)
            package = working_directory / 'pyscf'
            package.mkdir()
            package_init = package / '__init__.py'
            package_init.write_text('', encoding='utf-8')
            runtime_path = write_runtime_snapshot(
                working_directory / 'environment',
                mode='source-tree',
                returncode=1,
                pyscf_path=package_init,
            )

            runtime = runner.validate_environment_snapshot(
                runtime_path, 'source-tree', working_directory
            )

        self.assertEqual(runtime['pip_check']['returncode'], 1)

    def test_installed_wheel_requires_clean_pip_check(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as tmpdir:
            site_packages = Path(tmpdir) / 'venv' / 'Lib' / 'site-packages'
            package = site_packages / 'pyscf'
            package.mkdir(parents=True)
            package_init = package / '__init__.py'
            package_init.write_text('', encoding='utf-8')
            runtime_path = write_runtime_snapshot(
                site_packages / 'environment',
                mode='installed-wheel',
                returncode=1,
                pyscf_path=package_init,
            )

            with self.assertRaisesRegex(RuntimeError, 'pip check'):
                runner.validate_environment_snapshot(
                    runtime_path, 'installed-wheel', site_packages
                )

            runtime_path = write_runtime_snapshot(
                site_packages / 'environment',
                mode='installed-wheel',
                returncode=0,
                pyscf_path=package_init,
            )
            runner.validate_environment_snapshot(
                runtime_path, 'installed-wheel', site_packages
            )

    def test_environment_snapshot_rejects_mode_and_path_mismatch(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as tmpdir:
            working_directory = Path(tmpdir)
            package = working_directory / 'pyscf'
            package.mkdir()
            package_init = package / '__init__.py'
            package_init.write_text('', encoding='utf-8')
            runtime_path = write_runtime_snapshot(
                working_directory / 'environment',
                mode='installed-wheel',
                returncode=0,
                pyscf_path=package_init,
            )

            with self.assertRaisesRegex(RuntimeError, 'mode'):
                runner.validate_environment_snapshot(
                    runtime_path, 'source-tree', working_directory
                )
            with self.assertRaisesRegex(RuntimeError, 'site-packages'):
                runner.validate_environment_snapshot(
                    runtime_path, 'installed-wheel', working_directory
                )

    def test_environment_snapshot_rejects_pip_check_from_other_interpreter(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as tmpdir:
            working_directory = Path(tmpdir)
            package = working_directory / 'pyscf'
            package.mkdir()
            package_init = package / '__init__.py'
            package_init.write_text('', encoding='utf-8')
            runtime_path = write_runtime_snapshot(
                working_directory / 'environment',
                mode='source-tree',
                returncode=0,
                pyscf_path=package_init,
            )
            other_python = working_directory / 'other-python'
            other_python.write_text('', encoding='utf-8')
            runtime = json.loads(runtime_path.read_text(encoding='utf-8'))
            runtime['pip_check']['command'][0] = str(other_python)
            runtime_path.write_text(json.dumps(runtime), encoding='utf-8')

            with self.assertRaisesRegex(RuntimeError, 'interpreter'):
                runner.validate_environment_snapshot(
                    runtime_path, 'source-tree', working_directory
                )

    def test_failed_attempt_keeps_complete_evidence_and_exits_nonzero(self):
        runner = ROOT / '.github/workflows/run_precision_tests.py'
        collector = ROOT / '.github/workflows/collect_precision_environment.py'
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            package = root / 'pyscf'
            package.mkdir()
            (package / '__init__.py').write_text(
                "__version__ = 'source-tree'\n", encoding='utf-8'
            )
            payload = {
                'schema_version': 1,
                'case': {
                    'settings_index': 2,
                    'settings': [True, True, True, True, True],
                    'precision': 6,
                    'xc': 'HSE06',
                    'delta': 1e-4,
                    'translation_places': 12,
                    'finite_difference_places': 6,
                },
                'result': {
                    'translation_assertion_pass': True,
                    'finite_difference_post_pass': False,
                },
            }
            (root / 'test_sample.py').write_text(
                'import json\n'
                f'PREFIX = {SGX_HSE06_TELEMETRY_PREFIX!r}\n'
                f'PAYLOAD = {payload!r}\n'
                'def test_failure():\n'
                '    print(flush=True)\n'
                '    print(PREFIX + json.dumps(PAYLOAD), flush=True)\n'
                '    assert False\n',
                encoding='utf-8',
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
                    '--environment-mode',
                    'source-tree',
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
            attempt_log = (
                output / records[0]['log_file']
            ).read_text(encoding='utf-8')
            markers = [
                line for line in attempt_log.splitlines()
                if line.startswith(SGX_HSE06_TELEMETRY_PREFIX)
            ]
            self.assertEqual(len(markers), 1)
            self.assertEqual(
                json.loads(markers[0][len(SGX_HSE06_TELEMETRY_PREFIX):]),
                {
                    'schema_version': 1,
                    'case': {
                        'settings_index': 2,
                        'settings': [True, True, True, True, True],
                        'precision': 6,
                        'xc': 'HSE06',
                        'delta': 1e-4,
                        'translation_places': 12,
                        'finite_difference_places': 6,
                    },
                    'result': {
                        'translation_assertion_pass': True,
                        'finite_difference_post_pass': False,
                    },
                },
            )
            self.assertTrue((output / 'summary.csv').is_file())
            self.assertTrue((output / 'summary.md').is_file())


if __name__ == '__main__':
    unittest.main()
