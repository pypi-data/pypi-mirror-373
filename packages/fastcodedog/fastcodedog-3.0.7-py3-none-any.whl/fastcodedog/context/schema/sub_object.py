# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class SubObject(ContextBase):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.module = ''
        self.class_type = ''
        self.from_join_table = False
        self.is_list = True
        self.disabled = False
