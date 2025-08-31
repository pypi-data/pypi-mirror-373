# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-30 17:12
# @Author : 毛鹏
import json
import tempfile
import unittest

from mangotools.data_processor import SqlCache
from mangotools.enums import CacheValueTypeEnum


class TestSqlCache(unittest.TestCase):
    def setUp(self):
        """在每个测试方法前初始化"""
        temp_db = tempfile.NamedTemporaryFile(delete=False)
        temp_db.close()
        db_path = temp_db.name
        self.cache = SqlCache(db_path)

    def test_01(self):
        self.cache.set_sql_cache("test_str", "hello world", CacheValueTypeEnum.STR)
        print(type(self.cache.get_sql_cache("test_str")), self.cache.get_sql_cache("test_str"))
        assert self.cache.get_sql_cache("test_str") == "hello world"

    def test_02(self):
        self.cache.set_sql_cache("test_int", 42, CacheValueTypeEnum.INT)
        print(type(self.cache.get_sql_cache("test_int")), self.cache.get_sql_cache("test_int"))
        assert self.cache.get_sql_cache("test_int") == 42

    def test_03(self):
        self.cache.set_sql_cache("test_float", 3.14, CacheValueTypeEnum.FLOAT)
        print(type(self.cache.get_sql_cache("test_float")), self.cache.get_sql_cache("test_float"))
        assert self.cache.get_sql_cache("test_float") == 3.14

    def test_04(self):
        self.cache.set_sql_cache("test_bool", True, CacheValueTypeEnum.BOOL)
        print(type(self.cache.get_sql_cache("test_bool")), self.cache.get_sql_cache("test_bool"))
        assert self.cache.get_sql_cache("test_bool") is True

    def test_05(self):
        self.cache.set_sql_cache("test_none", None, CacheValueTypeEnum.NONE)
        print(type(self.cache.get_sql_cache("test_none")), self.cache.get_sql_cache("test_none"))
        assert self.cache.get_sql_cache("test_none") is None

    def test_06(self):
        test_list = [1, 2, 3, "four"]
        self.cache.set_sql_cache("test_list", test_list, CacheValueTypeEnum.LIST)
        print(type(self.cache.get_sql_cache("test_list")), self.cache.get_sql_cache("test_list"))
        assert self.cache.get_sql_cache("test_list") == test_list

    def test_07(self):
        test_dict = {"a": 1, "b": 2, "c": "three"}
        self.cache.set_sql_cache("test_dict", test_dict, CacheValueTypeEnum.DICT)
        print(type(self.cache.get_sql_cache("test_dict")), self.cache.get_sql_cache("test_dict"))
        assert self.cache.get_sql_cache("test_dict") == test_dict

    def test_08(self):
        test_tuple = (1, 2, 3, "four")
        self.cache.set_sql_cache("test_tuple", test_tuple, CacheValueTypeEnum.TUPLE)
        print(type(self.cache.get_sql_cache("test_tuple")), self.cache.get_sql_cache("test_tuple"))
        assert self.cache.get_sql_cache("test_tuple") == test_tuple

    def test_09(self):
        test_json = {"name": "John", "age": 30, "city": "New York"}
        self.cache.set_sql_cache("test_json", test_json, CacheValueTypeEnum.JSON)
        print(type(self.cache.get_sql_cache("test_json")), self.cache.get_sql_cache("test_json"))
        assert self.cache.get_sql_cache("test_json") == test_json

    def test_10(self):
        print(json.dumps(self.cache.get_sql_all()))
        assert self.cache.contains_sql_cache("nonexistent") is False

    def test_11(self):
        print("测试删除。..")
        self.cache.delete_sql_cache("test_str")
        assert self.cache.get_sql_cache("test_str") is None
        assert self.cache.contains_sql_cache("test_str") is False

    def test_12(self):
        print("测试清除。..")
        self.cache.clear_sql_cache()
        assert self.cache.get_sql_cache("test_int") is None
        assert self.cache.contains_sql_cache("test_int") is False
