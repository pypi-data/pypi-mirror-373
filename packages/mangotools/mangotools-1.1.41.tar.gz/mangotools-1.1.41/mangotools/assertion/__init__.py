# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023/4/6 13:36
# @Author : 毛鹏

from .custom import CustomAssertion
from .file import FileAssertion, ExcelAssertion
from .sql import SqlAssertion
from .text import TextAssertion
from ..data_processor import DataProcessor
from ..database import MysqlConnect


class MangoAssertion(CustomAssertion, FileAssertion, SqlAssertion, TextAssertion):

    def __init__(self, mysql_conn: MysqlConnect | None = None, test_data: DataProcessor | None = None):
        SqlAssertion.__init__(self, mysql_conn)
        CustomAssertion.__init__(self, test_data)

    def ass(self, method: str, actual, expect=None) -> str:
        from mangotools.mangos import ass
        return ass(self, method, actual, expect,
                   text=TextAssertion, excel=ExcelAssertion, sql=SqlAssertion, custom=CustomAssertion)


__all__ = [
    'MangoAssertion',
    'TextAssertion',
    'FileAssertion',
    'SqlAssertion',
    'CustomAssertion',
    'ExcelAssertion',
]
