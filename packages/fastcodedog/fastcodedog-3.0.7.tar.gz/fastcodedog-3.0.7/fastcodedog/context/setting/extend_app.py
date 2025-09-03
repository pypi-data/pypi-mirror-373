# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class ExtendApp(ContextBase):
    def __init__(self):
        super().__init__()
        self.from_ = ''
        self.import_ = ''
        self.alias = ''
