# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class OAuth2(ContextBase):
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.model = 'User'
        self.module = 'admin'
        self.user_name_column = 'number'
        self.password_column = 'password'
