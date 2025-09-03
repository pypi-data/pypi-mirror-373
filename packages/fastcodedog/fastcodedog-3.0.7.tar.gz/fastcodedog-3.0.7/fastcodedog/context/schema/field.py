# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Field(ContextBase):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.title = ''
        self.pydantic_type = ''
        self.pydantic_type_with_length = ''
        self.max_length = 0
        self.optional = True
        self.default_str = ''
        self.description = ''
        self.no_response = False
        self.no_input = False
