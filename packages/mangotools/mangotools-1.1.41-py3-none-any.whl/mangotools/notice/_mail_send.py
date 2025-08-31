# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 邮箱通知封装
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from socket import gaierror

from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0016
from ..models import EmailNoticeModel, TestReportModel


class EmailSend:

    def __init__(self, notice_config: EmailNoticeModel, test_report: TestReportModel = None, domain_name: str = None,
                 content: str = None):
        self.test_report = test_report
        self.notice_config = notice_config
        self.domain_name = domain_name
        self.content = content

    def send_main(self) -> None:
        if self.content is None:
            lines = [
                "       【芒果测试平台测试报告通知】"
            ]
            if self.test_report.project_name and self.test_report.product_name:
                lines.append(
                    f"                     项目产品：{self.test_report.project_name}/{self.test_report.product_name}")
            lines.append(f"                     测试环境：{self.test_report.test_environment}")
            if self.test_report.test_suite_id and self.test_report.task_name:
                lines.append(f"                     测试套ID：{self.test_report.test_suite_id}")
                lines.append(f"                     任务名称：{self.test_report.task_name}")
            lines.extend([
                f"                     执行用例数：{self.test_report.case_sum}",
                f"                     通过用例数：{self.test_report.success}",
                f"                     失败用例数：{self.test_report.fail}",
                f"                     成  功  率：{self.test_report.success_rate}%"
            ])

            # 接口相关统计
            if self.test_report.api_case_sum is not None:
                lines.append(f"                     接口用例数：{self.test_report.api_case_sum}")
            if self.test_report.api_fail is not None:
                lines.append(f"                     接口失败数：{self.test_report.api_fail}")
            if self.test_report.api_call is not None:
                lines.append(f"                     接口调用数：{self.test_report.api_call}")

            # 前端相关统计
            if self.test_report.ui_case_sum is not None:
                lines.append(f"                     前端用例数：{self.test_report.ui_case_sum}")
            if self.test_report.ui_fail is not None:
                lines.append(f"                     前端失败数：{self.test_report.ui_fail}")
            if self.test_report.ui_step_call is not None:
                lines.append(f"                     前端步骤数：{self.test_report.ui_step_call}")

            # 单元测试相关统计
            if self.test_report.pytest_case_sum is not None:
                lines.append(f"                     单元用例数：{self.test_report.pytest_case_sum}")
            if self.test_report.pytest_fail is not None:
                lines.append(f"                     单元失败数：{self.test_report.pytest_fail}")
            if self.test_report.pytest_func_call is not None:
                lines.append(f"                     单元函数数：{self.test_report.pytest_func_call}")

            # 执行信息
            lines.extend([
                f"                     用例执行耗时：{self.test_report.execution_duration}",
                f"                     测试开始时间：{self.test_report.test_time}",
                "",
                "**************************************************************************"
            ])

            # 平台地址
            if self.domain_name:
                lines.append(f"      芒果自动化平台地址：{self.domain_name}")

            lines.append("      详细情况可前往芒果自动化平台查看，非相关负责人员可忽略此消息。谢谢！")

            # 将所有行连接成最终的邮件内容
            content = "\n".join(lines)
        else:
            content = self.content
        self.send_mail(self.notice_config.send_list, f'【芒果测试平台通知】', content)

    def send_mail(self, user_list: list, sub: str, content: str, ) -> None:
        try:
            user = f"MangoTestPlatform <{self.notice_config.send_user}>"
            msg = MIMEMultipart()
            msg['From'] = user
            msg['To'] = ";".join(user_list)
            msg['Subject'] = sub
            msg.attach(MIMEText(content, 'plain'))
            with smtplib.SMTP(self.notice_config.email_host, ) as server:
                server.starttls()
                server.login(self.notice_config.send_user, self.notice_config.stamp_key)
                server.sendmail(user, user_list, msg.as_string())
                server.quit()
        except (gaierror, smtplib.SMTPServerDisconnected):
            raise MangoToolsError(*ERROR_MSG_0016)
