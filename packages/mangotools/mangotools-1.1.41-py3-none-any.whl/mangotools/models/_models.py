# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-11-08 15:48
# @Author : 毛鹏
from typing import Optional, Any

from pydantic import BaseModel


class MethodModel(BaseModel):
    f: str
    p: str | None = None
    d: bool = False
    v: Any = None


class ResponseModel(BaseModel):
    response_time: float
    headers: dict
    status_code: int
    text: str
    json_data: dict | str | None


class MysqlConingModel(BaseModel):
    host: str
    port: int
    user: str
    password: str | None = None
    database: str | None = None


class EmailNoticeModel(BaseModel):
    send_user: str
    email_host: str
    stamp_key: str
    send_list: list


class TestReportModel(BaseModel):
    test_suite_id: int | None = None
    task_name: str | None = None
    project_name: str
    product_name: str

    test_environment: str

    case_sum: int

    api_case_sum: int | None = None
    api_fail: int | None = None
    api_call: int | None = None

    ui_case_sum: int | None = None
    ui_fail: int | None = None
    ui_step_call: int | None = None

    pytest_case_sum: int | None = None
    pytest_fail: int | None = None
    pytest_func_call: int | None = None

    success: int
    success_rate: float
    warning: int = 0
    fail: int

    execution_duration: str
    test_time: str


class WeChatNoticeModel(BaseModel):
    webhook: str


class FunctionModel(BaseModel):
    label: str
    value: str
    parameter: dict[str, Optional[str]]


class ClassMethodModel(BaseModel):
    value: str
    label: str
    children: list[FunctionModel]
