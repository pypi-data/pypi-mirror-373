# -*- coding: utf-8 -*-
import json5

from fastcodedog.common.source_file_path import get_schema_file_path
from fastcodedog.context.common.get_relationship import get_class_type_by_model_and_relationship_name


def generate_sub_objects(expression, schema_data):
    # 把"users.roles.users", "users.roles.menus"格式转为
    # users{roles{users, menus}}的格式
    if not expression:
        return
    cur_exp = expression.split('.')[0]
    sub_class_type = {}
    if 'sub_objects' not in schema_data:
        schema_data['sub_objects'] = {}
    for sub_objet_name, sub_object in schema_data['sub_objects'].items():  # 子对象已经存在
        if sub_objet_name == cur_exp:
            sub_class_type = sub_object['class_type']
    if not sub_class_type:  # 子对象不存在
        sub_object_module, sub_object_class_type, sub_object_is_list = get_class_type_by_model_and_relationship_name(
            schema_data['base_class'], cur_exp, module=schema_data['module']
        )
        new_sub_object = {
            'name': cur_exp,
            'is_list': sub_object_is_list,
            'class_type': {
                'name': f'_{sub_object_class_type}',
                'module': sub_object_module,
                'base_class': sub_object_class_type,
            }
        }
        schema_data['sub_objects'][cur_exp] = new_sub_object
        sub_class_type = new_sub_object['class_type']
    if expression.find('.') != -1:
        sub_exp = expression[expression.find('.') + 1:]
        generate_sub_objects(sub_exp, sub_class_type)


def add_response_schemas(response_schemas):
    if not response_schemas:
        return
    for response_schema in response_schemas:
        module = response_schema['module']
        schema = response_schema['schema']
        name = response_schema['name']
        expressions = response_schema['expressions']
        schema_data = {
            'name': name,
            'module': module,
            'base_class': schema
        }
        for expression in expressions:
            generate_sub_objects(expression, schema_data)
        json_file = get_schema_file_path(module, schema)
        data = json5.load(open(json_file, 'r', encoding='utf-8'))
        if 'response_schemas' not in data:
            data['response_schemas'] = {}
        data['response_schemas'][name] = schema_data
        json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
