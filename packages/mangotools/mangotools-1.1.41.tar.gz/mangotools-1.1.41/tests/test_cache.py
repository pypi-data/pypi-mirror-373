# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-06-26 10:43
# @Author : 毛鹏
import unittest

from cachetools import LRUCache

from mangotools.data_processor import CacheTool


class TestCache(unittest.TestCase):
    def setUp(self):
        """在每个测试方法前初始化"""
        self.cache = CacheTool()

    def test_basic_operations(self):
        """测试基本缓存操作"""
        # 测试设置和获取缓存
        self.cache.set_cache('name', 'Alice')
        self.assertEqual(self.cache.get_cache('name'), 'Alice')

        # 测试缓存是否存在
        self.assertTrue(self.cache.has_cache('name'))
        self.assertFalse(self.cache.has_cache('nonexistent'))

        # 测试删除缓存
        self.cache.delete_cache('name')
        self.assertIsNone(self.cache.get_cache('name'))

    def test_clear_cache(self):
        """测试清空缓存"""
        self.cache.set_cache('key1', 'value1')
        self.cache.set_cache('key2', 'value2')
        self.cache.clear_cache()
        self.assertEqual(len(self.cache.get_all()), 0)

    def test_get_all(self):
        """测试获取所有缓存"""
        self.cache.set_cache('a', 1)
        self.cache.set_cache('b', 2)
        all_cache = self.cache.get_all()
        self.assertEqual(all_cache, {'a': 1, 'b': 2})

    def test_set_sql_cache(self):
        """测试SQL式缓存设置"""
        keys = 'id,name ,age'
        values = {'id': 1, 'name': 'Bob', 'age': 30}
        self.cache.set_sql_cache(keys, values)

        self.assertEqual(self.cache.get_cache('id'), 1)
        self.assertEqual(self.cache.get_cache('name'), 'Bob')
        self.assertEqual(self.cache.get_cache('age'), 30)

    def test_set_list_cache(self):
        """测试列表缓存设置"""
        keys = ['k1', 'k2', 'k3']
        values = ['v1', 'v2', 'v3']
        self.cache.set_list_cache(keys, values)

        self.assertEqual(self.cache.get_cache('k1'), 'v1')
        self.assertEqual(self.cache.get_cache('k2'), 'v2')
        self.assertEqual(self.cache.get_cache('k3'), 'v3')

    def test_set_dict_cache(self):
        """测试字典缓存设置"""
        data = {
            'color': 'red',
            'size': 'large',
            'price': 99.9
        }
        self.cache.set_dict_cache(data)

        self.assertEqual(self.cache.get_cache('color'), 'red')
        self.assertEqual(self.cache.get_cache('size'), 'large')
        self.assertEqual(self.cache.get_cache('price'), 99.9)

    def test_lru_eviction(self):
        """测试LRU淘汰机制"""
        # 创建最大容量为3的缓存
        small_cache = CacheTool()
        small_cache._cache = LRUCache(maxsize=3)

        small_cache.set_cache('1', 'one')
        small_cache.set_cache('2', 'two')
        small_cache.set_cache('3', 'three')

        # 访问'1'使其成为最近使用的
        small_cache.get_cache('1')

        # 添加第四个元素，应该淘汰'2'（因为'1'被访问过，'3'是最久未使用的）
        small_cache.set_cache('4', 'four')

        self.assertEqual(len(small_cache.get_all()), 3)
        self.assertIsNone(small_cache.get_cache('2'))
        self.assertEqual(small_cache.get_cache('1'), 'one')
        self.assertEqual(small_cache.get_cache('3'), 'three')
        self.assertEqual(small_cache.get_cache('4'), 'four')


if __name__ == '__main__':
    unittest.main()
