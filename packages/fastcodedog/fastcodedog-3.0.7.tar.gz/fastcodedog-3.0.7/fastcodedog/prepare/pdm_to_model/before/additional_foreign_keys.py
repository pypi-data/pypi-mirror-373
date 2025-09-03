# -*- coding: utf-8 -*-
def fill_additional_foreign_keys(pdm, additional_foreign_keys):
    """添加附加的外键。比如order_id,user_id之类的，如果在powerdesigner图中展示，会导致图太乱"""
    for referenced_key, foreign_keys in additional_foreign_keys.items():
        table_code, column_code = referenced_key.split('.')
        foreign_table = pdm.tables.get(table_code)
        foreign_column = foreign_table.columns.get(column_code)
        for table in pdm.tables.values():
            for column in table.columns.values():
                if f'{table.code}.{column.code}' in foreign_keys or column.code in foreign_keys:
                    if not column.foreign_table:
                        column.set_foreign_key(foreign_table, foreign_column)
