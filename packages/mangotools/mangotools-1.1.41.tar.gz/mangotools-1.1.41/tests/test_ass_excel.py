# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 11:13
# @Author : 毛鹏
import json
import unittest

from mangotools.assertion import MangoAssertion, FileAssertion

FILE_PATH = r'D:\GitCode\mango_tools\tests\任务爬取逻辑.xlsx'
SHEET_NAME = 'Sheet1'


class TestExcelTaskSheet(unittest.TestCase):
    def test_excel_headers(self):
        actual = {'文件路径': FILE_PATH, '工作表': SHEET_NAME}
        expect = {'预期表头': [
            '任务类型', '任务名称', '重试次数', '卡主任务重置状态的间隔时间',
            '去重间隔时间', '去重时间间隔（爬虫）', '自动触发类型']}
        MangoAssertion().ass(FileAssertion.assert_excel_headers.__name__, actual, expect)

    def test_excel_all_row_data(self):
        all_rows = [
            {'任务类型': 301, '任务名称': '小红书关键词', '重试次数': '1+3', '卡主任务重置状态的间隔时间': '10（分钟）',
             '去重间隔时间': '-', '去重时间间隔（爬虫）': '-', '自动触发类型': '自动触发类型1'},
            {'任务类型': 302, '任务名称': '小红书聚光创意报表', '重试次数': '1+3',
             '卡主任务重置状态的间隔时间': '30（分钟）', '去重间隔时间': '-', '去重时间间隔（爬虫）': '-',
             '自动触发类型': '自动触发类型2'},
            {'任务类型': 303, '任务名称': '小红书聚光笔记报表', '重试次数': '1+3',
             '卡主任务重置状态的间隔时间': '30（分钟）', '去重间隔时间': '-', '去重时间间隔（爬虫）': '-',
             '自动触发类型': '自动触发类型3'},
            {'任务类型': 304, '任务名称': '小红书聚光关键词报表', '重试次数': '1+3',
             '卡主任务重置状态的间隔时间': '30（分钟）', '去重间隔时间': '-', '去重时间间隔（爬虫）': '-',
             '自动触发类型': '自动触发类型4'},
            {'任务类型': 305, '任务名称': '小红书乘风创意报表', '重试次数': '1+3',
             '卡主任务重置状态的间隔时间': '30（分钟）', '去重间隔时间': '-', '去重时间间隔（爬虫）': '-',
             '自动触发类型': '自动触发类型5'},
            {'任务类型': 401, '任务名称': '小红书笔记详情（数据订阅）', '重试次数': '1+3',
             '卡主任务重置状态的间隔时间': '15（分钟）', '去重间隔时间': '-', '去重时间间隔（爬虫）': '2（小时）',
             '自动触发类型': '自动触发类型6'},
            {'任务类型': 402, '任务名称': '小红书笔记评论（数据订阅）', '重试次数': '1+3',
             '卡主任务重置状态的间隔时间': '15（分钟）', '去重间隔时间': '-', '去重时间间隔（爬虫）': '2（小时）',
             '自动触发类型': '自动触发类型7'},
            {'任务类型': 401, '任务名称': '小红书笔记详情（项目笔记）', '重试次数': '1+3',
             '卡主任务重置状态的间隔时间': '15（分钟）', '去重间隔时间': '-', '去重时间间隔（爬虫）': '2（小时）',
             '自动触发类型': '自动触发类型8'},
            {'任务类型': 402, '任务名称': '小红书笔记评论（项目笔记）', '重试次数': '1+3',
             '卡主任务重置状态的间隔时间': '15（分钟）', '去重间隔时间': '-', '去重时间间隔（爬虫）': '2（小时）',
             '自动触发类型': '自动触发类型9'},
            {'任务类型': 601, '任务名称': '蒲公英代下单截图', '重试次数': '-', '卡主任务重置状态的间隔时间': '-',
             '去重间隔时间': '-', '去重时间间隔（爬虫）': '-', '自动触发类型': '自动触发类型10'}
        ]
        for index, row_data in enumerate(all_rows):
            actual = {'文件路径': FILE_PATH, '工作表': SHEET_NAME}
            expect = {'第几行': f'{1 + index}', '行数据': row_data}
            MangoAssertion().ass(FileAssertion.assert_excel_row_data.__name__, actual, expect)

    def test_excel_cell_value(self):
        actual = {'文件路径': FILE_PATH, '工作表': SHEET_NAME}
        expect = {'单元格': 'B2', '预期值': '小红书关键词'}
        MangoAssertion().ass(FileAssertion.assert_excel_is_equal_to.__name__, actual, expect)
        expect = {'单元格': 'G6', '预期值': '自动触发类型5'}
        MangoAssertion().ass(FileAssertion.assert_excel_is_equal_to.__name__, actual, expect)

    def test_excel_row_count(self):
        actual = {'文件路径': FILE_PATH, '工作表': SHEET_NAME}
        expect = {'预期行数': '11'}  # 1表头+10数据行
        MangoAssertion().ass(FileAssertion.assert_excel_row_count.__name__, actual, expect)

    def test_excel_column_count(self):
        actual = {'文件路径': FILE_PATH, '工作表': SHEET_NAME}
        expect = {'预期列数': 7}
        MangoAssertion().ass(FileAssertion.assert_excel_column_count.__name__, actual, expect)

    def test_excel_sheet_names(self):
        actual = json.dumps({'文件路径': FILE_PATH})
        expect = {'工作表列表': [SHEET_NAME, 'Sheet2', 'Sheet3']}
        MangoAssertion().ass(FileAssertion.assert_excel_sheet_names.__name__, actual, expect)

    def test_excel_column_values(self):
        actual = {'文件路径': FILE_PATH, '工作表': SHEET_NAME}
        expect = {'列字母': 'A', '预期值列表': [
            '任务类型', 301, 302, 303, 304, 305, 401, 402, 401, 402, 601
        ]}
        MangoAssertion().ass(FileAssertion.assert_excel_column_values.__name__, actual, expect)

    def test_excel_column_values1(self):
        actual = {'文件路径': r"D:\GitCode\mango_tools\tests\任务爬取逻辑.xlsx",
                  '工作表': SHEET_NAME}
        expect = {'单元格': 'A2', '预期值': '301'}
        print(MangoAssertion().ass(FileAssertion.assert_excel_is_equal_to.__name__, actual, expect))
