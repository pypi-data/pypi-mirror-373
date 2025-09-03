# -*- coding: utf-8 -*-
import json5

from fastcodedog.common.source_file_path import get_crud_file_path


def add_queries(crud_directory, queries):
    for query in queries:
        module = query['module']
        model = query['model']
        json_file = get_crud_file_path(module, model)
        data = json5.load(open(json_file, 'r', encoding='utf-8'))
        if 'queries' not in data:
            data['queries'] = {}
        data['queries'][query['name']] = query
        # _refill_order_by(data['queries'][query['name']])
        # order_by要改写
        json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)


# def _refill_order_by(query):
#     if 'orders' in query:
#         orders = []
#         for order in query['orders']:
#             orders.append(order)
#             if '.desc()' not in order and '.asc()' not in order and ',' not in order:  # 没有指定只能顺序排或者倒序排
#                 orders.append(f'{order}.desc()')
#         query['orders'] = orders
