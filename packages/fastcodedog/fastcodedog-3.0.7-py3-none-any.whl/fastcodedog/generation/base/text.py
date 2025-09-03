# -*- coding: utf-8 -*-
# from fastcodedog.context.contextbase import ContextBase
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.required_import import RequiredImport
from fastcodedog.util.indent import add_indent


class Text(Block):
    def __init__(self, content, indent=None, possible_imports: list | str = None, parent=None):
        """纯文本类型"""
        super().__init__(name='__content__', possible_imports=possible_imports, parent=parent)
        self.content = content
        self.indent = indent

    def serialize(self, delimiter='\n', with_comment=True):
        """目前delimiter, with_comment都不支持"""
        return add_indent(self.content, self.indent)

    def get_required_imports(self) -> RequiredImport:
        if not self.possible_imports:
            return RequiredImport()
        return super().get_required_imports()
