from __future__ import annotations

from functools import reduce
from typing import Tuple, Union, Literal

from pydantic import Field, model_validator

from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._common.widgets import display
from lumipy.lumiflex._metadata import TableMeta
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._table.base_table import BaseTable
from lumipy.lumiflex._table.join import Join
from lumipy.lumiflex._table.parameter import Parameter
from lumipy.lumiflex._table.widgets import table_widget
from lumipy.lumiflex.column import Column


class Table(BaseTable):
    """The table class represents a table of data from a data provider or a table variable.

    Tables are a data source in the lumiflex syntax. You build queries from them by chaining .select() and then
    (optionally) other methods to build up your Luminesce SQL query.

    Attributes:
        A dynamic set of column objects that can be used as arguments to methods such as select. Columns live as
        snake case named attributes on the table, or as str indexed objects much like a pandas DataFrame.

    @DynamicAttrs
    """

    label_: Literal['data_table'] = Field('data_table', alias='label')
    meta_: TableMeta = Field(alias='meta')
    parameters_: tuple = Field(alias='parameters')
    params_hash_: Union[None, int] = Field(None, alias='params_hash')

    def _repr_mimebundle_(self, *args, **kwargs):
        return display(table_widget(self, True), *args, **kwargs)

    @model_validator(mode='before')
    def _validate_table(self):

        meta = self['meta']
        parents = self.get('parents', tuple())
        params = tuple(self['parameters'])
        params_hash = hash(params)

        self['from'] = f'@{meta.name}' if meta.type == 'TableVar' else f'[{meta.name}]'

        cols = tuple(c.update(params_hash=params_hash, prefix=meta.alias) for c in meta.columns)
        meta = meta.update(columns=cols)
        for c in meta.columns:
            self[c.python_name()] = make(c)

        self['params_hash'] = params_hash

        if meta.alias is not None:
            self['from'] += f' AS {meta.alias}'
            self['parameters'] = tuple(p.with_prefix(meta.alias) for p in params)

        if any(p.get_label() != 'parameter' for p in params):
            raise TypeError('Some of the input parameters were not Parameter objects. '
                            'something has gone wrong with upstream validation.')

        self['parents'] = parents + params

        self['meta'] = meta
        return self

    def _get_name(self):
        return self.meta_.name

    @input_constraints(..., Is.table, Is.boolean, ..., ..., name='table.left_join()')
    def left_join(self, other: Table, on: Column, left_alias='lhs', right_alias='rhs') -> Join:
        """Apply a left join between this table and another.

        Args:
            other (Table): The table on the right-hand side of the join.
            on (Column): The join condition. Must be a column or function of columns that resolves to bool.
            left_alias (str): the alias to grant the left table if it hasn't already been given one.
            right_alias (str): the alias to grant the right tabl if it hasn't already been given one.

        Returns:
            Join: a join table instance representing this join.

        """
        lhs = self.with_alias(left_alias) if self.meta_.alias is None else self
        rhs = other.with_alias(right_alias) if other.meta_.alias is None else other
        client = self.client_ if self.client_ is not None else other.client_
        return Join(join_type='left', client_=client, parents=(lhs, rhs, on))

    @input_constraints(..., Is.table, Is.boolean, ..., ..., name='table.inner_join()')
    def inner_join(self, other: Table, on: Column, left_alias='lhs', right_alias='rhs') -> Join:
        """Apply an inner join between this table and another.

        Args:
            other (Table): The table on the right-hand side of the join.
            on (Column): The join condition. Must be a column or function of columns that resolves to bool.
            left_alias (str): the alias to grant the left table if it hasn't already been given one.
            right_alias (str): the alias to grant the right tabl if it hasn't already been given one.

        Returns:
            Join: a join table instance representing this join.

        """
        lhs = self.with_alias(left_alias) if self.meta_.alias is None else self
        rhs = other.with_alias(right_alias) if other.meta_.alias is None else other
        client = self.client_ if self.client_ is not None else other.client_
        return Join(join_type='inner', client_=client, parents=(lhs, rhs, on))

    def with_alias(self, alias: str) -> Table:
        meta = self.meta_.update_fields(alias=alias)
        return Table(meta=meta, client_=self.client_, parameters=self.parameters_, parents=(self,))

    def _get_param_assignments(self) -> Tuple[Parameter]:
        return self.parameters_

    def __contains__(self, item: Union[Column, str]) -> bool:

        def is_in(x):
            return x.meta.table_name == self.meta_.name and x.meta.params_hash == self.params_hash_

        if isinstance(item, (Column, Ordering)):
            if item.label_ == 'data':
                return is_in(item)
            else:
                # Remove ancestors that come from const nodes
                # As far as this table's concerned scalar vars and sub-queries are just constant values.
                # It should not be decomposing them and checking their dependencies.
                get_data_nodes = lambda a: [an for an in a.get_ancestors() if an.get_label() == 'data']
                consts = [get_data_nodes(a) for a in item.get_ancestors() if a.get_label() == 'const']
                consts = set(reduce(lambda x, y: x + y, consts, []))

                return all(is_in(a) for a in item.get_ancestors() if a.label_ == 'data' and a not in consts)
        return False

    def _add_prefix(self, item) -> Node:
        if self.meta_.alias is None:
            return item

        def _prefix(c: Column, parents):
            if c.label_ != 'data':
                return c.update_node(parents=parents)
            if c in self:
                return make(c.meta.update(prefix=self.meta_.alias))
            return c

        return item.apply_map(_prefix)

    def _add_suffix(self, c: Column):
        if self.meta_.alias is None or c.get_label() != 'prefix':
            return c
        return c._with_alias(f'{c.meta.field_name}_{c.meta.prefix}')
