from fnmatch import fnmatch
from inspect import signature, stack, Parameter
from typing import Literal

from lumipy.common import indent_str


def call_location():
    context = ['<could not find code context!>']
    for frame in stack():
        if not fnmatch(frame.filename, '*/lumiflex/*.py'):
            context = frame.code_context
            break

    return f"   → {''.join(context).strip()}"


def check_kwargs(sig, f_name, kwargs):

    bad_kwargs = [k for k in kwargs.keys() if k not in sig.parameters.keys()]
    if len(bad_kwargs) > 0:
        bad_str = ', '.join(map(lambda x: f"'{x}'", bad_kwargs))
        real_args = [p for p in sig.parameters.values() if p.name != 'self' and (p.kind is p.KEYWORD_ONLY or p.kind is p.POSITIONAL_OR_KEYWORD)]

        ljust = max(len(p.name) for p in real_args)

        def make_line(p: Parameter) -> str:
            name = p.name.ljust(ljust)
            if p.annotation is p.empty:
                return name
            if isinstance(p.annotation, str):
                return f'{name}    ({p.annotation})'
            return f'{name}    ({p.annotation.__name__})'

        good_str = '\n'.join(map(make_line, real_args))
        s = 's' if len(bad_kwargs) > 1 else ''
        raise ValueError(
            f'Invalid keyword arg{s} given to {f_name} ({bad_str}) at\n{call_location()}\n'
            f'Valid keyword args for {f_name} are:\n{indent_str(good_str, 4)}'
        )


def assemble_arguments(f_name: str, fn, self, args, kwargs, missing: Literal['error', 'ellipsis']):

    names, values = ['self'], [self]

    sig = signature(fn)

    check_kwargs(sig, f_name, kwargs)
    params = list(sig.parameters.values())

    iter_args = iter(args)

    for p in params[1:]:

        arg_val = next(iter_args, ...)

        if p.kind is p.POSITIONAL_OR_KEYWORD:
            if p.name in kwargs and arg_val is not ...:
                raise TypeError(f"Duplicate values in {f_name} for arg '{p.name}' ('{arg_val}' and '{kwargs[p.name]}')")
            elif p.name in kwargs:
                values.append(kwargs[p.name])
            elif arg_val is ... and p.default is not p.empty:
                values.append(p.default)
            elif arg_val is ... and missing == 'error':
                raise TypeError(f"{f_name} is missing a required positional argument '{p.name}'")
            else:
                values.append(arg_val)

            names.append(p.name)

        if p.kind is p.VAR_POSITIONAL:
            count = 0
            while arg_val is not ...:
                names.append(f'{p.name}[{count}]')
                values.append(arg_val)
                count += 1
                arg_val = next(iter_args, ...)

    return names, values


def assemble_error(fn_name, errors):
    if len(errors) == 0:
        return

    word, s = ('were', 's') if len(errors) > 1 else ('was', '')

    exc_str = f"Invalid input{s} detected at\n"
    exc_str += call_location()
    exc_str += f'\nThere {word} {len(errors)} failed constraint{s} on {fn_name}:\n'
    err_strs = []
    for x in errors:
        err_strs.append('•' + indent_str(x, 2)[1:])
    exc_str += indent_str('\n'.join(err_strs), 3)
    raise TypeError(exc_str)


