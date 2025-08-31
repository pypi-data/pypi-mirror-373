# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import logging
import os

import colorlog
from concurrent_log_handler import ConcurrentRotatingFileHandler


class LogHandler:
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, file_name: str, level: str):
        # 确保日志目录存在
        log_dir = os.path.dirname(file_name)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger(file_name)
        self.logger.setLevel(self.level_relations.get(level, logging.DEBUG))

        self._add_console_handler(level)

        self._add_file_handler(file_name, level)

    def _add_console_handler(self, level):
        """添加彩色控制台日志处理器"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_color_formatter(level))
        self.logger.addHandler(console_handler)

    def _add_file_handler(self, filename, level):
        """添加多进程安全的文件日志处理器"""
        file_handler = ConcurrentRotatingFileHandler(
            filename,
            mode='a',
            maxBytes=100 * 1024 * 1024,  # 100MB（按大小轮转作为备用策略）
            backupCount=3,
            encoding='utf-8',
            use_gzip=False
        )

        file_fmt = "%(levelname)-8s[%(asctime)s][%(filename)s:%(lineno)d] %(message)s"
        file_handler.setFormatter(logging.Formatter(file_fmt))
        self.logger.addHandler(file_handler)

    @staticmethod
    def _get_color_formatter(level):
        """获取彩色日志格式"""
        if level in ["debug", "info"]:
            fmt = "%(log_color)s[%(asctime)s] [%(levelname)s]: %(message)s"
        else:
            fmt = "%(log_color)s[%(asctime)s] [%(filename)s-->行:%(lineno)d] [%(levelname)s]: %(message)s"

        return colorlog.ColoredFormatter(
            fmt,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'purple',
            }
        )
