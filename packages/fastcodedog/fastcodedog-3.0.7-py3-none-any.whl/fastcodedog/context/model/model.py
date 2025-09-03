# -*- coding: utf-8 -*-
"""
模型
"""
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.context.model.column import Column
from fastcodedog.context.model.computed_property import ComputedProperty
from fastcodedog.context.model.additional_method import AdditionalMethod
from fastcodedog.context.model.relationship import Relationship


class Model(ContextBase):
    def __init__(self):
        super().__init__()
        self.module = ''
        self.title = ''
        self.name = ''
        self.table_name = ''
        self.is_relationship = False
        self.comment = ''
        self.columns = {}
        self._types['columns'] = Column
        self.unique_constraints = []
        self._types['unique_constraints'] = list
        self.relationships = {}
        self._types['relationships'] = Relationship
        self.computed_properties = {}
        self._types['computed_properties'] = ComputedProperty
        self.additional_methods = {}
        self._types['additional_methods'] = AdditionalMethod
