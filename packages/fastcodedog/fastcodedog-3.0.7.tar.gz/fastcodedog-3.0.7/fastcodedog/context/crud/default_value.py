# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class DefaultValue(ContextBase):
    def __init__(self):
        super().__init__()
        self.change_when_update = False
        self.force_default = False
        self.import_ = []
        self._types['import_'] = str
        self.value_expression = ''
