# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.context.schema.alias_generator import AliasGenerator
from fastcodedog.context.schema.field import Field
from fastcodedog.context.schema.response_schema import ResponseSchema
from fastcodedog.context.schema.sub_object import SubObject


class Schema(ContextBase):
    def __init__(self):
        super().__init__()
        self.module = ''
        self.title = ''
        self.name = ''
        self.description = ''  # 对应model的comment
        self.fields = {}  # 对应model的columnss
        self._types['fields'] = Field
        self.computed_properties = {}  # 对应model的computed_properties
        self._types['computed_properties'] = Field
        self.sub_objects = {}  # 对应model的relationship
        self._types['sub_objects'] = SubObject
        self.alias_generator = None
        self._types['alias_generator'] = AliasGenerator
        self.response_schemas = {}  # 对应model的relationship
        self._types['response_schemas'] = ResponseSchema
