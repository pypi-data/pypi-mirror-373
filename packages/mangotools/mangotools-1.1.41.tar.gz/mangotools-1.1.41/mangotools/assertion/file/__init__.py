# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 14:09
# @Author : 毛鹏
from ._excel import ExcelAssertion
from ._txt import TxtAssertion


class FileAssertion(ExcelAssertion, TxtAssertion):
    """文件断言"""
