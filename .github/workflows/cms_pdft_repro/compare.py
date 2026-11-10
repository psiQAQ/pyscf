"""Compare two source trees with the exact archived native PySCF libraries."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/cms-evidence'


def main():
    results = []
    for revision, source in [('baseline', 'cms-baseline'), ('original', 'cms-source')]:
        for threads in (1, 2):
            for workers in (0, 2):
                label = f'{revision}-omp{threads}-workers{workers}'
                env = dict(os.environ, CMS_SOURCE=str(ROOT / 'tmp' / source),
                           CMS_OUT=str(OUT / label), CMS_PRIMARY_COUNT='5',
                           CMS_WORKERS=str(workers), CMS_CONTROLS='0',
                           OMP_NUM_THREADS=str(threads), OPENBLAS_CORETYPE='Haswell')
                proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name('run.py'))], env=env)
                print(f'controller {label}: PID {proc.pid}', flush=True)
                code = proc.wait()
                rows = json.loads((OUT / label / 'summary.json').read_text())
                results.append(dict(label=label, pid=proc.pid, exit_code=code,
                                    completed=len(rows), passed=sum(r['passed'] for r in rows)))
                (OUT / 'matrix.json').write_text(json.dumps(results, indent=2) + '\n')
        replay_out = OUT / f'{revision}-replay'
        scratch = replay_out / 'scratch'
        scratch.mkdir(parents=True)
        env.update(CMS_OUT=str(replay_out),
                   PYTHONPATH=os.pathsep.join((str(Path(__file__).parent), str(ROOT / 'tmp' / source))),
                   PYSCF_CONFIG_FILE=str(OUT / label / 'pyscf_conf.py'),
                   PYSCF_EXT_PATH='disabled-for-cms-diagnostic',
                   TMPDIR=str(scratch), PYSCF_TMPDIR=str(scratch))
        with (replay_out / 'console.log').open('w') as log:
            proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name('replay.py'))],
                                    env=env, stdout=log, stderr=subprocess.STDOUT)
            print(f'replay {revision}: PID {proc.pid}', flush=True)
            code = proc.wait()
        results.append(dict(label=f'{revision}-replay', pid=proc.pid, exit_code=code,
                            completed=0, passed=0))
        (OUT / 'matrix.json').write_text(json.dumps(results, indent=2) + '\n')
    return int(any(r['exit_code'] or (not r['label'].endswith('-replay') and r['completed'] != 5)
                   for r in results))


if __name__ == '__main__':
    sys.exit(main())
