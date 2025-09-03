# -*- coding: utf-8 -*-
from fastcodedog.generation.commonfiles.utilfiles.case_converter import CaseConverter
from fastcodedog.generation.commonfiles.utilfiles.log import Log


def generate_common_files():
    CaseConverter().save()
    Log().save()
