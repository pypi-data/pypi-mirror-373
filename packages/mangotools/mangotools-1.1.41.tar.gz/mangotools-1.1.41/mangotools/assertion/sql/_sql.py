# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-11-20 9:47
# @Author : 毛鹏
from deepdiff import DeepDiff

from mangotools.assertion.text import TextAssertion
from mangotools.database import MysqlConnect
from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel


def mysql_query(mysql_connect, actual, expect=None):
    result: list[dict] = mysql_connect.condition_execute(actual)
    assert result, f'实际={result}, 预期={expect}'
    first_row = result[0]
    return next(iter(first_row.values()))


class MysqlAssertion:
    """mysql"""

    def __init__(self, mysql_connect: MysqlConnect | None):
        self.mysql_connect: MysqlConnect = mysql_connect

    @sync_method_callback('sql断言', 'mysql', 1, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望条数', d=True),
    ])
    def assert_sql_count(self, actual: str, expect: int):
        """SQL查询结果条数"""
        result = self.mysql_connect.condition_execute(actual)
        assert len(result) == int(expect), f'实际条数={len(result)}, 预期条数={expect}'
        return f'实际条数={len(result)}, 预期条数={expect}'

    @sync_method_callback('sql断言', 'mysql', 2, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='请输入期望的dict', d=True),
    ])
    def assert_sql_first_row(self, actual: str, expect: dict):
        """数据相等"""
        result = self.mysql_connect.condition_execute(actual)
        assert result, f'实际={result}, 预期={expect}'
        first_row = result[0]
        diff = DeepDiff(first_row, expect, ignore_order=True)
        assert not diff, f'实际={actual}, 预期={expect}'
        return f'实际={actual}, 预期={expect}'

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_is_equal_to(self, actual: str, expect):
        """等于expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_is_equal_to(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_is_not_equal_to(self, actual: str, expect):
        """不等于expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_is_not_equal_to(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_is_length(self, actual: str, expect):
        """长度等于expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_is_length(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_sum_equal_expect(self, actual: str, expect):
        """长度等于expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_sum_equal_expect(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_contains(self, actual: str, expect):
        """包含expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_contains(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_is_equal_to_ignoring_case(self, actual: str, expect):
        """忽略大小写等于expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_is_equal_to_ignoring_case(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_contains_ignoring_case(self, actual: str, expect):
        """包含忽略大小写expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_contains_ignoring_case(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_contains_only(self, actual: str, expect):
        """仅包含expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_contains_only(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_does_not_contain(self, actual: str, expect):
        """不包含expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_does_not_contain(actual, expect)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
    ])
    def assert_sql_is_not_none(self, actual: str):
        """不是null"""
        actual = mysql_query(self.mysql_connect, actual, '不是null')
        return TextAssertion.p_is_not_none(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
    ])
    def assert_sql_is_none(self, actual: str):
        """是null"""
        actual = mysql_query(self.mysql_connect, actual, '是null')
        return TextAssertion.p_is_none(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
    ])
    def assert_sql_is_empty(self, actual: str):
        """是空字符串"""
        actual = mysql_query(self.mysql_connect, actual, '是空字符串')
        return TextAssertion.p_is_empty(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
    ])
    def assert_sql_is_not_empty(self, actual: str):
        """不是空符串"""
        actual = mysql_query(self.mysql_connect, actual, '不是空符串')
        return TextAssertion.p_is_not_empty(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
    ])
    def assert_sql_is_false(self, actual: str):
        """是false"""
        actual = mysql_query(self.mysql_connect, actual, '是false')
        return TextAssertion.p_is_false(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
    ])
    def assert_sql_is_true(self, actual: str):
        """是true"""
        actual = mysql_query(self.mysql_connect, actual, '是true')
        return TextAssertion.p_is_true(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
    ])
    def assert_sql_is_alpha(self, actual: str):
        """是字母"""
        actual = mysql_query(self.mysql_connect, actual, '是字母')
        return TextAssertion.p_is_alpha(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
    ])
    def assert_sql_is_digit(self, actual: str):
        """是数字"""
        actual = mysql_query(self.mysql_connect, actual, '是数字')
        return TextAssertion.p_is_digit(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_is_in(self, actual: str, expect: str):
        """在expect里面"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_is_in(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_is_not_in(self, actual: str, expect: str):
        """不在expect里面"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_is_not_in(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_starts_with(self, actual: str, expect: str):
        """以expect开头"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_starts_with(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_ends_with(self, actual: str, expect: str):
        """以expect结尾"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_ends_with(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_matches(self, actual: str, expect: str):
        """正则匹配等于expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_matches(actual)

    @sync_method_callback('sql断言', 'mysql', 3, [
        MethodModel(f='actual', p='请输入sql语句', d=True),
        MethodModel(f='expect', p='期望值', d=True),
    ])
    def assert_sql_does_not_match(self, actual: str, expect: str):
        """正则不匹配expect"""
        actual = mysql_query(self.mysql_connect, actual, expect)
        return TextAssertion.p_does_not_match(actual)
