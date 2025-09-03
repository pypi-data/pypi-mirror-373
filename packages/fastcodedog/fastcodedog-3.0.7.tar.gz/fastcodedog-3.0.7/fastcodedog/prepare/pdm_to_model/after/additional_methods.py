# -*- coding: utf-8 -*-
import json5
import os

from fastcodedog.util.case_converter import camel_to_snake


def add_additional_methods(model_directory, additional_methods):
    for additional_method in additional_methods:
        module = additional_method.get('module')
        model_name = additional_method.get('model_name')

        json_file = os.path.join(model_directory, module, f'{camel_to_snake(model_name)}.json5')
        data = json5.load(open(json_file, 'r', encoding='utf-8'))
        if 'additional_methods' not in data:
            data['additional_methods'] = {}
        data['additional_methods'][additional_method['name']] = additional_method
        json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
