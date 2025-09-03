import re

from pydantic import BaseModel

from lumipy.common import indent_str


def to_snake_case(camel_case_str: str) -> str:
    """Convert a camel case string to a snake case string

    Args:
        camel_case_str (str): input camel case string

    Returns:
        str: generated snake case string
    """
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    cleaned_str = "".join(camel_case_str.split())
    snake_case = a.sub(r'_\1', cleaned_str).lower()
    return snake_case.replace('__', '_')


def model_repr(x: BaseModel, *skip_fields: str) -> str:
    """Make a model repr string for nodes and metadata objects.

    Args:
        x (BaseModel): the model to make the repr string for.
        *skip_fields (str): fields on the model to skip.

    Returns:
        str: the repr string.
    """
    name = type(x).__name__
    lines = []
    for field_name in x.model_fields.keys():
        if field_name in skip_fields:
            continue
        values = getattr(x, field_name)
        if isinstance(values, (list, tuple)) and len(values) > 0:
            tuple_str = '\n'.join(f'[{i}]: {repr(v)}' for i, v in enumerate(values))
            lines.append(f'{field_name}: (\n{indent_str(tuple_str)}\n)')
        else:
            lines.append(f'{field_name}: {repr(values)}')
    content = indent_str('\n'.join(lines))
    return f'{name}(\n{content}\n)'
