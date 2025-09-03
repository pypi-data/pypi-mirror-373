# -*- coding: utf-8 -*-
from fastcodedog.generation.api.db import Db
from fastcodedog.generation.base.call import Call
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.base.variable import Variable


class ApiFunction(Function):
    def __init__(self, context, parent):
        super().__init__(context.name, context=context, async_=True, parent=parent, comment=context.comment)
        self.api = parent
        self.schemas = [f'{self.api.name}', f'{self.api.name}Create', f'{self.api.name}Update']
        # 多种条件都会用到的公共数据
        self.crud_params = self._get_crud_params()
        self.crud_imoprt = Import(LocationFinder.get_package(self.api.name, 'crud', self.api.module), as_='crud')
        self.fill_selectinload = f'fill_{self.api.snake_name}_selectinload' if self.api.validate_response_model else None

        # 添加decorator
        self._fill_funciton_decorators()
        # 添加参数
        self._fill_function_params()
        # 添加block
        self._fill_blocks()

    def _get_crud_params(self):
        # 应该把session和option_none_params也写入到self.context.params，api中判断不加入到api_function的参数
        params = (['session=session'] +
                  [f'{param.name}={param.name}' for param in self.context.params.values()])
        # 增加option_none_params
        if any([param.option_none for param in self.context.params.values()]):
            params.append('option_none_params=option_none_params')
        return params

    def _fill_blocks(self):
        self._fill_option_none()
        if self.context.return_list:
            self._fill_return_list_blocks()
        elif self.context.action == 'get':
            self._fill_get_blocks()
        elif self.context.name == f'delete_{self.api.snake_name}':
            self._fill_delete_blocks()
        elif self.context.action in ['post', 'put', 'delete']:
            self._fill_create_or_update_blocks()
        else:
            raise Exception(f'未知的action：{self.context.action}')

    def _fill_create_or_update_blocks(self):
        self.blocks.append(Text(f'{self.api.snake_name} = crud.{self.name}({", ".join(self.crud_params)})',
                                possible_imports=self.crud_imoprt))
        self.blocks.append(Text(f"""if not {self.api.snake_name}:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"数据未找到")""",
                                possible_imports=['from fastapi import HTTPException',
                                                  'from starlette.status import HTTP_404_NOT_FOUND']))
        self.blocks.append(Text(
            f'query = crud.get_{self.api.snake_name}(session, {self.api.snake_name}.{self.api.context.primary_key_name})',
            possible_imports=self.crud_imoprt))
        if self.fill_selectinload:
            self.blocks.append(
                (Text(f'query = crud.{self.fill_selectinload}(query, camel_to_snake(response_model.__name__))',
                      possible_imports=Import('camel_to_snake', LocationFinder.get_package('camel_to_snake')))))
            self.blocks.append(Text(f'return response_model.model_validate(query.first())'))
        else:
            self.blocks.append(Text(f'return query.first()'))

    def _fill_delete_blocks(self):
        self.blocks.append(Text(f"""{self.api.snake_name} = crud.{self.name}({", ".join(self.crud_params)})
if not {self.api.snake_name}:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"数据未找到")
return {{}}""", possible_imports=[self.crud_imoprt, 'from fastapi import HTTPException',
                                  'from starlette.status import HTTP_404_NOT_FOUND']))

    def _fill_get_blocks(self):
        self.blocks.append(
            Text(f'query = crud.{self.name}({", ".join(self.crud_params)})', possible_imports=self.crud_imoprt))
        if self.fill_selectinload:
            self.blocks.append(
                (Text(f'query = crud.{self.fill_selectinload}(query, camel_to_snake(response_model.__name__))',
                      possible_imports=Import('camel_to_snake', LocationFinder.get_package('camel_to_snake'))
                      )))
        self.blocks.append(Text(f'{self.api.snake_name} = query.first()'))
        self.blocks.append(Text(
            f'if not {self.api.snake_name}:\n    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"数据未找到")',
            possible_imports=['from fastapi import HTTPException', 'from starlette.status import HTTP_404_NOT_FOUND']
        ))
        if self.api.validate_response_model:
            self.blocks.append(Text(f"""return response_model.model_validate({self.api.snake_name})"""))
        else:
            self.blocks.append(Text(f"""return {self.api.snake_name}"""))

    def _fill_return_list_blocks(self):
        self.blocks.append(Text(f'query = crud.{self.name}({", ".join(self.crud_params)})',
                                possible_imports=self.crud_imoprt))
        self.blocks.append(Text('skip = (page - 1) * size\nlimit = size\ntotal = query.count()'))
        if self.fill_selectinload:
            self.blocks.append(
                (Text(f'query = crud.{self.fill_selectinload}(query, camel_to_snake(response_model.__name__))',
                      possible_imports=Import('camel_to_snake', LocationFinder.get_package('camel_to_snake'))
                      )))
        params_class_name = 'Params'
        if self.context.max_size:
            # 需要增加CustomParams的类定义
            self.blocks.append(Text(f"""class CustomParams(Params):
    size: int = Query(
        {self.context.max_size},
        gt=1,
        le={self.context.max_size},  # 这里将最大值设置为{self.context.max_size}
        description="Page size"
    )""", possible_imports=['from fastapi_pagination import Params']))
            params_class_name = 'CustomParams'
        if self.api.validate_response_model:
            self.blocks.append(Text(
                f"""return create_page([response_model.model_validate({self.api.snake_name}) for {self.api.snake_name}{', *_' if self.context.have_select_models else ''} in query.offset(skip).limit(limit).all()],
   total=total, params={params_class_name}(page=page, size=size))""",
                possible_imports=['from fastapi_pagination import create_page',
                                  'from fastapi_pagination import Params']))
        else:
            if self.context.have_select_models:
                self.blocks.append(Text(f"""return create_page([for {self.api.snake_name}, *_ in query.offset(skip).limit(limit).all()],
       total=total, params={params_class_name}(page=page, size=size))""",
                                        possible_imports=['from fastapi_pagination import create_page',
                                                          'from fastapi_pagination import Params']))
            else:
                self.blocks.append(Text(f"""return create_page(query.offset(skip).limit(limit).all(),
       total=total, params={params_class_name}(page=page, size=size))""",
                                        possible_imports=['from fastapi_pagination import create_page',
                                                          'from fastapi_pagination import Params']))

    def _fill_option_none(self):
        if any([param.option_none for param in self.context.params.values()]):
            self.blocks.append(Text('option_none_params=[]   # 传入null的参数'))
            for param in self.context.params.values():
                if param.option_none:
                    self.blocks.append(Text(f"""if {param.name} == '':
            {param.name} = None
            option_none_params.append({param.name})
        """))

    def _fill_function_params(self):
        # crud的调用参数
        for param in self.context.params.values():
            location = 'Body' if param.type in self.schemas else \
                ('Path' if f'{{{param.name}}}' in self.context.url else 'Query')  # 入参可能在query，path，body
            default_value = Call(location, possible_imports=Import(location, 'fastapi'))
            if param.nullable:
                default_value.params.append('None')  # default_value.params.append('None' if param.nullable else '...')
            if param.enum:
                default_value.params.append(f'enum={param.enum}')
            if param.description:
                default_value.params.append(f'description="{param.description}"')
            type = param.type if (not param.option_none or param.type == 'str') else f'{param.type} | str'
            p = self.Parameter(param.name, type=type, nullable=param.nullable, default_value=default_value,
                               comment=param.description)
            if param.type in self.schemas:
                p.add_possible_imports(
                    Import(param.type, LocationFinder.get_package(self.api.name, 'schema', self.api.module)))
            if param.type in ['date', 'datetime', 'time']:
                p.add_possible_imports(Import(param.type, 'datetime'))
            self.params[p.name] = p
        # 查询的通用参数
        if self.context.return_list:
            self.params['page'] = (
                self.Parameter('page', type='int',
                               default_value=Call('Query', params=[1, 'ge=1', 'description="页数"'],
                                                  possible_imports='from fastapi import Query')))
            size_params = [self.context.max_size if self.context.max_size else 100]
            size_params.append('ge=1')
            if self.context.max_size:
                size_params.append(f'le={self.context.max_size}')
            size_params.append('description="每页数量"')
            self.params['size'] = (
                self.Parameter('size', type='int',
                               default_value=Call('Query', params=size_params,
                                                  possible_imports='from fastapi import Query')))
        # 返回类型
        if self.context.name != f'delete_{self.api.snake_name}' and self.api.validate_response_model:  # 不是删除自身的时候，可以选择返回值类型
            self.params['response_model'] = self.Parameter('response_model', type='BaseModel',
                                                           default_value=f'Depends({self.api.validate_response_model})',
                                                           possible_imports=['from pydantic import BaseModel',
                                                                             'from fastapi import Depends'])
        # session依赖
        self.params['session'] = self.Parameter('session', type='Session', default_value='Depends(get_session)',
                                                possible_imports=['from fastapi import Depends',
                                                                  Import('Session', Db().package),
                                                                  Import('get_session', Db().package)])
        # Oauth2依赖
        if self.api.context.oauth2_enabled:
            self.params['token'] = self.Parameter('token', type='Annotated[str, Depends(oauth2_scheme)]', nullable=True,
                                                  possible_imports=['from fastapi import Depends',
                                                                    Import('Annotated', 'typing')])

    def _fill_funciton_decorators(self):
        decorator = self.Decorator(f'app.{self.context.action}')
        decorator.params = [f"'{self.context.url}'", Variable('tags', value=self.context.tags)]
        if self.name != f'delete_{self.api.snake_name}':
            decorator.params += [Variable('response_model',
                                          value=self.api.response_model if not self.context.return_list else self.api.response_model_list),
                                 Variable('response_model_exclude_none', value=True)]
        if self.context.summary:
            decorator.params.append(Variable('summary', value=f"'{self.context.summary}'"))
        self.decorators.append(decorator)
