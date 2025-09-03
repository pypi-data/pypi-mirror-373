# -*- coding: utf-8 -*-
import shutil

from fastcodedog.common.source_file_path import get_crud_file_path
from fastcodedog.common.write_file import write_json_file
from fastcodedog.context.common.get_context_object import get_model_context, get_schema_context
from fastcodedog.context.context import ctx_instance
from fastcodedog.prepare.model_and_schema_to_crud.default_values import add_default_value
from fastcodedog.prepare.model_and_schema_to_crud.queries import add_queries


def get_uuid_keys(model):
    uuid_keys = {}
    for column in model.columns.values():
        if column.domain == 'UUID':
            uuid_keys[column.name] = {'name': column.name, 'title': column.title, 'type': column.type, 'nullable': column.nullable,
                                      'description': column.comment}
    return uuid_keys

def get_primary_key(model):
    for column in model.columns.values():
        if column.primary_key:
            return {'name': column.name, 'title': column.title, 'type': column.type, 'nullable': column.nullable,
                    'description': column.comment}


def get_unique_constraints(model):
    unique_constraints = []
    for unique_constraint in model.unique_constraints:
        unique_columns = []
        for key in unique_constraint:
            column = model.columns[key]
            unique_columns.append(
                {'name': column.name, 'title': column.title, 'type': column.type, 'nullable': column.nullable,
                 'description': column.comment})
        unique_constraints.append(unique_columns)
    return unique_constraints


def get_foreign_keys(model):
    return {column.name: {'name': column.name, 'title': column.title, 'type': column.type,
                          'nullable': column.nullable,
                          'description': column.comment} for column in model.columns.values() if column.foreign_key}


def get_join_relationships(model):
    return {relationship.name: {'name': relationship.name, 'original_name': relationship.original_name,
                                'secondary_object_name': relationship.secondary_object_name,
                                'back_populates': relationship.back_populates,
                                'back_populates_module': relationship.back_populates_module,
                                'back_populates_model': relationship.back_populates_model,
                                'back_populates_primary_key': get_primary_key(
                                    get_model_context(relationship.back_populates_module,
                                                      relationship.back_populates_model))}
            for relationship in model.relationships.values() if relationship.from_join_table}


def model_and_schema_to_crud(model, schema):
    return {
        'title': model.title,
        'comment': model.comment,
        'module': model.module,
        'name': model.name,
        'uuid_keys': get_uuid_keys(model),
        'primary_key': get_primary_key(model),
        'foreign_keys': get_foreign_keys(model),
        'unique_constraints': get_unique_constraints(model),
        'join_relationships': get_join_relationships(model)
    }


def prepare_crud(pre_process_scripts):
    # 先清空目录
    shutil.rmtree(ctx_instance.source_directory.crud, ignore_errors=True)
    for module, models in ctx_instance.models.items():
        for model_context in models.values():
            if model_context.is_relationship:
                continue
            schema_context = get_schema_context(module, model_context.name)
            file_path = get_crud_file_path(module, model_context.name)
            write_json_file(file_path, model_and_schema_to_crud(model_context, schema_context))
    # 写入默认值
    add_default_value(ctx_instance.source_directory.crud, pre_process_scripts.get('default_values'))
    # 写入query
    add_queries(ctx_instance.source_directory.crud, pre_process_scripts.get('queries'))
