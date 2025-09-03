# -*- coding: utf-8 -*-
from fastcodedog.common.write_file import write_python_file
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.head_comment import HeadComment
from fastcodedog.generation.base.required_import import RequiredImport


class File(Block):
    def __init__(self, name: str, file_path: str, package: str, blocks: list = None, context: dict = None, comment=None,
                 parent=None):
        super().__init__(name=name, context=context, comment=comment, parent=parent)
        self.file_path = file_path
        self.package = package
        self.blocks = blocks or []
        self.head_comment = HeadComment(comment=comment, parent=self)  # 文件头注释
        self.required_import = RequiredImport()  # 必须导入的包

    def get_required_imports(self):
        """会被File.serialize()调用，本方法里不能调用File.serialize()，因为可能会有循环依赖"""
        required_import = RequiredImport()
        [required_import.update(block.get_required_imports()) for block in self.blocks]
        return required_import

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。这里调用File.get_required_imports()，必须改写File.get_required_imports，避免循环依赖"""
        content = self.head_comment.serialize() + delimiter
        required_import = self.get_required_imports()
        content += required_import.serialize() + delimiter
        for block in self.blocks:
            content += block.serialize() + delimiter
        return content

    def save(self):
        write_python_file(self.file_path, self.serialize())
