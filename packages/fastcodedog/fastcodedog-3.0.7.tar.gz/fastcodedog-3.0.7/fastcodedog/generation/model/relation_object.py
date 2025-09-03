# -*- coding: utf-8 -*-
from fastcodedog.context.model.model import Model as ModelContext
from fastcodedog.generation.base.call import Call
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.required_import import RequiredImport
from fastcodedog.generation.base.variable import Variable
from fastcodedog.generation.model.column import Column


class RelationObject(Variable):
    def __init__(self, context: ModelContext = None):
        super().__init__(context.name, context=context, comment=context.comment)
        self.module = context.module
        self.title = context.title
        self.table_name = context.table_name
        self.columns = [Column(column, self) for column in context.columns.values()]

        self.value = Call('Table', params=[f"'{self.table_name}'", 'Base.metadata',
                                           self._get_column(self.columns[0]),
                                           self._get_column(self.columns[1])],
                          parent=self)
        self.add_possible_imports(['from sqlalchemy import Table',
                                   Import(from_=LocationFinder.get_package('Base'), import_='Base')])

    def _get_column(self, column):
        foreign_key = Call('ForeignKey', params=[f"'{column.foreign_key}'", Variable('ondelete', value="'CASCADE'")],
                           parent=self)
        return Call('Column', params=[f"'{column.name}'", column.sqlalchemy_type_with_length, foreign_key,
                                      Variable('primary_key', value=column.primary_key)], parent=self)

    def get_required_imports(self):
        required_import = RequiredImport()
        required_import.add(self.possible_imports['Base'])
        required_import.add(self.possible_imports['Table'])
        for column in self.columns:
            required_import.update(column.get_required_imports())
        return required_import

    def serialize(self, delimiter=',\n    ', with_comment=False):
        return super().serialize(delimiter=delimiter, with_comment=with_comment)
