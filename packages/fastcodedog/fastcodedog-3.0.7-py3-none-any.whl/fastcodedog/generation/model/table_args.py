# -*- coding: utf-8 -*-
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.required_import import RequiredImport
from fastcodedog.util.wrap_str_with_quotation import wrap_quotation


class TableArgs(Block):
    def __init__(self, unique_constraints=[], commit=None):
        super().__init__('__table_args__', {})
        self.unique_constraints = unique_constraints
        self.commit = commit

        self.add_possible_imports('from sqlalchemy import UniqueConstraint')

    def get_required_imports(self):
        required_import = RequiredImport()
        if self.unique_constraints:
            required_import.add(self.possible_imports['UniqueConstraint'])
        return required_import

    def serialize(self):
        """有点不一样的是，参数最后的逗号,"""
        inner_content = ''
        if self.unique_constraints:
            for constraint in self.unique_constraints:
                inner_content += f'UniqueConstraint({", ".join(constraint)}),'
        if self.commit:
            inner_content += f"{{'comment': {wrap_quotation(self.commit)}}},"

        if inner_content:
            return f'__table_args__ = ({inner_content})'
        return ''
