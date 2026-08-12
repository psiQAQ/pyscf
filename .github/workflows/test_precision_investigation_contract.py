import contextlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]


FAKE_PYTHON = r'''#!/usr/bin/env bash
set -euo pipefail
: "${FAKE_INVOCATION_RECORD:?}"
: "${FAKE_PYTHON_EXIT:?}"
printf '%s\0' '__CALL__' "$@" >> "$FAKE_INVOCATION_RECORD"
output_count=0
output_dir=
while (($#)); do
  if [[ "$1" == '--output-dir' ]]; then
    output_count=$((output_count + 1))
    shift
    (($#)) || exit 96
    output_dir=$1
  fi
  shift
done
((output_count == 1)) || exit 96
[[ -d "$output_dir" ]] || exit 97
printf '%s\n' 'fake evidence sentinel' > "$output_dir/fake-evidence.txt"
exit "$FAKE_PYTHON_EXIT"
'''


def _is_within(path, parent):
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _probe_bash(candidate, require_msys):
    candidate = Path(candidate).resolve(strict=True)
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        raise RuntimeError(f'Bash is not an executable file: {candidate}')
    result = subprocess.run(
        [str(candidate), '--version'], capture_output=True, text=True,
        shell=False,
    )
    version = (result.stdout + result.stderr).casefold()
    if result.returncode != 0 or 'gnu bash' not in version:
        raise RuntimeError(f'GNU Bash probe failed: {candidate}')
    if require_msys and 'msys' not in version:
        raise RuntimeError(f'MSYS Bash is required on Windows: {candidate}')
    return candidate


def resolve_bash():
    if sys.platform == 'win32':
        discovered_git = shutil.which('git')
        if discovered_git is None:
            raise RuntimeError('git.exe is required to locate MSYS Bash')
        git_path = Path(discovered_git).resolve(strict=True)
        if git_path.name.casefold() != 'git.exe':
            raise RuntimeError(f'Expected git.exe, got {git_path}')
        if not git_path.is_file() or not os.access(git_path, os.X_OK):
            raise RuntimeError(f'git.exe is not executable: {git_path}')
        if git_path.parent.name.casefold() not in ('cmd', 'bin'):
            raise RuntimeError(f'Unexpected Git installation layout: {git_path}')
        system_root = Path(os.environ['SystemRoot']).resolve(strict=True)
        system32 = (system_root / 'System32').resolve(strict=True)
        if _is_within(git_path, system32):
            raise RuntimeError('System32 git.exe is forbidden')
        bash_path = (git_path.parent.parent / 'bin/bash.exe').resolve(strict=True)
        if _is_within(bash_path, system32):
            raise RuntimeError('System32/WSL Bash compatibility shim is forbidden')
        return _probe_bash(bash_path, require_msys=True)
    if sys.platform not in ('linux', 'darwin'):
        raise RuntimeError(f'Unsupported contract-test platform: {sys.platform}')
    discovered_bash = shutil.which('bash')
    if discovered_bash is None:
        raise RuntimeError('GNU Bash is required')
    return _probe_bash(discovered_bash, require_msys=False)


@contextlib.contextmanager
def unix_wrapper_case(fake_exit, output_kind, exit_path_directory=False):
    tmp_parent = ROOT / 'tmp'
    tmp_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=tmp_parent) as tmpdir:
        case_root = Path(tmpdir)
        case_rel = case_root.relative_to(ROOT).as_posix()
        bin_dir = case_root / 'bin'
        bin_dir.mkdir()
        fake_python = bin_dir / 'python'
        fake_python.write_bytes(FAKE_PYTHON.encode('utf-8'))
        fake_bytes = fake_python.read_bytes()
        if b'\x00' in fake_bytes:
            raise AssertionError('fake python contains an embedded NUL')
        if b"printf '%s\\0' '__CALL__' \"$@\"" not in fake_bytes:
            raise AssertionError('fake python lost the literal NUL escape')
        if b"printf '%s\\n' 'fake evidence sentinel'" not in fake_bytes:
            raise AssertionError('fake python lost the literal LF escape')
        fake_python.chmod(
            fake_python.stat().st_mode
            | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        nodeids = case_root / 'nodeids.txt'
        nodeids.write_bytes(
            b'pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing\n'
        )
        output = case_root / 'output'
        if output_kind == 'directory':
            output.mkdir()
        elif output_kind == 'file':
            output.write_bytes(b'not a directory\n')
        elif output_kind != 'missing':
            raise AssertionError(f'unknown output kind: {output_kind}')
        if exit_path_directory:
            if not output.is_dir():
                raise AssertionError(
                    'exit-path directory needs an output directory'
                )
            (output / 'runner-exit-code.txt').mkdir()
        invocation_record = case_root / 'invocations.bin'
        env = os.environ.copy()
        env['PATH'] = str(bin_dir) + os.pathsep + env['PATH']
        env['GITHUB_SHA'] = 'a' * 40
        env['FAKE_PYTHON_EXIT'] = str(fake_exit)
        env['FAKE_INVOCATION_RECORD'] = (
            f'{case_rel}/invocations.bin'
        )
        command = [
            str(resolve_bash()),
            '.github/workflows/run_unix_precision_tests.sh',
            f'{case_rel}/nodeids.txt',
            '1',
            '4/4',
            f'{case_rel}/output',
        ]
        result = subprocess.run(
            command, cwd=ROOT, env=env, capture_output=True, text=True,
            shell=False,
        )
        raw = invocation_record.read_bytes() if invocation_record.exists() else b''
        fields = raw.split(b'\0')
        if fields and fields[-1] == b'':
            fields.pop()
        calls = fields.count(b'__CALL__')
        argv = [field.decode('utf-8') for field in fields[1:]] if calls == 1 else []
        yield SimpleNamespace(
            result=result, calls=calls, argv=argv, output=output,
            exit_path=output / 'runner-exit-code.txt',
            sentinel=output / 'fake-evidence.txt',
            nodeids=f'{case_rel}/nodeids.txt',
            output_arg=f'{case_rel}/output',
        )


def assert_exact_fake_argv(test_case, case):
    test_case.assertEqual(case.calls, 1)
    test_case.assertEqual(case.argv.count('--output-dir'), 1)
    pairs = dict(zip(case.argv[1::2], case.argv[2::2]))
    test_case.assertTrue(
        case.argv[0].replace('\\', '/').endswith(
            '/.github/workflows/run_precision_tests.py'
        )
    )
    test_case.assertEqual(pairs['--nodeids-file'], case.nodeids)
    test_case.assertEqual(pairs['--repeats'], '1')
    test_case.assertEqual(pairs['--profile'], '4/4')
    test_case.assertEqual(pairs['--output-dir'], case.output_arg)
    test_case.assertEqual(pairs['--tested-sha'], 'a' * 40)
    test_case.assertEqual(pairs['--working-directory'], pairs['--rootdir'])
    root = pairs['--rootdir'].replace('\\', '/').rstrip('/')
    test_case.assertEqual(
        case.argv[0].replace('\\', '/'),
        root + '/.github/workflows/run_precision_tests.py',
    )
    test_case.assertEqual(
        pairs['--pytest-config'].replace('\\', '/'), root + '/pytest.ini'
    )
    test_case.assertEqual(pairs['--environment-mode'], 'source-tree')
    test_case.assertEqual(
        pairs['--collector'].replace('\\', '/'),
        root + '/.github/workflows/collect_precision_environment.py',
    )


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

    def test_unix_wrapper_creates_output_directory(self):
        with unix_wrapper_case(0, 'missing') as case:
            assert_exact_fake_argv(self, case)
            self.assertEqual(case.result.returncode, 0, case.result.stderr)
            self.assertEqual(case.sentinel.read_bytes(), b'fake evidence sentinel\n')
            self.assertEqual(case.exit_path.read_bytes(), b'0\n')

    def test_unix_wrapper_records_zero_and_nonzero_runner_exit(self):
        for runner_exit, expected_bytes in ((0, b'0\n'), (23, b'23\n')):
            with self.subTest(runner_exit=runner_exit):
                with unix_wrapper_case(runner_exit, 'directory') as case:
                    assert_exact_fake_argv(self, case)
                    self.assertEqual(case.sentinel.read_bytes(), b'fake evidence sentinel\n')
                    self.assertTrue(case.exit_path.is_file())
                    self.assertEqual(case.exit_path.read_bytes(), expected_bytes)
                    self.assertEqual(case.result.returncode, runner_exit)

    def test_unix_wrapper_rejects_output_file_before_runner(self):
        with unix_wrapper_case(0, 'file') as case:
            self.assertNotEqual(case.result.returncode, 0)
            self.assertEqual(case.calls, 0)
            self.assertTrue(case.output.is_file())

    def test_unix_wrapper_fails_closed_when_exit_path_is_directory(self):
        with unix_wrapper_case(
                0, 'directory', exit_path_directory=True
        ) as case:
            assert_exact_fake_argv(self, case)
            self.assertEqual(case.sentinel.read_bytes(), b'fake evidence sentinel\n')
            self.assertNotEqual(case.result.returncode, 0)
            self.assertTrue(case.exit_path.is_dir())
            self.assertFalse(case.exit_path.is_file())

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
            self.assertTrue((output / 'summary.csv').is_file())
            self.assertTrue((output / 'summary.md').is_file())


if __name__ == '__main__':
    unittest.main()
