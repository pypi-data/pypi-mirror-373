import inspect

from lumipy.lumiflex._method_tools.constraints import UnaryCheck
from lumipy.lumiflex.column import Column


class BaseFnAccessor:

    def __init__(self, label, column: Column, constraint: UnaryCheck):
        if not constraint(column):
            raise AttributeError(f'To use .{label} accessor the column {constraint.msg} type, but was {column.dtype.name}.')
        self._column = column

    def __repr__(self):
        name = type(self).__name__

        methods = inspect.getmembers(type(self), predicate=inspect.isfunction)
        names = [name for name, fn in methods if not name.startswith('_')]
        content = ', '.join(names)
        return f'{name}( {content} )'
