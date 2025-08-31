# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-28 14:38
# @Author : 毛鹏
import unittest

from mangotools.data_processor import ObtainRandomData


class TestRandom(unittest.TestCase):
    def setUp(self):
        """在每个测试方法前初始化"""
        self.random = ObtainRandomData()

    def test_basic_operations(self):
        """测试基本缓存操作"""
        # 测试设置和获取缓存
        print(self.random.regular('randint(left=2,right=5)'))
        print(self.random.regular('number_random_hex_str(digits=8)'))
        print(self.random.regular('number_random_hex_str(8)'))
        print(self.random.regular('number_random_bin_str()'))
        print(self.random.regular('time_day_reduce()'))


if __name__ == '__main__':
    unittest.main()
