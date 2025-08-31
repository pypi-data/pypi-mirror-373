# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-07 22:15
# @Author : 毛鹏
import sys

python_version = sys.version_info

if "3.1" not in f"{python_version.major}.{python_version.minor}":
    raise Exception("必须使用>Python3.10.4")
