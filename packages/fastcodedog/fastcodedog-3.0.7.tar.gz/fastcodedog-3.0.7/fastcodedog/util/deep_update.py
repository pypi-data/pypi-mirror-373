# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: deep_update
@time: 2024/5/29 13:44
@desc:
"""
import copy


def deep_update(*dicts):
    result = {}
    for d in dicts:
        for key, value in d.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_update(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    for i in value:
                        if i not in result[key]:
                            result[key].append(i)
                else:
                    result[key] = copy.deepcopy(value)
            else:
                result[key] = copy.deepcopy(value)
    return result


if __name__ == '__main__':
    d1 = {'a': 1, 'b': {'bb': 2, 'cc': ['3']}, 'c': ['4', 5, 6]}
    d2 = {'a': 3, 'b': {'cc': ['4']}, 'c': ['7', 8, 9]}
    d3 = {'a': 5, 'b': {'ee': 6}}
    print(deep_update(d1, d2))
    print(deep_update(d1, d2, d3))
