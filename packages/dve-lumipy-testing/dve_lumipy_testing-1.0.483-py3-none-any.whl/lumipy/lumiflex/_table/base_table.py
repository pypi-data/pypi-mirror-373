from __future__ import annotations

import typing
from abc import ABC, abstractmethod
from datetime import date, datetime
from difflib import SequenceMatcher
from typing import Union, Optional, Tuple, List

from pydantic import Field, StrictStr, model_validator

from lumipy.client import Client
from lumipy.common import indent_str
from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._common.str_utils import model_repr, to_snake_case
from lumipy.lumiflex._table.content import CoreContent
from lumipy.lumiflex._table.operation import Select, GroupBy
from lumipy.lumiflex.column import Column

if typing.TYPE_CHECKING:
    from lumipy.lumiflex._table.parameter import Parameter
    from lumipy.lumiflex.table import Table


class BaseTable(Node, ABC):
    """Base class for table objects such as providers, table vars and joins.

    """
    client_: Union[None, Client]
    from_: Optional[StrictStr] = Field(alias='from')

    class Config:
        frozen = True
        extra = 'allow'
        arbitrary_types_allowed = True
        allow_reuse = True

    def __repr__(self):
        return model_repr(self, 'client_')

    def __hash__(self):
        return hash(tuple(self.from_, ) + tuple(hash(c) for c in self.get_columns()) + tuple(
            hash(p) for p in self._get_param_assignments()))

    @model_validator(mode='after')
    def _add_attrs_for_tab_completion(self):
        for k, v in self.model_extra.items():
            self.__dict__[k] = v
        return self

    @abstractmethod
    def _get_param_assignments(self) -> Tuple[Parameter]:
        raise NotImplementedError()

    @abstractmethod
    def _add_prefix(self, col) -> Node:
        raise NotImplementedError()

    @abstractmethod
    def _add_suffix(self, col) -> Column:
        raise NotImplementedError()

    def _validate_inputs(self, name, *cols, **aliases) -> List[Column]:

        if len(cols) > 0 and isinstance(cols[0], str) and cols[0] == '*':
            cols = self.get_columns()
        elif len(cols) > 0 and isinstance(cols[0], str) and cols[0] == '^':
            main_cols = self.get_columns(True)
            if len(main_cols) == 0:
                cols = self.get_columns()
            else:
                cols = main_cols + cols[1:]

        errs = []
        for i, a in enumerate(cols):
            if not isinstance(a, Column):
                errs.append(f'cols[{i}] = {a} ({type(a).__name__})')
                continue

            if a.label_ not in ['data', 'alias', 'prefix']:
                errs.append(f'cols[{i}] = {a.sql} (Column {a.label_})')

        if len(errs) > 0:
            msg = ''
            col_type_msg = "\n  ".join(errs)
            msg += f'Inputs to *cols must be original table columns (not calculations or python values), but were\n  {col_type_msg}\n'
            msg += "Only table columns can be supplied as unnamed cols. Other columns types such as"
            msg += " functions of columns or python literals must be supplied as keyword args (except '*' and '^').\n"
            msg += "Try something like one of the following:\n"
            msg += "  •Scalar functions of columns: \n"
            msg += f"     table.select(col_doubled=provider.col*2)\n"
            msg += "  •Aggregate functions of columns: \n"
            msg += f"     table.select(col_sum=provider.col.sum())\n"
            msg += "  •Python literals: \n"
            msg += f"     table.select(higgs_mass=125.1)\n"
            raise ValueError(msg)

        aliases = {k: make(v) for k, v in aliases.items()}

        cols = [self._add_prefix(c) for c in cols]
        aliases = {k: self._add_prefix(c) for k, c in aliases.items()}
        cols += [v._with_alias(k) for k, v in aliases.items()]

        self._assert_in_table(name, *cols)

        return cols

    def _assert_in_table(self, name, *cols):
        errs = []
        for c in cols:
            if c not in self:
                if c.get_label() == 'data':
                    tables = c.meta.table_name
                else:
                    tables = " + ".join(sorted([d.meta.table_name for d in c._get_data_col_dependencies()]))
                errs.append(f'{c.sql} has dependence on {tables}')

        if len(errs) > 0:
            err_str = indent_str("\n".join(errs), 4)
            raise ValueError(
                f'There are columns in the input to {name} that do not belong to the table ({self._get_name()}):'
                f'\n{err_str}'
                '\nThe column may be from the same provider but a with a different set of parameter values and '
                'therefore constitutes a different table.'
            )

    @abstractmethod
    def __contains__(self, item):
        raise NotImplementedError()

    @abstractmethod
    def _get_name(self):
        pass

    def select(self, *cols: Union[str, Column], **aliases: Union[Column, str, int, float, bool, date, datetime]) -> Select:
        """Apply a select statement to the table.

        Notes:
            SELECT is used to query data from a table as is used to specify a selection of columns and/or calculations
            on columns.

            The .select() method takes both, but only original (data) columns of the table object can be used as positional
            args. Functions of data columns and python primitives must be given as keyword args where the keyword is the
            name you are giving to the column.

        Args:
            *cols (Union[str, Column]): columns to select. Can be column objects of this table, or either of two string values:
            '*' (select all columns), '^' (select main columns)
            **aliases (Union[Column, str, int, float, bool, date, datetime]): column values and their aliases (keyword used in input)

        Returns:
            Select: a select table op instance that represents this select statement.

        """
        cols = self._validate_inputs('.select()', *cols, **aliases)
        content = CoreContent(select_cols=cols, parents=(self,), table=self)
        return Select(parents=(self, content), client=self.client_)

    def group_by(self, *cols: Column, **aliases: Column) -> GroupBy:
        """Apply a group by statement to this table.

        Notes:
            GROUP BY is used to group rows by the values in one or more columns or derived columns.

            This method will generate a counterpart select statement that contains the same columns as the group by statement.

            The .group_by() method takes both table column and results of calculations, but only original (data) columns
            of the table object can be used as positional args. Functions of data columns must be given as keyword args
            where the keyword is the name you are giving to the column.

        Args:
            *cols (Column): columns to group by. Can be column objects of this table.
            **aliases (Union[Column, str, int, float, bool, date, datetime]): column values and their aliases (keyword used in input)

        Returns:
            GroupBy: a group by table op instance that represents this group by statement.

        """
        _cols = self._validate_inputs('.group_by()', *cols, **aliases)
        return self.select(*cols, **aliases).group_by(*cols, **aliases)

    def get_columns(self, main_only: Optional[bool] = False) -> Tuple[Column, ...]:
        """Get a list of the columns that are members of this table.

        Args:
            main_only (Optional[bool]): whether to return just the main columns of the table. Defaults to False.

        Returns:
            Tuple[Column, ...]: a tuple of the table's columns.
        """
        cols = tuple(self._add_prefix(c) for c in self.model_extra.values() if isinstance(c, Column))
        if main_only:
            return tuple(c for c in cols if c.meta.is_main)
        return cols

    def _get_table_ancestors(self) -> Tuple[Table]:
        from lumipy.lumiflex.table import Table
        return tuple(t for t in self.get_ancestors() if isinstance(t, Table))

    def __getitem__(self, item: str) -> Column:
        py_names = [c.meta.python_name() for c in self.get_columns()]

        name = to_snake_case(item)
        if name in py_names:
            return getattr(self, name)

        available = {c.meta.python_name(): c.meta.field_name for c in self.get_columns()}

        def dist(target, *patterns):
            dists = {p: SequenceMatcher(a=target, b=p).ratio() for p in patterns}
            return [k for k, v in sorted(dists.items(), key=lambda x: x[1], reverse=True)]

        suggestions = dist(item, *py_names)[:3]

        suggestions_str = '\n'.join(f'table.{s} / table["{available[s]}"]' for s in suggestions)
        raise AttributeError(
            f"{self._get_name()} has no column called '{item}'."
            f"\nDid you mean to use one of:\n{indent_str(suggestions_str)}"
        )

CoreContent.model_rebuild()
