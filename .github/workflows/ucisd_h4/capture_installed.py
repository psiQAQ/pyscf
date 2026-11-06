"""Reuse the preserved Windows wheel; stop at first H4 failure or 100 processes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import venv
import xml.etree.ElementTree as ET

repo = Path(__file__).resolve().parents[3]
report = repo / 'tmp/ucisd-h4-capture'
report.mkdir(parents=True, exist_ok=False)
assert sys.platform == 'win32' and sys.version_info[:3] == (3, 13, 17)
run = Path(os.environ['RUNNER_TEMP']) / 'installed'
assert not run.resolve().is_relative_to(repo)
run.mkdir(parents=True, exist_ok=False)
commands = []


def command(label, cmd, cwd):
    start = time.monotonic()
    with (report / (label + '.log')).open('wb') as stream:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
        print(label, 'pid', proc.pid, flush=True)
        code = proc.wait()
    commands.append({'label': label, 'command': list(map(str, cmd)), 'cwd': str(cwd),
                     'pid': proc.pid, 'exit_code': code, 'seconds': time.monotonic() - start})
    (report / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n', encoding='utf-8')
    return code


wheels = list((repo / 'tmp/ucisd-h4-input').glob('*.whl'))
assert len(wheels) == 1, wheels
wheel = wheels[0]
wheel_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
assert wheel_sha == '695314b64ab0afc32793f8504ac093844f536d260337c1028828c28053d7f352'
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
(report / 'input.json').write_text(json.dumps({'diagnostic_commit': commit,
    'wheel_source_commit': 'c05e968f4bd46d3f3eb1d99d11ca7fe9967e5c63',
    'wheel_source_run': 42281855545, 'wheel_source_artifact': 13538202274,
    'wheel_sha256': wheel_sha, 'maximum_h4_processes': 100}, indent=2) + '\n', encoding='utf-8')
env = run / '.venv'
venv.EnvBuilder(with_pip=True).create(env)
python = env / 'Scripts/python.exe'
config = run / 'pyscf_conf.py'
config.write_text('pbc_tools_pbc_fft_engine = "NUMPY+BLAS"\nscf_hf_SCF_mute_chkfile = True\n', encoding='utf-8')
os.environ['PYSCF_CONFIG_FILE'] = str(config)
for name in ('PYTHONPATH', 'PYSCF_EXT_PATH', 'PYTEST_ADDOPTS', 'PYTEST_PLUGINS'):
    os.environ.pop(name, None)
os.environ.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', OPENBLAS_THREAD_TIMEOUT='4',
                  OMP_WAIT_POLICY='passive')
# Same existing-flow dependencies as the failed wheel's original installed run.
deps = ['numpy==2.5.4', 'scipy==1.18.1', 'h5py==3.16.0', 'pytest==8.4.2',
        'pytest-xdist==3.8.0', 'setuptools==84.2.1', 'geometric==1.1.1',
        'spglib==2.8.0', 'pyberny==0.7.0']
assert command('install', [python, '-B', '-m', 'pip', 'install', str(wheel), *deps], run) == 0
assert command('pip-check', [python, '-B', '-m', 'pip', 'check'], run) == 0
assert command('environment', [python, '-B', '-m', 'pip', 'freeze'], run) == 0
site = Path(subprocess.check_output([python, '-I', '-B', '-c',
            'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip())
package = site / 'pyscf'
shutil.copytree(repo / 'pyscf/ci/test', package / 'ci/test', dirs_exist_ok=True)
(package / 'ci/test/__init__.py').touch(exist_ok=True)
shutil.copy2(Path(__file__).with_name('postmortem.py'), site / '_ucisd_postmortem.py')
shutil.copy2(repo / 'pytest.ini', report / 'pytest.ini')
for rel in ('ci/ucisd.py', 'ci/cisd.py', 'ci/test/test_ucisd.py', 'cc/uccsd.py',
            'scf/hf.py', 'lib/linalg_helper.py'):
    assert (package / rel).read_bytes() == (repo / 'pyscf' / rel).read_bytes(), rel
base = [python, '-B', '-m', 'pytest', '-s', '-v', '-c', str(repo / 'pytest.ini'),
        '--rootdir', '.', '--import-mode=prepend', '-p', 'no:cacheprovider',
        '-p', '_ucisd_postmortem', 'pyscf/ci/test/test_ucisd.py::KnownValues::test_h4']
outcomes = []
for attempt in range(1, 101):
    label = f'h4-{attempt:02d}'
    case = report / label
    case.mkdir()
    os.environ['UCISD_FAILURE_DIR'] = str(case / 'failure')
    xml = case / 'pytest.xml'
    code = command(label, base + ['--junitxml=' + str(xml)], site)
    root = ET.parse(xml).getroot()
    tests = list(root.iter('testcase'))
    assert len(tests) == 1 and tests[0].get('name') == 'test_h4'
    assert tests[0].get('classname') == 'pyscf.ci.test.test_ucisd.KnownValues'
    test = tests[0]
    failure = test.find('failure') is not None or test.find('error') is not None
    skipped = test.find('skipped') is not None
    captured = all((case / 'failure' / name).is_file() for name in
                   ('frames.json', 'arrays.npz', 'environment.json', 'exception.txt'))
    capture_error = (case / 'failure/capture-error.txt').exists()
    outcomes.append({'attempt': attempt, 'exit_code': code, 'failed': failure,
                     'skipped': skipped, 'failure_captured': captured,
                     'capture_error': capture_error})
    (report / 'outcomes.json').write_text(json.dumps(outcomes, indent=2) + '\n', encoding='utf-8')
    if code or failure or skipped:
        print('Stopped at', label, 'captured', captured, 'capture_error', capture_error, flush=True)
        raise SystemExit(code or 1)
    assert not (case / 'failure').exists(), 'Successful test unexpectedly wrote a snapshot'
print('Reached 100 passing H4 processes; no failure captured.', flush=True)
