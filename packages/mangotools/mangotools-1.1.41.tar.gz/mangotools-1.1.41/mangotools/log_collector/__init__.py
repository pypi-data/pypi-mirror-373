# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-04-05 12:40
# @Author : 毛鹏
from multiprocessing import Lock

from ..decorator import singleton
from ..log_collector._log_control import LogHandler


@singleton
class Log:
    def __init__(self, log_path, is_debug):
        self.log_path = log_path
        self.is_debug = is_debug
        self.lock = Lock()
        self.DEBUG = LogHandler(fr"{log_path}\debug-log.log", 'debug')
        self.INFO = LogHandler(fr"{log_path}\info-log.log", 'info')
        self.WARNING = LogHandler(fr"{log_path}\warning-log.log", 'warning')
        self.ERROR = LogHandler(fr"{log_path}\error-log.log", 'error')
        self.CRITICAL = LogHandler(fr"{log_path}\critical-log.log", 'critical')

    def _log(self, level, msg):
        log_file = {
            'debug': self.DEBUG.logger,
            'info': self.INFO.logger,
            'warning': self.WARNING.logger,
            'error': self.ERROR.logger,
            'critical': self.CRITICAL.logger,
        }[level]
        with self.lock:
            log_file.log(self.DEBUG.level_relations[level], str(msg))

    def set_debug(self, is_debug: bool):
        self.is_debug = is_debug

    def debug(self, msg: str):
        if self.is_debug:
            self._log('debug', msg)

    def info(self, msg: str):
        self._log('info', msg)

    def warning(self, msg: str):
        self._log('warning', msg)

    def error(self, msg: str):
        self._log('error', msg)

    def critical(self, msg: str):
        self._log('critical', msg)


def set_log(log_path, is_debug=False):
    log = Log(log_path, is_debug)
    return log


__all__ = ['set_log']
