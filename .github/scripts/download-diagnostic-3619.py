"""Compare anonymous download routes; retain every attempt, including failures."""
from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import time
from urllib.parse import urljoin

SOURCE = '391e8860d2363a0063b942f686e3ca83886b9fac'
URLS = {
    'original': 'https://github.com/pyscf/pyscf-build-deps/blob/master/pyscf-2.14.1-deps.tar.gz?raw=true',
    'media': 'https://media.githubusercontent.com/media/pyscf/pyscf-build-deps/refs/heads/master/pyscf-2.14.1-deps.tar.gz',
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def parse_hops(raw, initial):
    url = initial
    hops = []
    for block in re.split(r'\r?\n\r?\n', raw):
        lines = block.splitlines()
        if not lines or not lines[0].startswith('HTTP/'):
            continue
        status = int(lines[0].split()[1])
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers.setdefault(key.lower(), []).append(value.strip())
        proxy_connect = 'connection established' in lines[0].lower()
        hops.append({'url': url, 'status_line': lines[0], 'status': status,
                     'proxy_connect': proxy_connect, 'headers': headers,
                     'github_request_ids': headers.get('x-github-request-id', []),
                     'request_ids': {k: v for k, v in headers.items()
                                     if 'request-id' in k or k in ('x-amz-id-2', 'x-served-by', 'x-cache', 'via')}})
        if not proxy_connect and status in (301, 302, 303, 307, 308) and 'location' in headers:
            url = urljoin(url, headers['location'][-1])
    return hops


def main():
    root = Path('download-evidence')
    root.mkdir(exist_ok=False)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert head == os.environ['VALIDATION_SHA']
    source = subprocess.check_output(['git', 'show', SOURCE + ':.github/workflows/ci_linux/build_pyscf.sh'], text=True)
    assert URLS['original'] in source
    metadata = {'started_at': datetime.now(timezone.utc).isoformat(), 'pid': os.getpid(),
                'source_sha': SOURCE, 'validation_sha': head, 'urls': URLS,
                'runner_os': os.environ.get('RUNNER_OS'), 'runner_arch': os.environ.get('RUNNER_ARCH'),
                'image_os': os.environ.get('ImageOS'), 'image_version': os.environ.get('ImageVersion'),
                'curl_version': subprocess.check_output(['curl', '--version'], text=True),
                'os_release': Path('/etc/os-release').read_text(),
                'method': 'Four paired GET rounds, no internal curl retries, alternating route order; waits 1,2,4 seconds between rounds. Anonymous requests. Diagnostic comparison, not an exact replay of the PR retry command.'}
    save(root / 'environment.json', metadata)
    results = []
    for attempt in range(1, 5):
        if attempt > 1:
            time.sleep(2 ** (attempt - 2))
        order = ('original', 'media') if attempt % 2 else ('media', 'original')
        for route in order:
            folder = root / f'{attempt:02d}-{route}'
            folder.mkdir()
            body = folder / 'response.body'
            command = ['curl', '--disable', '--silent', '--show-error', '--verbose',
                       '--fail-with-body', '--location', '--max-redirs', '8',
                       '--connect-timeout', '15', '--max-time', '90',
                       '--dump-header', str(folder / 'headers.txt'), '--output', str(body),
                       '--write-out', '%{json}', URLS[route]]
            started = datetime.now(timezone.utc).isoformat()
            with (folder / 'curl.stderr.txt').open('wb') as stderr:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=stderr)
                stdout, _ = process.communicate()
            (folder / 'curl.writeout.json').write_bytes(stdout)
            info = json.loads(stdout)
            raw = (folder / 'headers.txt').read_text(encoding='iso-8859-1')
            hops = parse_hops(raw, URLS[route])
            save(folder / 'hops.json', hops)
            result = {'attempt': attempt, 'route': route, 'started_at': started,
                      'finished_at': datetime.now(timezone.utc).isoformat(), 'pid': process.pid,
                      'command': command, 'curl_exit': process.returncode,
                      'final_url': info['url_effective'], 'http_code': info['http_code'],
                      'num_redirects': info['num_redirects'], 'remote_ip': info['remote_ip'],
                      'body_bytes': body.stat().st_size if body.exists() else 0,
                      'hops': hops, 'archive_check': 'Not Run', 'success_body_removed': False}
            if process.returncode == 0 and info['http_code'] == 200:
                try:
                    with gzip.open(body, 'rb') as stream:
                        while stream.read(1024 * 1024):
                            pass
                    with tarfile.open(body, 'r:gz') as archive:
                        names = archive.getnames()
                    assert len(names) == 64 and body.stat().st_size == 14557577
                    (folder / 'archive-entries.txt').write_text('\n'.join(names) + '\n', encoding='utf-8')
                    result['archive_check'] = 'Passed'
                    result['archive_entries'] = len(names)
                    body.unlink()
                    result['success_body_removed'] = True
                except Exception as exc:
                    result['archive_check'] = 'Failed'
                    result['archive_error'] = str(exc)
            elif body.exists():
                body.rename(folder / 'error.body')
                result['error_body_file'] = 'error.body'
                result['error_body_preview'] = (folder / 'error.body').read_bytes()[:4096].decode('utf-8', errors='replace')
            save(folder / 'result.json', result)
            results.append(result)
            save(root / 'summary.json', results)
            print(json.dumps({k: result[k] for k in ('attempt', 'route', 'curl_exit', 'http_code', 'final_url', 'num_redirects', 'archive_check')}), flush=True)
            for hop in hops:
                print(json.dumps({'hop_url': hop['url'], 'status': hop['status'], 'request_ids': hop['request_ids']}), flush=True)
    print('DIAGNOSTIC_COLLECTION_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
