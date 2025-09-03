# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: find_file
@time: 2024/5/30 21:23
@desc:
"""
import glob
import os


def find(directory, pattern):
    pattern = pattern.replace('/', os.path.sep).replace('\\', os.path.sep)
    return [os.path.join(directory, file) for file in glob.glob(pattern, root_dir=directory)]
