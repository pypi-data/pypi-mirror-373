# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.context.crud.column import Column


class JoinRelationship(ContextBase):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.original_name = ''
        self.secondary_object_name = ''
        self.back_populates = ''
        self.back_populates_module = ''
        self.back_populates_model = ''
        self.back_populates_primary_key = Column()
