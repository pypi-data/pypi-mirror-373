# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-01-21 11:42
# @Author : 毛鹏
import unittest

from mangotools.data_processor import DataProcessor


class TestCache(unittest.TestCase):

    def test_001(self):
        """设置缓存和使用华城"""
        value = '设置到缓存中'
        processor = DataProcessor()
        processor.set_cache('value', value)  # 首先我们把value设置一个值
        assert processor.get_cache('value') == value
        return processor.get_cache('value')

    def test_002(self):
        """替换${{}}中间的内容"""
        key = '芒果测试平台'
        value = '替换：${{key}}'
        processor = DataProcessor()
        processor.set_cache('key', key)  # 首先我们把value设置一个值
        assert processor.replace(value) == '替换：芒果测试平台'
        return processor.replace(value)  # 调用replace进行替换

    def test_003(self):
        """获取公共方法中的数据"""
        processor = DataProcessor()
        assert processor.replace('${{md5_32_small(123456)}}') is not None
        return processor.replace('${{md5_32_small(123456)}}')

    def test_004(self):
        """直接将获取到的内容存到缓存中"""
        str_ = "我是基于时间戳的5位随机数：${{number_time_5()|flow名称}}"
        processor = DataProcessor()
        value = processor.replace(str_)
        assert value == f"我是基于时间戳的5位随机数：{processor.get_cache('flow名称')}"
        return f"我是基于时间戳的5位随机数：{processor.get_cache('flow名称')}"
