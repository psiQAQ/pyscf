#!/usr/bin/env python
"""Run precision diagnostics with one and four threads on the same runner."""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


THREAD_VARIABLES = (
    'OMP_NUM_THREADS',
    'OPENBLAS_NUM_THREADS',
    'MKL_NUM_THREADS',
    'VECLIB_MAXIMUM_THREADS',
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--script', required=True)
    parser.add_argument('--experiment', required=True)
    parser.add_argument('--repeats', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = {
        'experiment': args.experiment,
        'repeats': args.repeats,
        'python': args.python,
        'script': args.script,
        'runs': [],
    }
    metadata_path = args.output / 'paired-runs.json'
    for threads in (1, 4):
        env = os.environ.copy()
        env.update({key: str(threads) for key in THREAD_VARIABLES})
        output = args.output / f't{threads}'
        started = time.monotonic()
        command = [
            args.python, args.script,
            '--experiment', args.experiment,
            '--repeats', str(args.repeats),
            '--output', str(output),
        ]
        result = subprocess.run(command, env=env, check=False)
        metadata['runs'].append({
            'threads': threads,
            'elapsed_seconds': time.monotonic() - started,
            'returncode': result.returncode,
            'output': str(output),
            'thread_environment': {key: env[key] for key in THREAD_VARIABLES},
        })
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        if result.returncode:
            return result.returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
