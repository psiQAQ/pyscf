"""Build provenance and explicit, bounded SGX acceptance on a temporary runner."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
VALIDATION = HERE.parents[2]
CONFIG = json.loads((HERE / 'config.json').read_text())
INPUTS = ['pyscf', 'setup.py', 'pyproject.toml', 'MANIFEST.in', '.gitattributes', 'pytest.ini',
          '.github/workflows/ci_windows', '.github/workflows/ci_linux']


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['prepare', 'run'])
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    output = args.output.resolve()
    evidence = output / 'evidence'
    if args.phase == 'prepare':
        output.mkdir(parents=True, exist_ok=False)
        evidence.mkdir()
        scratch = output / 'scratch'
        scratch.mkdir()
        with Path(os.environ['GITHUB_ENV']).open('a', encoding='utf-8') as env_file:
            for key in ['TMP', 'TEMP', 'TMPDIR', 'PYSCF_TMPDIR']:
                env_file.write(key + '=' + str(scratch) + '\n')
        source_sha = git(candidate, 'rev-parse', 'HEAD')
        assert source_sha == CONFIG['science_sha']
        source_manifest = git(candidate, 'ls-tree', '-r', 'HEAD', '--', *INPUTS)
        validation_manifest = git(VALIDATION, 'ls-tree', '-r', 'HEAD', '--', *INPUTS)
        assert source_manifest == validation_manifest, 'Scientific/test/build inputs differ'
        metadata = {'science_sha': source_sha, 'validation_sha': git(VALIDATION, 'rev-parse', 'HEAD'),
                    'config': CONFIG, 'source_manifest': source_manifest.splitlines(),
                    'validation_manifest': validation_manifest.splitlines(),
                    'source_equivalence': 'Passed', 'runner_os': os.environ.get('RUNNER_OS'),
                    'image_os': os.environ.get('ImageOS'), 'image_version': os.environ.get('ImageVersion'),
                    'tool_files': {str(p.relative_to(HERE)): sha256(p) for p in sorted(HERE.glob('*')) if p.is_file()},
                    'workflow_sha256': sha256(HERE.parent / 'sgx-validation.yml')}
        write_json(evidence / 'provenance.json', metadata)
        shutil.copytree(HERE, evidence / 'tools')
        shutil.copy2(HERE.parent / 'sgx-validation.yml', evidence / 'sgx-validation.yml')
        return 0

    assert evidence.is_dir()
    for key in ['RUNNER_TEMP', 'TMP', 'TEMP', 'TMPDIR', 'PYSCF_TMPDIR']:
        os.environ[key] = str(output / 'scratch')
    commands = []

    def run(label, command, cwd=output):
        row = {'label': label, 'command': list(map(str, command)), 'cwd': str(cwd),
               'started_unix': time.time()}
        with (evidence / (label + '.stdout.log')).open('wb') as stdout, \
                (evidence / (label + '.stderr.log')).open('wb') as stderr:
            proc = subprocess.Popen(row['command'], cwd=cwd, stdout=stdout, stderr=stderr)
            row['pid'] = proc.pid
            commands.append(row)
            write_json(evidence / 'commands.json', commands)
            row['exit_code'] = proc.wait()
        row['finished_unix'] = time.time()
        write_json(evidence / 'commands.json', commands)
        if row['exit_code']:
            raise RuntimeError('%s failed with exit code %s; original logs retained' % (label, row['exit_code']))

    try:
        assert git(candidate, 'rev-parse', 'HEAD') == CONFIG['science_sha']
        assert not git(candidate, 'diff', '--name-only', 'HEAD', '--', *INPUTS)
        if os.name == 'nt':
            wheels = list((candidate / 'dist').glob('pyscf-*.whl'))
            assert len(wheels) == 1, wheels
            wheel = wheels[0]
            wheel_out = evidence / 'wheel'
            wheel_out.mkdir()
            shutil.copy2(wheel, wheel_out / wheel.name)
            write_json(evidence / 'wheel.json', {'name': wheel.name, 'sha256': sha256(wheel),
                       'size': wheel.stat().st_size, 'science_sha': CONFIG['science_sha']})
            venv = output / '.venv'
            run('create-venv', [sys.executable, '-I', '-B', '-m', 'venv', str(venv)])
            python = venv / 'Scripts/python.exe'
            run('install-wheel', [python, '-I', '-B', '-m', 'pip', 'install', '--report',
                                  evidence / 'install-report.json', wheel])
            run('pip-check', [python, '-I', '-B', '-m', 'pip', 'check'])
            source_args = []
            repeats = CONFIG['windows_attempts']
        else:
            python = sys.executable
            source_args = ['--source', str(candidate)]
            repeats = CONFIG['linux_attempts']
            native_files = sorted((candidate / 'pyscf/lib').glob('*.so'))
            native_files += sorted((candidate / 'pyscf/lib/deps/lib').glob('*.so*'))
            write_json(evidence / 'native-libraries.json', {str(p.relative_to(candidate)): sha256(p)
                       for p in native_files if p.is_file()})
        results = []
        for suite in CONFIG['suites']:
            expected_tests = {'lifecycle': 4, 'forwarding': 4, 'rks': 1, 'uks': 1, 'sgx': 8}[suite]
            count = repeats if suite == 'rks' else 1
            result_dir = evidence / suite
            run('tests-' + suite, [python, '-I', '-B', HERE / 'validate.py', '--test-root', candidate,
                '--source-sha', CONFIG['science_sha'], '--suite', suite, '--attempts', str(count),
                '--output', result_dir] + source_args)
            summary = json.loads((result_dir / 'summary.json').read_text())
            assert summary['result'] == 'Passed' and len(summary['attempts']) == count
            for i in range(1, count + 1):
                attempt = json.loads((result_dir / ('attempt-%04d' % i) / 'result.json').read_text())
                assert attempt['tests_run'] == attempt['expected_tests'] == expected_tests
                assert not attempt['skipped'] and not attempt['failures'] and not attempt['errors']
                assert attempt['source_sha'] == CONFIG['science_sha']
                assert attempt['openmp_threads'] == 4
                assert attempt['thread_queries'] and all(item['getters'] for item in attempt['thread_queries'])
                if suite in ['rks', 'uks']:
                    assert len(attempt['gradient_cases']) == 9
            results.append({'suite': suite, 'attempts': count, 'result': 'Passed'})
        write_json(evidence / 'acceptance.json', {'result': 'Passed', 'science_sha': CONFIG['science_sha'],
                   'config': CONFIG, 'suites': results, 'commands': commands})
        return 0
    except Exception:
        write_json(evidence / 'acceptance.json', {'result': 'Failed', 'science_sha': CONFIG['science_sha'],
                   'config': CONFIG, 'exception': traceback.format_exc(), 'commands': commands})
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
