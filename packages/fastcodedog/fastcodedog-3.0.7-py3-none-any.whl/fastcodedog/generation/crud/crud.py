# -*- coding: utf-8 -*-
from itertools import chain

from fastcodedog.generation.crud.crud_functions import BaseCreate, BaseUpdate, BaseDelete, BaseGet, UniqueGet, JoinAdd, \
    JoinDelete
from fastcodedog.generation.crud.query_functions import ForeignQuery, JoinQuery, Query
from fastcodedog.generation.crud.selectinload import SelectinLoad


def get_blocks(crud_context):
    queries = [Query(query) for query in crud_context.queries.values()]     # 自定一个query
    return [SelectinLoad(crud_context), BaseCreate(crud_context), BaseUpdate(crud_context),
            BaseDelete(crud_context), BaseGet(crud_context),
            *[UniqueGet(unique_constraint, crud_context) for unique_constraint in crud_context.unique_constraints],
            *list(chain.from_iterable(
                [[JoinAdd(join_relationship, crud_context), JoinDelete(join_relationship, crud_context)] for
                 join_relationship in crud_context.join_relationships.values()])),
            *[ForeignQuery(foreign_key, crud_context) for foreign_key in crud_context.foreign_keys.values() if ForeignQuery(foreign_key, crud_context).name not in [query.name for query in queries]],
            *[JoinQuery(join_relationship, crud_context) for join_relationship in
              crud_context.join_relationships.values()],
            *queries
            ]
