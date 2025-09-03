from typing import Literal

from pydantic import field_validator, Field

from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex.column import Column


class Ordering(Node):
    """A column ordering node.

    To be used as arguments to .order_by(*args) or in window(orders=)

    """

    label_: Literal["asc", "desc"] = Field(alias='label')

    @field_validator('parents_')
    def _validate_parents(cls, val):
        if len(val) != 1:
            raise ValueError(f'Ordering must have exactly one parent, received {len(val)}.')

        if not isinstance(val[0], Column):
            clss_str = type(val[0]).__name__
            raise TypeError(f'Parent must be Column type but was {clss_str}.')

        return val

    @property
    def sql(self) -> str:
        col = self.parents_[0]
        val_str = col.sql
        if col.label_ == 'op':
            val_str = f'({val_str})'
        return f'{val_str} {self.label_.upper()}'

    def _get_data_col_dependencies(self):
        return self.parents_[0]._get_data_col_dependencies()
