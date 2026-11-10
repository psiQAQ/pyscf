"""Test orchestration with synthetic subprocess outcomes, not scientific results."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('controller', Path(__file__).with_name('run.py'))
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


class ControllerTests(unittest.TestCase):
    def run_scenario(self, failed):
        scratch = controller.ROOT / 'tmp/controller-validation'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            out = Path(directory)
            def execute(command, env, cwd, log, timeout):
                dest = log.parent
                if '-p' in command and 'capture' in command:
                    (dest / 'trace-test.json').write_text(json.dumps({
                        'final': {'energies': [0]}, 'rhf': {'converged': True},
                        'casscf': {'converged': True}, 'cms': {'converged': True}}))
                return (1 if dest.name == failed else 0), False
            with patch.object(controller, 'OUT', out), patch.object(controller, 'execute', execute), \
                 patch.object(controller.subprocess, 'check_output', return_value='source-sha'), \
                 patch('builtins.print'):
                code = controller.main()
            return code, json.loads((out / 'summary.json').read_text())

    def test_failure_does_not_stop_200(self):
        code, rows = self.run_scenario('isolated-001')
        self.assertEqual(code, 1)
        self.assertEqual(len(rows), 203)
        self.assertEqual(sum(r['label'].startswith('isolated-') for r in rows), 200)
        self.assertFalse(rows[1]['passed'])

    def test_success_runs_bounded_order_controls(self):
        code, rows = self.run_scenario(None)
        self.assertEqual(code, 0)
        self.assertEqual(len(rows), 224)
        self.assertEqual(len({r['label'] for r in rows}), 224)
        self.assertEqual(rows[-1]['label'], 'subset-000')


if __name__ == '__main__':
    unittest.main()
