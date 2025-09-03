from __future__ import annotations

from datetime import datetime, date
from typing import Union, Any, Callable

from lumipy.lumiflex._metadata import ColumnMeta, DType
from lumipy.lumiflex.column import Column


def make(x: Union[int, float, bool, str, datetime, date, ColumnMeta, Column, None]) -> Column:
    if isinstance(x, Column):
        if x.label_ != 'op':
            return x
        return Column(fn=lambda v: f'({v.sql})', parents=(x,), dtype=x.dtype, label='func')

    def setter(value: Any) -> Callable:
        return lambda: value

    if isinstance(x, ColumnMeta) and x.prefix is None:
        return Column(fn=setter(f'[{x.field_name}]'), dtype=x.dtype, meta=x, label='data')

    if isinstance(x, ColumnMeta) and x.prefix is not None:
        return Column(fn=setter(f'{x.prefix}.[{x.field_name}]'), label='prefix', dtype=x.dtype, meta=x)

    if isinstance(x, bool):
        return Column(fn=setter('TRUE' if x else 'FALSE'), dtype=DType.Boolean, meta=x, label='const')

    if isinstance(x, int):
        return Column(fn=setter(str(x)), dtype=DType.Int, meta=x, label='const')

    if isinstance(x, float):
        val_str = f"{x:1.15f}".rstrip('0')
        if val_str.endswith('.'):
            val_str += '0'
        return Column(fn=setter(val_str), dtype=DType.Double, meta=x, label='const')

    if isinstance(x, str):
        return Column(fn=setter(f"'{x}'"), dtype=DType.Text, meta=x, label='const')

    if isinstance(x, datetime):
        fmt = '%Y-%m-%d %H:%M:%S.%f'
        return Column(fn=setter(f"#{x.strftime(fmt)}#"), dtype=DType.DateTime, meta=x, label='const')

    if isinstance(x, date):
        fmt = '%Y-%m-%d'
        return Column(fn=setter(f"#{x.strftime(fmt)}#"), dtype=DType.Date, meta=x, label='const')

    if x is None:
        return Column(fn=setter('NULL'), dtype=DType.Null, meta=x, label='const')

    raise TypeError(
        f'Unsupported type! Can\'t make Column object for object of type \'{type(x).__name__}\', (value={x})'
    )
