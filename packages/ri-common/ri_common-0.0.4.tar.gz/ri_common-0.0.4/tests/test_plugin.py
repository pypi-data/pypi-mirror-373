import os
import unittest
import contextlib

import riu.plugin
import riu.utility


_TEST_MODULE = """\
class TestModule(object):
    def test_method(self):
        return 123
"""


class Test(unittest.TestCase):
    @contextlib.contextmanager
    def _stage_gen(self):
        with riu.utility.temp_path() as temp_path:
            filename = 'test_module.py'
            filepath = os.path.join(temp_path, filename)

            with open(filepath, 'w') as f:

                # Write

                f.write(_TEST_MODULE)
                f.flush()

            yield temp_path, filepath

    def test_get_module_from_module_filepath(self):
        with self._stage_gen() as (temp_path, filepath):

            # Retrieve

            g = riu.plugin.get_module_from_module_filepath(filepath)


        # Instantiate

        cls = g['TestModule']
        o = cls()


        # Call method

        actual = o.test_method()
        self.assertEqual(actual, 123)

    def test_get_module_symbol_with_filepath(self):
        with self._stage_gen() as (temp_path, filepath):

            # Retrieve

            cls = riu.plugin.get_module_symbol_with_filepath(
                    filepath,
                    'TestModule')


        # Instantiate and call method

        o = cls()

        actual = o.test_method()
        self.assertEqual(actual, 123)

    def test_get_module_symbol_with_reference(self):
        with self._stage_gen() as (temp_path, filepath):

            cls = riu.plugin.get_module_symbol_with_reference(
                    temp_path,
                    'test_module.TestModule')


        # Instantiate and call method

        o = cls()

        actual = o.test_method()
        self.assertEqual(actual, 123)
