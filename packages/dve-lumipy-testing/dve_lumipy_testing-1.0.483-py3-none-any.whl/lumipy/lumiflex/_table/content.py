from __future__ import annotations

import typing
from abc import ABC, abstractmethod
from typing import Tuple, Optional, List, Literal

from pydantic import Field, PositiveInt, NonNegativeInt
from pydantic import field_validator, model_validator

from lumipy.common import indent_str
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex.column import Column

if typing.TYPE_CHECKING:
    from lumipy.lumiflex._table.base_table import BaseTable


class BaseContent(Node, ABC):

    parents_: tuple = Field(alias='parents')
    order_bys: Optional[Tuple] = tuple()
    limit: Optional[PositiveInt] = None
    offset: Optional[NonNegativeInt] = None

    @abstractmethod
    def get_columns(self) -> List[Column]:
        raise NotImplementedError()

    @abstractmethod
    def _get_sql(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_table(self) -> BaseTable:
        raise NotImplementedError()

    @abstractmethod
    def is_compoundable(self):
        raise NotImplementedError()

    def get_sql(self) -> str:
        return self._get_sql() + self.order_by_str() + self.limit_str()

    def combine_columns(self, other: BaseContent) -> List[Column]:
        cols1 = self.get_columns()
        cols2 = other.get_columns()
        if len(cols1) != len(cols2):
            raise ValueError()

        out_cols = []
        for c1, c2 in zip(cols1, cols2):
            # Take name of the first parent, resolve dtypes by numeric / dt priority or text
            c = c1
            out_cols.append(c)

        return out_cols

    def order_by_str(self) -> str:
        if len(self.order_bys) > 0:
            return f"\nORDER BY\n{indent_str(', '.join(o.sql for o in self.order_bys))}"
        return ''

    def limit_str(self) -> str:

        parts = []
        if self.limit is not None:
            parts.append(f'LIMIT {self.limit}')
        if self.limit is None and self.offset is not None:
            parts.append('LIMIT -1')
        if self.offset is not None:
            parts.append(f'OFFSET {self.offset}')
        return '' if len(parts) == 0 else f'\n{" ".join(parts)}'


# noinspection SqlNoDataSourceInspection
class CoreContent(BaseContent):

    label_: Literal['content'] = Field('content', alias='label')
    table: BaseTable
    select_cols: Tuple
    where_filter: Optional[Column] = None
    group_by_cols: Optional[Tuple] = tuple()
    aggregates: Optional[Tuple] = tuple()
    having_filter: Optional[Column] = None

    # noinspection PyMethodParameters
    @model_validator(mode='before')
    def _validate_content(self):
        if 'select_cols' not in self or 'table' not in self:
            return self

        table = self['table']

        select_cols = self['select_cols']
        if len(select_cols) == 0:
            raise ValueError("Content must have at least one select col but was zero.")
        if any(c not in table for c in select_cols):
            raise ValueError("There are columns in select_cols that are not in the parent table")

        where_filter = self.get('where_filter')
        if where_filter is not None and where_filter.dtype != DType.Boolean:
            raise ValueError(f"Where filter input must resolve to a boolean, but was {where_filter.dtype.name}.")

        group_by_cols = self.get('group_by_cols')

        agg_cols = self.get('aggregates')

        having_filter = self.get('having_filter')

        order_bys = self.get('order_bys')

        # construct parents so column DAGs are linked to the main query DAG
        parents = tuple()
        if select_cols:
            parents += tuple(select_cols)
        if where_filter:
            parents += (where_filter,)
        if group_by_cols:
            parents += tuple(group_by_cols)
        if agg_cols:
            parents += tuple(agg_cols)
        if having_filter:
            parents += (having_filter,)
        if order_bys:
            parents += tuple(order_bys)

        self['parents'] = parents
        return self

    def get_columns(self) -> List[Column]:
        hashes, output = [], []
        for col in self.select_cols + self.group_by_cols + self.aggregates:
            if hash(col) not in hashes:
                output.append(col)
                hashes.append(hash(col))

        return output

    def get_table(self) -> BaseTable:
        return self.table

    def select_str(self) -> str:
        select_str = indent_str(', '.join(x.sql for x in self.get_columns()))
        from_str = indent_str(self.table.from_)
        return f"SELECT\n{select_str}\nFROM\n{from_str}"

    def where_str(self) -> str:
        params_set = '\nand '.join(p.sql for p in self.table._get_param_assignments())

        content = None
        if params_set == '' and self.where_filter is not None:
            content = self.where_filter.sql
        if params_set != '' and self.where_filter is not None:
            content = f'({params_set})\nand ({self.where_filter.sql})'
        elif params_set != '':
            content = params_set

        return '' if content is None else f'\nWHERE\n{indent_str(content)}'

    def group_by_str(self) -> str:
        if len(self.group_by_cols) == 0:
            return ''
        groups = [g.get_parents()[0] if g.label_ == 'alias' else g for g in self.group_by_cols]
        return f"\nGROUP BY\n{indent_str(', '.join(g.sql for g in groups))}"

    def having_str(self) -> str:
        if self.having_filter is None:
            return ''
        return f"\nHAVING\n{indent_str(self.having_filter.sql)}"

    def _get_sql(self) -> str:
        return self.select_str() \
               + self.where_str() \
               + self.group_by_str() \
               + self.having_str()

    def is_compoundable(self) -> bool:
        return self.having_filter is None and len(self.group_by_cols) == 0


class CompoundContent(BaseContent):

    label_: Literal['union', 'union all', 'intersect', 'except'] = Field(alias='label')

    @field_validator('parents_')
    def _validate_parents(cls, val):

        if len(val) != 2:
            raise ValueError(f'Compound content must have two parents, but received {len(val)}.')

        if any(not isinstance(p, BaseContent) for p in val):
            cls1, cls2 = type(val[0]), type(val[1])
            raise ValueError(
                f'Both parents of CompoundContent must be subclasses of BaseContent, '
                f'but were {cls1.__name__}, {cls2.__name__}.'
            )

        if any(not p.is_compoundable() for p in val):
            raise ValueError(f'One of the compound content inputs wasn\'t compoundable '
                             f'(a subquery that contains a group by, having, order by or limit clause).')

        return val

    def get_columns(self) -> List[Column]:
        c1, c2 = self.get_parents()
        return c1.combine_columns(c2)

    def get_table(self) -> BaseTable:
        return self.get_parents()[0].get_table()

    def _get_sql(self) -> str:
        def sql(a: BaseContent):
            string = a.get_sql()
            if self.get_label() in ['intersect', 'except'] and a.get_label() != 'content':
                string = f'(\n{string}\n)'
            if a.get_label() not in ['union', 'union all']:
                string = indent_str(string, 4)

            return string

        arg1, arg2 = self.get_parents()
        return f'{sql(arg1)}\n{self.get_label().upper()}\n{sql(arg2)}'

    def is_compoundable(self) -> bool:
        return True
