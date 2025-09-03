from __future__ import annotations

import typing
from functools import wraps
from itertools import zip_longest
from typing import Iterable, Literal

from lumipy.common import indent_str
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._method_tools.constraints import VariadicCheck, TableVarCheck, UnaryCheck
from lumipy.lumiflex._method_tools.method_tools import assemble_arguments, assemble_error

if typing.TYPE_CHECKING:
    from lumipy.lumiflex.column import Column


def input_constraints(*assertions, **params):

    def assertion_fn(fn):
        if params.get('name') is None:
            raise ValueError(f'Function must be labelled by using name=<fn name> in @dtype_check()')

        @wraps(fn)
        def wrapper(self, *args, **kwargs) -> Column:
            from lumipy.lumiflex.column import Column
            from lumipy.lumiflex._column.make import make

            names, args = assemble_arguments(params.get('name'), fn, self, args, kwargs, params.get('missing', 'error'))

            # col conversion
            to_the_end = False
            for i, (name, a, assertion) in enumerate(zip_longest(names, args, assertions, fillvalue=...)):
                if assertion is ... and not to_the_end:
                    continue
                if a is ...:
                    continue
                if isinstance(assertion, VariadicCheck):
                    to_the_end = True
                args[i] = a if isinstance(a, Node) and not isinstance(a, Column) else make(a)

            failures = []
            for i, (name, a, assertion) in enumerate(zip_longest(names, args, assertions, fillvalue=...)):
                if assertion is ... or a is ...:
                    continue

                if isinstance(assertion, TableVarCheck) and not assertion(a):
                    failures.append(assertion.make_error_msg(name, a))

                if isinstance(assertion, UnaryCheck) and not assertion(a):
                    failures.append(assertion.make_error_msg(name, a))

                if isinstance(assertion, VariadicCheck):
                    if not assertion(*[arg for arg in args[i:]]):
                        failures.append(assertion.make_error_msg(names[i:], args[i:]))
                    break

            assemble_error(params.get('name'), failures)
            return fn(*args)

        return wrapper

    return assertion_fn


def preprocess_collection(fn):

    @wraps(fn)
    def wrapper(self, *args, **kwargs):

        from lumipy.lumiflex._table.operation import Select, Where
        from lumipy.lumiflex.column import Column

        if len(args) == 1 and isinstance(args[0], (Select, Where)):
            if len(args[0].content.get_columns()) != 1:
                raise ValueError(f'Membership subquery must only have one column, had {len(args[0].get_columns())}.')
            # Make a 'fake' column representing the subquery and the single column type
            dtype = args[0].content.get_columns()[0].dtype
            cols = Column(fn=lambda x: f'\n{indent_str(x.content.get_sql())}\n', dtype=dtype, meta=None, label='const', parents=(args[0], ))
            return fn(self, cols, **kwargs)
        elif len(args) == 1 and isinstance(args[0], Iterable):
            return fn(self, *args[0], **kwargs)
        elif len(args) == 1 and not isinstance(args[0], Iterable):
            raise TypeError('Input to is_in or not_in must be individual *args or a single iterable')
        return fn(self, *args, **kwargs)

    return wrapper


def block_node_type(label: Literal['aggfunc', 'windowfunc'], name: str):

    def assertion_fn(fn):

        if label == 'aggfunc':
            reason = f'Can\'t use an aggregate function inside {name}!'
        elif label == 'windowfunc':
            reason = f'Can\'t use a window function inside {name}!'
        else:
            raise ValueError(f'Unrecognised node type label in block_node_type: {label}.')

        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            inputs = [self] + list(args) + list(kwargs.values())
            aggs = []
            for i in inputs:
                if isinstance(i, Node) and (
                        any(a.label_ == label for a in i.get_ancestors()) or i.label_ == label):
                    aggs.append(i)
            if len(aggs) > 0:
                assemble_error(name, [reason])

            return fn(self, *args, **kwargs)

        return wrapper

    return assertion_fn
