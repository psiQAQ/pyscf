"""Stage only tests over a freshly installed wheel, outside the checkout."""
import argparse
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

parser = argparse.ArgumentParser()
parser.add_argument('--full', action='store_true')
args = parser.parse_args()
repo = Path(__file__).resolve().parents[3]
report = repo / 'tmp/ucisd-h4'
report.mkdir(parents=True, exist_ok=True)
run = Path(os.environ['RUNNER_TEMP']) / 'ucisd-installed'
assert not run.exists(), run
assert not run.resolve().is_relative_to(repo)
run.mkdir(parents=True)
env = run / '.venv'
venv.EnvBuilder(with_pip=True).create(env)
python = env / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
config = run / 'pyscf_conf.py'
config.write_text('pbc_tools_pbc_fft_engine = "NUMPY+BLAS"\nscf_hf_SCF_mute_chkfile = True\n', encoding='utf-8')
os.environ['PYSCF_CONFIG_FILE'] = str(config)
for name in ('PYTHONPATH', 'PYSCF_EXT_PATH', 'PYTEST_ADDOPTS', 'PYTEST_PLUGINS'):
    os.environ.pop(name, None)
os.environ.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', OPENBLAS_THREAD_TIMEOUT='4',
                  OMP_WAIT_POLICY='passive', UCISD_REPORT=str(report), UCISD_SOURCE_REPO=str(repo))
results = []


def command(label, cmd, cwd):
    start = time.monotonic()
    with (report / (label + '.log')).open('wb') as stream:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
        print(label, 'pid', proc.pid, flush=True)
        code = proc.wait()
    result = {'label': label, 'command': list(map(str, cmd)), 'cwd': str(cwd),
              'pid': proc.pid, 'exit_code': code, 'seconds': time.monotonic() - start}
    results.append(result)
    (report / 'commands.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(label, code, flush=True)
    return code


wheels = list((repo / 'dist').glob('pyscf-*.whl'))
assert len(wheels) == 1, wheels
wheel = wheels[0]
(report / 'wheel-sha256.txt').write_text(hashlib.sha256(wheel.read_bytes()).hexdigest() + '\n')
deps = ['numpy==2.5.4', 'scipy==1.18.1', 'h5py==3.16.0',
        'pytest==8.4.2', 'pytest-xdist==3.8.0', 'setuptools==84.2.1']
if args.full:
    deps += ['geometric==1.1.1', 'spglib==2.8.0', 'pyberny==0.7.0']
assert command('install', [python, '-B', '-m', 'pip', 'install', str(wheel), *deps], run) == 0
assert command('pip-check', [python, '-B', '-m', 'pip', 'check'], run) == 0
assert command('environment', [python, '-B', '-m', 'pip', 'freeze'], run) == 0
site = Path(subprocess.check_output([python, '-I', '-B', '-c',
            'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip())
package = site / 'pyscf'
source_package = repo / 'pyscf'
tests = sorted(source_package.rglob('test')) if args.full else [source_package / 'ci/test']
for src in tests:
    if not src.is_dir():
        continue
    dst = package / src.relative_to(source_package)
    shutil.copytree(src, dst, dirs_exist_ok=True)
    for directory in [dst, *[p for p in dst.rglob('*') if p.is_dir()]]:
        while directory != package:
            marker = directory / '__init__.py'
            if not marker.exists():
                marker.touch()
            directory = directory.parent
shutil.copy2(Path(__file__).with_name('runtime.py'), site / '_ucisd_runtime.py')
shutil.copy2(repo / 'pytest.ini', report / 'pytest.ini')
for rel in ('ci/ucisd.py', 'ci/cisd.py', 'ci/test/test_ucisd.py', 'cc/uccsd.py',
            'scf/hf.py', 'lib/linalg_helper.py'):
    assert (package / rel).read_bytes() == (source_package / rel).read_bytes(), rel
identity = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
(report / 'commit.txt').write_text(identity + '\n')
smoke = ('import os,pathlib,pyscf,sys; p=pathlib.Path(pyscf.__file__).resolve(); '
         'print(sys.version); print(p); assert "site-packages" in str(p); '
         'source=pathlib.Path(os.environ["UCISD_SOURCE_REPO"]).resolve(); '
         'assert all(pathlib.Path(x or ".").resolve()!=source for x in sys.path); '
         'from pyscf import gto,scf; from pyscf.dft import libxc,xcfun; '
         'assert abs(scf.RHF(gto.M(atom="H 0 0 0; H 0 0 1.4",unit="Bohr",'
         'basis="sto-3g",verbose=0)).kernel()+1.116714325062551)<1e-9')
assert command('import-smoke', [python, '-I', '-B', '-c', smoke], site) == 0
base = [python, '-B', '-m', 'pytest', '-s', '-v', '-c', str(repo / 'pytest.ini'),
        '--rootdir', '.', '--import-mode=prepend', '-p', 'no:cacheprovider']
for label, targets, extra in (
    ('regression', ['pyscf/ci/test/test_ucisd.py::KnownValues::test_contract_empty_spin_channel'], []),
    ('isolated-h4', ['pyscf/ci/test/test_ucisd.py::KnownValues::test_h4'], []),
    ('whole-ucisd', ['pyscf/ci/test/test_ucisd.py'], []),
    ('full-runtime' if args.full else 'ci-runtime', ['pyscf' if args.full else 'pyscf/ci/test'],
     ['-p', '_ucisd_runtime', '-p', 'xdist', '-n', '2', '--dist', 'loadfile']),
):
    junit = report / (label + '.xml')
    command(label, base + targets + extra + ['--junitxml=' + str(junit)], site)
    root = ET.parse(junit).getroot()
    expected_node = 'test_contract_empty_spin_channel' if label == 'regression' else 'test_h4'
    h4 = [t for t in root.iter('testcase') if t.get('name') == expected_node
          and t.get('classname') == 'pyscf.ci.test.test_ucisd.KnownValues']
    assert len(h4) == 1, (label, 'target absent or ambiguous')
    assert h4[0].find('skipped') is None, (label, 'target skipped')
    results[-1]['target'] = {'node': expected_node, 'executed': True, 'failed': h4[0].find('failure') is not None,
                         'skipped': h4[0].find('skipped') is not None,
                         'seconds': h4[0].get('time')}
    (report / 'commands.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
manifest = {str(p.relative_to(report)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(report.rglob('*')) if p.is_file()}
(report / 'sha256.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
raise SystemExit(any(r['exit_code'] for r in results))
