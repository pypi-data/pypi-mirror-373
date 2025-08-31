# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-08-11 11:12
# @Author : 毛鹏
import hashlib


class EncryptionTool:
    """ 加密 """

    @classmethod
    def md5_32_small(cls, string) -> str:
        """MD5_32位小写加密"""
        md5 = hashlib.md5()
        md5.update(string.encode('utf-8'))
        encrypted_string = md5.hexdigest()
        return encrypted_string

    @classmethod
    def md5_32_large(cls, string) -> str:
        """MD5_32位大写加密"""
        md5 = hashlib.md5()
        md5.update(string.encode('utf-8'))
        encrypted_string = md5.hexdigest().upper()
        return encrypted_string

    @classmethod
    def md5_16_small(cls, string) -> str:
        """MD5_16位小写加密"""
        md5 = hashlib.md5()
        md5.update(string.encode('utf-8'))
        encrypted_string = md5.hexdigest()[8:-8]
        return encrypted_string

    @classmethod
    def md5_16_large(cls, string) -> str:
        """MD5_16位大写加密"""
        md5 = hashlib.md5()
        md5.update(string.encode('utf-8'))
        encrypted_string = md5.hexdigest().upper()[8:-8]
        return encrypted_string
