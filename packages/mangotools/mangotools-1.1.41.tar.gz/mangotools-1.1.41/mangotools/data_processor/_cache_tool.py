# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-08-29 10:23
# @Author : 毛鹏

from cachetools import LRUCache


class CacheTool:
    """ 内存缓存 """

    def __init__(self):
        self._cache: LRUCache = LRUCache(maxsize=10_000)

    def get_cache(self, key: str) -> any:
        """得到缓存key的value"""
        return self._cache.get(key)

    def set_cache(self, key: str, value: any) -> None:
        """设置一个内容到缓存"""
        self._cache[key] = value

    def delete_cache(self, key: str) -> None:
        """删除一个缓存"""
        if key in self._cache:
            del self._cache[key]

    def clear_cache(self) -> None:
        """清理所有缓存"""
        self._cache.clear()

    def has_cache(self, key: str) -> bool:
        """判断缓存是否存在"""
        return key in self._cache

    def get_all(self, ) -> dict:
        """获取全部的缓存数据"""
        return {k: v for k, v in self._cache.items()}

    def set_sql_cache(self, key: str, value: dict) -> None:
        """根据sql进行缓存数据"""
        if key is None or key == '':
            return
        for k, v in zip([part.strip() for part in key.split(',')], value):
            self.set_cache(k, value.get(v))

    def set_list_cache(self, key: list, value: list) -> None:
        """设置list缓存"""
        if key is None or key == '':
            return
        for k, v in zip(key, value):
            self.set_cache(k, v)

    def set_dict_cache(self, data: dict) -> None:
        """设置dict缓存"""
        for k, v in data.items():
            self.set_cache(k, v)
