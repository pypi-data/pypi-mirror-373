# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 企微通知封装
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
from json import JSONDecodeError

import requests

from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0018, ERROR_MSG_0014
from ..models import WeChatNoticeModel, TestReportModel


class WeChatSend:
    def __init__(self,
                 notice_config: WeChatNoticeModel,
                 test_report: TestReportModel | None = None,
                 domain_name: str = None,
                 content: str = None):
        self.notice_config = notice_config
        self.test_report = test_report
        self.domain_name = domain_name
        self.content = content
        self.headers = {"Content-Type": "application/json"}

    def send_wechat_notification(self):
        if self.content is None:
            # 收集所有有值的行
            lines = [
                "【芒果测试平台测试报告通知】",
                f">项目产品：<font color=\"info\">{self.test_report.project_name}/{self.test_report.product_name}</font>",
                f">测试环境：{self.test_report.test_environment}"
            ]

            # 测试套ID行
            if self.test_report.test_suite_id:
                lines.append(f">测试套ID：{self.test_report.test_suite_id}")
            if self.test_report.task_name:
                lines.append(f">任务名称：{self.test_report.task_name}")

            lines.extend([
                "",
                ">",
                "> **执行结果**",
                f"><font color=\"info\">成  功  率  : {self.test_report.success_rate}%</font>",
                f">执行用例数：<font color=\"info\">{self.test_report.case_sum}</font>",
                f">成功用例数：<font color=\"info\">{self.test_report.success}</font>",
                f">失败用例数：`{self.test_report.fail}个`"
            ])

            # 接口相关统计
            if self.test_report.api_case_sum is not None:
                lines.append(f">接口用例数：{self.test_report.api_case_sum}")
            if self.test_report.api_fail is not None:
                lines.append(f">接口失败数：{self.test_report.api_fail}")
            if self.test_report.api_call is not None:
                lines.append(f">接口调用数：{self.test_report.api_call}")

            # 前端相关统计
            if self.test_report.ui_case_sum is not None:
                lines.append(f">前端用例数：{self.test_report.ui_case_sum}")
            if self.test_report.ui_fail is not None:
                lines.append(f">前端失败数：{self.test_report.ui_fail}")
            if self.test_report.ui_step_call is not None:
                lines.append(f">前端步骤数：{self.test_report.ui_step_call}")

            # 单元测试相关统计
            if self.test_report.pytest_case_sum is not None:
                lines.append(f">单元用例数：{self.test_report.pytest_case_sum}")
            if self.test_report.pytest_fail is not None:
                lines.append(f">单元用例失败数：{self.test_report.pytest_fail}")
            if self.test_report.pytest_func_call is not None:
                lines.append(f">单元函数数：{self.test_report.pytest_func_call}")

            # 执行信息
            lines.extend([
                f">用例执行耗时：<font color=\"warning\">{self.test_report.execution_duration}</font>",
                f">测试开始时间：<font color=\"comment\">{self.test_report.test_time}</font>",
                ">",
                ">非相关负责人员可忽略此消息。"
            ])

            # 平台地址
            if self.domain_name:
                lines.append(f">测试报告，点击查看>>[测试报告入口]({self.domain_name})")

            # 将所有行连接成最终的内容
            content = "\n".join(lines)
        else:
            content = self.content
        self.send_markdown(content)

    def send_markdown(self, content):
        res = requests.post(
            url=self.notice_config.webhook,
            json={"msgtype": "markdown", "markdown": {"content": content}},
            headers=self.headers,
            proxies={'http': None, 'https': None}
        )
        try:
            if res.json()['errcode'] != 0:
                raise MangoToolsError(*ERROR_MSG_0018)
        except JSONDecodeError:
            raise MangoToolsError(*ERROR_MSG_0018)

    def send_file_msg(self, file):
        res = requests.post(
            url=self.notice_config.webhook,
            json={"msgtype": "file", "file": {"media_id": self.__upload_file(file)}},
            headers=self.headers,
            proxies={'http': None, 'https': None}
        )
        if res.json()['errcode'] != 0:
            raise MangoToolsError(*ERROR_MSG_0014)

    def __upload_file(self, file):
        data = {"file": open(file, "rb")}
        res = requests.post(
            url=self.notice_config.webhook,
            files=data,
            proxies={'http': None, 'https': None}
        ).json()
        return res['media_id']

    def send_text(self, content, mentioned_mobile_list=None):
        if mentioned_mobile_list is None or isinstance(mentioned_mobile_list, list):
            if len(mentioned_mobile_list) >= 1:
                for i in mentioned_mobile_list:
                    if isinstance(i, str):
                        res = requests.post(
                            url=self.notice_config.webhook,
                            json={
                                "msgtype": "text",
                                "text": {
                                    "content": content,
                                    "mentioned_list": None,
                                    "mentioned_mobile_list": mentioned_mobile_list
                                }
                            },
                            headers=self.headers,
                            proxies={'http': None, 'https': None}
                        )
                        if res.json()['errcode'] != 0:
                            raise MangoToolsError(*ERROR_MSG_0014)

                    else:
                        raise MangoToolsError(*ERROR_MSG_0014)
        else:
            raise MangoToolsError(*ERROR_MSG_0014)
