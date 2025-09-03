# -*- coding: utf-8 -*-
"""
各种需要生成的文件的路径，类等的获取
"""
import os

from fastcodedog.context.context import ctx_instance
from fastcodedog.util.case_converter import camel_to_snake


class LocationFinder:
    """计算各个类对应的package，这个类用起来有点啰嗦。"""
    class Location:
        def __init__(self, path, package):
            self.path = path
            self.package = package

    @staticmethod
    def get(name, *packages):
        if len(packages) == 0 and name in LocationFinder.get_common_locations():
            return LocationFinder.get_common_locations()[name]
        return LocationFinder.Location(
            path=os.path.join(ctx_instance.project.directory, *packages, camel_to_snake(name) + '.py'),
            package=f'{ctx_instance.project.package}.{".".join(packages)}.{camel_to_snake(name)}')

    @staticmethod
    def get_path(name, *packages):
        if len(packages) == 0 and name in LocationFinder.get_common_locations():
            return LocationFinder.get_common_locations()[name].path
        return os.path.join(ctx_instance.project.directory, *packages, camel_to_snake(name) + '.py')

    @staticmethod
    def get_package(name, *packages):
        if len(packages) == 0 and name in LocationFinder.get_common_locations():
            return LocationFinder.get_common_locations()[name].package
        if len(packages) == 0:
            return f'{ctx_instance.project.package}.{camel_to_snake(name)}'
        return f'{ctx_instance.project.package}.{".".join(packages)}.{camel_to_snake(name)}'

    # noinspection PyArgumentList
    @staticmethod
    def get_common_locations():
        return {
            'snake_to_camel': LocationFinder.Location(
                path=os.path.join(ctx_instance.project.directory, 'util', 'case_converter.py'),
                package=f'{ctx_instance.project.package}.util.case_converter'),
            'camel_to_snake': LocationFinder.Location(
                path=os.path.join(ctx_instance.project.directory, 'util', 'case_converter.py'),
                package=f'{ctx_instance.project.package}.util.case_converter'),
            'get_session': LocationFinder.Location(path=os.path.join(ctx_instance.project.directory, 'db.py'),
                                                   package=f'{ctx_instance.project.package}.db'),
            '__name__': LocationFinder.Location(path=os.path.join(ctx_instance.project.directory, 'name.py'),
                                                package=f'{ctx_instance.project.package}.name'),
            'port': LocationFinder.Location(path=os.path.join(ctx_instance.project.directory, 'config', 'config.py'),
                                            package=f'{ctx_instance.project.package}.config.config'),
            'db_url': LocationFinder.Location(path=os.path.join(ctx_instance.project.directory, 'config', 'config.py'),
                                              package=f'{ctx_instance.project.package}.config.config'),
            'Base': LocationFinder.Location(path=os.path.join(ctx_instance.project.directory, 'model', 'base.py'),
                                            package=f'{ctx_instance.project.package}.model.base')
        }
