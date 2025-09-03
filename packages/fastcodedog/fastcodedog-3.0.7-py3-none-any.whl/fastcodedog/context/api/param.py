# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Param(ContextBase):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.type = ''
        self.option_none = False
        self.description = ''
        self.nullable = True
        self.enum = []
        self._types['enum'] = str
        self.default_value = ''
