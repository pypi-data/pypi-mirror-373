# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: string_case
@time: 2024/5/28 17:12
@desc:
"""


def snake_to_camel(string: str, upper_first: bool = False) -> str:
    components = string.split('_')
    if upper_first:
        return ''.join(x.title() for x in components)
    elif len(components) > 1:
        return components[0] + ''.join(x.title() for x in components[1:])
    return string


def camel_to_snake(str):
    snake_str = ''.join('_' + char.lower() if i > 0 and str[i - 1].islower() and char.isupper() else char.lower()
                        for i, char in enumerate(str))
    return snake_str  # Remove any leading underscore that might have been added


if __name__ == '__main__':
    print(snake_to_camel(''))
    print(snake_to_camel('hello', True))
    print(snake_to_camel('hello_world'))
    print(camel_to_snake('HelloWorld'))
    print(camel_to_snake('userID'))
    print(camel_to_snake(''))
