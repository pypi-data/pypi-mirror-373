import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.txttoqti.converter import TxtToQtiConverter
from src.txttoqti.exceptions import TxtToQtiError

class TestTxtToQtiConverter(unittest.TestCase):
    
    def setUp(self):
        self.converter = TxtToQtiConverter()

    def test_conversion_valid_file(self):
        result = self.converter.convert_file("tests/sample_questions.txt")
        self.assertTrue(result.endswith('.zip'))

    def test_conversion_invalid_file(self):
        with self.assertRaises(TxtToQtiError):
            self.converter.convert_file("tests/non_existent_file.txt")

    def test_conversion_empty_file(self):
        result = self.converter.convert_file("tests/empty_file.txt")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()