import json5
import os

from fastcodedog.util.case_converter import camel_to_snake


def add_specified_class_names(pdm, specified_class_name):
    """添加附加的外键。比如order_id,user_id之类的，如果在powerdesigner图中展示，会导致图太乱"""
    for src, dst in specified_class_name.items():
        table = pdm.tables.get(src)
        table.specified_class_name = dst

# def rename_specified_class_names(model_directory, specified_class_names):
#     for src, dst in specified_class_names.items():
#         module = src.split('.')[0]
#         model_name = src.split('.')[1]
#         json_file = os.path.join(model_directory, module, f'{camel_to_snake(model_name)}.json5')
#         data = json5.load(open(json_file, 'r', encoding='utf-8'))
#         data['name'] = dst
#         for name, relationship in data['relationships'].items():
#             if (relationship['back_populates_module'] == module and
#                     relationship['back_populates_model'] == model_name):
#                 relationship['back_populates_model'] = dst
#             else:
#                 _rename_backpopulates_model(model_directory, dst, relationship)
#         dst_file = os.path.join(model_directory, module, f'{camel_to_snake(dst)}.json5')
#         json5.dump(data, open(dst_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
#         os.remove(json_file)
#
#
# def _rename_backpopulates_model(model_directory, dst, another_side_relationship):
#     json_file = os.path.join(model_directory,
#                              another_side_relationship['back_populates_module'],
#                              f'{camel_to_snake(another_side_relationship["back_populates_model"])}' + '.json5')
#     data = json5.load(open(json_file, 'r', encoding='utf-8'))
#     for name, relationship in data['relationships'].items():
#         if name == another_side_relationship['back_populates']:
#             relationship['back_populates_model'] = dst
#     json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
