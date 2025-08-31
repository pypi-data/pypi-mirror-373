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


class ContainAssertion:
    """值包含什么"""

    @staticmethod
    @sync_method_callback('内容断言', '值包含什么', 0, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_contains(actual: str, expect: str):
        """包含expect"""
        try:
            _assert_that(str(actual)).contains(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值包含什么', 1, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_is_equal_to_ignoring_case(actual: str, expect: str):
        """忽略大小写等于expect"""
        try:
            _assert_that(str(actual)).is_equal_to_ignoring_case(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值包含什么', 2, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_contains_ignoring_case(actual: str, expect: str):
        """包含忽略大小写expect"""
        try:
            _assert_that(str(actual)).contains_ignoring_case(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值包含什么', 3, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_contains_only(actual: str, expect: str):
        """仅包含expect"""
        try:
            _assert_that(str(actual)).contains_only(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值包含什么', 4, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_does_not_contain(actual: str, expect: str):
        """不包含expect"""
        try:
            _assert_that(actual).does_not_contain(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期={expect}') from e
        return f'实际={actual}, 预期={expect}'
