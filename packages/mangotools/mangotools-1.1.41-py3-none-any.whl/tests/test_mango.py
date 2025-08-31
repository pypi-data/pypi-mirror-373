# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-23 16:55
# @Author : 毛鹏
import unittest

from mangotools.data_processor import DataProcessor
from mangotools.database import MysqlConnect
from mangotools.log_collector import set_log
from mangotools.mangos import Mango
from mangotools.models import MysqlConingModel


class TestMango(unittest.TestCase):

    def test_001(self, is_send=False):
        if is_send:
            text = '哈哈哈，测试内容！'
            Mango.s(self.test_001, text, self.test_001)

    def test_004(self):
        mysql_connect = MysqlConnect(MysqlConingModel(
            host='118.196.24.189',
            port=3306,
            user='root',
            password='mP123456&',
            database='mango_server',
        ))
        result = mysql_connect.execute('SHOW TABLES;')
        assert result is not None

    def test_005(self):
        pass

    def test_006(self):
        value = 'haha'
        key = '${{key}}'
        processor = DataProcessor()
        Mango.s_e(processor, 'set_cache', {'key': 'key', "value": value})
        print(processor.replace(key))
        assert Mango.s_e(processor, 'replace', key) == value

    def test_0066(self):
        key = '${{randint(left= 1,left=2)}}'
        processor = DataProcessor()
        print(processor.replace(key))

    def test_007(self):
        log = set_log("D:\GitCode\MangoKit\logs", True)
        log.debug('DEBUG')
        log.info("INFO")
        log.warning("WARNING")
        log.error("ERROR")
        log.critical("CRITICAL")

    def test_008(self):
        pass
