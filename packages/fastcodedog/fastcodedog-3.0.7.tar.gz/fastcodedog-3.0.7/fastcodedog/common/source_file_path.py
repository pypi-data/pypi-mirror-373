# -*- coding: utf-8 -*-
import os

from fastcodedog.context.context import ctx_instance
from fastcodedog.util.case_converter import camel_to_snake


def get_model_file_path(module, model_name):
    return os.path.join(ctx_instance.source_directory.model, module, f'{camel_to_snake(model_name)}.json5')


def get_schema_file_path(module, schema_name):
    return os.path.join(ctx_instance.source_directory.schema, module, f'{camel_to_snake(schema_name)}.json5')


def get_crud_file_path(module, crud_name):
    return os.path.join(ctx_instance.source_directory.crud, module, f'{camel_to_snake(crud_name)}.json5')


def get_api_file_path(module, crud_name):
    return os.path.join(ctx_instance.source_directory.api, module, f'{camel_to_snake(crud_name)}.json5')
