# -*- coding: utf-8 -*-
import json5

from fastcodedog.common.source_file_path import get_crud_file_path
from fastcodedog.context.context import ctx_instance
from fastcodedog.context.crud.crud import Crud
from fastcodedog.context.model.model import Model
from fastcodedog.util.find_file import find


def add_default_value(crud_directory, default_values):
    for column_name, default_value in default_values.items():
        k_model = ''
        k_column = ''
        if column_name.find('.') > 0:
            k_model = column_name.split('.')[0]
            k_column = column_name.split('.')[1]
        else:
            k_column = column_name
        files = find(ctx_instance.source_directory.model, '*/*.json5')
        for file in files:
            model = Model()
            model.load(json5.load(open(file, 'r', encoding='utf-8')))
            if k_model and k_model != model.name:
                continue
            for column in model.columns.keys():
                if k_column != column:
                    continue
                json_file = get_crud_file_path(model.module, model.name)
                data = json5.load(open(json_file, 'r', encoding='utf-8'))
                if 'default_values' not in data:
                    data['default_values'] = {}
                data['default_values'][column_name] = default_value
                json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)


