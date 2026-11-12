"""Build the installed-wheel environment used by the UCISD repeat diagnostic.

The measured package is the *released* wheel, because that is what the failing CI
installed.  In ``wheel`` mode nothing in the wheel is touched, so the repeat loop
measures the unpatched code.  In ``overlay`` mode the checkout's pure-Python
files are copied over the wheel (same compiled extensions), which isolates the
effect of the Python-level change from any build difference.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import venv
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RUNNER_TEMP = Path(os.environ.get('RUNNER_TEMP') or REPO / 'tmp')
OUT = REPO / 'tmp' / 'ucisd-repeat'
TAG = platform.system().lower()

PYSCF_VERSION = os.environ.get('PYSCF_VERSION', '2.15.0')
NUMPY_VERSION = os.environ.get('NUMPY_VERSION', '2.5.4')
PYTEST_VERSION = os.environ.get('PYTEST_VERSION', '8.4.2')
MODE = os.environ.get('UCISD_MODE', 'wheel')

# Pure-Python files that carry the fix.  Only these are overlaid; compiled
# extensions keep coming from the wheel so both modes share the same binary.
OVERLAY = (
    'pyscf/lib/numpy_helper.py',
    'pyscf/ci/ucisd.py',
    'pyscf/ci/cisd.py',
    'pyscf/cc/uccsd.py',
)

# Test files always come from the checkout; they define the node under test.
TESTS = (('pyscf/ci/test/test_ucisd.py', 'copy'),
         ('pyscf/ci/test/__init__.py', 'ensure'))

CONF = '''\
pbc_tools_pbc_fft_engine = "NUMPY+BLAS"
scf_hf_SCF_mute_chkfile = True
'''


def run(command, cwd=None, env=None):
    print('+', ' '.join(str(x) for x in command), flush=True)
    subprocess.run([str(x) for x in command], cwd=cwd, env=env, check=True)


def sha256(path):
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_env(variables):
    text = ''.join('{}={}\n'.format(k, v) for k, v in variables.items())
    target = os.environ.get('GITHUB_ENV')
    if target:
        with open(target, 'a', encoding='utf-8') as handle:
            handle.write(text)
    print(text, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reuse', action='store_true', help='reuse an existing venv')
    args = parser.parse_args()

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    root = RUNNER_TEMP / ('ucisd-repeat-{}'.format(TAG))
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    env = dict(os.environ)
    env.pop('PYTHONPATH', None)

    # The venv lives outside the checkout so that neither the repository nor its
    # tmp/ tree can end up on the import path of the measured interpreter.
    venv_dir = root / '.venv'
    if not (args.reuse and (venv_dir / 'pyvenv.cfg').is_file()):
        venv.EnvBuilder(with_pip=True, symlinks=False).create(str(venv_dir))
    python = venv_dir / ('Scripts/python.exe' if TAG == 'windows' else 'bin/python')

    run([python, '-m', 'pip', 'install', '--disable-pip-version-check',
         '--no-input', '--upgrade', 'pip'], env=env)

    # Binary wheels only: the measured code must be the released one, and a
    # source build would silently substitute the checkout's sources instead.
    wheels = ['pyscf=={}'.format(PYSCF_VERSION), 'numpy=={}'.format(NUMPY_VERSION)]
    run([python, '-m', 'pip', 'install', '--disable-pip-version-check',
         '--no-input', '--only-binary=:all:'] + wheels, env=env)
    run([python, '-m', 'pip', 'install', '--disable-pip-version-check',
         '--no-input', 'scipy', 'h5py', 'setuptools',
         'pytest=={}'.format(PYTEST_VERSION)], env=env)

    installed = subprocess.check_output(
        [str(python), '-B', '-c',
         'import numpy, pyscf; print(numpy.__version__, pyscf.__version__)'],
        text=True, env=env).split()
    assert installed == [NUMPY_VERSION, PYSCF_VERSION], installed

    site = Path(subprocess.check_output(
        [str(python), '-c',
         'import sysconfig; print(sysconfig.get_paths()["purelib"])'],
        text=True, env=env).strip())
    package = site / 'pyscf'
    assert package.is_dir(), package

    copied = {}
    for rel, how in TESTS:
        source = REPO / rel
        target = site / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if how == 'copy' and source.is_file():
            shutil.copy2(source, target)
            copied[rel] = {'sha256': sha256(source), 'origin': 'checkout'}
        elif how == 'ensure' and not target.is_file():
            # The wheel omits the test tree; pytest needs the package marker so
            # the module name does not collide with the other test packages.
            target.write_text('', encoding='utf-8')
            copied[rel] = {'sha256': sha256(source) if source.is_file() else None,
                           'origin': 'created-empty'}

    # Hash both sides in every mode: the artifact then proves exactly which
    # wheel files differ from the checkout before any overlay is applied.
    for rel in OVERLAY:
        source = REPO / rel
        target = site / rel
        checkout_hash = sha256(source) if source.is_file() else None
        wheel_hash = sha256(target) if target.is_file() else None
        if checkout_hash == wheel_hash:
            copied[rel] = {'sha256': wheel_hash, 'wheel_sha256': wheel_hash,
                           'origin': 'identical'}
            continue
        if MODE != 'overlay':
            copied[rel] = {'sha256': None, 'wheel_sha256': wheel_hash,
                           'checkout_sha256': checkout_hash,
                           'origin': 'wheel-kept'}
            continue
        shutil.copy2(source, target)
        copied[rel] = {'sha256': checkout_hash, 'wheel_sha256': wheel_hash,
                       'origin': 'checkout-overlay'}

    conf = root / 'pyscf_conf.py'
    conf.write_text(CONF, encoding='utf-8')

    smoke = (
        'import os, pathlib, sys, pyscf\n'
        'path = pathlib.Path(pyscf.__file__).resolve()\n'
        'assert "site-packages" in str(path), path\n'
        'source = pathlib.Path(os.environ["REPEAT_REPO"]).resolve()\n'
        'assert all(pathlib.Path(x or ".").resolve() != source '
        'for x in sys.path), sys.path\n'
        'print(pyscf.__version__, pyscf.__file__)\n'
    )
    smoke_env = dict(env, REPEAT_REPO=str(REPO), PYSCF_CONFIG_FILE=str(conf))
    run([python, '-I', '-B', '-c', smoke], cwd=site, env=smoke_env)

    freeze = subprocess.check_output(
        [str(python), '-m', 'pip', 'freeze'], text=True, env=env)
    (OUT / 'pip-freeze.txt').write_text(freeze, encoding='utf-8')
    system = subprocess.check_output(
        [str(python), '-B', '-c',
         'import platform, sys, numpy, pyscf; '
         'print(sys.version); print(platform.platform()); '
         'print("numpy", numpy.__version__); print("pyscf", pyscf.__version__)'],
        text=True, env=env)
    (OUT / 'system.txt').write_text(system, encoding='utf-8')

    identity = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True, env=env).strip()
    (OUT / 'commit.txt').write_text(identity + '\n', encoding='utf-8')

    (OUT / 'identity.json').write_text(json.dumps({
        'mode': MODE,
        'runner': os.environ.get('RUNNER_NAME'),
        'os': TAG,
        'commit': identity,
        'branch': subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=REPO, text=True,
            env=env).strip(),
        'pyscf_version': PYSCF_VERSION,
        'numpy_version': NUMPY_VERSION,
        'pytest_version': PYTEST_VERSION,
        'purelib': str(site),
        'files': copied,
    }, indent=2) + '\n', encoding='utf-8')

    write_env({
        'REPEAT_PYTHON': python,
        'REPEAT_SITE': site,
        'REPEAT_OUT': OUT,
        'PYSCF_CONFIG_FILE': conf,
    })


if __name__ == '__main__':
    sys.exit(main())
