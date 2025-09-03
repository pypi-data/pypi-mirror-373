# -*- coding: utf-8 -*-
from fastcodedog.context.schema.field import Field as FieldContext
from fastcodedog.generation.base.call import Call
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.variable import Variable
from fastcodedog.util.wrap_str_with_quotation import wrap_quotation


class Field(Variable):
    def __init__(self, context: FieldContext, optional=False, default_str='...', parent=None):
        super().__init__(context.name, type=context.pydantic_type, nullable=optional,
                         context=context, parent=parent)
        self.title = context.title
        self.pydantic_type_with_length = context.pydantic_type_with_length
        self.max_length = context.max_length
        self.optional = optional
        self.default_str = default_str
        self.description = context.description
        # self.no_response = context.no_response
        # self.no_input = context.no_input

        # 通过计算的类型
        self.type = self.get_type()
        self.value = self.get_value()

        self.add_possible_imports([
            Import(from_='pydantic', import_='constr'),
            Import(from_='pydantic', import_='Field'),
            Import(from_='typing', import_='Optional'),
            Import(from_='typing', import_='List'),
            Import(from_='typing', import_='Dict'),
            Import(from_='datetime', import_='datetime'),
            Import(from_='datetime', import_='date'),
            Import(from_='datetime', import_='time')
        ])

    def get_type(self):
        return self.pydantic_type_with_length if not self.optional else f'Optional[{self.pydantic_type_with_length}]'

    def get_value(self):
        params = [self.default_str, f'title={wrap_quotation(self.title)}', f'description={wrap_quotation(self.description)}']
        return Call('Field', params)
