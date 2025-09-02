from medsenger_api import prepare_file, prepare_binary
from unittest import TestCase

class TestFileHelpers(TestCase):
    def test_prepare_file(self):
        result = prepare_file("test_file_helpers.py")
        self.assertEqual(result['type'], 'text/x-script.python')

    def test_prepare_binary(self):
        result = prepare_binary("test_file_helpers.py", open("test_file_helpers.py", "rb").read())

        self.assertEqual(result['type'], 'text/x-script.python')