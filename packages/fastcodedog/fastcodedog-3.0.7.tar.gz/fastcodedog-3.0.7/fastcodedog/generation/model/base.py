# -*- coding: utf-8 -*-
import os

from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.variable import Variable


class Base(File):
    def __init__(self):
        super().__init__('base',
                         file_path=os.path.join(ctx_instance.project.directory, 'model', 'base.py'),
                         package=f'{ctx_instance.project.package}.model.base',
                         context={}, comment='基类。一个工程内应该只有一个Base基类')
        self.base = Variable('Base', value='declarative_base()',
                             possible_imports='from sqlalchemy.orm import declarative_base')

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        content = self.head_comment.serialize() + delimiter
        content += self.base.get_required_imports().serialize() + delimiter
        content += self.base.serialize() + delimiter
        return content
