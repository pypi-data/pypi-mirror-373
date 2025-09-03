# -*- coding: utf-8 -*-
from fastcodedog.context.schema.response_schema import ResponseSchema as ResponseSchemaContext
from fastcodedog.generation.base.class_type import ClassType
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import, RequiredImport
from fastcodedog.generation.base.variable import Variable
from fastcodedog.util.indent import add_indent

POSSIBLE_IMPORTS = ['from typing import List', 'from typing import Optional']


class ResponseSchema(ClassType):
    class SubObject(Variable):
        def __init__(self, context: ResponseSchemaContext.SubObject):
            super().__init__(context.name, context=context, possible_imports=POSSIBLE_IMPORTS)
            self.is_list = context.is_list
            # 如果没有子对象，就直接使用基类。
            sub_class_name = context.class_type.name if context.class_type.sub_objects else context.class_type.base_class
            self.class_type = ResponseSchema(sub_class_name, context.class_type,
                                             base_class=context.class_type.base_class)

            # 需要计算的属性
            self.type = f'Optional[{self.class_type.name}]' if not self.is_list else f'List[{self.class_type.name}]'
            self.value = '[]' if self.is_list else 'None'

        def serialize_sub_class(self, delimiter='\n', with_comment=True):
            """序列化子类"""
            return self.class_type.serialize(delimiter=delimiter, with_comment=with_comment)

        def serialize(self, delimiter='\n', with_comment=True):
            """序列化子对象"""
            return super().serialize(delimiter=delimiter, with_comment=with_comment)

        def get_required_imports(self) -> RequiredImport:
            # 判断是否import List + 基类的import
            return super().get_required_imports().update(self.class_type.get_required_imports())

    def __init__(self, name, context: ResponseSchemaContext, base_class):
        super().__init__(name, base_class=base_class, context=context,
                         possible_imports=POSSIBLE_IMPORTS)
        self.add_possible_imports([Import(import_=base_class, from_=LocationFinder.get_package(base_class,
                                                                                               'schema',
                                                                                               context.module))])
        for sub_object in context.sub_objects.values():
            self.blocks.append(ResponseSchema.SubObject(sub_object))

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        content = f"""class {self.name}({self.base_class}):{delimiter}""" if self.base_class else f'class {self.name}:{delimiter}'
        body_content = ''
        for block in self.blocks:
            # 先导出子类
            if block.class_type.name != block.class_type.base_class:  # 如果类型和基类名一致，就不能生成新类
                body_content += block.serialize_sub_class(delimiter=delimiter, with_comment=with_comment) + delimiter
        for block in self.blocks:
            # 再导出子对象
            body_content += block.serialize(delimiter=delimiter, with_comment=with_comment) + delimiter
        content += f'{add_indent(body_content, self.DEFAULT_INDENT)}{delimiter}' \
            if body_content else f'{self.DEFAULT_INDENT}...{delimiter}'
        return content
