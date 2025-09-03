# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.generation.base.required_import import RequiredImport, Import
from fastcodedog.util.extractor import extract_variables


class Block:
    DEFAULT_INDENT = '    '

    def __init__(self, name: str, context: ContextBase = None, comment=None,
                 possible_imports: list | object | str = None,
                 parent=None):
        """其中possible_imports可以是和Import同结构的对应，Import支持的字符串或者前者的列表"""
        self.name = name
        self.context = context or {}
        self.comment = comment or ''
        self.possible_imports = {}
        self.add_possible_imports(possible_imports)
        self.parent = parent

    def add_possible_imports(self, any_import):
        if not any_import:
            return
        if isinstance(any_import, list):
            for possible_import in any_import:
                self.add_possible_imports(possible_import)
            return
        import_statement = Import(any_import)
        key = import_statement.as_ if import_statement.as_ else import_statement.import_
        self.possible_imports[key] = import_statement

    def get_required_imports(self) -> RequiredImport:
        required_import = RequiredImport()
        content = self.serialize(with_comment=False)
        all_variables = extract_variables(content)
        for varibale, import_ in self.possible_imports.items():
            if varibale in all_variables:
                required_import.add(import_)
        return required_import

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        raise NotImplemented
