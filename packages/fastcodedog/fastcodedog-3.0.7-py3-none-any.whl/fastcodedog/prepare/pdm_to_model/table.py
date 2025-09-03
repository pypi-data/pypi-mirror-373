# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: class
@time: 2024/5/29 10:54
@desc:
"""
from fastcodedog.util.case_converter import camel_to_snake, snake_to_camel
from fastcodedog.util.inflect_wrapper import plural
from .column import Column


class Table:
    """
    数据库表，父类负责数据模型
    """

    class ForeignReference:
        def __init__(self, parent_table, parent_column, child_table, child_column):
            self.parent = parent_table  # Table或者Table的子类
            self.parent_column = parent_column
            self.child = child_table  # Table或者Table的子类
            self.child_column = child_column

        def get_another_foreign_reference_of_child_table(self):
            """
            获取child_table的另一条外键关联，在child_table是join_table的时候有用
            :return:
            """
            if not self.child.is_join_table:  # 是否是关联表
                raise Exception(f'child_table {self.child.code} is not join_table')
            for child_reference in self.child.child_side_references:
                if child_reference.parent != self.parent:
                    return child_reference
            # 从自身到自身的多对多关系，比如，质检定单和普通采样定单之间的多对多关系
            for child_reference in self.child.child_side_references:
                if child_reference.child_column.code != self.child_column.code:
                    return child_reference
            return None

    def __init__(self, node, pdm_file):
        self.node = node
        self.pdm_file = pdm_file

        self.id = ''  # powerdesigner里的id
        self.module = ''  # 归属的module，对应pdm的diagram。根据table.code和module自动归属
        self.name = ''
        self.code = ''
        self.comment = ''
        self.columns = {}
        # # 主键，column.code列表，
        # self.primary_keys = {}  # {'key_1': [column1, column2, column3]}
        # 唯一约束，column.code列表
        self.unique_keys = {}  # {'key_2': [column4, column5, column6]}

        # 外键约束中被作为parent的部分
        self.parent_side_references = []  # [ForeignReference]
        # 外键约束中被作为child的部分
        self.child_side_references = []  # [ForeignReference]
        # 是否是关联表
        self.is_join_table = False
        # 不需要no_back_populates的字段，保存的是column对象
        self.no_back_populates_columns = []
        # 指定了类名
        self.specified_class_name = None

    def to_model(self):
        # 基本数据
        data = {'module': self.module, 'title': self.name, 'name': self.get_model_name(),
                'table_name': self.code, 'is_relationship': self.is_join_table,
                'comment': self.get_smart_comment()}
        # 'comment': self.comment or self.name})
        # 导出列
        for k, v in self.columns.items():
            if 'columns' not in data:
                data['columns'] = {}
            data['columns'][k] = v.to_model()
        # 导出唯一键
        for k, v in self.unique_keys.items():
            if 'unique_constraints' not in data:
                data['unique_constraints'] = []
            data['unique_constraints'].append([_.code for _ in v])
        for k, v in self.columns.items():
            # 导出外键的relationship
            if v.foreign_table:
                if 'relationships' not in data:
                    data['relationships'] = {}
                relationship = self._get_relationship_by_foreign_key(v)
                data['relationships'][relationship['name']] = relationship
        for k, v in self.columns.items():
            # 导出主键被外键引用的relationship
            if v.referenced_keys:
                for vv in v.referenced_keys:
                    if not vv.table.is_join_table:
                        if 'relationships' not in data:
                            data['relationships'] = {}
                        relationship = self._get_relationship_by_referenced_primary_key(v, vv)
                        data['relationships'][relationship['name']] = relationship
        # 关联表对应的relationship
        for reference in self.parent_side_references:
            if reference.child.is_join_table:
                if 'relationships' not in data:
                    data['relationships'] = {}
                relationship = self._get_relationship_by_reference(reference)
                if relationship['name'] in data['relationships']:
                    raise Exception(
                        f'relationship {relationship["name"]} for table {self.code} already exists. You need specified the name')
                data['relationships'][relationship['name']] = relationship
        return data

    def _get_relationship_by_foreign_key(self, foreign_key):
        name = self.get_sub_object_name_by_foreign_key(foreign_key)
        original_name = self.get_original_sub_object_name_by_foreign_key(foreign_key)
        back_populates = self.get_sub_object_name_by_referenced_primary_key(foreign_key.foreign_column, foreign_key)
        back_populates_model = foreign_key.foreign_table.get_model_name()
        back_populates_module = foreign_key.foreign_table.module
        foreign_keys = foreign_key.code
        remote_side = None \
            if not (self.module == back_populates_module and self.get_model_name() == back_populates_model) \
            else foreign_key.foreign_column.code
        return {'name': name, 'original_name': original_name, 'back_populates_module': back_populates_module,
                'back_populates_model': back_populates_model,
                'foreign_keys': foreign_keys, 'remote_side': remote_side, 'back_populates': back_populates,
                'is_list': False}

    def _get_relationship_by_referenced_primary_key(self, primary_key, referenced_key):
        name = self.get_sub_object_name_by_referenced_primary_key(primary_key, referenced_key)
        original_name = self.get_original_sub_object_name_by_referenced_primary_key(primary_key, referenced_key)
        back_populates = self.get_sub_object_name_by_foreign_key(referenced_key)
        back_populates_model = referenced_key.table.get_model_name()
        back_populates_module = referenced_key.table.module
        remote_side = None \
            if not (self.module == back_populates_module and self.get_model_name() == back_populates_model) \
            else referenced_key.code
        # foreign_keys = None \
        #     if not (self.module == back_populates_module and self.get_model_name() == back_populates_model) \
        #     else referenced_key.code
        foreign_keys = None
        if self.module == back_populates_module and self.get_model_name() == back_populates_model:
            # 指向自己的外键关联
            foreign_keys = referenced_key.code
        # 如果有多个外键关联过来关联到同一个表，需要指定外键
        if (not foreign_keys) and len([p_referenced_key for p_referenced_key in primary_key.referenced_keys
                if p_referenced_key.table.code == referenced_key.table.code]) > 1:
            foreign_keys = f'{back_populates_model}.{referenced_key.code}'
        return {'name': name, 'original_name': original_name, 'back_populates_module': back_populates_module,
                'back_populates_model': back_populates_model,
                'foreign_keys': foreign_keys, 'remote_side': remote_side, 'cascade': 'save-update, merge, delete',
                'back_populates': back_populates, 'is_list': True}

    def _get_relationship_by_reference(self, reference):
        another_side_reference = reference.get_another_foreign_reference_of_child_table()
        name = self.get_sub_object_name_by_join_reference(another_side_reference)
        original_name = self.get_original_sub_object_name_by_join_reference(another_side_reference)
        back_populates = self.get_sub_object_name_by_join_reference(reference)
        back_populates_model = another_side_reference.parent.get_model_name()
        back_populates_module = another_side_reference.parent.module
        secondary = reference.child.code
        secondary_object_name = reference.child.get_model_name()  # crud中需要
        primaryjoin = f"{reference.parent.get_model_name()}.{reference.parent_column.code}=={reference.child.code}.c.{reference.child_column.code}"
        secondaryjoin = f"{another_side_reference.parent.get_model_name()}.{another_side_reference.parent_column.code}=={another_side_reference.child.code}.c.{another_side_reference.child_column.code}"

        ret = {'name': name, 'original_name': original_name, 'back_populates_module': back_populates_module,
                'back_populates_model': back_populates_model, 'back_populates': back_populates, 'secondary': secondary,
                'secondary_object_name': secondary_object_name, 'from_join_table': True, 'is_list': True}
        if (reference.child == another_side_reference.child
                and reference.parent == another_side_reference.parent
                and reference.parent_column.code == another_side_reference.parent_column.code):
            # 如果是同一个表的多对多关系
            ret['primaryjoin'] = primaryjoin
            ret['secondaryjoin'] = secondaryjoin
        return ret

    def get_sub_object_name_by_foreign_key(self, foreign_key):
        """根据外键生成子对象名"""
        if foreign_key.specified_relationship_name:
            return foreign_key.specified_relationship_name
        name = foreign_key.code
        if name.endswith('_id'):
            name = name[:-3]
        elif name.endswith('_uid'):
            name = name[:-4]
        else:
            raise Exception(f'foreign key must end with _id or _uid: {foreign_key.code}')
        return name

    def get_original_sub_object_name_by_foreign_key(self, foreign_key):
        """根据外键生成子对象名"""
        if foreign_key.specified_relationship_name:
            return foreign_key.specified_relationship_name
        return foreign_key.code

    def get_sub_object_name_by_referenced_primary_key(self, referenced_primary_key, child_column):
        """根据别外键引用的主表和主键生成子对象名"""
        child_sub_object_name = child_column.table.get_sub_object_name_by_foreign_key(child_column)
        if child_sub_object_name == 'parent':
            return 'children'
        name = plural(camel_to_snake(child_column.table.get_model_name()))
        # 如果有多个外键关联过来关联到同一个表，增加child_column的code作为前缀，避免重名
        if len([referenced_key for referenced_key in referenced_primary_key.referenced_keys
                if referenced_key.table.code == child_column.table.code]) > 1:
            name = self.get_sub_object_name_by_foreign_key(child_column) + '_' + name
        return name

    def get_original_sub_object_name_by_referenced_primary_key(self, referenced_primary_key, child_column):
        """根据别外键引用的主表和主键生成子对象名"""
        child_sub_object_name = child_column.table.get_sub_object_name_by_foreign_key(child_column)
        if child_sub_object_name == 'parent':
            return 'child'
        name = camel_to_snake(child_column.table.get_model_name())
        # 如果有多个外键关联过来关联到同一个表，增加child_column的code作为前缀，避免重名
        if len([referenced_key for referenced_key in referenced_primary_key.referenced_keys
                if referenced_key.table.code == child_column.table.code]) > 1:
            name = self.get_sub_object_name_by_foreign_key(child_column) + '_' + name
        return name

    def get_sub_object_name_by_join_reference(self, reference):
        """根据别外键引用的主表和主键生成子对象名"""
        if reference.child_column.specified_relationship_name:
            return plural(reference.child_column.specified_relationship_name)
        name = reference.child_column.code
        if name.endswith('_id'):
            name = name[:-3]
        elif name.endswith('_uid'):
            name = name[:-4]
        else:
            raise Exception(f'foreign key must end with _id or _uid: {reference.child_column.code}')
        return plural(name)

    def get_original_sub_object_name_by_join_reference(self, reference):
        """获取到未变复数前的sub_object_name"""
        if reference.child_column.specified_relationship_name:
            return reference.child_column.specified_relationship_name
        return reference.child_column.code

    def get_model_name(self):
        if self.specified_class_name:
            return self.specified_class_name
        if self.is_join_table:
            return self.code[len(self.module) + 1:]
        return snake_to_camel(self.code[len(self.module) + 1:], upper_first=True)

    def load(self):
        """
        从pdm中提取表的数据
        xml参考table.xml
        :return:
        """
        self.id = self.node.attrib.get('Id')
        self.name = self.node.find('{attribute}Name').text
        self.code = self.node.find('{attribute}Code').text
        if self.node.find('{attribute}Comment') is not None:
            self.comment = self.node.find('{attribute}Comment').text.strip()
        self.load_all_columns(self.node)
        # 继续找到主键和唯一键约束
        # 通过identity判断主键不准确，因为还有联合主键的情况
        self.get_all_keys()

    def set_join_table(self):
        # 判断是否是join_table
        self.is_join_table = (len(self.child_side_references) == len(self.columns))
        if self.is_join_table:
            # join_table每个字段都是主键
            for column in self.columns.values():
                if not column.primary_key:
                    raise Exception(
                        f'The table is join table, but the column is not primary key: {self.code}.{column.code}')
        else:
            # 非join_table只能有一个主键
            if len([column for column in self.columns.values() if column.primary_key]) != 1:
                raise Exception(
                    f'The table {self.code} should and must have one primary key')

    def load_all_columns(self, node):
        """
        从pdm中提取表的列
        :param node:
        :return:
        """
        children = node.find('{collection}Columns')
        if not children:
            raise Exception(f'Table {self.code} has no columns')
        for child in children:
            if child.tag == '{object}Column' and child.attrib.get('Id') is not None:
                column = Column(self, child)
                column.load()
                self.columns[column.code] = column
                continue
            # self.get_all_columns(child)

    def get_all_keys(self):
        """
        从pdm中提取表的主键和唯一键
        :return:
        """
        children = self.node.find('{collection}Keys')
        if not children:
            return
        for child in children:  # key节点
            if child.tag == '{object}Key' and child.attrib.get('Id') is not None:
                id = child.attrib.get('Id')
                code = child.find('{attribute}Code').text
                columns = []
                if child.find('{collection}Key.Columns'):
                    for column in child.find('{collection}Key.Columns').findall('{object}Column'):
                        columns.append(self.get_column_by_id(column.get('Ref')))
                    if self._is_primary_key(id):
                        # self.primary_keys[code] = columns
                        for column in columns:
                            if column.code not in ['id', 'uid'] and not column.code.endswith(
                                    '_id') and not column.code.endswith('_uid'):
                                raise Exception(
                                    f'The primary key {self.code}.{column.code} must be id or uid, or end with _id or _uid')
                            column.primary_key = True
                    else:
                        self.unique_keys[code] = columns
                        if len(columns) == 1:
                            columns[0].unique = True

    def _is_primary_key(self, id):
        primary_key = self.node.find('{collection}PrimaryKey')
        if primary_key:
            primary_id = primary_key.find('{object}Key').get('Ref')
            if primary_id == id:
                return True
        return False

    def get_column_by_id(self, id):
        """
        通过id查找column，其中id是pdm里的id，<o:Column Id="o88">，<o:Column Ref="o88" />，o88是pdm里的id
        :param id:
        :return:
        """
        for column in self.columns.values():
            if column.id == id:
                return column

    def get_column_by_code(self, code):
        return self.columns.get(code)

    def add_parent_side_reference(self, reference):
        """
        添加外键中被作为parent的部分
        :param reference:
        :return:
        """
        self.parent_side_references.append(reference)

    def add_child_side_reference(self, reference):
        """
        添加外键中被作为child的部分
        :param reference:
        :return:
        """
        self.child_side_references.append(reference)
        reference.child_column.set_foreign_key(reference.parent, reference.parent_column)

    def get_primary_keys(self):
        primary_keys = []
        for column in self.columns.values():
            if column.primary_key:
                primary_keys.append(column.code)
        return primary_keys

    def get_smart_comment(self):
        if not self.comment or self.comment == '':
            return self.name
        if self.comment.find(self.name) >= 0:
            return self.comment

        return f'{self.name}. {self.comment}'
