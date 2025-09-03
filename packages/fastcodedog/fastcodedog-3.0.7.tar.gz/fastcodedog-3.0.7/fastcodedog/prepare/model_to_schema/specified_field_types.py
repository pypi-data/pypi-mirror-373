# -*- coding: utf-8 -*-
import json5
import os


def rename_specified_field_types(schema_directory, specified_field_types):
    if not specified_field_types:
        return
    for root, modules, _ in os.walk(schema_directory):
        for module in modules:
            for _, _, files in os.walk(os.path.join(root, module)):
                for file in files:
                    if file.endswith('.json5'):
                        json_file = os.path.join(root, module, file)
                        data = json5.load(open(json_file, 'r', encoding='utf-8'))
                        schema_name = data['name']
                        for field_name, field in data['fields'].items():
                            if field_name in specified_field_types:
                                field['pydantic_type'] = field['pydantic_type_with_length'] = specified_field_types[field_name]
                            elif f'{schema_name}.{field_name}' in specified_field_types:
                                field['pydantic_type'] = field['pydantic_type_with_length'] = specified_field_types[f'{schema_name}.{field_name}']
                        json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

