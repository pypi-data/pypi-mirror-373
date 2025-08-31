# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-23 16:55
# @Author : 毛鹏

from mangotools.data_processor import DataProcessor
from mangotools.database import MysqlConnect
from mangotools.log_collector import set_log
from mangotools.mangos import Mango
from mangotools.models import MysqlConingModel


def test_001(is_send=False):
    if is_send:
        text = '哈哈哈，测试内容！'
        Mango.s(test_001, text, test_001)


def test_004():
    mysql_connect = MysqlConnect(MysqlConingModel(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mP123456&',
        database='mango_server',
    ))
    result = mysql_connect.execute('SHOW TABLES;')
    assert result is not None


def test_005():
    pass


def test_006():
    value = 'haha'
    key = '${key}'
    processor = DataProcessor()
    Mango.s_e(processor, 'set_cache', {'key': 'key', "value": value})
    print(processor.replace(key))
    assert Mango.s_e(processor, 'replace', key) == value


def test_0066():
    key = '${{randint({"left": 1,"left"=2})}}'
    processor = DataProcessor()
    print(processor.replace(key))


def test_007():
    log = set_log("D:\GitCode\MangoKit\logs", True)
    log.debug('DEBUG')
    log.info("INFO")
    log.warning("WARNING")
    log.error("ERROR")
    log.critical("CRITICAL")


def test_008():
    pass


if __name__ == '__main__':
    test_001(True)
    # test_004()
    # test_005()
    # test_006()
    # test_007()
    # test_008()
    # test_0066()
