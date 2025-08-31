# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-10 23:08
# @Author : 毛鹏
import functools
from typing import Type, Callable, Any


def inject_to_class(target_class: Type[Any]):
    """装饰器工厂，用于将函数注入到指定类中"""

    def decorator(func: Callable) -> Callable:
        """实际装饰器"""
        setattr(target_class, func.__name__, func)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
