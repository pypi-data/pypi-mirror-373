from __future__ import annotations

from typing import Optional, Union, List, Literal

from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._window.window import Window, OverPartition, OverOrder, OverFilter, OverFrame
from lumipy.lumiflex.column import Column


def window(
        groups: Optional[Union[Column, List[Column]]] = None,
        orders: Optional[Union[Ordering, List[Ordering]]] = None,
        lower: Optional[Union[None, int]] = None,
        upper: Optional[Union[None, int]] = 0,
        exclude: Literal['no others', 'group', 'ties'] = 'no others'
) -> Window:
    """Create a window object that may be used to construct window functions.

    Notes:
        to add a filter clause to this window call .filter() on the window instance made by this function.

    Args:
        groups (Optional[Union[Column, List[Column]]]): columns and calculated values to partition the window by. Defaults to None.
        orders (Optional[Union[Ordering, List[Ordering]]]): column/calculation orderings to order the window by. Defaults to None.
        lower (Optional[Union[None, int]]): lower bound of the window frame specified as an integer number of rows before current, or None (unbounded).
        upper (Optional[Union[None, int]]): upper bound of the window frame specified as an integer number of rows after current, or None (unbounded).
        exclude (Literal['no others', 'group', 'ties']): which rows to exclude from the window (default = 'no others').
        See SQLite's documentation at https://www.sqlite.org/windowfunctions.html for more information on what each exclude
        option does.

    Returns:
        Window: a window instance that represents the SQL OVER clause with the given values.

    """
    if isinstance(groups, Column):
        groups = [groups]
    if isinstance(orders, Ordering):
        orders = [orders]

    partition = OverPartition(parents=groups) if groups is not None else OverPartition()
    orders = OverOrder(parents=orders) if orders is not None else OverOrder()
    frame = OverFrame(lower=lower, upper=upper, exclude=exclude)
    return Window(parents=(partition, orders, frame, OverFilter()))