# -*- coding: utf-8 -*-
"""
换行
"""
from fastcodedog.generation.base.block import Block


class LineBreak(Block):
    def __init__(self):
        """换行"""
        super().__init__('__line_break__')

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        return delimiter
