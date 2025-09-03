import inspect

from lumipy.lumiflex._window.window import Window


class BaseWinFnAccessor:

    def __init__(self, window: Window):
        self._window = window

    def __repr__(self):
        name = type(self).__name__

        methods = inspect.getmembers(type(self), predicate=inspect.isfunction)
        names = [name for name, fn in methods if not name.startswith('_')]
        content = ', '.join(names)
        return f'{name}( {content} )'
