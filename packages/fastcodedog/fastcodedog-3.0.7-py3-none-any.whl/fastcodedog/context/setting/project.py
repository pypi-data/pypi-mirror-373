# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Project(ContextBase):
    def __init__(self):
        super().__init__()
        self.name = "fastcodedog"
        self.author = "fastcodedog"
        self.package = "fastcodedog"
        self.directory = r"D:\workspaces\tourhoo\fastcodedog2\test\review"
