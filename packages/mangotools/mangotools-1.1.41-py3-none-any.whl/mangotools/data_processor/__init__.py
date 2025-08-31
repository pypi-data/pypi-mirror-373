# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import re

from ..data_processor._cache_tool import CacheTool
from ..data_processor._coding_tool import CodingTool
from ..data_processor._encryption_tool import EncryptionTool
from ..data_processor._json_tool import JsonTool
from ..data_processor._random_character_info_data import RandomCharacterInfoData
from ..data_processor._random_number_data import RandomNumberData
from ..data_processor._random_string_data import RandomStringData
from ..data_processor._random_time_data import RandomTimeData
from ..data_processor._sql_cache import SqlCache
from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0047, ERROR_MSG_0002, ERROR_MSG_0022
from ..mangos import Mango

"""
ObtainRandomData类的函数注释必须是： “”“中间写值”“”
"""


class ObtainRandomData(RandomNumberData, RandomCharacterInfoData, RandomTimeData, RandomStringData):
    """ 获取随机数据 """

    def regular(self, func: str):
        try:
            return Mango.regular(self, func, MangoToolsError, ERROR_MSG_0022)
        except AttributeError:
            raise MangoToolsError(*ERROR_MSG_0047)


class DataClean(JsonTool, CacheTool, EncryptionTool, CodingTool):
    """存储或处理随机数据"""
    pass


class DataProcessor(ObtainRandomData, DataClean):

    def __init__(self):
        ObtainRandomData.__init__(self)
        DataClean.__init__(self)

    def replace(self, data: list | dict | str | None) -> list | dict | str | None:
        if not data:
            return data
        if isinstance(data, list):
            return [self.replace(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.replace(value) for key, value in data.items()}
        else:
            return Mango.replace_str(self, data, ERROR_MSG_0002, MangoToolsError)

    @classmethod
    def remove_parentheses(cls, data: str) -> str:
        return data.replace("${{", "").replace("}}", "").strip()

    @classmethod
    def identify_parentheses(cls, value: str):
        return re.search(r'\((.*?)\)', str(value))

    @classmethod
    def is_extract(cls, string: str) -> bool:
        return bool(re.search(r'\$\{\{.*\}\}', string))


__all__ = [
    'CacheTool',
    'CodingTool',
    'EncryptionTool',
    'JsonTool',
    'RandomCharacterInfoData',
    'RandomNumberData',
    'RandomStringData',
    'RandomTimeData',
    'ObtainRandomData',
    'DataClean',
    'DataProcessor',
    'SqlCache'
]
