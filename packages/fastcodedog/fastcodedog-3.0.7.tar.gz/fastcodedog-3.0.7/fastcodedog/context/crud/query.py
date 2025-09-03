# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.context.crud.column import Column


class Query(ContextBase):
    class Filter(ContextBase):
        def __init__(self):
            super().__init__()
            self.or_ = []
            self._types['or_'] = [str, Query.Filter]
            self.and_ = []
            self._types['and_'] = [str, Query.Filter]

    def __init__(self):
        super().__init__()
        self.name = ''
        self.model = ''
        self.module = ''
        self.select_models = []
        self._types['select_models'] = str
        # self.select_from = ''
        self.summary = ''
        self.description = ''
        self.max_size = None     # 一个请求允许的最大返回值
        self._types['max_size'] = int
        self.parameters = {}
        self._types['parameters'] = Column
        self.filters = []
        self._types['filters'] = [str, Query.Filter]
        self.aliases = {}
        self._types['aliases'] = str
        self.joins = []
        self._types['joins'] = str
        self.outerjoins = []
        self._types['outerjoins'] = str
        self.distinct = ''
        self.orders = []
        self._types['orders'] = str
