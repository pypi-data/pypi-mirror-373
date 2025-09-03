# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.call import Call
from fastcodedog.generation.base.required_import import RequiredImport
from fastcodedog.generation.base.variable import Variable
from fastcodedog.util.indent import add_indent


class Function(Block):
    class Parameter(Variable):
        def __init__(self, name: str, context: ContextBase = None, type=None, nullable=True,
                     option_none=False, default_value=None, comment=None,
                     valid_values: list | str = None,
                     possible_imports: list | str = None, parent=None):
            #  用value字段代表默认值
            super().__init__(name=name, context=context, type=type, nullable=nullable, value=default_value,
                             comment=comment,
                             possible_imports=possible_imports, parent=parent)
            self.valid_values = valid_values
            self.option_none = option_none

    class Decorator(Call):
        def serialize(self, delimiter=', ', with_comment=False):
            if not self.params:
                return f'@{self.name}'
            return f'@{super().serialize(delimiter=delimiter, with_comment=with_comment)}'

    def __init__(self, name: str, context: ContextBase = None, decorators=None, params=None, return_type=None,
                 blocks=None, comment=None, async_=False, possible_imports: list | str = None,
                 parent=None):
        """函数类型，包含装饰器和方法内容，是否异步"""
        super().__init__(name=name, context=context, comment=comment, possible_imports=possible_imports, parent=parent)
        self.decorators = [] if not decorators else decorators
        self.params = {} if not params else params
        self.return_type = return_type
        self.blocks = [] if not blocks else blocks
        self.async_ = async_

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        content = ''
        for decorator in self.decorators:
            content += f'{decorator.serialize()}{delimiter}'
        # 重新排序参数，没有默认值的要放到前面
        params = []
        [params.append(param) for param in self.params.values() if not param.serialize_value()]
        [params.append(param) for param in self.params.values() if param.serialize_value()]
        if self.async_:
            content += 'async '
        content += f'def {self.name}({", ".join([param.serialize(with_comment=False) for param in params])})'
        if self.return_type:
            content += f' -> {self.return_type}'
        content += f':{delimiter}'
        content += '' if not self.comment else add_indent(f'"""{self.comment}"""{delimiter}', self.DEFAULT_INDENT)
        body_content = ''
        for block in self.blocks:
            body_content += f'{block.serialize(delimiter=delimiter, with_comment=with_comment)}{delimiter}'
        content += add_indent(body_content, self.DEFAULT_INDENT) if body_content else f'{self.DEFAULT_INDENT}...'
        return content

    def get_required_imports(self):
        required_import = RequiredImport()
        for decorator in self.decorators:
            required_import.update(decorator.get_required_imports())
        for param in self.params.values():
            required_import.update(param.get_required_imports())
        for block in self.blocks:
            required_import.update(block.get_required_imports())
        required_import.update(super().get_required_imports())
        return required_import
