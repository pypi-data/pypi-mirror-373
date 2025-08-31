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


class WhatIsItAssertion:
    """类型是什么"""

    @staticmethod
    @sync_method_callback('内容断言', '类型是什么', 0, [
        MethodModel(f='actual', d=True)])
    def p_is_not_none(actual):
        """不是null"""
        try:
            assert_that(actual).is_not_none()
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期=不是None') from e
        return f'实际={actual}, 预期=不是None'

    @staticmethod
    @sync_method_callback('内容断言', '类型是什么', 1, [
        MethodModel(f='actual', d=True)])
    def p_is_none(actual):
        """是null"""
        try:
            assert_that(actual).is_none()
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期=是None') from e
        return f'实际={actual}, 预期=是None'

    @staticmethod
    @sync_method_callback('内容断言', '类型是什么', 2, [
        MethodModel(f='actual', d=True)])
    def p_is_empty(actual):
        """是空字符串"""
        try:
            _assert_that(actual).is_empty()
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期=是空字符串') from e
        return f'实际={actual}, 预期=是空字符串'

    @staticmethod
    @sync_method_callback('内容断言', '类型是什么', 3, [
        MethodModel(f='actual', d=True)])
    def p_is_not_empty(actual):
        """不是空符串"""
        try:
            _assert_that(actual).is_not_empty()
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期=不是空符串') from e
        return f'实际={actual}, 预期=不是空符串'

    @staticmethod
    @sync_method_callback('内容断言', '类型是什么', 4, [
        MethodModel(f='actual', d=True)])
    def p_is_false(actual):
        """是False"""
        try:
            assert_that(actual).is_false()
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期=是False') from e
        return f'实际={actual}, 预期=是False'

    @staticmethod
    @sync_method_callback('内容断言', '类型是什么', 5, [
        MethodModel(f='actual', d=True)])
    def p_is_true(actual):
        """是True"""
        try:
            assert_that(actual).is_true()
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期=是True') from e
        return f'实际={actual}, 预期=是True'

    @staticmethod
    @sync_method_callback('内容断言', '类型是什么', 6, [
        MethodModel(f='actual', d=True)])
    def p_is_alpha(actual):
        """是字母"""
        try:
            _assert_that(actual).is_alpha()
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期=是字母') from e
        return f'实际={actual}, 预期=是字母'

    @staticmethod
    @sync_method_callback('内容断言', '类型是什么', 7, [
        MethodModel(f='actual', d=True)])
    def p_is_digit(actual):
        """是整数"""
        try:
            _assert_that(str(actual)).is_digit()
        except AssertionError as e:
            raise AssertionError(f'实际={actual}, 预期=是数字') from e

        return f'实际={actual}, 预期=是数字'
