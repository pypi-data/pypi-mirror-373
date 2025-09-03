from typing import Union, Optional

from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._window.window import WindowColumn
from lumipy.lumiflex.column import Column
from .base_win_fn_accessor import BaseWinFnAccessor


class StrWinFnAccessor(BaseWinFnAccessor):

    @input_constraints(..., Is.text, Is.text, name='.str.group_concat()')
    def group_concat(self, values: Union[Column, str], sep: Optional[str] = ','):
        """Apply a group concat function in this window.

        Notes:
            This will return the string values in this window concatenated together with a separator (',' by default).

        Args:
            values (Union [Column, str]): the string values to concatenate. If the input is a python literal it'll just
            be repeated n-many times where n is the size of the window.
            sep (Optional[str]): separator to put between values in the concatenation. Defaults to ','.

        Returns:
            WindowColumn: window column instance representing this calculation.
        """
        fn = lambda x, y: f'group_concat({x.sql}, {y.sql})'
        return WindowColumn(fn=fn, parents=(self._window, values, sep), dtype=DType.Text)
