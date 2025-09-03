# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

from fastcodedog.common.source_file_path import get_model_file_path
from fastcodedog.common.write_file import write_json_file
from fastcodedog.prepare.pdm_to_model.table import Table
from fastcodedog.util.valid_name import is_valid_name


class Pdm:
    def __init__(self, pdm_file):
        self.pdm_file = pdm_file

        # 从pdm装载出的数据
        self.domains = {}
        self.modules = {}
        self.tables = {}

        self._init()

    def _init(self):
        tree = ET.parse(self.pdm_file)
        root = tree.getroot()
        self._load_all_domains(root)
        self._load_all_modules(root)
        self._load_all_tables(root)
        # 填充外键
        self._fill_foreign_keys(root)
        # 判断是否是join表
        for table in self.tables.values():
            table.set_join_table()

    def to_model(self):
        for table in self.tables.values():
            json_file = get_model_file_path(table.module, table.get_model_name())
            write_json_file(json_file, table.to_model())

    def _load_all_domains(self, node):
        for child in node:
            if child.tag == '{object}PhysicalDomain' and child.attrib.get('Id') is not None:
                id = child.attrib.get('Id')
                code = child.find('{attribute}Code').text
                # if not is_valid_name(code):
                #     raise Exception(f'The domain code is not valid: {code}')
                self.domains[id] = code.upper()
                continue
            self._load_all_domains(child)

    def _load_all_modules(self, node):
        for child in node:
            if child.tag == '{object}PhysicalDiagram' and child.attrib.get('Id') is not None:
                name = child.find('{attribute}Name').text
                code = child.find('{attribute}Code').text
                if not is_valid_name(code):
                    raise Exception(f'The module code is not valid: {code}')
                self.modules[code] = name
                continue
            self._load_all_modules(child)

    def _load_all_tables(self, node):
        for child in node:
            if child.tag == '{object}Table' and child.attrib.get('Id') is not None:
                table = Table(child, self)
                table.load()
                module = self._get_table_module(table.code)
                # if not module:
                #     continue
                table.module = module
                self.tables[table.code] = table
                continue
            self._load_all_tables(child)

    def _fill_foreign_keys(self, node):
        """
        填充外键.xml参考reference.xml
        :param node:
        :return:
        """
        for child in node:
            if child.tag == '{object}Reference' and child.find('{collection}ParentTable'):
                # parent_table
                parent_table_id = child.find('{collection}ParentTable').find('{object}Table').get('Ref')
                # child_table
                child_table_id = child.find('{collection}ChildTable').find('{object}Table').get('Ref')
                # parent_table.column
                parent_column_id = child.find('{collection}Joins').find('{object}ReferenceJoin').find(
                    '{collection}Object1').find('{object}Column').get('Ref')
                # child_table.column
                child_column_id = child.find('{collection}Joins').find('{object}ReferenceJoin').find(
                    '{collection}Object2').find('{object}Column').get('Ref')
                # 回填
                parent_table = self._get_table_by_id(parent_table_id)
                child_table = self._get_table_by_id(child_table_id)
                if f'{child_table.code}' == 'sampling_point':
                    ...
                if not parent_table or not child_table:
                    continue
                parent_column = parent_table.get_column_by_id(parent_column_id)
                child_column = child_table.get_column_by_id(child_column_id)
                child_column.foreign_table = parent_table
                child_column.foreign_column = parent_column
                reference = Table.ForeignReference(parent_table, parent_column, child_table, child_column)
                parent_table.add_parent_side_reference(reference)
                child_table.add_child_side_reference(reference)
            self._fill_foreign_keys(child)

    def _get_table_module(self, table_code):
        module = None
        for m in self.modules.keys():
            if table_code.startswith(m):
                if module and len(module) > len(m):
                    continue
                module = m
        return module

    def _get_table_by_id(self, id):
        """
        根据pdm文件中的id获取表
        id通常是如下两个形式<o:Table Ref="o29"/>，<o:Table Id="o29">其中o29是表的id
        :param id:
        :return:
        """
        for t in self.tables.values():
            if t.id == id:
                return t
        return None
