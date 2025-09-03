# -*- coding: utf-8 -*-
import os

from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.text import Text


class CaseConverter(File):
    def __init__(self):
        super().__init__(name='case_converter',
                         file_path=os.path.join(ctx_instance.project.directory, 'util', 'case_converter.py'),
                         package=f'{ctx_instance.project.package}.util.case_converter')
        self.blocks = [self.get_snake_to_camel(), self.get_camel_to_snake()]

    def get_snake_to_camel(self):
        function = Function('snake_to_camel')
        function.params['string'] = Function.Parameter('string', type='str', nullable=False)
        function.params['upper_first'] = Function.Parameter('upper_first', type='bool', default_value=False)
        content = f"""components = string.split('_')
if upper_first:
    return ''.join(x.title() for x in components)
elif len(components) > 1:
    return components[0] + ''.join(x.title() for x in components[1:])
return string
"""
        function.blocks.append(Text(content))
        return function

    def get_camel_to_snake(self):
        function = Function('camel_to_snake')
        function.params['string'] = Function.Parameter('string', type='str', nullable=False)
        content = f"""snake_str = ''.join('_' + char.lower() if i > 0 and string[i - 1].islower() and char.isupper() else char.lower()
                    for i, char in enumerate(string))
return snake_str.lstrip('_')  # Remove any leading underscore that might have been added
"""
        function.blocks.append(Text(content))
        return function
