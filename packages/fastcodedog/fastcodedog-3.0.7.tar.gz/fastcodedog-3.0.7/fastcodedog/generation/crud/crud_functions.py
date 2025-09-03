# -*- coding: utf-8 -*-
from enum import Enum

from fastcodedog.context.context import ctx_instance
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.context.crud.crud import Crud as CrudContext
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.text import Text
from fastcodedog.util.case_converter import camel_to_snake
from fastcodedog.util.inflect_wrapper import plural


class Crud(Function):
    POSSIBLE_IMPORTS = ['import datetime', 'from datetime import datetime', 'from datetime import date', 'from datetime import time',
                        'from sqlalchemy import exists', 'from sqlalchemy import select', 'from sqlalchemy import join',
                        'from sqlalchemy import or_', 'from sqlalchemy import and_']

    class Action(Enum):
        CREATE = 'create'  # '创建'
        UPDATE = 'update'  # '更新'
        DELETE = 'delete'  # '删除'
        READ = 'read'  # '查询'

    def __init__(self, name: str, context: ContextBase = None, decorators=None, params=None, blocks=None, comment=None,
                 parent=None):
        super().__init__(name=name, context=context, decorators=decorators, params=params, blocks=blocks,
                         comment=comment,
                         possible_imports=self.POSSIBLE_IMPORTS, parent=parent)
        if not hasattr(self, 'snake_name'):
            self.snake_name = None
        if not hasattr(self, 'action'):
            self.action = None
        if not hasattr(self, 'return_list'):
            self.return_list = False
        if not hasattr(self, 'summary'):
            self.summary = None

    @staticmethod
    def get_luckyname(name):
        if name.endswith('_id'):
            return name[:-3]
        if name.endswith('_uid'):
            return name[:-4]
        return name

    @staticmethod
    def get_package_by_model_name(model_name):
        for models in ctx_instance.models.values():
            for model in models.values():
                if model.name == model_name:
                    return LocationFinder.get_package(model_name, 'model', model.module)
        # 支持的系统模型
        if model_name == 'datetime':
            return None
        raise Exception(f'未找到模型：{model_name}')


class BaseCreate(Crud):
    def __init__(self, context: CrudContext):
        self.snake_name = camel_to_snake(context.name)
        self.action = Crud.Action.CREATE
        self.class_type = context.name
        super().__init__(f'create_{self.snake_name}', context=context, comment=f'创建{context.title}({context.name})')
        self.params['session'] = Function.Parameter('session', nullable=False)
        self.params[f'{self.snake_name}_create'] = Function.Parameter(f'{self.snake_name}_create',
                                                                      type=f'{context.name}Create', nullable=False)
        self.add_possible_imports(
            Import(context.name, LocationFinder.get_package(context.name, 'model', context.module)))
        self.params[f'{self.snake_name}_create'].add_possible_imports(
            Import(f'{context.name}Create', LocationFinder.get_package(context.name, 'schema', context.module)))
        self._init_blocks_and_possible_imports()

    def _init_blocks_and_possible_imports(self):
        self.blocks.append(Text(f"{self.snake_name} = {self.class_type}()"))
        self.blocks.append(Text(f"for key, value in {self.snake_name}_create.dict(exclude_unset=True).items():"))
        for relationship in self.context.join_relationships.values():
            self.add_possible_imports(Import(relationship.back_populates_model,
                                             LocationFinder.get_package(relationship.back_populates_model, 'model',
                                                                        relationship.back_populates_module)))
            v = relationship.back_populates_model[0].lower() + '_'
            content = f"""if key == '{relationship.name}':
    {self.snake_name}.{relationship.name} = [{v} for {v} in session.query({relationship.back_populates_model}).filter({relationship.back_populates_model}.{relationship.back_populates_primary_key.name}.in_(value)).all()]
    continue"""
            self.blocks.append(Text(content, indent=self.DEFAULT_INDENT))
        self.blocks.append(Text(f"setattr({self.snake_name}, key, value)", indent=self.DEFAULT_INDENT))
        for column in self.context.uuid_keys.values():
            if not column.nullable:
                self.blocks.append(Text(f"if not {self.snake_name}.{column.name}:\n    {self.snake_name}.{column.name} = str(uuid.uuid4())",
                                        possible_imports='import uuid'))
        # 添加默认值
        for column, default_value in self.context.default_values.items():
            if default_value.force_default:
                self.blocks.append(Text(f"{self.snake_name}.{column} = {default_value.value_expression}"))
            else:
                self.blocks.append(Text(f"if '{column}' not in {self.snake_name}_create.dict(exclude_unset=True).keys():\n    {self.snake_name}.{column} = {default_value.value_expression}"))
            if default_value.import_:
                self.add_possible_imports(default_value.import_)
        self.blocks.append(Text(f"session.add({self.snake_name})"))
        self.blocks.append(Text(f"session.commit()"))
        self.blocks.append(Text(f"return {self.snake_name}"))


class BaseUpdate(Crud):
    def __init__(self, context: CrudContext):
        self.snake_name = camel_to_snake(context.name)
        self.action = Crud.Action.UPDATE
        super().__init__(f'update_{self.snake_name}', context=context, comment=f'更新{context.title}({context.name})')
        self.class_type = context.name
        self.primary_key_name = context.primary_key.name
        self.primary_key_type = context.primary_key.type
        self.params['session'] = Function.Parameter('session', nullable=False)
        self.params[self.primary_key_name] = Function.Parameter(self.primary_key_name, type=self.primary_key_type,
                                                                comment=context.primary_key.description, nullable=False)
        self.params[f'{self.snake_name}_update'] = Function.Parameter(f'{self.snake_name}_update',
                                                                      type=f'{context.name}Update', nullable=False)
        self.params[f'{self.snake_name}_update'].add_possible_imports(
            Import(f'{context.name}Update', LocationFinder.get_package(context.name, 'schema', context.module)))
        self.add_possible_imports(
            Import(context.name, LocationFinder.get_package(context.name, 'model', context.module)))
        self._init_blocks_and_possible_imports()

    def _init_blocks_and_possible_imports(self):
        self.blocks.append(Text(
            f"{self.snake_name} = session.query({self.class_type}).filter({self.class_type}.{self.primary_key_name} == {self.primary_key_name}).first()"))
        self.blocks.append(Text(f"if not {self.snake_name}:"))
        self.blocks.append(Text(f"return None", indent=self.DEFAULT_INDENT))
        self.blocks.append(Text(f"for key, value in {self.snake_name}_update.dict(exclude_unset=True).items():"))
        for relationship in self.context.join_relationships.values():
            self.add_possible_imports(Import(relationship.back_populates_model,
                                             LocationFinder.get_package(relationship.back_populates_model, 'model',
                                                                        relationship.back_populates_module)))
            v = relationship.back_populates_model[0].lower() + '_'
            content = f"""if key == '{relationship.name}':
    {self.snake_name}.{relationship.name} = [{v} for {v} in session.query({relationship.back_populates_model}).filter({relationship.back_populates_model}.{relationship.back_populates_primary_key.name}.in_(value)).all()]
    continue"""
            self.blocks.append(Text(content, indent=self.DEFAULT_INDENT))
        self.blocks.append(Text(f"setattr({self.snake_name}, key, value)", indent=self.DEFAULT_INDENT))
        # 添加默认值
        for column, default_value in self.context.default_values.items():
            if not default_value.change_when_update:
                continue
            if default_value.force_default:
                self.blocks.append(Text(f"{self.snake_name}.{column} = {default_value.value_expression}"))
            else:
                self.blocks.append(Text(f"if '{column}' not in {self.snake_name}_update.dict(exclude_unset=True).keys():\n    {self.snake_name}.{column} = {default_value.value_expression}"))
            if default_value.import_:
                self.add_possible_imports(default_value.import_)
        self.blocks.append(Text(f"session.commit()"))
        self.blocks.append(Text(f"return {self.snake_name}"))


class BaseDelete(Crud):
    def __init__(self, context: CrudContext):
        self.snake_name = camel_to_snake(context.name)
        self.action = Crud.Action.DELETE
        super().__init__(f'delete_{self.snake_name}', context=context, comment=f'删除{context.title}({context.name})')
        self.class_type = context.name
        self.primary_key_name = context.primary_key.name
        self.primary_key_type = context.primary_key.type
        self.params['session'] = Function.Parameter('session', nullable=False)
        self.params[self.primary_key_name] = Function.Parameter(self.primary_key_name, type=self.primary_key_type,
                                                                comment=context.primary_key.description, nullable=False)
        self.add_possible_imports(
            Import(context.name, LocationFinder.get_package(context.name, 'model', context.module)))
        self._init_blocks()

    def _init_blocks(self):
        self.blocks.append(Text(
            f"{self.snake_name} = session.query({self.class_type}).filter({self.class_type}.{self.primary_key_name} == {self.primary_key_name}).first()"))
        self.blocks.append(Text(f"if not {self.snake_name}:"))
        self.blocks.append(Text(f"return None", indent=self.DEFAULT_INDENT))
        self.blocks.append(Text(f"session.delete({self.snake_name})"))
        self.blocks.append(Text(f"session.commit()"))
        self.blocks.append(Text(f"return {self.snake_name}"))


class BaseGet(Crud):
    def __init__(self, context: CrudContext):
        self.snake_name = camel_to_snake(context.name)
        self.action = Crud.Action.READ
        super().__init__(f'get_{self.snake_name}', context=context, comment=f'获取{context.title}({context.name})')
        self.class_type = context.name
        self.primary_key_name = context.primary_key.name
        self.primary_key_type = context.primary_key.type
        self.params['session'] = Function.Parameter('session', nullable=False)
        self.params[self.primary_key_name] = Function.Parameter(self.primary_key_name, type=self.primary_key_type,
                                                                comment=context.primary_key.description, nullable=False)
        self.add_possible_imports(
            Import(context.name, LocationFinder.get_package(context.name, 'model', context.module)))
        self._init_blocks()

    def _init_blocks(self):
        self.blocks.append(Text(
            f"return session.query({self.class_type}).filter({self.class_type}.{self.primary_key_name} == {self.primary_key_name})"))


class UniqueGet(Crud):
    def __init__(self, unique_keys: list, context: CrudContext):
        self.snake_name = camel_to_snake(context.name)
        self.action = Crud.Action.READ
        super().__init__(f'get_{self.snake_name}_by_{"_and_".join([key.name for key in unique_keys])}', context=context)
        self.unique_keys = unique_keys
        self.comment = f'使用{"和".join([key.title for key in unique_keys])}查询'
        self.class_type = context.name
        self.params['session'] = Function.Parameter('session', nullable=False)
        for key in unique_keys:
            self.params[key.name] = Function.Parameter(key.name, type=key.type, comment=key.description, nullable=False)
        self._init_blocks()

    def _init_blocks(self):
        filters = [f'filter({self.class_type}.{key.name} == {key.name})' for key in self.unique_keys]
        self.blocks.append(Text(f"return session.query({self.class_type}).{'.'.join(filters)}"))


class JoinAdd(Crud):
    def __init__(self, relationship_context, context: CrudContext):
        self.snake_name = camel_to_snake(context.name)
        self.action = Crud.Action.CREATE
        self.relationship_name = relationship_context.name
        super().__init__(f'add_{self.relationship_name}_to_{self.snake_name}', context=context)
        self.relationship_context = relationship_context
        self.comment = f'添加关联的{relationship_context.name}'
        self.primary_key_name = context.primary_key.name
        self.primary_key_type = context.primary_key.type
        self.class_type = context.name
        self.params['session'] = Function.Parameter('session', nullable=False)
        self.params[self.primary_key_name] = Function.Parameter(self.primary_key_name, type=self.primary_key_type,
                                                                nullable=False)
        self.param_relationship = Function.Parameter(plural(relationship_context.original_name),
                                                     type=f'list[{relationship_context.back_populates_primary_key.type}]',
                                                     nullable=False)
        self.params[self.param_relationship.name] = self.param_relationship
        self._init_blocks_and_possible_imports()

    def _init_blocks_and_possible_imports(self):
        self.blocks.append(Text(
            f"{self.snake_name} = session.query({self.class_type}).filter({self.class_type}.{self.primary_key_name} == {self.primary_key_name}).first()"))
        self.blocks.append(Text(f"if not {self.snake_name}:"))
        self.blocks.append(Text(f"return None", indent=self.DEFAULT_INDENT))
        self.blocks.append(Text(
            f"{self.relationship_name} = session.query({self.relationship_context.back_populates_model}).filter({self.relationship_context.back_populates_model}.{self.relationship_context.back_populates_primary_key.name}.in_({self.param_relationship.name})).all()"))
        self.add_possible_imports(Import(self.relationship_context.back_populates_model,
                                         LocationFinder.get_package(self.relationship_context.back_populates_model,
                                                                    'model',
                                                                    self.relationship_context.back_populates_module)))
        v = self.relationship_name[0].lower() + '_'
        content = f"""for {v} in {self.relationship_name}:
    if {v} not in {self.snake_name}.{self.relationship_name}:
        {self.snake_name}.{self.relationship_name}.append({v})
session.commit()"""
        self.blocks.append(Text(content))
        self.blocks.append(Text(f"return {self.snake_name}"))


class JoinDelete(Crud):
    def __init__(self, relationship_context, context: CrudContext):
        self.snake_name = camel_to_snake(context.name)
        self.action = Crud.Action.DELETE
        self.relationship_name = relationship_context.name
        super().__init__(f'delete_{self.relationship_name}_from_{self.snake_name}', context=context)
        self.relationship_context = relationship_context
        self.comment = f'删除关联的{relationship_context.name}'
        self.primary_key_name = context.primary_key.name
        self.primary_key_type = context.primary_key.type
        self.class_type = context.name
        self.params['session'] = Function.Parameter('session', nullable=False)
        self.params[self.primary_key_name] = Function.Parameter(self.primary_key_name, type=self.primary_key_type,
                                                                nullable=False)
        self.param_relationship = Function.Parameter(plural(relationship_context.original_name),
                                                     type=f'list[{relationship_context.back_populates_primary_key.type}]',
                                                     nullable=False)
        self.params[self.param_relationship.name] = self.param_relationship
        self._init_blocks_and_possible_imports()

    def _init_blocks_and_possible_imports(self):
        self.blocks.append(Text(
            f"{self.snake_name} = session.query({self.class_type}).filter({self.class_type}.{self.primary_key_name} == {self.primary_key_name}).first()"))
        self.blocks.append(Text(f"if not {self.snake_name}:"))
        self.blocks.append(Text(f"return None", indent=self.DEFAULT_INDENT))
        self.blocks.append(Text(
            f"{self.relationship_name} = session.query({self.relationship_context.back_populates_model}).filter({self.relationship_context.back_populates_model}.{self.relationship_context.back_populates_primary_key.name}.in_({self.param_relationship.name})).all()"))
        # self.possible_imports[self.relationship_context.back_populates_model] = Import(
        #     LocationFinder.get_package(self.relationship_context.back_populates_model, 'model', self.relationship_context.back_populates_module),
        #     self.relationship_context.back_populates_model)
        self.add_possible_imports(Import(self.relationship_context.back_populates_model,
                                         LocationFinder.get_package(self.relationship_context.back_populates_model,
                                                                    'model',
                                                                    self.relationship_context.back_populates_module)))
        v = self.relationship_name[0].lower() + '_'
        content = f"""for {v} in {self.relationship_name}:
    if {v} in {self.snake_name}.{self.relationship_name}:
        {self.snake_name}.{self.relationship_name}.remove({v})
session.commit()"""
        self.blocks.append(Text(content))
        self.blocks.append(Text(f"return {self.snake_name}"))
