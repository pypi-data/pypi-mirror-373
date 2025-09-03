# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.model.base import Base
from fastcodedog.generation.model.init import Init
from fastcodedog.generation.model.model import Model
from fastcodedog.generation.model.relation_object import RelationObject


def generate_model(models: list = None):
    base = Base()
    base.save()
    init = Init()
    init.save()
    for module, models in ctx_instance.models.items():
        for model_context in models.values():
            if models:
                if model_context.name not in models:
                    continue
            if model_context.is_relationship:
                relation_object_file = File(model_context.name,
                                            file_path=LocationFinder.get_path(model_context.name, 'model', module),
                                            package=LocationFinder.get_package(model_context.name, 'model', module),
                                            blocks=[RelationObject(model_context)],
                                            context=model_context, comment=model_context.comment)
                relation_object_file.save()
            else:
                model_file = File(model_context.name,
                                  file_path=LocationFinder.get_path(model_context.name, 'model', module),
                                  package=LocationFinder.get_package(model_context.name, 'model', module),
                                  blocks=[Model(model_context)],
                                  context=model_context, comment=model_context.comment)
                model_file.save()
