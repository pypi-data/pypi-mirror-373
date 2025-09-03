# -*- coding: utf-8 -*-
import re

from fastcodedog.context.crud.crud import Crud as CrudContext
from fastcodedog.context.crud.query import Query as QueryContext
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.required_import import Import, RequiredImport
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.crud.crud_functions import Crud
from fastcodedog.util.case_converter import camel_to_snake
from fastcodedog.util.extractor import extract_variables
from fastcodedog.util.inflect_wrapper import plural


class ForeignQuery(Crud):
    def __init__(self, foreign_key_context, context: CrudContext):
        self.snake_name = camel_to_snake(context.name)
        self.snake_name = f'{plural(self.snake_name)}_by_{self.get_luckyname(foreign_key_context.name)}'
        super().__init__(f'get_{self.snake_name}', context=context, comment=f'使用{foreign_key_context.title}查询')
        self.action = Crud.Action.READ
        self.return_list = True
        self.class_type = context.name
        self.foreign_key_context = foreign_key_context
        self.params['session'] = Function.Parameter('session', nullable=False)
        self.params[foreign_key_context.name] = Function.Parameter(foreign_key_context.name,
                                                                   type=foreign_key_context.type,
                                                                   comment=foreign_key_context.description,
                                                                   nullable=False)
        self._init_blocks()

    def _init_blocks(self):
        self.blocks.append(Text(
            f"return session.query({self.class_type}).filter({self.class_type}.{self.foreign_key_context.name} == {self.foreign_key_context.name})"))


class JoinQuery(Crud):
    def __init__(self, relationship_context, context: CrudContext):
        # 如果relationship父子都是指向自身，需要一个更友好的名字
        self.snake_name = plural(camel_to_snake(context.name))
        if (relationship_context.back_populates_model == context.name
                and relationship_context.back_populates_module == context.module):
            self.snake_name = camel_to_snake(relationship_context.back_populates)
        self.snake_name = f'{self.snake_name}_by_{self.get_luckyname(relationship_context.original_name)}'
        # 后续要改成下面的版本
        # self.snake_name = plural(camel_to_snake(context.name)) if not relationship_context.back_populates else relationship_context.back_populates
        # self.snake_name = f'{self.snake_name}_by_{self.get_luckyname(relationship_context.original_name)}'
        super().__init__(f'get_{self.snake_name}', context=context)
        self.action = Crud.Action.READ
        self.relationship_name = relationship_context.name
        self.relationship_context = relationship_context
        self.return_list = True
        self.class_type = context.name
        self.params['session'] = Function.Parameter('session', nullable=False)
        self.param_relationship = Function.Parameter(relationship_context.original_name,
                                                     type=f'{relationship_context.back_populates_primary_key.type}',
                                                     nullable=False)
        self.params[self.param_relationship.name] = self.param_relationship
        self._init_blocks_and_possible_imports()

    def _init_blocks_and_possible_imports(self):
        self.blocks.append(Text(f"query = session.query({self.class_type})"))
        self.blocks.append(Text(f"query = query.join({self.relationship_context.secondary_object_name})"))
        self.add_possible_imports(Import(self.relationship_context.secondary_object_name,
                                         from_=self.get_package_by_model_name(
                                             self.relationship_context.secondary_object_name)))
        self.blocks.append(Text(
            f"query = query.filter({self.relationship_context.secondary_object_name}.c.{self.param_relationship.name} == {self.param_relationship.name})"))
        self.blocks.append(Text(f"return query"))


class Query(Crud):
    class Filter(Block):
        def __init__(self, context: str | QueryContext.Filter, parameters: dict = None, aliases: dict = None,
                     indent=Block.DEFAULT_INDENT, parent=None):
            super().__init__('filter', context=context,  possible_imports=Crud.POSSIBLE_IMPORTS, parent=parent)
            self.parameters = parameters if parameters else {}
            self.aliases = aliases if aliases else {}
            self.nullable_param_names = [parameter.name for parameter in parameters.values() if
                                         parameter.nullable]
            self.option_none_param_names = [parameter.name for parameter in parameters.values() if
                                            parameter.option_none]
            self.indent = indent
            self.method = None      # sqlalchemy的方法，or_，and_等
            self.expression = ''
            self.sub_filters = []

            self._init_filter()

        def _init_filter(self):
            if isinstance(self.context, str):
                self.expression = self.context
                for model_name in self._get_model_names_in_filter_string(self.expression):
                    if model_name not in self.aliases.keys():
                        self.add_possible_imports(Import(model_name, Crud.get_package_by_model_name(model_name)))
            elif self.context.or_:
                self.method = 'or_'
                for f in self.context.or_:
                    self.sub_filters.append(Query.Filter(f, parameters=self.parameters, aliases=self.aliases, parent=self))
            elif self.context.and_:
                self.method = 'and_'
                for f in self.context.and_:
                    self.sub_filters.append(Query.Filter(f, parameters=self.parameters, aliases=self.aliases, parent=self))
            else:
                raise Exception('not support')

        def serialize(self, delimiter='\n', with_comment=True, parent_stmts_name=None):
            """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
            content = ''
            if self.method:
                stmts_name = 'stmts_1' if not parent_stmts_name else f'stmts_{int(parent_stmts_name.split("_")[-1]) + 1}'
                content += f'{stmts_name} = []  # {self.method}(*{stmts_name})\n'
                for f in self.sub_filters:
                    content += f"{f.serialize(parent_stmts_name=stmts_name)}\n"
                content += f'if {stmts_name}:  # {self.method}(*{stmts_name})\n'
                if not parent_stmts_name:
                    content += f'{self.indent}query = query.filter({self.method}(*{stmts_name}))'
                else:
                    content += f'{self.indent}{parent_stmts_name}.append({self.method}(*{stmts_name}))'
            elif self.expression:
                param_in_filters = self._get_param_names_in_filter_string(self.expression)
                if param_in_filters:
                    conditions = [(param_in_filter + ' is not None') if (param_in_filter not in self.option_none_param_names)
                                  else ('(' + param_in_filter + ' is not None' + ' or ' + param_in_filter + ' in option_none_params)') for param_in_filter in param_in_filters]
                    if len(conditions) == 1 and conditions[0].startswith('('):
                        # 只有一个条件的时候，不要括号
                        conditions[0] = conditions[0][1:-1]
                    content += f'if {" and ".join(conditions)}:\n'
                if not parent_stmts_name:
                    content += f'{self.indent if param_in_filters else ""}query = query.filter({self.expression})'
                else:
                    content += f'{self.indent if param_in_filters else ""}{parent_stmts_name}.append({self.expression})'
            else:
                raise Exception('未设置method或者expression')
            return content

        def get_required_imports(self) -> RequiredImport:
            required_import = RequiredImport()
            fs = extract_variables(self.expression) if self.expression else []
            if self.method:
                fs.append(self.method)
            [required_import.add(import_) for key, import_ in self.possible_imports.items() if key in fs]
            [required_import.update(f.get_required_imports()) for f in self.sub_filters]
            return required_import

        def _get_param_names_in_filter_string(self, filter_string):
            fs = extract_variables(filter_string)
            return [f for f in fs if f in self.nullable_param_names]

        def _get_model_names_in_filter_string(self, filter_string):
            pettern = r'([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_.]*)'
            parts = re.findall(pettern, filter_string)
            return [p.split('.')[0] for p in parts]

    def __init__(self, context: QueryContext):
        self.snake_name = camel_to_snake(context.name)
        super().__init__(f'get_{context.name}', context=context, comment=context.description)
        self.action = Crud.Action.READ
        self.return_list = True
        self.have_select_models = bool(self.context.select_models)
        self.summary = context.summary
        self.params['session'] = Function.Parameter('session', nullable=False)
        for parameter in context.parameters.values():
            self.params[parameter.name] = Function.Parameter(parameter.name, type=parameter.type,
                                                             nullable=parameter.nullable,
                                                             option_none=parameter.option_none,
                                                             comment=parameter.description)
        if context.orders:
            self.params['order_by'] = Function.Parameter('order_by', type='str', valid_values=context.orders, comment='排序方式')
            # self.params['desc'] = Function.Parameter('desc', type='bool', comment='是否倒序')
        self.nullable_param_names = [parameter.name for parameter in context.parameters.values() if parameter.nullable]
        self.option_none_param_names = [parameter.name for parameter in context.parameters.values() if
                                        parameter.option_none]
        self.option_none = len(self.option_none_param_names) > 0
        if self.option_none:
            self.params['option_none_params'] = Function.Parameter('option_none_params', default_value='[]')
            self.comment = ((self.comment + '\n' if self.comment else '')
                            + f'允许传入为null值的参数：{", ".join(self.option_none_param_names)}')
        self._init_blocks_and_possible_imports()

    def _init_blocks_and_possible_imports(self):
        # 添加session.query
        if self.context.select_models:
            # self.add_possible_imports(Import(self.context.select_models[0], self.get_package_by_model_name(self.context.select_models[0])))
            self.blocks.append(Text(f'query = session.query({", ".join([self.context.model] + self.context.select_models)})'))
            for select_model in self.context.select_models:
                if select_model not in self.context.aliases.keys():
                    self.add_possible_imports(Import(select_model, self.get_package_by_model_name(select_model)))
        else:
            self.blocks.append(Text(f'query = session.query({self.context.model})'))
        # # 添加select_from，一般需要先有select_models
        # if self.context.select_from:
        #     self.blocks.append(Text(f'query = query.select_from({self.context.select_from})'))
        #     for select_from in extract_variables(self.context.select_from):
        #         if select_from not in ['join', 'outerjoin'] and select_from not in self.context.aliases.keys():
        #             ...
        for alias_name, alias_value in self.context.aliases.items():
            model_name = alias_value.split('.')[0]
            self.add_possible_imports(Import(model_name, self.get_package_by_model_name(model_name)))
            self.blocks.append(Text(f'{alias_name} = {alias_value}'))
        for join in self.context.joins:
            self._check_join_condition(join)
            model_name = join.split('.')[0]
            if model_name not in self.context.aliases.keys():
                self.add_possible_imports(Import(model_name, self.get_package_by_model_name(model_name)))
            self.blocks.append(Text(f'query = query.join({join})'))
        for outerjoin in self.context.outerjoins:
            self._check_join_condition(outerjoin)
            model_name = outerjoin.split('.')[0]
            if model_name not in self.context.aliases.keys():
                self.add_possible_imports(Import(model_name, self.get_package_by_model_name(model_name)))
            self.blocks.append(Text(f'query = query.outerjoin({outerjoin})'))
        for filter in self.context.filters:
            self.blocks.append(Query.Filter(filter, parameters=self.context.parameters, aliases=self.context.aliases))
        if self.context.distinct:
            self.blocks.append(Text(f'query = query.distinct({self.context.distinct})'))
        if self.context.orders:
            self.blocks.append(Text(f"""if order_by and order_by not in {self.context.orders}:
    raise Exception(f'未知的排序方式：{{order_by}}，可选值：{", ".join(self.context.orders)}')"""))
            self.blocks.append(Text(f"""if order_by:
    query = eval(f'query.order_by({{order_by}})')   # 采用eval，由上面的if语句确保不执行危险代码"""))
        self.blocks.append(Text(f'return query'))

    def _check_join_condition(self, join):
        if join in self.context.aliases.keys():
            join = self.context.aliases[join]
        if '.' not in join and ',' not in join:
            raise Exception(f'''join参数{join}配置错误，需明确指定关联条件。如果你使用了别名，别名也需要明确指定关联条件。
请参考https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.join。
支持使用类似(User.addresses)和(Address, User.id==Address.user_id)两种写法明确指定关联条件''')
