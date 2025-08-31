# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 14:09
# @Author : 毛鹏
from ...data_processor import DataProcessor
from ...decorator import sync_method_callback
from ...exceptions import MangoToolsError
from ...exceptions.error_msg import ERROR_MSG_0061
from ...models import MethodModel

v = """
def func(self):
    # 示例函数，函数名称必须是func，必须带有self参数，self.test_data.get_cache('key')可以获取到缓存中的数据，断言必须返回结果，因为返回的结果会作为提示显示在页面
    user = self.test_data.get_cache('账号A')
    print(user)
    assert user == 'auto_te1st@qq.com', f'用户邮箱不匹配,实际={user}，预期=auto_test@qq.com'
"""


class CustomAssertion:
    """函数断言"""

    def __init__(self, test_data: DataProcessor):
        self.test_data = test_data

    @sync_method_callback('函数断言', '函数断言', 7, [
        MethodModel(f='func_str', p='请输入一个python函数，函数名称必须是：func', d=True, v=v)])
    def ass_func(self, func_str):
        """输入断言代码"""
        try:
            global_namespace = {}
            exec(func_str, global_namespace)
            return global_namespace['func'](self)
        except (KeyError, SyntaxError, TypeError):
            import traceback
            traceback.print_exc()
            raise MangoToolsError(*ERROR_MSG_0061)

    def func(self):
        # 示例函数，函数名称必须是func，必须带有self参数，self.test_data.get_cache('key')可以获取到缓存中的数据，断言必须返回结果，因为返回的结果会作为提示显示在页面
        user = self.test_data.get_cache('账号A')
        print(user)
        assert user == 'auto_te1st@qq.com', f'用户邮箱不匹配,实际={user}，预期=auto_test@qq.com'