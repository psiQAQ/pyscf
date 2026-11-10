"""Bounded independent pytest invocations; preserve every failed attempt."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(os.environ.get('CMS_SOURCE', ROOT / 'tmp/cms-source'))
OUT = Path(os.environ.get('CMS_OUT', ROOT / 'tmp/cms-evidence'))
NODE = 'pyscf/mcpdft/test/test_diatomic_energies.py::KnownValues::test_h2_cms3ftlda22_631g'
SUBSET = ('agf2 ao2mo cc dft gto lib mcpdft mcscf mp scf tdscf '
          'pbc/df pbc/dft pbc/scf').split()


def execute(command, env, cwd, log, timeout):
    with log.open('w') as stream:
        proc = subprocess.Popen(command, env=env, cwd=cwd, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
        identity = {'pid': proc.pid, 'command': command, 'started': time.time()}
        log.with_suffix('.process.json').write_text(json.dumps(identity, indent=2))
        try:
            return proc.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            # This process group was created above exclusively for this invocation.
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            return proc.returncode, True


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    count = int(os.environ.get('CMS_PRIMARY_COUNT', '200'))
    workers = int(os.environ.get('CMS_WORKERS', '2'))
    controls = os.environ.get('CMS_CONTROLS', '1') == '1'
    deadline = time.monotonic() + 120 * 60
    rows = []
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join((str(Path(__file__).parent), str(SOURCE)))
    config = OUT / 'pyscf_conf.py'
    config.write_text("import os\npbc_tools_pbc_fft_engine = 'NUMPY+BLAS'\n"
                      "scf_hf_SCF_mute_chkfile = True\nTMPDIR = os.environ['PYSCF_TMPDIR']\n"
                      "dftd3_DFTD3PATH = './pyscf/lib/deps/lib'\n")
    env['PYSCF_CONFIG_FILE'] = str(config)
    env['PYSCF_EXT_PATH'] = 'disabled-for-cms-diagnostic'
    identity = {k: env.get(k) for k in ('GITHUB_SHA', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT',
                                      'ImageOS', 'ImageVersion', 'OMP_NUM_THREADS')}
    identity['source_sha'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SOURCE, text=True).strip()
    identity['controller_pid'] = os.getpid()
    (OUT / 'identity.json').write_text(json.dumps(identity, indent=2))

    def run(label, paths, instrument=True, timeout=960):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        dest = OUT / label
        dest.mkdir()
        scratch = dest / 'scratch'
        scratch.mkdir()
        case_env = dict(env, CMS_CASE_DIR=str(dest), TMPDIR=str(scratch), PYSCF_TMPDIR=str(scratch))
        cmd = [sys.executable, '-m', 'pytest', '-s', '-v', '-c', 'pytest.ini',
               '--timeout=900',
               '--basetemp', str(scratch / 'pytest'), '-p', 'no:cacheprovider',
               '--junitxml', str(dest / 'junit.xml')]
        if workers:
            cmd += ['-n', str(workers), '--dist', 'loadfile']
        if instrument:
            cmd += ['-p', 'cms_capture']
        cmd += paths
        code, timed_out = execute(cmd, case_env, SOURCE, dest / 'pytest.log', min(timeout, remaining))
        traces = list(dest.glob('trace-*.json'))
        trace_data = [json.loads(p.read_text()) for p in traces]
        captured = any(t.get('final') for t in trace_data)
        converged = all(all(t.get(s, {}).get('converged', False)
                            for s in ('rhf', 'casscf', 'cms')) for t in trace_data)
        ok = code == 0 and not timed_out and (not instrument or (captured and converged))
        rows.append(dict(label=label, exit_code=code, timed_out=timed_out,
                         captured=captured, converged=converged, passed=ok))
        (OUT / 'summary.json').write_text(json.dumps(rows, indent=2))
        print(json.dumps(rows[-1]), flush=True)
        # Collection/plugin startup failures cannot supply numerical evidence.
        return not (instrument and not traces and code != 0 and not timed_out)

    for i in range(count):
        if not run(f'isolated-{i:03d}', [NODE]):
            break
    primary_ok = len(rows) == count and all(r['passed'] for r in rows)
    if not controls:
        return 0 if primary_ok else 1
    # Observation-effect controls are separately counted.
    for i in range(3):
        if not run(f'uninstrumented-{i:03d}', [NODE], instrument=False):
            break
    if primary_ok:
        for i in range(20):
            if not run(f'file-{i:03d}', [NODE.split('::')[0]]):
                break
        run('subset-000', ['pyscf/' + p for p in SUBSET], timeout=2400)
    complete = (sum(r['label'].startswith('isolated-') for r in rows) == count
                and sum(r['label'].startswith('uninstrumented-') for r in rows) == 3
                and (not primary_ok or len(rows) == count + 24))
    return 0 if complete and all(r['passed'] for r in rows) else 1


if __name__ == '__main__':
    sys.exit(main())
