import importlib.util
import pathlib
import types
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
COLLECTOR_PATH = REPO_ROOT / '.github' / 'workflows' / 'collect_precision_environment.py'
SPEC = importlib.util.spec_from_file_location('collect_precision_environment', COLLECTOR_PATH)
COLLECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COLLECTOR)


class CollectPrecisionEnvironmentTests(unittest.TestCase):
    def test_namespace_package_has_no_native_library_directory(self):
        namespace_package = types.SimpleNamespace(__file__=None)
        self.assertEqual(COLLECTOR.native_libraries(namespace_package), [])


if __name__ == '__main__':
    unittest.main()
