"""Validate the exact reviewed fix against the archived failure runtime."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/cms-evidence'
SOURCE = ROOT / 'tmp/cms-source'
scripts = Path(__file__).parent
results = []


def run_case(label, count, threads, workers, paths=None):
    env = dict(os.environ, CMS_SOURCE=str(SOURCE), CMS_OUT=str(OUT / label),
               CMS_PRIMARY_COUNT=str(count), CMS_WORKERS=str(workers), CMS_CONTROLS='0',
               OMP_NUM_THREADS=str(threads), OPENBLAS_CORETYPE='Haswell')
    if paths:
        env['CMS_TEST_PATHS'] = json.dumps(paths)
    proc = subprocess.Popen([sys.executable, str(scripts / 'run.py')], env=env)
    print(f'{label}: PID {proc.pid}', flush=True)
    code = proc.wait()
    rows = json.loads((OUT / label / 'summary.json').read_text())
    results.append(dict(label=label, pid=proc.pid, exit_code=code,
                        requested=count, completed=len(rows), passed=sum(r['passed'] for r in rows)))
    (OUT / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')


run_case('fixed-repeat', 200, 2, 2)
for threads in (1, 2):
    for workers in (0, 2):
        run_case(f'fixed-omp{threads}-workers{workers}', 5, threads, workers)
    run_case(f'fixed-neighbors-omp{threads}', 1, threads, 0,
             [f'pyscf/mcpdft/test/{name}' for name in
              ('test_diatomic_energies.py', 'test_cmspdft.py', 'test_mspdft.py')])

replay_out = OUT / 'fixed-replay'
scratch = replay_out / 'scratch'
scratch.mkdir(parents=True)
env = dict(os.environ, CMS_SOURCE=str(SOURCE), CMS_OUT=str(replay_out),
           CMS_REPLAY_FIXED='1', OMP_NUM_THREADS='2', OPENBLAS_CORETYPE='Haswell',
           PYTHONPATH=os.pathsep.join((str(scripts), str(SOURCE))),
           PYSCF_CONFIG_FILE=str(OUT / 'fixed-repeat/pyscf_conf.py'),
           PYSCF_EXT_PATH='disabled-for-cms-diagnostic',
           TMPDIR=str(scratch), PYSCF_TMPDIR=str(scratch))
with (replay_out / 'console.log').open('w') as log:
    proc = subprocess.Popen([sys.executable, str(scripts / 'replay.py')],
                            env=env, stdout=log, stderr=subprocess.STDOUT)
    print(f'fixed-replay: PID {proc.pid}', flush=True)
    code = proc.wait()
results.append(dict(label='fixed-replay', pid=proc.pid, exit_code=code))
(OUT / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')
sys.exit(int(any(r['exit_code'] or r.get('requested') != r.get('completed') for r in results)))
