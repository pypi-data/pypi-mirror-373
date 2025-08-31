# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 11:13
# @Author : 毛鹏
import unittest

from mangotools.assertion import MangoAssertion
from mangotools.assertion.custom import v
from mangotools.data_processor import DataProcessor


class TestCustomAssertion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_txt_equal(self):
        self.test_data = DataProcessor()
        self.test_data.set_cache('账号A', 'maopeng@qq.com')
        MangoAssertion(test_data=self.test_data).ass(MangoAssertion.ass_func.__name__, v)
