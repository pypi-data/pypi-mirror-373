# -*- coding: utf-8 -*-
import json5
import os

from fastcodedog.util.case_converter import camel_to_snake


def add_computed_properties(model_directory, computed_properties):
    for computed_property in computed_properties:
        module = computed_property.get('module')
        model_name = computed_property.get('model_name')

        json_file = os.path.join(model_directory, module, f'{camel_to_snake(model_name)}.json5')
        data = json5.load(open(json_file, 'r', encoding='utf-8'))
        if 'computed_properties' not in data:
            data['computed_properties'] = {}
        data['computed_properties'][computed_property['name']] = computed_property
        json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
