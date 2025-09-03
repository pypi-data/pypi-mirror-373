# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Column(ContextBase):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.title = ''
        self.type = ''
        self.nullable = True
        self.option_none = False  # 是否需要处理输入的None。可以在地址中输入变量名而不输入变量值来传递None
        self.description = ''

