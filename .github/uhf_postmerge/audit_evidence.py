"""Audit downloaded UHF artifacts; no scientific calculations or source edits."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


BASE = 'ab749b4fd00f95a08ad00997356c9f6f77fc8674'
TARGET = 'pyscf/scf/test/test_addons.py::KnownValues::test_uhf_smearing'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root, platform_filter=None, expected_formal=None, allow_incomplete=False):
    errors, summaries, attempts, environments = [], [], [], []
    incomplete_shards, unrecorded_attempts = [], []
    energies = defaultdict(list)
    file_index = []
    for path in sorted(root.rglob('*')):
        if path.is_file():
            file_index.append({'path': path.relative_to(root).as_posix(),
                               'bytes': path.stat().st_size, 'sha256': digest(path)})
    for manifest_path in sorted(root.rglob('manifest.json')):
        if not manifest_path.relative_to(root).parts[0].startswith('uhf-bundle-'):
            continue
        manifest = json.loads(manifest_path.read_text())
        wheel = manifest_path.parent / manifest['wheel']
        if not wheel.is_file() or digest(wheel) != manifest['wheel_sha256']:
            errors.append(f'{manifest_path}: wheel payload/hash missing or mismatched')
    for summary_path in sorted(root.rglob('summary.json')):
        directory = summary_path.parent
        artifact = directory.relative_to(root).parts[0]
        if not artifact.startswith('uhf-'):
            continue
        if platform_filter and artifact.split('-')[2] != platform_filter:
            continue
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        records = [json.loads(line) for line in (directory / 'records.jsonl').read_text().splitlines()]
        installation = json.loads((directory / 'installation.json').read_text())
        manifest = installation['manifest']
        if summary['source_sha'] != BASE or manifest['source_sha'] != BASE:
            errors.append(f'{artifact}: source SHA mismatch')
        if summary['executed'] != len(records):
            errors.append(f'{artifact}: incorrect executed count')
        if summary['planned'] != len(records):
            incomplete_shards.append({'artifact': artifact, 'label': summary['label'],
                                      'planned': summary['planned'], 'completed': len(records)})
            if not allow_incomplete:
                errors.append(f'{artifact}: incomplete execution')
        recorded_dirs = {Path(r['result'].replace('\\', '/')).parent.name for r in records}
        for process_file in directory.glob('*/process.json'):
            if process_file.parent.name not in recorded_dirs:
                unrecorded_attempts.append({'artifact': artifact, 'label': summary['label'],
                                            'directory': process_file.parent.name,
                                            'status': 'Not Run to completion; inspect retained logs'})
        if summary['passed'] != sum(r['status'] == 'Passed' for r in records):
            errors.append(f'{artifact}: incorrect passed count')
        summaries.append({'artifact': artifact, **summary})
        for record in records:
            result_path = directory / record['result'].replace('\\', '/')
            log_path = directory / record['log'].replace('\\', '/')
            process_path = result_path.parent / 'process.json'
            junit_path = result_path.with_suffix('.xml')
            missing = [str(p) for p in (result_path, log_path, process_path, junit_path)
                       if not p.is_file() or not p.stat().st_size]
            if missing:
                errors.append(f'{artifact}/{record["attempt"]}: missing {missing}')
                continue
            result = json.loads(result_path.read_text())
            process = json.loads(process_path.read_text())
            item = {'artifact': artifact, 'label': summary['label'], **record}
            attempts.append(item)
            if result['status'] != 'Passed' or record['returncode'] != 0:
                errors.append(f'{artifact}/{record["attempt"]}: test failed')
            for key in ('source_sha', 'tool_sha', 'wheel_sha256'):
                if not result[key] == record[key] == summary[key] == manifest[key]:
                    errors.append(f'{artifact}/{record["attempt"]}: {key} mismatch')
            if process['pid'] != record['pid']:
                errors.append(f'{artifact}/{record["attempt"]}: process mismatch')
            expected_nodes = manifest['regressions'] if summary['label'] == 'regressions' else [TARGET]
            calls = [r for r in result['reports'] if r['when'] == 'call']
            if (result['deselected'] or sorted(result['collected']) != sorted(expected_nodes)
                    or sorted(r['nodeid'] for r in calls) != sorted(expected_nodes)
                    or any(r['outcome'] != 'passed' for r in result['reports'])):
                errors.append(f'{artifact}/{record["attempt"]}: missing/skipped/deselected/failed node')
            junit = ET.parse(junit_path).getroot()
            suites = list(junit.iter('testsuite'))
            if (sum(int(s.get('tests', 0)) for s in suites) != len(expected_nodes)
                    or any(int(s.get(k, 0)) for s in suites for k in ('failures', 'errors', 'skipped'))):
                errors.append(f'{artifact}/{record["attempt"]}: JUnit not fully passed')
            env = result['environment_after']
            if env['pid'] != result['environment_before']['pid']:
                errors.append(f'{artifact}/{record["attempt"]}: runtime PID changed')
            # CPython's Windows venv redirector launches the actual interpreter.
            # Keep its Popen PID and the interpreter's os.getpid() as distinct
            # observations. Both are bound to this attempt's unique output path.
            # https://github.com/python/cpython/blob/3.13/PC/venvlauncher.c
            if env['pid'] != record['pid'] and not env['platform'].startswith('Windows'):
                errors.append(f'{artifact}/{record["attempt"]}: unexpected runtime PID')
            if env['pyscf_openmp_threads'] != 4:
                errors.append(f'{artifact}/{record["attempt"]}: actual OpenMP count mismatch')
            if not env['native_pools'] or any(p.get('num_threads') is None for p in env['native_pools']):
                errors.append(f'{artifact}/{record["attempt"]}: thread metadata missing')
            for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS'):
                if env['environment'].get(key) != '4':
                    errors.append(f'{artifact}/{record["attempt"]}: requested profile mismatch')
            for key in ('RUNNER_TEMP', 'TMP', 'TEMP', 'PYSCF_TMPDIR'):
                if env['environment'][key] != process['scratch']:
                    errors.append(f'{artifact}/{record["attempt"]}: scratch isolation mismatch')
            if record['attempt'] == 1:
                environments.append({'artifact': artifact, 'label': summary['label'],
                                     'environment': env})
            if summary['label'] != 'regressions':
                stages = result['stages']
                if len(stages) != 2 or [s['sigma'] for s in stages] != [.01, .1]:
                    errors.append(f'{artifact}/{record["attempt"]}: incomplete Fe2 stages')
                else:
                    if not stages[-1]['converged'] or stages[-1]['conv_tol'] != 1e-9:
                        errors.append(f'{artifact}/{record["attempt"]}: final convergence mismatch')
                    for index, stage in enumerate(stages, 1):
                        energies[(artifact.split('-')[2], summary['label'], index)].append(stage)
                for stage_id in (1, 2):
                    checks = [c for c in result['checks'] if c['stage'] == stage_id]
                    main_converged = any(c['returned_converged'] for c in checks if not c['extra'])
                    if not checks or (main_converged and not any(c['extra'] for c in checks)):
                        errors.append(f'{artifact}/{record["attempt"]}: main/extra telemetry incomplete')
                    for c in checks:
                        energy_pass = c['dF_or_fallback_dE'] < c['conv_tol']
                        grad_pass = c['norm_gorb'] < c['conv_tol_grad']
                        expected = energy_pass or grad_pass if c['extra'] else energy_pass and grad_pass
                        if c['returned_converged'] != expected:
                            errors.append(f'{artifact}/{record["attempt"]}: convergence decision mismatch')
    if not summaries:
        errors.append('No run summaries found')
    counts = Counter((a['artifact'].split('-')[2], a['label'], a['status']) for a in attempts)
    formal_passed = sum(a['label'] == 'formal' and a['status'] == 'Passed' for a in attempts)
    if expected_formal is not None and formal_passed != expected_formal:
        errors.append(f'Expected {expected_formal} formal passes, found {formal_passed}')
    energy_ranges = []
    for (platform, label, stage), values in sorted(energies.items()):
        energy_ranges.append({'platform': platform, 'label': label, 'stage': stage,
                              'attempts': len(values),
                              'ranges': {key: [min(v[key] for v in values), max(v[key] for v in values)]
                                         for key in ('e_tot', 'e_free', 'entropy', 'cycles')}})
    return {'source_sha': BASE, 'scope_platform': platform_filter or 'all',
            'expected_formal': expected_formal, 'formal_passed': formal_passed,
            'allow_incomplete': allow_incomplete, 'incomplete_shards': incomplete_shards,
            'unrecorded_attempts': unrecorded_attempts,
            'integrity_status': 'Failed' if errors else 'Passed',
            'errors': errors, 'summaries': summaries,
            'counts': [{'platform': p, 'label': l, 'status': s, 'count': n}
                       for (p, l, s), n in sorted(counts.items())],
            'energy_ranges': energy_ranges, 'environments': environments,
            'files': file_index}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--platform', choices=('linux312', 'windows313'))
    parser.add_argument('--expect-formal', type=int)
    parser.add_argument('--allow-incomplete', action='store_true')
    args = parser.parse_args()
    result = audit(args.root.resolve(), args.platform, args.expect_formal, args.allow_incomplete)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('files', 'environments', 'summaries')}, indent=2))
    raise SystemExit(bool(result['errors']))
