# -*- coding: utf-8 -*-
def add_specified_relationship_names(pdm, specified_relationship_names):
    for column_name, name in specified_relationship_names.items():
        table_code, column_code = column_name.split('.')
        column = pdm.tables.get(table_code).columns.get(column_code)
        column.specified_relationship_name = name
