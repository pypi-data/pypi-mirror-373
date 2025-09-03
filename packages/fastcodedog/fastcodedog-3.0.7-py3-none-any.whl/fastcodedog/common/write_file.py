# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: write_file
@time: 2024/5/30 15:39
@desc:
"""
import json5
import os
import subprocess

from fastcodedog.context.context import ctx_instance


def write_python_file(path, content):
    """
    写入python文件
    :param path:
    :param content:
    :return:
    """
    _make_pathon_package(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    # 调用autopep8格式化文件
    # subprocess.run(['autopep8', '--in-place', '--aggressive', '--max-line-length=120', path], check=True)
    subprocess.run(['autopep8', '--in-place', '--max-line-length=120', path], check=True)
    # 临时版本，把异步支持去掉,把文件中的 `async def` 替换为 `def`
    with open(path, 'r+', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('async def ', 'def ')
        f.seek(0)
        f.write(content)
        f.truncate()
    print(f'writed {path}')  # 先临时放这里，后续再改
    # # 调用flake8格式化文件
    # subprocess.run(['flake8', path], check=True)


def _make_pathon_package(directory):
    if not os.path.exists(directory):
        parent_directory = os.path.dirname(directory)
        _make_pathon_package(parent_directory)
        os.makedirs(directory)
        if directory.startswith(ctx_instance.project.directory):
            init_file = os.path.join(directory, '__init__.py')
            open(init_file, 'a').close()


def write_json_file(path, data):
    """
    写入json文件
    :param path:
    :param data:
    :return:
    """
    directory = os.path.dirname(path)
    if os.path.exists(directory) is False:
        os.makedirs(directory)
    with open(path, 'w', encoding='utf-8') as f:
        json5.dump(data, f, ensure_ascii=False, indent=4)
