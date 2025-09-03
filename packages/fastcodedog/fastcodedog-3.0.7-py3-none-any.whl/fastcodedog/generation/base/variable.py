# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.required_import import RequiredImport
from fastcodedog.util.wrap_str_with_quotation import wrap_quotation


class Variable(Block):
    def __init__(self, name: str, context: ContextBase = None, type=None, nullable=True, value=None, comment=None,
                 possible_imports: list | str = None, parent=None):
        """变量类型"""
        super().__init__(name=name, context=context, comment=comment, possible_imports=possible_imports, parent=parent)
        self.type = str(type) if type else None
        self.nullable = nullable
        self.value = value

    def serialize(self, delimiter=', ', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        content = f'{self.name}'
        if self.type:
            content += f': {self.type}'
        value = self.serialize_value(delimiter=delimiter)
        if value:
            content += f' = {value}'
        if self.comment and with_comment:
            content += f'  # {self.comment}'
        return content

    def serialize_value(self, delimiter=', '):
        if self.value:
            if isinstance(self.value, Block):
                # Block类型，可以继续serialize
                return self.value.serialize(delimiter=delimiter)
            if isinstance(self.value, str):
                if self.value[0] == self.value[-1] and self.value[0] in ['\'', '"']:
                    # 已经明确指定是字符串
                    return self.value  # 已经包含引号的字符串
                if self.value[-1] in [')', ']', '}']:
                    # 是类定义，函数，列表，集合，字典等。这个判断不严谨
                    return self.value
                if self.type:
                    type_ = self.type if self.type.find('(') < 0 else self.type[:self.type.find('(')]
                    if type_ in ['str', 'datetime', 'date', 'time', 'constr']:
                        return wrap_quotation(self.value)  # 字符串强制增加引号)
            return str(self.value)
        if self.nullable:
            return str(None)
        return None

    def get_required_imports(self):
        required_import = RequiredImport()
        if isinstance(self.type, Block):
            required_import.update(self.type.get_required_imports())
        if isinstance(self.value, Block):
            required_import.update(self.value.get_required_imports())
        required_import.update(super().get_required_imports())
        return required_import
