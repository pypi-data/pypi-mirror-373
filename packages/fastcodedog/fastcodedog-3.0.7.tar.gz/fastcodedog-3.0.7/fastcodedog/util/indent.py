# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: add_indent
@time: 2024/5/30 8:46
@desc:
"""


def add_indent(s, indent=None):
    """
    给每一行添加一个缩进（默认是4个空格），除非这一行在“un-indent case”中。
    """
    if not indent or indent == '':
        return s
    end_with_newline = s.endswith('\n')
    lines = s.splitlines()
    for i in range(len(lines)):
        if not _line_in_un_indent_case(i, lines):
            lines[i] = indent + lines[i]
    return '\n'.join(lines) + ('\n' if end_with_newline else '')


def _line_in_un_indent_case(lineno, lines):
    # lineno是否处于非indent的情况
    if lineno == 0:
        return False
    # before = ''.join(lines[:lineno])
    # if before.count('"""') % 2 == 1:
    #     return True
    # if before.count("'''") % 2 == 1:
    #     return True
    return False
