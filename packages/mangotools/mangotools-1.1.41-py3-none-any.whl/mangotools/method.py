# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-12-26 14:17
# @Author : 毛鹏
import inspect
import os
import socket

from .data_processor import ObtainRandomData
from .models import FunctionModel, ClassMethodModel


def root_path():
    """ 获取根路径 """
    path = os.path.dirname(__file__)
    return path


def ensure_path_sep(path: str) -> str:
    """兼容 windows 和 linux 不同环境的操作系统路径 """
    if "/" in path:
        path = os.sep.join(path.split("/"))

    if "\\" in path:
        path = os.sep.join(path.split("\\"))
    return path


def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    _s = None
    try:
        _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _s.connect(('8.8.8.8', 80))
        l_host = _s.getsockname()[0]
    finally:
        _s.close()

    return l_host


def class_methods(self) -> list[ClassMethodModel]:
    class_list = []
    for subclass in self.mro()[1:]:
        children = []
        for method_name in dir(subclass):
            if not method_name.startswith("__"):
                method = getattr(subclass, method_name)
                if callable(method):
                    doc = method.__doc__
                    signature = inspect.signature(method)
                    parameters = signature.parameters
                    param_dict = {}
                    for param in parameters.values():
                        if param.name != 'self':
                            param_dict[param.name] = ''
                    children.append(FunctionModel(
                        label=method_name + '()',
                        value=doc,
                        parameter=param_dict
                    ))

        if children:
            class_list.append(ClassMethodModel(label=subclass.__doc__, value=subclass.__name__, children=children))

    return class_list


def class_own_methods(self) -> list[FunctionModel]:
    methods = []
    for attr in dir(self):
        obj = getattr(self, attr)
        if (inspect.ismethod(obj) or inspect.isfunction(obj)) and obj.__qualname__.split('.')[
            0] == self.__name__:
            if attr != '__init__':
                doc = inspect.getdoc(obj)
                signature = inspect.signature(obj)
                parameters = signature.parameters
                param_dict = {}
                for param in parameters.values():
                    if param.name != 'self':
                        param_dict[param.name] = ''
                methods.append(FunctionModel(
                    label=attr,
                    value=doc,
                    parameter=param_dict
                ))
    return methods


if __name__ == '__main__':
    print([i.model_dump() for i in class_methods(ObtainRandomData)])
