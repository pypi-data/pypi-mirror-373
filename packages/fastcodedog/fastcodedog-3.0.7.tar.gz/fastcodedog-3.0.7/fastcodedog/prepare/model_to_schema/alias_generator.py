# -*- coding: utf-8 -*-
import json5
import os


def set_alias_generator(schema_directory, alias_generator):
    if not alias_generator:
        return
    for root, modules, _ in os.walk(schema_directory):
        for module in modules:
            for _, _, files in os.walk(os.path.join(root, module)):
                for file in files:
                    if file.endswith('.json5'):
                        json_file = os.path.join(root, module, file)
                        data = json5.load(open(json_file, 'r', encoding='utf-8'))
                        data['alias_generator'] = alias_generator
                        json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
