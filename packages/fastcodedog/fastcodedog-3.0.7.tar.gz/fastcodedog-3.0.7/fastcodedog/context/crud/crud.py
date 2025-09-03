# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.context.crud.column import Column
from fastcodedog.context.crud.default_value import DefaultValue
from fastcodedog.context.crud.join_relationship import JoinRelationship
from fastcodedog.context.crud.query import Query


class Crud(ContextBase):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.comment = ''
        self.module = ''
        self.name = ''
        self.primary_key = Column()
        self.uuid_keys = {}
        self._types['uuid_keys'] = Column
        self.foreign_keys = {}
        self._types['foreign_keys'] = Column
        self.unique_constraints = []
        self._types['unique_constraints'] = Column
        self.join_relationships = {}
        self._types['join_relationships'] = JoinRelationship
        self.queries = {}
        self._types['queries'] = Query
        self.default_values = {}
        self._types['default_values'] = DefaultValue

    def load(self, json):
        for k, v in json.items():
            if k == 'unique_constraints':
                for unique_constraint in v:
                    unique_columns = []
                    for c in unique_constraint:
                        column = Column()
                        column.load(c)
                        unique_columns.append(column)
                    self.unique_constraints.append(unique_columns)
            else:
                super().load({k: v})
