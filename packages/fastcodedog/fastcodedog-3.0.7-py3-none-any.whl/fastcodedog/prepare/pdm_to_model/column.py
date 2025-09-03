# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: attribute
@time: 2024/5/29 10:55
@desc:
"""
from fastcodedog.util.type_converter import database_type_to_python_type, database_type_to_sqlalchemy_type


class Column:
    """
    列，父类负责数据模型
    """

    def __init__(self, table, node):
        self.table = table
        self.node = node

        self.id = ''  # powerdesigner里的id
        self.name = ''
        self.code = ''
        self.comment = ''
        self.data_type = ''
        self.length = None
        self.nullable = True
        self.identity = False  # 生成：sqlalchemyIdentity(start=42, cycle=True)等之类
        self.domain = None     # 字段在powerdesigner的domain，逐步支持pydantic的类型和校验

        # pdm不支持的扩展属性
        self.specified_relationship_name = None  # 定义子对象的时候，指定的子对象名字。外键默认是code去除id或者uid，主键默认是使用表名

        # 需要从全局查找并填充
        self.primary_key = False
        self.unique = False
        self.foreign_table = None  # 外键对应的表
        self.foreign_column = None  # 外键对应的列
        self.referenced_keys = []  # 做主键时，被其他表的外检引用的清单 [column]

    def to_model(self):
        return {
            'title': self.name,
            'name': self.code,
            'specified_relationship_name': self.specified_relationship_name,
            'comment': self.get_smart_comment(),
            # 'comment': self.comment or self.name,
            'sqlalchemy_type': database_type_to_sqlalchemy_type(self.data_type, self.length)[0],
            # python的类型不足，还需要保存sqlalchemy的type
            'sqlalchemy_type_with_length': database_type_to_sqlalchemy_type(self.data_type, self.length)[1],
            # python的类型不足，还需要保存sqlalchemy的type
            'type': database_type_to_python_type(self.data_type),
            'length': self.length,
            'nullable': self.nullable,
            'primary_key': self.primary_key,
            'unique': self.unique,
            'domain': self.domain,      # 字段对应的域
            # 主键一律自增。
            'autoincrement': self.primary_key and self.data_type.startswith('int') and not self.foreign_table,
            'foreign_key': f'{self.foreign_table.code}.{self.foreign_column.code}' if self.foreign_table else None
        }

    def load(self):
        """
        从pdm中提取列的数据
        xml参考table.xml中<c:Columns>的部分
        :return:
        """
        self.id = self.node.attrib.get('Id')
        for child in self.node:
            if child.tag == '{attribute}Name':
                self.name = child.text
            if child.tag == '{attribute}Code':
                self.code = child.text
            if child.tag == '{attribute}Comment':
                self.comment = child.text.strip()
            if child.tag == '{attribute}DataType':
                self.data_type = child.text
            if child.tag == '{attribute}Length':
                self.length = int(child.text)
            if child.tag == '{attribute}Column.Mandatory' and child.text == '1':
                self.nullable = False
            if child.tag == '{collection}Domain':
                domain_id = child.find('{object}PhysicalDomain').attrib.get('Ref')
                self.domain = self.table.pdm_file.domains.get(domain_id)

    def set_foreign_key(self, foreign_table, foreign_column):
        """
        设置外键.
        :param foreign_table:
        :param foreign_column:
        :return:
        """
        self.foreign_table = foreign_table
        self.foreign_column = foreign_column
        foreign_column.referenced_keys.append(self)

    def get_smart_comment(self):
        if not self.comment or self.comment == '':
            return self.name
        if self.comment.find(self.name) >= 0:
            return self.comment

        return f'{self.name}. {self.comment}'
