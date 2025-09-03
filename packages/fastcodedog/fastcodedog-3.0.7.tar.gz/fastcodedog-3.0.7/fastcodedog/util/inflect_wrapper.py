# -*- coding: utf-8 -*-
"""
@author: hubo
@project: fastframe
@file: inflect_wrapper
@time: 2024/5/29 14:48
@desc:
"""
import inflect

_engine = None


def get_inflect_engine():
    global _engine
    if _engine is None:
        _engine = inflect.engine()
    return _engine


def plural(noun):
    return get_inflect_engine().plural(noun)
