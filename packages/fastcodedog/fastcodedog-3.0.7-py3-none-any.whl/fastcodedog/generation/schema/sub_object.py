# -*- coding: utf-8 -*-
from fastcodedog.context.schema.sub_object import SubObject as SubObjectContext
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.variable import Variable


class SubObject(Variable):
    def __init__(self, context: SubObjectContext, parent):
        super().__init__(context.name, type='List[int]', nullable=True,
                         context=context, parent=parent)
        self.name = context.name
        self.module = context.module
        self.class_type = context.class_type
        self.is_list = context.is_list
        self.disabled = context.disabled
        self.value = 'Field(None)'

        self.add_possible_imports([
            Import(from_='pydantic', import_='Field'),
            Import(from_='typing', import_='Optional'),
            Import(from_='typing', import_='List')
        ])
