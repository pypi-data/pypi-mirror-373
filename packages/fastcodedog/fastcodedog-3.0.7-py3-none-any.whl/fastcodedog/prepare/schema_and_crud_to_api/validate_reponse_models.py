# -*- coding: utf-8 -*-
from fastcodedog.util.case_converter import camel_to_snake


def get_validate_response_models(schema_context):
    return [camel_to_snake(schema_context.name)] + [schema for schema in schema_context.response_schemas.keys()]
