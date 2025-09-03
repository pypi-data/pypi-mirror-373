# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.api.api import Api
from fastcodedog.generation.api.config import Config
from fastcodedog.generation.api.db import Db
from fastcodedog.generation.api.main import Main
from fastcodedog.generation.api.oauth2 import Oauth2


def generate_api(specify_api=None):
    # 只能在使用的时候才import，因为这些文件在初始化的时候，需要保证ctx_instance已经初始化
    Db().save()
    Config().save()
    Main().save()
    Oauth2().save()
    for module, apis in ctx_instance.apis.items():
        for api_context in apis.values():
            if specify_api and api_context.name not in specify_api:
                continue
            api_file = Api(api_context)
            api_file.save()
