# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.text import Text
from fastcodedog.util.case_converter import camel_to_snake


class SelectinLoad(Function):
    def __init__(self, context):
        super().__init__(f'fill_{camel_to_snake(context.name)}_selectinload', context=context,
                         comment='根据需要返回的数据类型调整加载策略，减少数据库查询的次数')
        self.params['query'] = Function.Parameter('query', context=context, nullable=False)
        self.params['response_model_name'] = Function.Parameter('response_model_name', context=context, type='str',
                                                                nullable=False)
        self._fill_blocks_and_possible_imports()
        self.add_possible_imports('from sqlalchemy.orm import selectinload')

    def _fill_blocks_and_possible_imports(self):
        schema = ctx_instance.schemas[self.context.module][self.context.name]
        for schema_name, response_schema in schema.response_schemas.items():
            self.blocks.append(Text(f"if response_model_name == '{schema_name}':"))
            for nested_objects in self._get_nested_objects_and_fill_possible_imports(response_schema):
                selectinloads = [f'selectinload({nested_object})' for nested_object in nested_objects]
                self.blocks.append(Text(f"query = query.options({'.'.join(selectinloads)})",
                                        indent=self.DEFAULT_INDENT))
        self.blocks.append(Text('return query'))

    def _get_nested_objects_and_fill_possible_imports(self, class_type):
        nested_objects = []
        for name, sub_object in class_type.sub_objects.items():
            self.add_possible_imports(Import(class_type.base_class,
                                             from_=LocationFinder.get_package(class_type.base_class, 'model',
                                                                              class_type.module)))
            nested_object = f'{class_type.base_class}.{name}'
            sub_nested_objects = self._get_nested_objects_and_fill_possible_imports(sub_object.class_type)
            if sub_nested_objects:
                for s in sub_nested_objects:
                    nested_objects.append([nested_object] + s)
            else:
                nested_objects.append([nested_object])
        return nested_objects

    def serialize(self, delimiter='\n', with_comment=True):
        schema = ctx_instance.schemas[self.context.module][self.context.name]
        if not schema.response_schemas:
            return ''
        return super().serialize(delimiter=delimiter, with_comment=with_comment)
