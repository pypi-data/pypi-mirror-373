# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: make_dirs
@time: 2024/5/30 16:37
@desc:
"""
import os


def make_python_package_dirs(path, project_dir):
    if not os.path.exists(path):
        os.makedirs(path)

    relative_path = os.path.relpath(path, start=project_dir)
    subpaths = relative_path.split(os.sep)
    for i in range(len(subpaths)):
        subpath = os.path.join(project_dir, *subpaths[:i + 1])
        init_file = os.path.join(subpath, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'a').close()


if __name__ == '__main__':
    make_python_package_dirs(path='test', project_dir='test')
    make_python_package_dirs(path='a/b/c/d/e', project_dir='.')
