# -*- coding: utf-8 -*-
from fastcodedog.context.model.relationship import Relationship as RelationshipContext
from fastcodedog.generation.base.call import Call
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.variable import Variable


class Relationship(Variable):
    def __init__(self, context: RelationshipContext = None, parent=None):
        super().__init__(context.name, context=context, parent=parent)
        self.back_populates_module = context.back_populates_module  # back_populates的模块
        self.back_populates_model = context.back_populates_model  # back_populates的model
        self.foreign_keys = context.foreign_keys  # 关联使用的外键
        self.remote_side = context.remote_side
        self.secondary = context.secondary  # 多对多关联时的关系表名
        self.cascade = context.cascade
        self.back_populates = context.back_populates  # back_populates变量名
        self.no_back_populates = context.no_back_populates  # 不生成back_populates
        # self.disabled = context.disabled                      # 禁用的时候，直接不创建relationship
        self.primaryjoin = context.primaryjoin  # 主连接条件
        self.secondaryjoin = context.secondaryjoin

        self.value = self.get_value()
        self.comment = f"no back populates {self.back_populates}" if self.no_back_populates else ''
        # self.possible_imports = {
        #     'relationship': Import('sqlalchemy.orm', 'relationship')
        # }
        self.add_possible_imports([
            Import('from sqlalchemy.orm import relationship'),
        ])

    def get_value(self):
        relationship_params = [f"'{self.back_populates_model}'"]
        if self.foreign_keys:
            relationship_params.append(f"foreign_keys={self.foreign_keys}" if self.foreign_keys.find('.') == -1 else f"foreign_keys='{self.foreign_keys}'")
        if self.secondary:
            relationship_params.append(f"secondary='{self.secondary}'")
        if self.remote_side:
            relationship_params.append(f"remote_side={self.remote_side}")
        if self.primaryjoin:
            relationship_params.append(f"primaryjoin='{self.primaryjoin}'")
        if self.secondaryjoin:
            relationship_params.append(f"secondaryjoin='{self.secondaryjoin}'")
        if self.cascade:
            relationship_params.append(f"cascade='{self.cascade}'")
        if self.back_populates and not self.no_back_populates:
            relationship_params.append(f"back_populates='{self.back_populates}'")
        return Call('relationship', params=relationship_params)
