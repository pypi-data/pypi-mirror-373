# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 14:12
# @Author : 毛鹏
from assertpy import assert_that
from deepdiff import DeepDiff

from ...decorator import sync_method_callback
from ...models import MethodModel


def _assert_that(actual):
    if actual is None:
        raise AssertionError(f"实际值不能为 None ，可能是在获取实际值的时候就失败了！")
    return assert_that(actual)


class MatchingAssertion:
    """值匹配什么"""

    @staticmethod
    @sync_method_callback('内容断言', '值匹配什么', 0, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_in_dict(actual: dict, expect: dict):
        """实际JSON匹配预期JSON"""
        try:
            filtered_actual = filter_dict(dict(actual), dict(expect))
        except ValueError:
            assert False, f'实际={actual}, 预期={expect}, 预期或者实际不可序列化为json'
        diff = DeepDiff(filtered_actual, expect, ignore_order=True)
        assert not diff, f'实际={str(actual)}, 预期={expect}'
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值匹配什么', 1, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_is_in(actual: str, expect: str):
        """在expect里面"""
        try:
            _assert_that(str(actual)).is_in(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值匹配什么', 2, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_is_not_in(actual: str, expect: str):
        """不在expect里面"""
        try:
            _assert_that(str(actual)).is_not_in(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值匹配什么', 3, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_starts_with(actual: str, expect: str):
        """以expect开头"""
        try:
            _assert_that(str(actual)).starts_with(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值匹配什么', 4, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_ends_with(actual: str, expect: str):
        """以expect结尾"""
        try:
            _assert_that(str(actual)).ends_with(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值匹配什么', 5, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_matches(actual: str, expect: str):
        """正则匹配等于expect"""
        try:
            _assert_that(str(actual)).matches(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'

    @staticmethod
    @sync_method_callback('内容断言', '值匹配什么', 6, [
        MethodModel(f='actual', d=True), MethodModel(f='expect', p='请输入断言值', d=True)])
    def p_does_not_match(actual: str, expect: str):
        """正则不匹配expect"""
        try:
            _assert_that(str(actual)).does_not_match(expect)
        except AssertionError as e:
            raise AssertionError(f'实际={str(actual)}, 预期={expect}') from e
        return f'实际={str(actual)}, 预期={expect}'


def filter_dict(actual: dict, expect: dict) -> dict:
    filtered = {}
    for key in expect.keys():
        if key in actual:
            if isinstance(expect[key], dict):
                filtered[key] = filter_dict(actual[key], expect[key])
            elif isinstance(expect[key], list) and isinstance(actual[key], list):
                filtered[key] = []
                for item in actual[key]:
                    if isinstance(item, dict):
                        filtered_item = filter_dict(item, expect[key][0])
                        filtered[key].append(filtered_item)
                    else:
                        filtered[key].append(item)
            else:
                filtered[key] = actual[key]
    return filtered
