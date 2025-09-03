# -*- coding: utf-8 -*-
from fastcodedog.context.api.param import Param
from fastcodedog.context.contextbase import ContextBase


class Endpoint(ContextBase):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.have_select_models = False
        self.summary = ''
        self.comment = ''
        self.action = ''
        self.return_list = False
        self.url = ''
        self.max_size = None
        self._types['max_size'] = int
        self.tags = []
        self._types['tags'] = str
        self.params = {}
        self._types['params'] = Param
