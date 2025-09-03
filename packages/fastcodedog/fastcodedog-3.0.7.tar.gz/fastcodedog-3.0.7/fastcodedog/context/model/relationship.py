# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Relationship(ContextBase):
    def __init__(self):
        super().__init__()
        self.name = ''  # 关系名
        self.original_name = ''  # 原始关系名，为转为复数。有时候需要非复数原始版本
        self.back_populates_module = ''  # back_populates的模块
        self.back_populates_model = ''  # back_populates的model
        self.foreign_keys = ''  # 关联使用的外键
        self.remote_side = ''
        self.secondary = ''  # 多对多关联时的关系表名
        self.secondary_object_name = ''  # 多对多关联时的secondary_object_name
        self.cascade = ''
        self.back_populates = ''  # back_populates变量名
        self.no_back_populates = False  # 不生成back_populates
        self.disabled = False  # 禁用。和上面的no_backup是一对
        self.from_join_table = False  # 是否是join_table
        self.is_list = False  # 是否是列表
        self.primaryjoin = ''  # 主连接条件
        self.secondaryjoin = ''  # 次连接条件
