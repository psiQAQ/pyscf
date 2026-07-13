#!/usr/bin/env python
"""Run paired or OpenMP/BLAS-split precision diagnostics on one runner."""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


BLAS_VARIABLES = (
    'OPENBLAS_NUM_THREADS',
    'MKL_NUM_THREADS',
    'VECLIB_MAXIMUM_THREADS',
)
THREAD_VARIABLES = ('OMP_NUM_THREADS',) + BLAS_VARIABLES


def execution_profiles(experiment, requested_profiles='all'):
    if experiment.startswith('split-'):
        profiles = (
            ('omp1-blas1', 1, 1),
            ('omp4-blas1', 4, 1),
            ('omp1-blas4', 1, 4),
            ('omp4-blas4', 4, 4),
        )
        if requested_profiles != 'all':
            by_name = {profile[0]: profile for profile in profiles}
            names = requested_profiles.split(',')
            if len(names) != len(set(names)) or any(name not in by_name for name in names):
                raise ValueError(f'invalid profiles: {requested_profiles}')
            profiles = tuple(by_name[name] for name in names)
        return experiment[len('split-'):], profiles
    if requested_profiles != 'all':
        raise ValueError('profiles can only be selected for split experiments')
    return experiment, (('t1', 1, 1), ('t4', 4, 4))


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--script', required=True)
    parser.add_argument('--experiment', required=True)
    parser.add_argument('--profiles', default='all')
    parser.add_argument('--repeats', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    experiment, profiles = execution_profiles(args.experiment, args.profiles)
    metadata = {
        'experiment': experiment,
        'requested_experiment': args.experiment,
        'requested_profiles': args.profiles,
        'repeats': args.repeats,
        'python': args.python,
        'script': args.script,
        'runs': [],
    }
    metadata_path = args.output / 'paired-runs.json'
    shared_fixture = None
    for profile, omp_threads, blas_threads in profiles:
        env = os.environ.copy()
        env['OMP_NUM_THREADS'] = str(omp_threads)
        env.update({key: str(blas_threads) for key in BLAS_VARIABLES})
        output = args.output / profile
        started = time.monotonic()
        command = [
            args.python, args.script,
            '--experiment', experiment,
            '--repeats', str(args.repeats),
            '--output', str(output),
        ]
        if shared_fixture is not None:
            command.extend(('--fixture', str(shared_fixture)))
        result = subprocess.run(command, env=env, check=False)
        metadata['runs'].append({
            'profile': profile,
            'threads': omp_threads if omp_threads == blas_threads else None,
            'omp_threads': omp_threads,
            'blas_threads': blas_threads,
            'elapsed_seconds': time.monotonic() - started,
            'returncode': result.returncode,
            'output': str(output),
            'thread_environment': {key: env[key] for key in THREAD_VARIABLES},
        })
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        if result.returncode:
            return result.returncode
        if experiment in ('pbc-tdhf-replay', 'pbc-tdhf-fixture-bank') and shared_fixture is None:
            shared_fixture = output / ('fixtures' if experiment == 'pbc-tdhf-fixture-bank' else 'fixture.npz')
            if not shared_fixture.exists():
                raise FileNotFoundError(f'replay fixture was not created: {shared_fixture}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
