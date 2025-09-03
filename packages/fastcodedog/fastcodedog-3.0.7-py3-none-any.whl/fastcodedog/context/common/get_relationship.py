# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance


def get_class_type_by_model_and_relationship_name(model_name, relationship_name, module=None):
    """
    根据模型名和关系名获取类名
    :param model_name:
    :param relationship_name:
    :param module:
    :return: class_name, module, is list(bool)。
    """
    for c_module, models in ctx_instance.models.items():
        if module and module != c_module:
            continue
        if model_name not in models:
            continue
        model = models[model_name]
        if not relationship_name in model.relationships:
            raise ValueError(f'relationship {relationship_name} not in model {model_name}')
        relationship = model.relationships[relationship_name]
        if relationship.disabled:
            raise ValueError(f'relationship {relationship_name} disabled')
        return relationship.back_populates_module, relationship.back_populates_model, relationship.is_list

    raise ValueError(f'model {model_name} not found')
