"""Join the audited final-merge samples without counting interrupted attempts."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


BASE = 'ab749b4fd00f95a08ad00997356c9f6f77fc8674'
SAMPLES = [
    ('acceptance-windows.json', 42281471449, 'windows313', 200),
    ('acceptance-linux-821.json', 42284337939, 'linux312', 821),
    ('acceptance-linux-179.json', 42286423369, 'linux312', 179),
]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def assemble(root):
    provenance, accepted, exclusions, environments = [], [], [], []
    identity, process_identity = set(), set()
    stage_values = defaultdict(list)
    thread_profiles = Counter()
    for audit_name, run_id, platform, expected in SAMPLES:
        audit_path = root / audit_name
        audit = read(audit_path)
        require(audit['integrity_status'] == 'Passed' and not audit['errors'], audit_name)
        require(audit['source_sha'] == BASE and audit['formal_passed'] == expected,
                'Incorrect source/count: ' + audit_name)
        run_root = root / 'remote' / str(run_id)
        metadata = read(sorted(run_root.glob('metadata-*.json'))[-1])
        require(metadata['run']['status'] == 'completed', 'Run still in progress')
        provenance.append({
            'run_id': run_id, 'url': metadata['run']['html_url'],
            'workflow_conclusion': metadata['run']['conclusion'],
            'runtime_tool_sha': metadata['run']['head_sha'],
            'platform': platform, 'formal_passed': expected,
            'audit': audit_name, 'audit_sha256': digest(audit_path),
            'archives': read(run_root / 'downloads.json'),
        })
        exclusions.extend({'run_id': run_id, **entry}
                          for entry in audit.get('unrecorded_attempts', []))
        for summary in audit['summaries']:
            if summary['label'] != 'formal':
                continue
            artifact = summary['artifact']
            directory = run_root / artifact / 'formal'
            installation = read(directory / 'installation.json')
            manifest = installation['manifest']
            require(manifest['source_sha'] == BASE, 'Installation source mismatch')
            require(manifest['tool_sha'] == metadata['run']['head_sha'], 'Run tool mismatch')
            for line in (directory / 'records.jsonl').read_text().splitlines():
                record = json.loads(line)
                key = (run_id, artifact, record['attempt'])
                require(key not in identity, 'Duplicate sample')
                identity.add(key)
                path = directory / record['result'].replace('\\', '/')
                result = read(path)
                process = read(path.parent / 'process.json')
                env = result['environment_after']
                process_key = (run_id, artifact, process['pid'], process['started_unix'])
                require(process_key not in process_identity, 'Reused process record')
                process_identity.add(process_key)
                require(record['status'] == result['status'] == 'Passed', 'Non-pass sample')
                for field in ('source_sha', 'tool_sha', 'wheel_sha256'):
                    require(record[field] == result[field] == manifest[field], field)
                require(len(result['stages']) == 2, 'Missing Fe2 stage')
                for stage, value in enumerate(result['stages'], 1):
                    stage_values[(platform, stage)].append(value)
                pool_profile = tuple(sorted((p['api'], p['num_threads'])
                                            for p in env['native_pools']))
                thread_profiles[(platform, pool_profile)] += 1
                accepted.append({
                    'run_id': run_id, 'artifact': artifact, 'attempt': record['attempt'],
                    'launcher_pid': process['pid'], 'runtime_pid': env['pid'],
                    'started_unix': process['started_unix'], 'platform': platform,
                    'result': path.relative_to(root).as_posix(), 'sha256': digest(path),
                })
                if record['attempt'] == 1:
                    environments.append({
                        'run_id': run_id, 'artifact': artifact, 'platform': platform,
                        'python': env['python'], 'os': env['platform'],
                        'packages': sorted(set(tuple(p) for p in env['packages'])),
                        'libxc': env['libxc_version'], 'xcfun': env['xcfun_version'],
                        'openmp_threads': env['pyscf_openmp_threads'],
                        'native_pools': env['native_pools'],
                        'source_sha': BASE, 'runtime_tool_sha': manifest['tool_sha'],
                        'build_tool_sha': manifest.get('build_tool_sha', manifest['tool_sha']),
                        'wheel_sha256': manifest['wheel_sha256'],
                        'production_files_verified': installation['production_files_verified'],
                    })
    counts = Counter(a['platform'] for a in accepted)
    require(counts == {'linux312': 1000, 'windows313': 200}, 'Incomplete final total')
    regressions = []
    run_root = root / 'remote/42281471449'
    for platform in ('linux312', 'windows313'):
        directory, = run_root.glob('uhf-preflight-' + platform + '-*')
        for label, count in (('preflight', 1), ('regressions', 9)):
            result_path, = directory.glob('**/' + label + '/0001/result.json')
            result = read(result_path)
            calls = [r for r in result['reports'] if r['when'] == 'call']
            require(result['status'] == 'Passed' and not result['deselected'], label)
            require(len(calls) == count and all(r['outcome'] == 'passed' for r in calls), label)
            regressions.append({'platform': platform, 'label': label, 'passed': count,
                                'nodeids': [r['nodeid'] for r in calls]})
    ranges = []
    for (platform, stage), values in sorted(stage_values.items()):
        ranges.append({'platform': platform, 'stage': stage, 'count': len(values),
                       'converged': sum(v['converged'] for v in values),
                       'ranges': {key: [min(v[key] for v in values), max(v[key] for v in values)]
                                  for key in ('e_tot', 'e_free', 'entropy', 'cycles')}})
    return {
        'status': 'Passed', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'assembler_sha256': digest(Path(__file__).resolve()),
        'audit_script_sha256': digest(Path(__file__).with_name('audit_evidence.py')),
        'source_sha': BASE,
        'final_pr_head': 'e7d2001bc49df99b65cd182fc3cb70ea9948724b',
        'merge_sha': 'fd6b6898a3d06fa0628f9d8544476a856dc711a8',
        'formal_passed': dict(counts), 'unique_formal_samples': len(identity),
        'runs': provenance, 'preflight_and_regressions': regressions,
        'excluded_interrupted_attempts': exclusions,
        'thread_profiles': [{'platform': p, 'pools': pools, 'attempts': n}
                            for (p, pools), n in sorted(thread_profiles.items())],
        'stage_ranges': ranges, 'environments': environments,
        'accepted_attempts': accepted,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--summary-output', type=Path, required=True)
    args = parser.parse_args()
    report = assemble(args.root.resolve())
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    report.pop('accepted_attempts')
    args.summary_output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'formal_passed', 'unique_formal_samples')}))
