# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.context.model.parameter import Parameter

class AdditionalMethod(ContextBase):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.name = ''
        self.type = ''
        # self.pydantic_type = ''
        self.comment = ''
        self.module = ''
        self.model_name = ''
        self.parameters = []
        self._types['parameters'] = Parameter
        # self.nullable = True
        self.script = ''
        self.import_ = []
        self._types['import_'] = str
