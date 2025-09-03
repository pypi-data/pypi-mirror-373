# -*- coding: utf-8 -*-
from fastcodedog.context.model.column import Column as ColumnContext
from fastcodedog.generation.base.call import Call
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.variable import Variable
from fastcodedog.util.wrap_str_with_quotation import wrap_quotation


class Column(Variable):
    def __init__(self, context: ColumnContext, parent):
        super().__init__(context.name, type=context.sqlalchemy_type, nullable=context.nullable,
                         context=context, comment=context.comment, parent=parent)
        self.title = context.title
        self.sqlalchemy_type_with_length = context.sqlalchemy_type_with_length
        self.length = context.length
        self.primary_key = context.primary_key
        self.unique = context.unique
        self.nullable = context.nullable
        self.autoincrement = context.autoincrement
        self.foreign_key = context.foreign_key

        self.value = self.get_value()
        self._init_possible_imports()
        # self.possible_imports = self.get_possible_imports()

    def get_value(self):
        column_init_params = [self.sqlalchemy_type_with_length]
        if self.foreign_key:
            column_init_params.append(f"ForeignKey('{self.foreign_key}')")
        if self.primary_key:
            column_init_params.append('primary_key=True')
            if not self.autoincrement:  # True是默认值
                column_init_params.append('autoincrement=False')
        if self.unique:
            column_init_params.append('unique=True')
        if not self.primary_key and not self.nullable:
            column_init_params.append('nullable=False')
        column_init_params.append(f"comment={wrap_quotation(self.comment)}")
        return Call('Column', params=column_init_params, parent=self)

    def serialize(self, delimiter=', ', with_comment=False):
        return super().serialize(delimiter=delimiter, with_comment=with_comment)

    def _init_possible_imports(self):
        self.add_possible_imports([
            Import(from_='sqlalchemy', import_='Column'),
            Import(from_='sqlalchemy', import_='ForeignKey'),
            Import(from_='sqlalchemy', import_='Integer'),
            Import(from_='sqlalchemy', import_='BigInteger'),
            Import(from_='sqlalchemy', import_='String'),
            Import(from_='sqlalchemy', import_='Boolean'),
            Import(from_='sqlalchemy', import_='DateTime'),
            Import(from_='sqlalchemy', import_='Date'),
            Import(from_='sqlalchemy', import_='Time'),
            Import(from_='sqlalchemy', import_='BLOB'),
            Import(from_='sqlalchemy', import_='Text'),
            Import(from_='sqlalchemy', import_='DECIMAL'),
            Import(from_='sqlalchemy', import_='Float'),
            Import(from_='sqlalchemy', import_='JSON')
        ])
