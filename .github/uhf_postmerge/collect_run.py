"""Preserve this task's GitHub run metadata, raw ZIPs and extracted evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import zipfile

REPO = 'psiQAQ/pyscf'
BRANCH = 'codex/verify/uhf-postmerge-20261107'


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path]))


def download(path, destination, expected_digest=None):
    if not destination.exists():
        partial = destination.with_suffix(destination.suffix + '.partial')
        with partial.open('xb') as stream:
            subprocess.run(['gh', 'api', path], stdout=stream, check=True)
        partial.rename(destination)
    actual = 'sha256:' + hashlib.sha256(destination.read_bytes()).hexdigest()
    if expected_digest and actual != expected_digest:
        raise RuntimeError(f'Download hash mismatch: {destination}: {actual}')
    return actual


def extract(archive_path, destination):
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (root / member.filename).resolve()
            if not target.is_relative_to(root):
                raise RuntimeError('Unsafe archive path: ' + member.filename)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                content = archive.read(member)
                if target.exists():
                    if target.read_bytes() != content:
                        raise RuntimeError('Existing evidence differs: ' + str(target))
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)


def main(run_id, output_root):
    root = output_root.resolve() / str(run_id)
    root.mkdir(parents=True, exist_ok=True)
    endpoint = f'repos/{REPO}/actions/runs/{run_id}'
    run = api(endpoint)
    workflows = ('.github/workflows/uhf-postmerge-20261107.yml',
                 '.github/workflows/uhf-postmerge-linux-resume-20261107.yml')
    if run['head_branch'] != BRANCH or run['path'] not in workflows:
        raise RuntimeError('Refusing to collect another task or workflow')
    artifacts = api(endpoint + '/artifacts?per_page=100')
    jobs = api(endpoint + '/jobs?per_page=100')
    snapshot = {'run': run, 'artifacts': artifacts, 'jobs': jobs,
                'collected_unix': time.time()}
    (root / f'metadata-{int(time.time())}.json').write_text(
        json.dumps(snapshot, indent=2) + '\n', encoding='utf-8')
    archives = root / 'archives'
    archives.mkdir(exist_ok=True)
    downloads = []
    for artifact in artifacts['artifacts']:
        name = artifact['name']
        if not name.startswith('uhf-') or not re.fullmatch(r'[A-Za-z0-9_.-]+', name):
            raise RuntimeError('Unexpected artifact name: ' + name)
        archive = archives / (name + '.zip')
        digest = download(f'repos/{REPO}/actions/artifacts/{artifact["id"]}/zip',
                          archive, artifact.get('digest'))
        extract(archive, root / name)
        downloads.append({'name': name, 'id': artifact['id'], 'sha256': digest})
        print(json.dumps(downloads[-1]), flush=True)
    if run['status'] == 'completed':
        archive = archives / 'workflow-logs.zip'
        log_digest = download(endpoint + '/logs', archive)
        extract(archive, root / 'workflow-logs')
        print(json.dumps({'workflow_logs': log_digest}), flush=True)
    (root / 'downloads.json').write_text(json.dumps(downloads, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', type=int)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    main(args.run_id, args.output_root)
