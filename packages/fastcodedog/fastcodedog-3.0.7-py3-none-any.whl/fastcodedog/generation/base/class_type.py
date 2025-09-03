# -*- coding: utf-8 -*-
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.required_import import RequiredImport
from fastcodedog.util.indent import add_indent


class ClassType(Block):
    def __init__(self, name: str, base_class: str = None, blocks: list = None, context: dict = None, comment=None,
                 possible_imports: list | str = None, parent=None):
        """类。"""
        super().__init__(name=name, context=context, comment=comment, possible_imports=possible_imports, parent=parent)
        self.base_class = base_class
        self.blocks = blocks or []

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        content = f"""class {self.name}({self.base_class}):{delimiter}""" if self.base_class else f'class {self.name}:{delimiter}'
        body_content = ''
        for block in self.blocks:
            block_content = block.serialize()
            if block_content:
                body_content += block_content + delimiter
        content += add_indent(body_content, self.DEFAULT_INDENT) \
            if body_content else f'{self.DEFAULT_INDENT}...{delimiter}'
        return content

    def get_required_imports(self):
        required_import = RequiredImport()
        if self.base_class in self.possible_imports:
            required_import.add(self.possible_imports[self.base_class])
        for block in self.blocks:
            required_import.update(block.get_required_imports())
        return required_import
