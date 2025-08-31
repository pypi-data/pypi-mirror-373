import os
import unittest

from mangotools.assertion import MangoAssertion
from mangotools.assertion.file import FileAssertion


class TestTxtAssertion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.txt_file = 'test_sample.txt'
        cls.content = 'hello world\n这是一个测试文件。\nEND.'
        with open(cls.txt_file, 'w', encoding='utf-8') as f:
            f.write(cls.content)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.txt_file):
            os.remove(cls.txt_file)

    def test_txt_equal(self):
        MangoAssertion().ass(FileAssertion.assert_txt_equal.__name__, 'hello world\n这是一个测试文件。\nEND.',
                             'hello world\n这是一个测试文件。\nEND.')
        MangoAssertion().ass(FileAssertion.assert_txt_equal.__name__, self.txt_file,
                             'hello world\n这是一个测试文件。\nEND.')

    def test_txt_contains(self):
        MangoAssertion().ass(FileAssertion.assert_txt_contains.__name__, 'hello world\n这是一个测试文件。\nEND.',
                             '测试文件')
        MangoAssertion().ass(FileAssertion.assert_txt_contains.__name__, self.txt_file, '测试文件')

    def test_txt_length_equal(self):
        MangoAssertion().ass(FileAssertion.assert_txt_length_equal.__name__, 'hello world', 11)
        MangoAssertion().ass(FileAssertion.assert_txt_length_equal.__name__, self.txt_file, len(self.content))

    def test_txt_startswith(self):
        MangoAssertion().ass(FileAssertion.assert_txt_startswith.__name__, 'hello world\nabc', 'hello')
        MangoAssertion().ass(FileAssertion.assert_txt_startswith.__name__, self.txt_file, 'hello world')

    def test_txt_endswith(self):
        MangoAssertion().ass(FileAssertion.assert_txt_endswith.__name__, 'abcEND.', 'END.')
        MangoAssertion().ass(FileAssertion.assert_txt_endswith.__name__, self.txt_file, 'END.')

    def test_txt_endswith1(self):
        from mangotools.data_processor import DataProcessor
        data = {
            'd': False,
        }
        MangoAssertion().p_is_false(DataProcessor.get_json_path_value(data, '$.d'))

    def test_txt_endswith2(self):
        MangoAssertion().p_is_not_none('None')

    def test_txt_endswith3(self):
        MangoAssertion().p_is_digit(1)
