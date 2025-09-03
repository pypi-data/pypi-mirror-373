# -*- coding: utf-8 -*-
def rename_specified_column_types(pdm, specified_column_types):
    for table in pdm.tables.values():
        for column in table.columns.values():
            if f'{table.code}.{column.code}' in specified_column_types:
                column.type = specified_column_types[f'{table.code}.{column.code}']
            elif column.code in specified_column_types:
                column.data_type = specified_column_types[f'{column.code}']
