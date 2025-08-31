# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-11-22 19:45
# @Author : 毛鹏
import asyncio
import functools

import time


def async_retry(failed_retry_time=15, retry_waiting_time=0.2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as error:
                    if (time.time() - start_time) > failed_retry_time:
                        raise error
                await asyncio.sleep(retry_waiting_time)

        return wrapper

    return decorator


def sync_retry(failed_retry_time=15, retry_waiting_time=0.2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    if (time.time() - start_time) > failed_retry_time:
                        raise error
                time.sleep(retry_waiting_time)

        return wrapper

    return decorator
