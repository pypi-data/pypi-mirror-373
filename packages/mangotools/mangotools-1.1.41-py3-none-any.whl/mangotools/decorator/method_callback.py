# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-10 21:55
# @Author : 毛鹏
import functools

from mangotools.models import MethodModel

func_info: list[dict] = []
__func_name_list = []


def _func_info_add(_type, class_name, func, parameter, sort):
    class_dict = next((item for item in func_info if item.get("value") == _type), None)
    if not class_dict:
        new_entry = {
            "label": _type,
            "value": _type,
            "children": []
        }
        func_info.append(new_entry)
        class_dict = new_entry
    found_dict = next((item for item in class_dict['children'] if item.get("value") == class_name), None)
    if not found_dict:
        new_entry = {
            "label": class_name,
            "value": class_name,
            "children": []
        }
        class_dict['children'].append(new_entry)
        found_dict = new_entry
    if func.__name__ not in __func_name_list:
        __func_name_list.append(func.__name__)
        found_dict['children'].append({
            "value": func.__name__,
            "label": func.__doc__,
            "parameter": [i.model_dump() for i in parameter] if parameter else None,
            "sort": sort,
        })


def async_method_callback(_type, class_name, sort=-1, parameter: list[MethodModel] | None = None):
    def decorator(func):
        _func_info_add(_type, class_name, func, parameter, sort)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def sync_method_callback(_type, class_name, sort=-1, parameter: list[MethodModel] | None = None):
    def decorator(func):
        _func_info_add(_type, class_name, func, parameter, sort)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
