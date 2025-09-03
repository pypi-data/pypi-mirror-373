# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance


def get_model_context(module, model_name):
    return ctx_instance.models[module][model_name]


def get_schema_context(module, schema_name):
    return ctx_instance.schemas[module][schema_name]
