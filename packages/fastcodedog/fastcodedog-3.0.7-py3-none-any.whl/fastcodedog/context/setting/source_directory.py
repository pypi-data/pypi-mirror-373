# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class SourceDirectory(ContextBase):
    def __init__(self):
        super().__init__()
        self.pdm_file = 'fastcodedog.pdm'
        self.pre_process_scripts_file = r'prepare/*/*.json5'
        self.model = 'build/model'
        self.schema = 'build/schema'
        self.crud = 'build/crud'
        self.api = 'build/api'
