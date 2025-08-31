# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏

from ..notice._mail_send import EmailSend
from ..notice._wechat_send import WeChatSend
__all__ = [
    'WeChatSend',
    'EmailSend',
]
