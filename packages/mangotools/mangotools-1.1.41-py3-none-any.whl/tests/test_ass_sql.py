# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-07 16:38
# @Author : 毛鹏
import unittest

from mangotools.assertion import MangoAssertion
from mangotools.database import MysqlConnect
from mangotools.models import MysqlConingModel


class TestAssSql(unittest.TestCase):

    def test_001(self):
        mysql_conn = MysqlConnect(MysqlConingModel(
            **{"host": "172.16.100.26", "port": 3306, "user": "root", "password": "Root@123",
               "database": "z_desk_efficiency_pre"}
        ))

        MangoAssertion(mysql_conn).ass("assert_sql_is_not_empty",
                                       "SELECT oss_url FROM `data_subscription_mine_task_send_detail` WHERE subscription_mine_id = '387';")
