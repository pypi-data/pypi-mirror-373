# -*- coding: utf-8 -*-
from fastcodedog.context.api.endpoint import Endpoint
from fastcodedog.context.contextbase import ContextBase


class Api(ContextBase):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.comment = ''
        self.module = ''
        self.name = ''
        self.primary_key_name = ''
        self.oauth2_enabled = False
        self.validate_response_models = []
        self._types['validate_response_models'] = str
        self.endpoints = {}
        self._types['endpoints'] = Endpoint
