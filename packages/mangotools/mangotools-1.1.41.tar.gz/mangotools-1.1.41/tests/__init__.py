# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-07 23:25
# @Author : 毛鹏
import unittest

# 确保这些导入路径是正确的
from tests.test_ass_excel import TestExcelTaskSheet
from tests.test_ass_sql import TestAssSql
from tests.test_ass_txt import TestTxtAssertion
from tests.test_cache import TestCache
from tests.test_mango import TestMango
from tests.test_mangos import TestMangos
from tests.test_random import TestRandom
from tests.test_sql_cache import TestSqlCache


def create_suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # 添加所有测试类
    suite.addTest(loader.loadTestsFromTestCase(TestExcelTaskSheet))
    suite.addTest(loader.loadTestsFromTestCase(TestAssSql))
    suite.addTest(loader.loadTestsFromTestCase(TestTxtAssertion))
    suite.addTest(loader.loadTestsFromTestCase(TestCache))
    suite.addTest(loader.loadTestsFromTestCase(TestMango))
    suite.addTest(loader.loadTestsFromTestCase(TestMangos))
    suite.addTest(loader.loadTestsFromTestCase(TestRandom))
    suite.addTest(loader.loadTestsFromTestCase(TestSqlCache))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(create_suite())