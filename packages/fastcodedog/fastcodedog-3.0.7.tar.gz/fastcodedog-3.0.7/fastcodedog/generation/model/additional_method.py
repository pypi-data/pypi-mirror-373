# -*- coding: utf-8 -*-
from fastcodedog.generation.base.function import Function
from fastcodedog.context.model.additional_method import AdditionalMethod as AdditionalMethodContext
from fastcodedog.generation.base.text import Text


class AdditionalMethod(Function):
    def __init__(self, context: AdditionalMethodContext):
        super().__init__(name=context.name, context=context, # decorators=[Function.Decorator('property')],
                         params={'self': Function.Parameter('self', nullable=False)}, return_type=context.type, comment=context.comment)
        for parameter in context.parameters:
            self.params[parameter.name] = Function.Parameter(name=parameter.name, type=parameter.type,
                                                             default_value=parameter.default_value,
                                                             nullable=parameter.nullable, comment=parameter.comment)
        self.blocks.append(Text(context.script, possible_imports=context.import_))

    # def serialize(self, delimiter='\n', with_comment=True):
    #     return delimiter + super().serialize(delimiter=delimiter, with_comment=with_comment)
