# -*- coding: utf-8 -*-
import shutil

from fastcodedog.common.source_file_path import get_api_file_path
from fastcodedog.common.write_file import write_json_file
from fastcodedog.context.common.get_context_object import get_schema_context
from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.crud.crud import get_blocks
from fastcodedog.generation.crud.crud_functions import Crud
from fastcodedog.prepare.schema_and_crud_to_api.endpoint import Endpoint
from fastcodedog.prepare.schema_and_crud_to_api.validate_reponse_models import get_validate_response_models


def crud_and_schema_to_api(crud_context, schema_context):
    return {
        'title': crud_context.title,
        'comment': crud_context.comment,
        'module': crud_context.module,
        'name': crud_context.name,
        'primary_key_name': crud_context.primary_key.name,
        'oauth2_enabled': ctx_instance.oauth2.enabled,
        # 'schemas': get_schems(schema_context),
        'validate_response_models': get_validate_response_models(schema_context),
        'endpoints': {block.name: Endpoint(block, crud_context, schema_context).to_json() for block in
                      get_blocks(crud_context) if isinstance(block, Crud)},
    }


def prepare_api(pre_process_scripts):
    # 先清空目录
    shutil.rmtree(ctx_instance.source_directory.api, ignore_errors=True)
    for module, cruds in ctx_instance.cruds.items():
        for crud_context in cruds.values():
            schema_context = get_schema_context(module, crud_context.name)
            file_path = get_api_file_path(module, crud_context.name)
            write_json_file(file_path, crud_and_schema_to_api(crud_context, schema_context))
