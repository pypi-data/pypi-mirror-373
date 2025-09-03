# -*- coding: utf-8 -*-
import shutil

from fastcodedog.common.source_file_path import get_schema_file_path
from fastcodedog.common.write_file import write_json_file
from fastcodedog.context.context import ctx_instance
from fastcodedog.prepare.model_to_schema.alias_generator import set_alias_generator
from fastcodedog.prepare.model_to_schema.no_input_fields import set_no_input_fields
from fastcodedog.prepare.model_to_schema.no_response_fields import set_no_response_fields
from fastcodedog.prepare.model_to_schema.response_schemas import add_response_schemas
from fastcodedog.prepare.model_to_schema.specified_field_types import rename_specified_field_types
from fastcodedog.util.type_converter import sqlalchemy_type_to_pydantic_type


def relationships_to_subobject(relationships):
    sub_objects = {}
    for relationship in relationships:
        if not relationship.disabled:
            sub_objects[relationship.name] = {
                'name': relationship.name,
                'module': relationship.back_populates_module,
                'class_type': relationship.back_populates_model,
                'from_join_table': relationship.from_join_table,
                'is_list': relationship.is_list,
                'disabled': relationship.disabled
            }
    return sub_objects


def columns_to_fields(columns):
    fields = {}
    for column in columns:
        fields[column.name] = {
            'name': column.name,
            'title': column.title,
            'pydantic_type': sqlalchemy_type_to_pydantic_type(column.sqlalchemy_type, column.length)[0],
            'pydantic_type_with_length': sqlalchemy_type_to_pydantic_type(column.sqlalchemy_type, column.length)[1],
            'max_length': column.length,
            'optional': column.nullable,  # 类型中添加Optional标记[]
            'default_str': 'None' if column.nullable else '...',  # 默认值，用字符串表示
            'description': column.comment
        }
    return fields


def computed_properties_to_fields(computed_properties):
    fields = {}
    for computed_property in computed_properties.values():
        fields[computed_property.name] = {
            'name': computed_property.name,
            'title': computed_property.title,
            'pydantic_type': computed_property.pydantic_type,
            'pydantic_type_with_length': computed_property.pydantic_type,
            'description': computed_property.comment
        }
    return fields


def model_to_schema(context):
    return {
        'title': context.title,
        'description': context.comment,
        'module': context.module,
        'name': context.name,
        'fields': columns_to_fields(context.columns.values()),
        'computed_properties': computed_properties_to_fields(context.computed_properties),
        'sub_objects': relationships_to_subobject(context.relationships.values())
    }


def prepare_schema(pre_process_scripts):
    # 先清空目录
    shutil.rmtree(ctx_instance.source_directory.schema, ignore_errors=True)
    # 根据model生成schema
    for module, models in ctx_instance.models.items():
        for model_context in models.values():
            if not model_context.is_relationship:
                file_path = get_schema_file_path(module, model_context.name)
                write_json_file(file_path, model_to_schema(model_context))
    # 设置指定的类型
    rename_specified_field_types(ctx_instance.source_directory.schema, pre_process_scripts.get('specified_field_types'))
    # 增加别名
    set_alias_generator(ctx_instance.source_directory.schema, pre_process_scripts.get('alias_generator'))
    # 设置不返回的field
    set_no_response_fields(ctx_instance.source_directory.schema, pre_process_scripts.get('no_response_fields'))
    # 设置禁止用户输入的field，一般这里的设置会配置默认值使用
    set_no_input_fields(ctx_instance.source_directory.schema, pre_process_scripts.get('no_input_fields'))
    # 默认值
    # 添加扩展schema
    add_response_schemas(pre_process_scripts.get('response_schemas'))
