# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.schema.response_schema import ResponseSchema
from fastcodedog.generation.schema.schema import SchemaBase, Schema, SchemaCreate, SchemaUpdate
from fastcodedog.util.case_converter import snake_to_camel


def genenrate_schema(specify_schema=None):
    for module, schemas in ctx_instance.schemas.items():
        for schema_context in schemas.values():
            if specify_schema and schema_context.name not in specify_schema:
                continue
            schema_base = SchemaBase(schema_context)
            # 标准的schema文件
            schema_file = File(schema_context.name,
                               file_path=LocationFinder.get_path(schema_context.name, 'schema', module),
                               package=LocationFinder.get_package(schema_context.name, 'schema', module),
                               blocks=[schema_base, Schema(schema_context, schema_base),
                                       SchemaCreate(schema_context, schema_base),
                                       SchemaUpdate(schema_context, schema_base)],
                               context=schema_context, comment=schema_context.description)
            schema_file.save()

            # response_schema文件
            if schema_context.response_schemas:
                schema_base.parent = schema_file  # 通过parent获取package
                response_schema_file = File(schema_context.name + 'Response',
                                            file_path=LocationFinder.get_path(f'{schema_context.name}_additional',
                                                                              'schema', module),
                                            package=LocationFinder.get_package(f'{schema_context.name}_additional',
                                                                               'schema', module),
                                            context=schema_context, comment=schema_context.description)
                for response_schema in schema_context.response_schemas.values():
                    response_schema_file.blocks.append(
                        ResponseSchema(snake_to_camel(response_schema.name, upper_first=True), response_schema,
                                       schema_context.name))
                response_schema_file.save()
