# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: txt文件断言
# @Time   : 2025-07-04
# @Author : 毛鹏

from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel


class TxtAssertion:
    """txt文件"""

    @staticmethod
    @sync_method_callback('文件断言', 'txt断言', 0, [
        MethodModel(f='actual', p='实际内容或文件路径', d=True),
        MethodModel(f='expect', p='期望内容', d=True),
    ])
    def assert_txt_equal(actual: str, expect: str):
        """内容完全相等"""
        if actual.endswith('.txt'):
            with open(actual, encoding='utf-8') as f:
                actual_content = f.read()
        else:
            actual_content = actual
        assert actual_content == expect, f'实际内容={actual_content}, 期望内容={expect}'
        return f'实际内容={actual_content}, 期望内容={expect}'

    @staticmethod
    @sync_method_callback('文件断言', 'txt断言', 1, [
        MethodModel(f='actual', p='实际内容或文件路径', d=True),
        MethodModel(f='expect', p='期望包含内容', d=True),
    ])
    def assert_txt_contains(actual: str, expect: str):
        """内容包含指定字符串"""
        if actual.endswith('.txt'):
            with open(actual, encoding='utf-8') as f:
                actual_content = f.read()
        else:
            actual_content = actual
        assert expect in actual_content, f'实际内容={actual_content}, 期望包含={expect}'
        return f'实际内容={actual_content}, 期望包含={expect}'

    @staticmethod
    @sync_method_callback('文件断言', 'txt断言', 2, [
        MethodModel(f='actual', p='实际内容或文件路径', d=True),
        MethodModel(f='expect', p='期望长度', d=True),
    ])
    def assert_txt_length_equal(actual: str, expect: int):
        """内容长度等于期望值"""
        if actual.endswith('.txt'):
            with open(actual, encoding='utf-8') as f:
                actual_content = f.read()
        else:
            actual_content = actual
        assert len(actual_content) == int(expect), f'实际长度={len(actual_content)}, 期望长度={expect}'
        return f'实际长度={len(actual_content)}, 期望长度={expect}'

    @staticmethod
    @sync_method_callback('文件断言', 'txt断言', 3, [
        MethodModel(f='actual', p='实际内容或文件路径', d=True),
        MethodModel(f='expect', p='期望开头内容', d=True),
    ])
    def assert_txt_startswith(actual: str, expect: str):
        """内容以指定字符串开头"""
        if actual.endswith('.txt'):
            with open(actual, encoding='utf-8') as f:
                actual_content = f.read()
        else:
            actual_content = actual
        assert actual_content.startswith(expect), f'实际内容={actual_content}, 期望开头={expect}'
        return f'实际内容={actual_content}, 期望开头={expect}'

    @staticmethod
    @sync_method_callback('文件断言', 'txt断言', 4, [
        MethodModel(f='actual', p='实际内容或文件路径', d=True),
        MethodModel(f='expect', p='期望结尾内容', d=True),
    ])
    def assert_txt_endswith(actual: str, expect: str):
        """内容以指定字符串结尾"""
        if actual.endswith('.txt'):
            with open(actual, encoding='utf-8') as f:
                actual_content = f.read()
        else:
            actual_content = actual
        assert actual_content.endswith(expect), f'实际内容={actual_content}, 期望结尾={expect}'
        return f'实际内容={actual_content}, 期望结尾={expect}'
