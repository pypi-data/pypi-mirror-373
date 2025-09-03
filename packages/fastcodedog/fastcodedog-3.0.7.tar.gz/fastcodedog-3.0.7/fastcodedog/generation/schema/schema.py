# -*- coding: utf-8 -*-
from fastcodedog.context.schema.schema import Schema as SchemaContext
from fastcodedog.generation.base.class_type import ClassType
from fastcodedog.generation.base.variable import Variable
from fastcodedog.generation.schema.field import Field
from fastcodedog.generation.schema.sub_object import SubObject

POSSIBLE_IMPORTS = ['from pydantic import BaseModel']


class SchemaBase(ClassType):
    def __init__(self, context: SchemaContext = None):
        super().__init__(f'{context.name}Base', base_class='BaseModel', context=context,
                         comment=context.description, possible_imports=POSSIBLE_IMPORTS)
        # 添加基本字段
        for field in context.fields.values():
            if not field.no_response and not field.no_input and field.optional:
                self.blocks.append(Field(field, optional=field.optional, default_str=field.default_str, parent=self))
        # 添加Config
        config = ClassType('Config')
        config.blocks.append(Variable('from_attributes', value=True))
        config.blocks.append(Variable('populate_by_name', value=True))
        if context.alias_generator:
            alias_generator = Variable('alias_generator', value=context.alias_generator.function)
            if context.alias_generator.import_:
                alias_generator.add_possible_imports(context.alias_generator.import_)
            config.blocks.append(alias_generator)
        self.blocks.append(config)


class Schema(ClassType):
    def __init__(self, context: SchemaContext = None, base_class=None):
        super().__init__(context.name, base_class=base_class.name, context=context,
                         comment=context.description, possible_imports=POSSIBLE_IMPORTS)
        # 添加基本字段
        for field in context.fields.values():
            if not field.no_response and field.name not in [block.name for block in base_class.blocks]:
                self.blocks.append(Field(field, optional=field.optional, default_str=field.default_str, parent=self))
        for field in context.computed_properties.values():
            self.blocks.append(Field(field, optional=True, default_str='None', parent=self))


class SchemaCreate(ClassType):
    def __init__(self, context: SchemaContext = None, base_class=None):
        super().__init__(f'{context.name}Create', base_class=base_class.name, context=context,
                         comment=context.description, possible_imports=POSSIBLE_IMPORTS)
        # 添加基本字段
        for field in context.fields.values():
            if not field.no_input and field.name not in [block.name for block in base_class.blocks]:
                self.blocks.append(Field(field, optional=field.optional, default_str=field.default_str, parent=self))
        # 添加关联关系或子对象
        for sub_object in context.sub_objects.values():
            if sub_object.from_join_table:
                self.blocks.append(SubObject(sub_object, self))


class SchemaUpdate(ClassType):
    def __init__(self, context: SchemaContext = None, base_class=None):
        super().__init__(f'{context.name}Update', base_class=base_class.name, context=context,
                         comment=context.description, possible_imports=POSSIBLE_IMPORTS)
        # 添加基本字段
        for field in context.fields.values():
            if not field.no_input and field.name not in [block.name for block in base_class.blocks]:
                self.blocks.append(Field(field, optional=True, default_str='None', parent=self))
        # 添加关联关系或子对象
        for sub_object in context.sub_objects.values():
            if sub_object.from_join_table:
                self.blocks.append(SubObject(sub_object, self))
