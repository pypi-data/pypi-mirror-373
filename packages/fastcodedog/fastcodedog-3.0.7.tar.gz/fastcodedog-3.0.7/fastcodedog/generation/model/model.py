# -*- coding: utf-8 -*-
from fastcodedog.context.model.model import Model as ModelContext
from fastcodedog.generation.base.class_type import ClassType
from fastcodedog.generation.base.line_break import LineBreak
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.variable import Variable
from fastcodedog.generation.model.column import Column
from fastcodedog.generation.model.computed_property import ComputedProperty
from fastcodedog.generation.model.additional_method import AdditionalMethod
from fastcodedog.generation.model.relationship import Relationship
from fastcodedog.generation.model.table_args import TableArgs


class Model(ClassType):
    def __init__(self, context: ModelContext = None):
        super().__init__(context.name, base_class='Base', context=context, comment=context.comment)
        self.title = context.title

        self.blocks.append(Variable('__tablename__', value=f"'{context.table_name}'"))  # __tablename__
        self.blocks.extend([Column(column, self) for column in context.columns.values()])  # columns
        self.blocks.append(LineBreak())  # 空行
        for computed_property in context.computed_properties.values():
            self.blocks.append(ComputedProperty(computed_property))
        self.blocks.append(TableArgs(context.unique_constraints, commit=(context.title if (not context.comment or context.title == context.comment) else f'{context.title}: {context.comment}') ))  # __table_args__
        # relationships
        self.blocks.extend([Relationship(relationship, self) for relationship in context.relationships.values() if
                            not relationship.disabled])

        for additional_method in context.additional_methods.values():
            self.blocks.append(AdditionalMethod(additional_method))
        self.add_possible_imports(Import('Base', LocationFinder.get_package('Base')))
