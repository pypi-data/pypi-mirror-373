# -*- coding: utf-8 -*-
import datetime
import os

from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.block import Block


class HeadComment(Block):
    def __init__(self, comment, parent=None):
        """文件头注释，会自动是被已经生成文件的日期"""
        super().__init__('head_comment', comment=comment, parent=parent)
        from fastcodedog.generation.base.file import File
        if not parent or not isinstance(parent, File):
            raise Exception('The parent of head comment must be File')
        self.author = ctx_instance.project.author
        self.project = ctx_instance.project.name
        self.file = os.path.split(parent.file_path)[1]
        self.time = self._get_create_time()
        self.description = '本文件由自动生成脚本自动创建，请勿修改'
        if comment:
            self.description += '\n' + comment

    def _get_create_time(self):
        """
        从已经存在的文件里提取文件生成日期
        """
        if os.path.exists(self.parent.file_path):
            with open(self.parent.file_path, 'r', encoding='utf-8') as f:
                keywords = '@time: '
                old_file_content = f.read()
                start = old_file_content.find(keywords)
                if start == -1:
                    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                end = old_file_content.find('\n', start + 1)
                if end == -1:
                    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return old_file_content[start + len(keywords):end]
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        return f"""# -*- coding: utf-8 -*-
\"\"\"
@author: {self.author}
@project: {self.project}
@file: {self.file}
@time: {self.time}
@desc: {self.description}
\"\"\""""
