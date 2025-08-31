# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-11 10:17
# @Author : 毛鹏
from ..enums._base_enum import BaseEnum


class CacheValueTypeEnum(BaseEnum):
    """缓存数据类型"""
    STR = 0
    INT = 1
    FLOAT = 2
    BOOL = 3
    NONE = 4
    LIST = 5
    DICT = 6
    TUPLE = 7
    JSON = 8

    @classmethod
    def obj(cls):
        return {0: "字符串", 1: "整数", 2: "小数", 3: "布尔", 4: "null", 5: "列表", 6: "字典", 7: "元组", 8: "JSON"}


class NoticeEnum(BaseEnum):
    """通知枚举"""
    MAIL = 0
    WECOM = 1
    NAILING = 2

    @classmethod
    def obj(cls):
        return {0: "邮箱", 1: "企微", 2: "钉钉-未测试"}


class StatusEnum(BaseEnum):
    """状态枚举"""
    SUCCESS = 1
    FAIL = 0

    @classmethod
    def obj(cls):
        return {0: "关闭&进行中&失败", 1: "启用&已完成&通过"}


class AssEnum(BaseEnum):
    """状态枚举"""
    TEXT = 0
    FILE = 1
    SQL = 2
    CUSTOM = 3

    @classmethod
    def obj(cls):
        return {0: "关闭&进行中&失败", 1: "启用&已完成&通过"}
