# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-08-08 17:13
# @Author : 毛鹏
import unittest

from mangotools.data_processor import DataProcessor

data = {"resExt": None, "resMsg": "请求成功!", "resCode": 200, "resData": {"list": [
    {"id": 196, "name": "Vb4Zd7u6Ma1", "type": 0, "userId": 77, "kolCount": 1, "userName": "自动化巡检员",
     "createTime": "2025-08-08 17:09:46", "requestStatus": 1, "lastUpdateTime": "2025-08-08 17:09:47",
     "requestStatusStats": {"fail": 0, "total": 1, "pending": 0, "running": 0, "success": 1, "requestId": ""}},
    {"id": 194, "name": "ZDfc0ROvKK1", "type": 0, "userId": 77, "kolCount": 1, "userName": "自动化巡检员",
     "createTime": "2025-08-08 17:06:52", "requestStatus": 1, "lastUpdateTime": "2025-08-08 17:06:53",
     "requestStatusStats": {"fail": 0, "total": 1, "pending": 0, "running": 0, "success": 1, "requestId": ""}},
    {"id": 193, "name": "OKN7ckRAFY1", "type": 0, "userId": 77, "kolCount": 1, "userName": "自动化巡检员",
     "createTime": "2025-08-08 16:55:55", "requestStatus": 1, "lastUpdateTime": "2025-08-08 16:55:56",
     "requestStatusStats": {"fail": 0, "total": 1, "pending": 0, "running": 0, "success": 1, "requestId": ""}},
    {"id": 192, "name": "213213", "type": 0, "userId": 77, "kolCount": None, "userName": "自动化巡检员",
     "createTime": "2025-08-08 16:48:31", "requestStatus": None, "lastUpdateTime": None, "requestStatusStats": None},
    {"id": 191, "name": "测试提报1", "type": 0, "userId": 77, "kolCount": 1, "userName": "自动化巡检员",
     "createTime": "2025-08-08 15:52:40", "requestStatus": 1, "lastUpdateTime": "2025-08-08 16:16:56",
     "requestStatusStats": {"fail": 0, "total": 1, "pending": 0, "running": 0, "success": 1, "requestId": ""}},
    {"id": 190, "name": "自动化提报22", "type": 0, "userId": 77, "kolCount": None, "userName": "自动化巡检员",
     "createTime": "2025-07-01 15:51:27", "requestStatus": None, "lastUpdateTime": None, "requestStatusStats": None}],
                                                                           "total": 6, "pageSize": 20, "pageIndex": 1},
        "resSuccess": True}


class TestMango(unittest.TestCase):

    def test_001(self):
        res = DataProcessor.get_json_path_value(data, '$.resData.list[*].name')
        print(res)
        assert res is not None
        from mangotools.assertion import MangoAssertion
        print(MangoAssertion.p_contains(res, 'Vb4Zd7u6Ma1'))

    def test_002(self):
        res = DataProcessor.get_json_path_value(data, '$.resData.list[*].name', 3)
        print(res)
        assert res is not None

    def test_003(self):
        res = DataProcessor.get_json_path_value(data, '$.resMsg')
        print(res)
        assert res is not None
