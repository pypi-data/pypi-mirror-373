# -*- coding: utf-8 -*-
import sys

import json5

from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.api.generation import generate_api
from fastcodedog.generation.commonfiles.generation import generate_common_files
from fastcodedog.generation.crud.generation import generate_crud
from fastcodedog.generation.model.generation import generate_model
from fastcodedog.generation.schema.generation import genenrate_schema
from fastcodedog.prepare.model_and_schema_to_crud.prepare import prepare_crud
from fastcodedog.prepare.model_to_schema.prepare import prepare_schema
from fastcodedog.prepare.pdm_to_model.prepare import prepare_model
from fastcodedog.prepare.schema_and_crud_to_api.prepare import prepare_api
from fastcodedog.util.deep_update import deep_update
from fastcodedog.util.find_file import find


def main():
    if len(sys.argv) == 1:
        raise ValueError('缺少参数，请传入json5配置文件')
    ctx_instance.load(sys.argv[1])
    pre_process_scripts = {}
    for file in find('.', ctx_instance.source_directory.pre_process_scripts_file):
        pre_process_scripts = deep_update(pre_process_scripts, json5.load(open(file, 'r', encoding='utf-8')))
    prepare_model(pre_process_scripts)
    ctx_instance.load_models(ctx_instance.source_directory.model)
    prepare_schema(pre_process_scripts)
    ctx_instance.load_schemas(ctx_instance.source_directory.schema)
    prepare_crud(pre_process_scripts)
    ctx_instance.load_cruds(ctx_instance.source_directory.crud)
    prepare_api(pre_process_scripts)
    ctx_instance.load_apis(ctx_instance.source_directory.api)
    generate_common_files()
    generate_model()
    genenrate_schema()
    generate_crud()
    generate_api()


if __name__ == '__main__':
    """    
$env:PYTHONPATH = "."
python fastcodedog/cli.py fastcodegen/test/fastframe.diagram.json5 fastcodegen/test/fastframe.model.json5
"""
    main()
