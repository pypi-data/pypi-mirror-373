# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Column(ContextBase):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.name = ''
        self.specified_relationship_name = ''
        self.comment = ''
        self.sqlalchemy_type = ''
        self.sqlalchemy_type_with_length = ''
        self.type = ''
        self.length = 0
        self.nullable = True
        self.primary_key = False
        self.unique = False
        self.domain = ''
        self._types = {'unique': str}
        self.autoincrement = False
        self.foreign_key = ''
