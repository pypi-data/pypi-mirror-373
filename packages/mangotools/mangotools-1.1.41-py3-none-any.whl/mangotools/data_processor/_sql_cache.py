# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-08-30 14:20
# @Author : 毛鹏
import json
import sqlite3
from typing import Any

from ..database import SQLiteConnect
from ..enums import CacheValueTypeEnum


class SqlCache:
    """文件缓存"""
    create_table_query1 = '''
    CREATE TABLE "cache_mango_2023" (
      "id" INTEGER PRIMARY KEY AUTOINCREMENT,
      "key" TEXT NOT NULL,
      "value" TEXT,
      "case_id" TEXT,
      "type" INTEGER,
      "internal" INTEGER
    );
    '''

    def __init__(self, cache_path):
        self.cache_path = cache_path
        self.conn = SQLiteConnect(self.cache_path)
        for i in [self.create_table_query1]:
            try:
                self.conn.execute(i)
            except sqlite3.OperationalError:
                pass
        self.sql_statement_2 = f'SELECT * FROM cache_mango_2023;'
        self.sql_statement_4 = f'INSERT INTO "cache_mango_2023" ("key", "value", "type") VALUES (?, ?, ?);'
        self.sql_statement_5 = f'SELECT * FROM cache_mango_2023 WHERE `key` = ?;'
        self.sql_statement_6 = f'DELETE FROM cache_mango_2023 WHERE `key` = ?;'
        self.sql_statement_7 = f'SELECT COUNT(*) FROM cache_mango_2023 WHERE `key` = ?;'
        self.sql_statement_8 = f'DELETE FROM cache_mango_2023;'

    def get_sql_cache(self, key: str) -> [str, list, dict, int, float, bool, tuple, None]:
        """
        获取缓存中指定键的值
        :param key: 缓存键
        :return:
        """
        res = self.conn.execute(self.sql_statement_5, (key,))
        if res:
            res = res[0]
        else:
            return None

        value = res.get('value')
        value_type = res.get('type')

        if value_type == CacheValueTypeEnum.STR.value:
            return value if value != '' else None
        elif value_type == CacheValueTypeEnum.INT.value:
            return int(value)
        elif value_type == CacheValueTypeEnum.FLOAT.value:
            return float(value)
        elif value_type == CacheValueTypeEnum.BOOL.value:
            return value.lower() == 'true'
        elif value_type == CacheValueTypeEnum.NONE.value:
            return None
        elif value_type == CacheValueTypeEnum.LIST.value:
            return json.loads(value)
        elif value_type == CacheValueTypeEnum.DICT.value:
            return json.loads(value)
        elif value_type == CacheValueTypeEnum.TUPLE.value:
            return tuple(json.loads(value))
        elif value_type == CacheValueTypeEnum.JSON.value:
            return json.loads(value)
        return value

    def set_sql_cache(self, key: str, value: Any, value_type: CacheValueTypeEnum = CacheValueTypeEnum.STR) -> None:
        """
        设置缓存键的值
        :param key: 缓存键
        :param value: 缓存值
        :param value_type: 值类型
        :return: None
        """
        if value_type == CacheValueTypeEnum.STR:
            str_value = str(value)
        elif value_type == CacheValueTypeEnum.INT:
            str_value = str(int(value))
        elif value_type == CacheValueTypeEnum.FLOAT:
            str_value = str(float(value))
        elif value_type == CacheValueTypeEnum.BOOL:
            str_value = str(bool(value)).lower()
        elif value_type == CacheValueTypeEnum.NONE:
            str_value = 'null'
        elif value_type in (CacheValueTypeEnum.LIST, CacheValueTypeEnum.DICT,
                            CacheValueTypeEnum.TUPLE, CacheValueTypeEnum.JSON):
            str_value = json.dumps(value)
        else:
            str_value = str(value)
            value_type = CacheValueTypeEnum.STR

        res = self.conn.execute(self.sql_statement_5, (key,))
        if res:
            self.conn.execute(self.sql_statement_6, (key,))

        self.conn.execute(self.sql_statement_4, (key, str_value, value_type.value))

    def delete_sql_cache(self, key: str) -> None:
        """
        删除缓存中指定键的值
        :param key: 缓存键
        :return: None
        """
        self.conn.execute(self.sql_statement_6, (key,))

    def contains_sql_cache(self, key: str) -> bool:
        """
        检查缓存中是否包含指定键
        :param key: 缓存键
        :return: 如果缓存中包含指定键，返回True；否则返回False
        """
        res = self.conn.execute(self.sql_statement_7, (key,))
        return res[0]['COUNT(*)'] > 0 if res else False

    def clear_sql_cache(self) -> None:
        """
        清空缓存中的所有键值对
        :return: None
        """
        self.conn.execute(self.sql_statement_8)

    def get_sql_all(self):
        return {i.get('key'): self.get_sql_cache(i.get('key')) for i in self.conn.execute(self.sql_statement_2)}
