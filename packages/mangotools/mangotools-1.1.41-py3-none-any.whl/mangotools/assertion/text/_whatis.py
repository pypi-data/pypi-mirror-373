# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 14:10
# @Author : 毛鹏
from assertpy import assert_that

from ...decorator import sync_method_callback
from ...models import MethodModel


def _assert_that(actual):
    if actual is None:
        raise AssertionError(f"实际值不能为 None ，可能是在获取实际值的时候就失败了！")
    return assert_that(actual)


class WhatIsEqualToAssertion:
    """值等于什么"""

    @staticmethod
    @sync_method_callback('内容断言', '值等于什么', 0, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_is_equal_to(actual: str, expect: str):
        """等于expect"""
        try:
            _assert_that(str(actual)).is_equal_to(expect),
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值等于什么', 1, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_is_not_equal_to(actual: str, expect: str):
        """不等于expect"""
        try:
            _assert_that(str(actual)).is_not_equal_to(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值等于什么', 2, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_is_length(actual: str, expect: str):
        """长度等于expect"""
        try:
            _assert_that(str(actual)).is_length(int(expect))
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值等于什么', 3, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_sum_equal_expect(actual: list, expect: str):
        """长度等于expect"""
        try:
            _assert_that(sum(actual)).is_equal_to(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'
