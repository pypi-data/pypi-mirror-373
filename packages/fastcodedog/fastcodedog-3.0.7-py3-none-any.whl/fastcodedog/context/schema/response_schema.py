# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class ResponseSchema(ContextBase):
    class SubObject(ContextBase):
        def __init__(self):
            super().__init__()
            self.name = ''
            self.is_list = True
            self.class_type = None
            self._types['class_type'] = ResponseSchema

    def __init__(self):
        super().__init__()
        self.name = ''
        self.module = ''
        self.base_class = ''
        # self.is_list = False
        self.sub_objects = {}
        self._types['sub_objects'] = ResponseSchema.SubObject
