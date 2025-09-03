# -*- coding: utf-8 -*-
from fastcodedog.context.crud.crud import Crud as CrudContext
from fastcodedog.context.schema.schema import Schema as SchemaContext
from fastcodedog.generation.crud.crud_functions import BaseCreate, BaseUpdate, BaseDelete, BaseGet, UniqueGet, JoinAdd, \
    JoinDelete, Crud
from fastcodedog.util.case_converter import camel_to_snake
from fastcodedog.util.inflect_wrapper import plural


class Endpoint:
    def __init__(self, block, crud_context: CrudContext, schema_context: SchemaContext):
        self.name = block.name
        self.block = block
        self.crud_context = crud_context
        self.schema_context = schema_context
        self.snake_name = camel_to_snake(crud_context.name)

    def to_json(self):
        return {
            'name': self.name,
            'have_select_models': False if not hasattr(self.block, 'have_select_models') else self.block.have_select_models,
            'summary': self.block.summary,
            'comment': self.block.comment,
            'action': self._get_action(),
            'return_list': self.block.return_list,
            'max_size': self.block.context.max_size if hasattr(self.block.context, 'max_size') else None,
            'url': self._get_url(),
            'tags': self._get_tags(),
            'params': self._get_params(),
        }

    def _get_action(self):
        if self.block.action == Crud.Action.CREATE:
            return 'post'
        if self.block.action == Crud.Action.UPDATE:
            return 'put'
        if self.block.action == Crud.Action.DELETE:
            return 'delete'
        if self.block.action == Crud.Action.READ:
            return 'get'
        raise Exception(f'未知的Action：{self.block.action}')

    def _get_params(self):
        return {param.name: {
            'name': param.name,
            'type': param.type,
            'option_none': param.option_none,
            'description': param.comment,
            'nullable': param.nullable,
            'enum': param.valid_values,
            'default_value': param.value
        } for param in self.block.params.values() if param.name not in ['session', 'option_none_params']}

    def _get_tags(self):
        return [f'{self.crud_context.title}({self.crud_context.name})']

    def _get_url(self):
        plural_snake_name = plural(self.snake_name)
        url = f'/{self.snake_name}' if not self.block.return_list else f'/{plural_snake_name}'
        if isinstance(self.block, BaseCreate):
            ...
        elif isinstance(self.block, BaseUpdate) or isinstance(self.block, BaseDelete) or isinstance(self.block,
                                                                                                    BaseGet):
            url += f'/{{{self.crud_context.primary_key.name}}}'
        elif isinstance(self.block, UniqueGet):
            unique_key_names = [unique_key.name for unique_key in self.block.unique_keys]
            url += f'/{self.snake_name}_by_{"_and_".join(unique_key_names)}'
            url += f'/{"/".join(["{" + key + "}" for key in unique_key_names])}'
        elif isinstance(self.block, JoinAdd) or isinstance(self.block, JoinDelete):
            url += f'/{{{self.crud_context.primary_key.name}}}/{self.block.relationship_name}'
        else:
            url += f'/{self.block.snake_name}'
        return url
