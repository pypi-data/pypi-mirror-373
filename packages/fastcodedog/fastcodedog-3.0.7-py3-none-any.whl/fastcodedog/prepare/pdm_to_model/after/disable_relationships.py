# -*- coding: utf-8 -*-
import json5
import os
import re

from fastcodedog.util.case_converter import camel_to_snake


def disable_relationships(model_directory, disabled_relationships):
    """系统默认建议的子对象，有时候不需要，比如定单表关联用户，但是不能在用户表创建用户的所有定单这个变量，否则数据量太大。所以需要禁用"""
    for disabled_relationship in disabled_relationships:
        module = disabled_relationship.get('module')
        model_name = disabled_relationship.get('model_name')
        sub_object_patterns = disabled_relationship.get('sub_object_patterns')
        if module and model_name and sub_object_patterns:
            json_file = os.path.join(model_directory, module, f'{camel_to_snake(model_name)}.json5')
            data = json5.load(open(json_file, 'r', encoding='utf-8'))
            for name, relationship in data['relationships'].items():
                for sub_object_pattern in sub_object_patterns:
                    if re.match(sub_object_pattern, name):
                        relationship['disabled'] = True
                        _add_no_backpopulates(model_directory, relationship)
                        break
            json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)


def _add_no_backpopulates(model_directory, another_side_relationship):
    """子对象被禁用之后，对应的结对子对象要不能创建back_populates"""
    json_file = os.path.join(model_directory,
                             another_side_relationship['back_populates_module'],
                             f'{camel_to_snake(another_side_relationship["back_populates_model"])}' + '.json5')
    data = json5.load(open(json_file, 'r', encoding='utf-8'))
    for name, relationship in data['relationships'].items():
        if name == another_side_relationship['back_populates']:
            relationship['no_back_populates'] = True
            break
    json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
