# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 14:09
# @Author : 毛鹏
from ._contain import ContainAssertion
from ._matching import MatchingAssertion
from ._whatis import WhatIsEqualToAssertion
from ._whatisit import WhatIsItAssertion


class TextAssertion(WhatIsItAssertion, ContainAssertion, MatchingAssertion, WhatIsEqualToAssertion):
    """内容断言"""
    pass


if __name__ == '__main__':
    TextAssertion.p_is_equal_to('1', '2')
