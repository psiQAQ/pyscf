"""Repeat the UCISD node in independent subprocesses and keep every failure.

Each run gets its own working directory, scratch directory and junit file, so a
failure can be reproduced and the surrounding log survives.  Runs never share a
process: the defect depends on process-level heap layout, so a single pytest
process would not measure it.

A non-zero exit status means "the diagnostic recorded failures", which in the
unpatched mode is the evidence we are after.  It is not a harness error.
"""

import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(os.environ['REPEAT_OUT'])
PYTHON = os.environ['REPEAT_PYTHON']
SITE = Path(os.environ['REPEAT_SITE'])
REPO = Path(__file__).resolve().parents[3]

NODE = os.environ.get(
    'REPEAT_NODE', 'pyscf/ci/test/test_ucisd.py::KnownValues::test_h4')
FILE = os.environ.get('REPEAT_FILE', 'pyscf/ci/test/test_ucisd.py')
COUNT = int(os.environ.get('REPEAT_COUNT', '300'))
FILE_COUNT = int(os.environ.get('REPEAT_FILE_COUNT', '20'))
PER_RUN_TIMEOUT = int(os.environ.get('REPEAT_TIMEOUT', '600'))
DEADLINE = time.monotonic() + 60 * int(os.environ.get('REPEAT_DEADLINE_MINUTES', '200'))

results = []


def target_name(node):
    return node.rsplit('::', 1)[-1]


def read_junit(path, name):
    if not path.is_file():
        return None
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None
    for case in root.iter('testcase'):
        if case.get('name') != name:
            continue
        failure = case.find('failure')
        skipped = case.find('skipped')
        message = ''
        if failure is not None:
            message = (failure.get('message') or failure.text or '').strip()
        return {
            'executed': True,
            'failed': failure is not None,
            'skipped': skipped is not None,
            'seconds': case.get('time'),
            'message': message[:400],
        }
    return {'executed': False, 'failed': None, 'skipped': None, 'seconds': None,
            'message': ''}


def run_once(label, target, name):
    work = OUT / label
    work.mkdir(parents=True, exist_ok=True)
    scratch = work / 'scratch'
    scratch.mkdir(exist_ok=True)
    junit = work / 'junit.xml'
    log = work / 'pytest.log'
    env = dict(os.environ)
    for key in ('TMP', 'TEMP', 'TMPDIR', 'PYSCF_TMPDIR'):
        env[key] = str(scratch)
    command = [PYTHON, '-B', '-m', 'pytest', target, '-q', '-s',
               '-p', 'no:cacheprovider', '--rootdir', '.',
               '--junitxml', str(junit)]
    started = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(command, cwd=SITE, env=env, text=True,
                                   capture_output=True, timeout=PER_RUN_TIMEOUT)
        code, output = completed.returncode, completed.stdout + completed.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        code = -1
        output = (error.stdout or '') + (error.stderr or '')
    elapsed = round(time.monotonic() - started, 3)
    log.write_text('$ {}\n{}'.format(' '.join(command), output), encoding='utf-8')
    detail = read_junit(junit, name) or {'executed': False, 'failed': None,
                                         'skipped': None, 'seconds': None,
                                         'message': ''}
    row = {
        'label': label,
        'target': target,
        'exit_code': code,
        'timed_out': timed_out,
        'seconds': elapsed,
        'passed': code == 0 and detail['failed'] is False,
        'target_executed': detail['executed'],
        'target_skipped': detail['skipped'],
        'failure_message': detail['message'],
        'nan_signature': bool(re.search(r'nan', detail['message'], re.I)),
    }
    results.append(row)
    (OUT / 'summary.json').write_text(json.dumps(results, indent=2) + '\n',
                                      encoding='utf-8')
    print(json.dumps({k: row[k] for k in ('label', 'passed', 'seconds',
                                          'target_executed', 'nan_signature')}),
          flush=True)
    return row


def main():
    name = target_name(NODE)
    print('node={} count={} file_count={} out={}'.format(
        NODE, COUNT, FILE_COUNT, OUT), flush=True)

    for index in range(COUNT):
        if time.monotonic() > DEADLINE:
            print('deadline reached after {} runs'.format(index), flush=True)
            break
        run_once('isolated-{:03d}'.format(index), NODE, name)

    # The same file also holds the other UCISD cases; a fix that perturbs them
    # would show up here rather than in the single-node loop.
    for index in range(FILE_COUNT):
        if time.monotonic() > DEADLINE:
            print('deadline reached in file phase after {} runs'.format(index),
                  flush=True)
            break
        run_once('file-{:03d}'.format(index), FILE, name)

    isolated = [r for r in results if r['label'].startswith('isolated-')]
    files = [r for r in results if r['label'].startswith('file-')]
    summary = {
        'node': NODE,
        'isolated_runs': len(isolated),
        'isolated_failures': sum(1 for r in isolated if not r['passed']),
        'isolated_nan_failures': sum(1 for r in isolated
                                     if not r['passed'] and r['nan_signature']),
        'file_runs': len(files),
        'file_failures': sum(1 for r in files if not r['passed']),
        'skipped_or_missing': sum(1 for r in results if not r['target_executed']),
    }
    (OUT / 'counts.json').write_text(json.dumps(summary, indent=2) + '\n',
                                     encoding='utf-8')
    print('COUNTS ' + json.dumps(summary), flush=True)
    return 0 if summary['isolated_failures'] == 0 and summary['file_failures'] == 0 \
        and summary['skipped_or_missing'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
