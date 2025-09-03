# -*- coding: utf-8 -*-
from fastcodedog.context.api.api import Api as ApiContext
from fastcodedog.generation.api.api_function import ApiFunction
from fastcodedog.generation.api.oauth2 import Oauth2
from fastcodedog.generation.base.call import Call
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.base.variable import Variable
from fastcodedog.util.case_converter import snake_to_camel, camel_to_snake


class Api(File):
    def __init__(self, context: ApiContext):
        super().__init__(context.name,
                         file_path=LocationFinder.get_path(context.name, 'api', context.module),
                         package=LocationFinder.get_package(context.name, 'api', context.module),
                         context=context, comment=context.comment)
        self.snake_name = camel_to_snake(self.name)
        self.module = context.module
        self.response_model = None  # 返回数据类型的model，默认是对应的Schema，如果有自定义返回的schema，会是一个union
        self.response_model_list = None  # 和上一个变量对应，返回数据类型的list
        self.validate_response_model = None  # 和上面的啷个变量对应，校验输入的返回数据类型是否合法
        self._init_blocks()

    def _init_blocks(self):
        self.blocks.append(Variable('app', value=Call('FastAPI'), possible_imports='from fastapi import FastAPI'))
        if self.context.oauth2_enabled:
            self.blocks.append(
                Variable('oauth2_scheme', value=Call('OAuth2PasswordBearer', params=[f"tokenUrl='{Oauth2.token_url}'"]),
                         possible_imports='from fastapi.security import OAuth2PasswordBearer'))
        self._init_response_model()
        for endpoint in self.context.endpoints.values():
            self.blocks.append(ApiFunction(endpoint, parent=self))
            # self._init_endpoint(endpoint)

    def _init_response_model(self):
        all_response_models = [snake_to_camel(m, upper_first=True) for m in self.context.validate_response_models]
        if len(self.context.validate_response_models) > 1:
            self.response_model = f'ALL_{self.name.upper()}_RESPONSE_MODEL'
            self.response_model_list = f'ALL_{self.name.upper()}_LIST_RESPONSE_MODEL'
            self.validate_response_model = f'validate_{self.snake_name}_response_model'
            self.blocks.append(Variable(self.response_model, type='Union',
                                        value=Call('Union', brackets='[]', params=all_response_models,
                                                   possible_imports=[
                                                                        'from typing import Union'] + self._get_reponse_schema_imports())))
            self.blocks.append(Variable(self.response_model_list, type='Union',
                                        value=Call('Page', brackets='[]', params=[self.response_model],
                                                   possible_imports='from fastapi_pagination import Page')))
            self._init_validate_response_model_funciton()

        else:
            self.response_model = Text(all_response_models[0], possible_imports=[
                Import(all_response_models[0], LocationFinder.get_package(self.name, 'schema', self.module))])
            self.response_model_list = Call('Page', brackets='[]', params=[self.response_model],
                                            possible_imports=[Import(all_response_models[0],
                                                                     LocationFinder.get_package(self.name, 'schema',
                                                                                                self.module)),
                                                              'from fastapi_pagination import Page'])

    def _init_validate_response_model_funciton(self):
        function = Function(self.validate_response_model)
        # 拼装入参
        input_query_params = ['None',
                              Function.Parameter('description',
                                                 default_value=f'"指定返回的数据类型，默认为\'{self.snake_name}\'"'),
                              Function.Parameter('enum', default_value=self.context.validate_response_models)]
        function.params = {
            'response_model': Function.Parameter('response_model', type='str',
                                                 default_value=Call('Query', params=input_query_params,
                                                                    possible_imports='from fastapi import Query'))
        }
        function.comment = '查询请求时允许选择的模型类型'
        function.blocks.append(Text(
            f"""if response_model and response_model not in [{', '.join(["'" + validate_response_model + "'" for validate_response_model in self.context.validate_response_models])}]:
    raise HTTPException(status_code=400,
        detail="Invalid response_model. Must in {', '.join(self.context.validate_response_models)}.")""",
            possible_imports='from fastapi import HTTPException'))
        for validate_response_model in self.context.validate_response_models:
            function.blocks.append(Text(f"if response_model == '{camel_to_snake(validate_response_model)}':"))
            function.blocks.append(
                Text(f"return {snake_to_camel(validate_response_model, upper_first=True)}", indent=self.DEFAULT_INDENT))
        function.blocks.append(Text(f'return {self.name}'))
        self.blocks.append(function)

    def _get_reponse_schema_imports(self):
        imports = []
        all_response_models = [snake_to_camel(m, upper_first=True) for m in self.context.validate_response_models]
        # 第一个是基本版
        imports.append(
            Import(all_response_models[0], from_=LocationFinder.get_package(self.name, 'schema', self.module)))
        # 第二个开始时扩展版本
        for model in all_response_models[1:]:
            imports.append(Import(model, LocationFinder.get_package(f'{self.name}_additional', 'schema', self.module)))
        return imports
