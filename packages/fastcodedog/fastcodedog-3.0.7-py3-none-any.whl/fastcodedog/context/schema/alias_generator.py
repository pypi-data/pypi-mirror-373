# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class AliasGenerator(ContextBase):
    def __init__(self):
        super().__init__()
        self.import_ = []
        self._types['import_'] = str
        self.function = ''
