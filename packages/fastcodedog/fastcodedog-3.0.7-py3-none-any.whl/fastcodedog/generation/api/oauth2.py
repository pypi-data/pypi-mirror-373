# -*- coding: utf-8 -*-

from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.api.db import Db
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.base.variable import Variable
from fastcodedog.util.case_converter import camel_to_snake


class Oauth2(File):
    token_url = '/oauth/token'
    logout_url = '/oauth/logout'
    refresh_token_url = '/oauth/refresh_token'
    me_url = '/oauth/me'

    def __init__(self):
        super().__init__('oauth2',
                         file_path=LocationFinder.get_path('oauth', 'api', 'oauth'),
                         package=LocationFinder.get_package('oauth', 'api', 'oauth'),
                         context=None, parent=None, comment="""OAuth2.SECRET_KEY =
OAuth2.EXPIRE_SECONDS = 60*60*2
OAuth2.REDIS_URL = 'redis://localhost:6379/oauth2'""")
        self._init_blocks()

    def _init_blocks(self):
        self.blocks.append(
            Variable('app', value='FastAPI()', possible_imports='from fastapi import FastAPI'))
        self.blocks.append(Variable('oauth2_scheme', value=f"OAuth2PasswordBearer(tokenUrl='{self.token_url}')",
                                    possible_imports='from fastapi.security import OAuth2PasswordBearer'))
        self._init_login()
        self._init_remove_and_refresh()
        self._init_read_me()

    def _init_login(self):
        module = ctx_instance.oauth2.module
        model_name = ctx_instance.oauth2.model
        snake_name = camel_to_snake(model_name)
        user_name_column_name = ctx_instance.oauth2.user_name_column
        password_column = ctx_instance.oauth2.password_column
        user_model = ctx_instance.models[module][model_name]
        primary_key_name = [column.name for column in user_model.columns.values() if column.primary_key][0]
        function = Function('login_for_access_token', async_=True)
        function.params = {
            'form_data': Variable('form_data', type='Annotated[OAuth2PasswordRequestForm, Depends()]', nullable=False,
                                  possible_imports=[
                                      Import('from fastapi.security import OAuth2PasswordRequestForm', ),
                                      'from typing import Annotated',
                                      'from fastapi import Depends']),
            'session': Variable('session', type='Session', value='Depends(get_session)',
                                possible_imports=[
                                    Import('Session', Db().package),
                                    Import('get_session', Db().package)])
        }
        decorator = Function.Decorator('app.post',
                                       params=[f"'{self.token_url}'", Variable('tags', value=['认证(OAtuh)']),
                                               Variable('response_model', value='Token',
                                                        possible_imports=['from fastoauth import Token']
                                                        ), Variable('response_model_exclude_none', value=True)])
        function.decorators.append(decorator)
        function.blocks.append(Text('username = form_data.username\npassword = form_data.password'))
        function.blocks.append(Text(
            f'{snake_name} = session.query({model_name}).filter({model_name}.{user_name_column_name} == username).filter({model_name}.{password_column} == password).first()',
            possible_imports=Import(model_name, LocationFinder.get_package(model_name, 'model', module))
        ))
        function.blocks.append(Text(f"""if {snake_name}:
    return OAuth2.create_access_token({{"{primary_key_name}": {snake_name}.{primary_key_name}, "{user_name_column_name}": username}})""",
                                    possible_imports='from fastoauth import OAuth2'))
        function.blocks.append(
            Text("""raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")""",
                 possible_imports=['from fastapi import HTTPException',
                                   'from starlette.status import HTTP_401_UNAUTHORIZED']
                 ))
        self.blocks.append(function)

    def _init_remove_and_refresh(self):
        self.blocks.append(Text(f"""@app.post('/oauth/logout', tags=['认证(OAtuh)'])
async def remove(token: Annotated[str, Depends(oauth2_scheme)]):
    OAuth2.remove_token(token)
    return {{}}


@app.post('/oauth/refresh_token', tags=['认证(OAtuh)'], response_model=Token, response_model_exclude_none=True)
async def refresh(refresh_token: str= Body(..., embed=True)):
    return OAuth2.refresh_token(refresh_token)
""", possible_imports=['from typing import Annotated', 'from fastapi import Body', 'from fastoauth import Token']))

    def _init_read_me(self):
        module = ctx_instance.oauth2.module
        model_name = ctx_instance.oauth2.model
        snake_name = camel_to_snake(model_name)
        user_api = ctx_instance.apis[module][model_name]
        from fastcodedog.generation.api.api import Api
        api = Api(user_api)
        primary_key_name = user_api.primary_key_name
        function = Function('read_me', async_=True)
        function.decorators.append(
            Function.Decorator('app.get', params=[f"'{self.me_url}'", Variable('tags', value=['认证(OAtuh)']),
                                                  Variable('response_model', value='UserResponse',
                                                           possible_imports=Import(api.response_model,
                                                                                   from_=api.package,
                                                                                   as_='UserResponse')
                                                           ),
                                                  Variable('response_model_exclude_none', value=True)]))
        function.params = {'token': Variable('token', type='Annotated[str, Depends(oauth2_scheme)]',
                                             nullable=False,
                                             possible_imports=['from typing import Annotated',
                                                               'from fastapi import Depends']
                                             )}
        if api.validate_response_model:
            function.params['response_model'] = Variable('response_model', type='BaseModel',
                                                         value=f'Depends({api.validate_response_model})',
                                                         possible_imports=[
                                                             Import(api.validate_response_model, from_=api.package),
                                                             'from fastapi import Depends',
                                                             'from pydantic import BaseModel']
                                                         )
        function.params['session'] = Variable('session', type='Session', value='Depends(get_session)',
                                              possible_imports=[Import('Session', Db().package),
                                                                Import('get_session', Db().package)]
                                              )
        function.blocks.append(Text(f"""{primary_key_name} = OAuth2.get_token_user(token)['{primary_key_name}']""",
                                    possible_imports='from fastoauth import OAuth2'))
        function.blocks.append(
            Text(f"""query = crud.get_{snake_name}(session=session, {primary_key_name}={primary_key_name})""",
                 possible_imports=Import(LocationFinder.get_package(model_name, 'crud', module), as_='crud')
                 ))
        if api.validate_response_model:
            function.blocks.append(Text(
                f"""query = crud.fill_{snake_name}_selectinload(query, camel_to_snake(response_model.__name__))""",
                possible_imports=Import('camel_to_snake', LocationFinder.get_package('camel_to_snake'))))
        function.blocks.append(Text(f"""{snake_name} = query.first()
if not {snake_name}:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"数据未找到")""",
                                    possible_imports=['from fastapi import HTTPException',
                                                      'from starlette.status import HTTP_404_NOT_FOUND']))
        if api.validate_response_model:
            function.blocks.append(Text(f"""return response_model.model_validate({snake_name})"""))
        else:
            function.blocks.append(Text(f"""return {snake_name}"""))
        self.blocks.append(function)
