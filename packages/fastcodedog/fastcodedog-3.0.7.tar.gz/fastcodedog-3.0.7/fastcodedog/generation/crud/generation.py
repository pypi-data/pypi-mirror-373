# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.crud.crud import get_blocks


def generate_crud(specify_schema=None):
    for module, cruds in ctx_instance.cruds.items():
        for crud_context in cruds.values():
            if specify_schema and crud_context.name not in specify_schema:
                continue
            crud_file = File(crud_context.name,
                             file_path=LocationFinder.get_path(crud_context.name, 'crud', module),
                             package=LocationFinder.get_package(crud_context.name, 'crud', module),
                             blocks=get_blocks(crud_context),
                             context=crud_context, comment=crud_context.comment)
            crud_file.save()
