# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time: 2023-07-16 15:17
# @Author : 毛鹏


class MangoToolsError(Exception):

    def __init__(self, code: int, msg: str, value: tuple = None):
        self.msg = msg.format(*value) if value else msg
        self.code = code

    def __str__(self):
        return f"[{self.code}] {self.msg}"
