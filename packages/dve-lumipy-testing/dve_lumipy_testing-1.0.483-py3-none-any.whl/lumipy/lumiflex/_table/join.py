from __future__ import annotations

import typing
from collections import Counter
from typing import Literal, Tuple, Set, Optional

from pydantic import Field, StrictStr, model_validator

from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._common.widgets import display
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._table.base_table import BaseTable
from lumipy.lumiflex._table.widgets import join_table_widget
from lumipy.lumiflex.column import Column

if typing.TYPE_CHECKING:
    from lumipy.lumiflex._table.parameter import Parameter
    from lumipy.lumiflex.table import Table


class Join(BaseTable):
    """The Join class represents the result of joining two tables together.

    Join instances are responsible for validating inputs, adding prefixes to columns, and avoiding column name clashes.

    """

    label_: Literal['join_table'] = 'join_table'
    join_type_: Literal['inner', 'left'] = Field(alias='join_type')
    clashes_: Set[StrictStr] = set()

    @model_validator(mode='before')
    def _validate_join(self):
        from lumipy.lumiflex.table import Table

        join_type = self['join_type']
        lhs, rhs, on = self['parents']

        if not isinstance(lhs, BaseTable) or not isinstance(rhs, Table):
            raise TypeError()

        if isinstance(lhs, Table) and lhs.meta_.alias is None:
            raise ValueError(f'Both sides of the join must be aliased.')

        if rhs.meta_.alias is None:
            raise ValueError(f'Both sides of the join must be aliased.')

        if isinstance(lhs, Table) and lhs.meta_.alias == rhs.meta_.alias:
            raise ValueError(
                f'The two sides of the join must have different aliases, but were both \'{rhs.meta_.alias}\'.')

        parent_aliases = [t.meta_.alias for t in lhs._get_table_ancestors() if t.meta_.alias is not None]
        if rhs.meta_.alias in parent_aliases:
            parents_str = ', '.join(f'\'{p}\'' for p in parent_aliases)
            raise ValueError(
                f"Right table has an alias (\'{rhs.meta_.alias}\') that clashes with an existing parent table alias"
                f" ({parents_str})."
            )

        on = lhs._add_prefix(on)
        on = rhs._add_prefix(on)

        bad_cols = [a for a in on.get_ancestors() if a.label_ == 'data' and a not in lhs and a not in rhs]
        if len(bad_cols) > 0:
            anc = lhs._get_table_ancestors() + rhs._get_table_ancestors()
            table_lineage = [t.meta_.name for t in anc if t.meta_.alias is None]
            bad_col_strs = "\n    ".join(f'{c.sql} ({c.meta.table_name})' for c in bad_cols)
            raise ValueError(
                f"There are columns in the join\'s on condition that don\'t belong to any parent table ({', '.join(table_lineage)}):"
                f'\n    {bad_col_strs}'
            )

        self['from'] = f'{lhs.from_}\n  {join_type.upper()} JOIN\n{rhs.from_} ON {on.sql}'

        self['clashes_'] = set.intersection(
            {c.meta.field_name for c in lhs.get_columns()},
            {c.meta.field_name for c in rhs.get_columns()},
        )

        for c in lhs.get_columns():
            if c.meta.field_name in self['clashes_']:
                c = lhs._add_suffix(c)
            self[c.meta.python_name()] = c

        for c in rhs.get_columns():
            if c.meta.field_name in self['clashes_']:
                c = rhs._add_suffix(c)
            self[c.meta.python_name()] = c

        return self

    def _repr_mimebundle_(self, *args, **kwargs):
        return display(join_table_widget(self), *args, **kwargs)

    def _get_name(self):
        lhs, rhs = self.get_parents()[:2]
        return f'{lhs._get_name()} join {rhs._get_name()}'

    def get_join_condition(self):
        lhs, rhs, on = self.get_parents()
        on = lhs._add_prefix(on)
        on = rhs._add_prefix(on)
        return on

    def get_columns(self, main_only: Optional[bool] = False) -> Tuple[Column]:
        """Get a list of the columns that are members of this table.

        Args:
            main_only (Optional[bool]): whether to return just the main columns of the table. Defaults to False.

        Returns:
            Tuple[Column, ...]: a tuple of the table's columns.
        """
        return self.parents_[0].get_columns(main_only) + self.parents_[1].get_columns(main_only)

    def _get_param_assignments(self) -> Tuple[Parameter]:
        return self.parents_[0]._get_param_assignments() + self.parents_[1]._get_param_assignments()

    def _add_prefix(self, col: Column) -> Node:
        lhs, rhs = self.parents_[0:2]
        return lhs._add_prefix(rhs._add_prefix(col))

    def _add_suffix(self, col) -> Column:
        for t in self._get_table_ancestors():
            col = t._add_suffix(col)
        return col

    @input_constraints(..., Is.table, Is.boolean, ..., name='join.inner_join()')
    def inner_join(self, other: Table, on: Column, right_alias) -> Join:
        """Chain an inner join clause on to this join.

        Notes:
            other table must be a data provider table or a table var. This method won't accept another join table.

        Args:
            other (Table): The table on the right-hand side of the join.
            on (Column): The join condition. Must be a column or function of columns that resolves to bool.
            right_alias (str): the alias to grant the right table.

        Returns:
            Join: a join table instance representing this join.

        """
        client = self.client_ if self.client_ is not None else other.client_
        return Join(join_type='inner', client_=client, parents=(self, other.with_alias(right_alias), on))

    @input_constraints(..., Is.table, Is.boolean, ..., name='join.left_join()')
    def left_join(self, other: Table, on: Column, right_alias) -> Join:
        """Chain a left join clause on to this join.

        Notes:
            other table must be a data provider table or a table var. This method won't accept another join table.

        Args:
            other (Table): The table on the right-hand side of the join.
            on (Column): The join condition. Must be a column or function of columns that resolves to bool.
            right_alias (str): the alias to grant the right table.

        Returns:
            Join: a join table instance representing this join.

        """
        client = self.client_ if self.client_ is not None else other.client_
        return Join(join_type='left', client_=client, parents=(self, other.with_alias(right_alias), on))

    def _validate_inputs(self, name, *cols, **aliases):
        cols = super()._validate_inputs(name, *cols, **aliases)

        counts = Counter([c.meta.field_name for c in cols])
        clashes = [k for k, v in counts.items() if v > 1]
        cols = [self._add_suffix(c) if c.meta.field_name in clashes else c for c in cols]
        return cols

    def __contains__(self, item):
        lhs, rhs = self.parents_[:2]

        if isinstance(item, (Column, Ordering)):
            if item.label_ == 'data':
                return item in lhs or item in rhs
            else:
                return all(a in lhs or a in rhs for a in item.get_ancestors() if a.label_ == 'data')
        return False
