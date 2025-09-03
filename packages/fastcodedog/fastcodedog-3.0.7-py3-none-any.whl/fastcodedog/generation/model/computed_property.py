# -*- coding: utf-8 -*-
from fastcodedog.generation.base.function import Function
from fastcodedog.context.model.computed_property import ComputedProperty as ComputedPropertyContext
from fastcodedog.generation.base.text import Text


class ComputedProperty(Function):
    def __init__(self, context: ComputedPropertyContext):
        super().__init__(name=context.name, context=context, decorators=[Function.Decorator('property')],
                         params={'self': Function.Parameter('self', nullable=False)}, return_type=context.type, comment=context.comment)
        self.blocks.append(Text(context.script, possible_imports=context.import_))

    # def serialize(self, delimiter='\n', with_comment=True):
    #     return delimiter + super().serialize(delimiter=delimiter, with_comment=with_comment)
