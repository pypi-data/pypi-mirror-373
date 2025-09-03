# -*- coding: utf-8 -*-
import keyword
import re


def is_valid_name(name):
    """是否符合python的命名规范"""
    # 检查是否只包含字母、数字和下划线，并且以字母或下划线开头
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        return False

    # 确保name不是Python关键字
    if keyword.iskeyword(name):
        return False

    return True

# print(is_valid_name('try'))
# print(is_valid_name('try_'))
