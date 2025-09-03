# -*- coding: utf-8 -*-
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.required_import import RequiredImport


class Call(Block):
    def __init__(self, name: str, params: list = None, brackets='()', comment=None, possible_imports: list | str = None,
                 parent=None):
        """call类型，适用于方法调用，方法装饰器之类。brackets，取值(),[],{}之一"""
        super().__init__(name, comment=comment, possible_imports=possible_imports, parent=parent)
        self.params = params or []  # call里面的参数是可以重复的，所以，这里需要列表
        if brackets not in ['()', '[]', '{}']:
            raise ValueError(f'brackets {brackets} must in (), [], {{}}')
        self.left_bracket = brackets[0]
        self.right_bracket = brackets[1]

    def serialize(self, delimiter=', ', with_comment=True):
        params = [str(param) if not isinstance(param, Block) else param.serialize() for param in self.params]
        return f'{self.name}{self.left_bracket}{delimiter.join(params)}{self.right_bracket}'

    def get_required_imports(self):
        required_import = RequiredImport()
        for param in self.params:
            if isinstance(param, Block):
                required_import.update(param.get_required_imports())
        required_import.update(super().get_required_imports())
        return required_import
