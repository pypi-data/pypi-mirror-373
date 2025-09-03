# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Config(ContextBase):
    class Database(ContextBase):
        def __init__(self):
            super().__init__()
            self.url = 'sqlite:///fastcodedog.db'

    class Logging(ContextBase):
        def __init__(self):
            super().__init__()
            self.filename = 'fastcodedog.log'
            self.level = 'INFO'
            self.encoding = 'utf-8'
            self.datefmt = '%Y-%m-%d %H:%M:%S'
            self.format = '%(asctime)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d'
            self.max_bytes = 50 * 1024 * 1024
            self.backup_count = 10
            self.console = True

    def __init__(self):
        super().__init__()
        self.database = Config.Database()
        self.logging = Config.Logging()
        self.user_configs = {}
        self._types['user_configs'] = dict
