# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-24 10:01
# @Author : 毛鹏
import unittest

from mangotools.mangos import Mango, get, inside_post


class TestMangos(unittest.TestCase):

    def test_mango(self):
        Mango.v(1, '测试通过')
        print(type(get), get.__name__)
        print(type(inside_post), get.__name__)
