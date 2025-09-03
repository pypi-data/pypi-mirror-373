from __future__ import annotations

import typing
from abc import ABC
from typing import Callable, Literal
from typing import Optional, Union

from pandas import DataFrame
from pydantic import Field

from lumipy.client import Client
from lumipy.common import indent_str
from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._common.str_utils import to_snake_case
from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex._metadata.var_name import record
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._table.content import CompoundContent
from lumipy.lumiflex.column import Column

if typing.TYPE_CHECKING:
    from lumipy.lumiflex.table import Table


class TableOperation(Node, ABC):
    """Base class for all table operation statements such as select, where and so on.

    """

    client: Union[None, Client]

    @property
    def content(self):
        return self.get_parents()[-1]

    def go(self, timeout: Optional[int] = 3600, keep_for: Optional[int] = 7200, quiet: Optional[bool] = False) -> DataFrame:
        """Send query off to Luminesce, monitor progress and then get the result back as a pandas dataframe.

        Args:
            timeout (Optional[int]): max time for the query to run in seconds (defaults to 3600)
            keep_for (Optional[int]): time to keep the query result for in seconds (defaults to 7200)
            quiet (Optional[bool]): whether to print query progress or not

        Returns:
            DataFrame: the result of the query as a pandas dataframe.
        """
        return self.client.run(
            f"-- built with fluent syntax\n{self.get_sql()}",
            timeout=timeout,
            keep_for=keep_for,
            quiet=quiet
        )

    def go_async(self, timeout: Optional[int] = 3600, keep_for: Optional[int] = 7200, _print_fn: Optional[Callable] = None):
        """Just send the query to luminesce. Don't monitor progress or fetch result, just return a job object.

        Args:
            timeout (Optional[int]): max time for the query to run in seconds (defaults to 3600)
            keep_for (Optional[int]): time to keep the query result for in seconds (defaults to 7200)
            _print_fn (Optional[callable]): alternative print function for showing progress. This is mainly for internal use with
            the streamlit utility functions that show query progress in a cell. Defaults to the normal python print() fn.

        Returns:
            QueryJob: a job instance representing the query.
        """
        return self.client.run(
            f"-- built with fluent syntax\n{self.get_sql()}",
            timeout=timeout,
            keep_for=keep_for,
            return_job=True,
            _print_fn=_print_fn
        )

    def get_sql(self) -> str:
        """Get the Luminesce SQL that this object resolves to.

        Returns:
            str: the underlying SQL string.
        """
        return dependency_sql(self) + self.content.get_sql()

    def print_sql(self):
        """Print the Luminesce SQL that this object resolves to.

        """
        print(self.get_sql())

    def to_table_var(self, name: Optional[str] = None) -> Table:
        """Create a table variable from this query.

        Args:
            name (Optional[str]): the name to give to the table variable. If not given one will be generated.

        Returns:
            Table: a table instance representing this table variable.
        """
        from lumipy.lumiflex._table import TableVar
        tv_def = TableVar(client=self.client, name=name, parents=(self,))
        return tv_def.build()

    def to_scalar_var(self, name: Optional[str] = None) -> Column:
        from lumipy.lumiflex._table.variable import ScalarVar
        sv_def = ScalarVar(client=self.client, name=name, parents=(self,))
        return sv_def.build()

    def _repr_markdown_(self):
        # Pretty jupyter visual

        sql = self.get_sql()
        msg = f'#### Luminesce SQL\n\n'
        msg += f'```SQLite\n\n{indent_str(sql, 4)}\n```\n\n'
        msg += '---\n\n'

        # content table
        cols = self.content.get_columns()
        table_rows = [
            '| | Name | Data Type |',
            '| --- | :- | :- |'
        ]
        table_rows += [f'| {i} | {c.meta.field_name} | {c.dtype.name} |' for i, c in enumerate(cols)]
        content_str = '\n'.join(table_rows)

        msg += f'#### Column Content\n\n>{content_str}\n\n'
        msg += '---\n\n'
        msg += 'ℹ️ Call `.go()` to send this query to Luminesce.\n\n'
        msg += '---\n\n'
        return msg

    def to_drive(self, file_path: str) -> Select:
        """Add a drive write operation to the end of this query. This will write the query result to a specified
        location in Drive.

        Notes:
            The file type and file name will be inferred from the file_path input. Supported file types are CSV, XLSX,
            and Sqlite.

        Args:
            file_path (str): the full file path in drive to write to.

        Returns:
            Select: select instance that triggers the write when sent off with .go()
        """
        from lumipy.lumiflex._table.variable import DriveWriteVar
        tv = self.to_table_var(record.make_name('drive_input', self))
        return DriveWriteVar(file_path=file_path, client=self.client, parents=(tv,)).build().select('*')

    def setup_view(self, name: str) -> Select:
        """Add a create view operation to the end of this query. This will package up the query into a view which can
        then be queried like a data provider.

        Args:
            name (str): the name to give to the view. Must only contain letters, numbers and '.'

        Returns:
            Select: select instance that triggers the view creation when sent off with .go()
        """
        from lumipy.lumiflex._table.variable import MakeViewVar
        return MakeViewVar(view_name=name, client=self.client, parents=(self,)).build().select('*')

    def sample(self, n: Optional[int] = None, prob: Optional[float] = None) -> Select:
        """Add a sample operation to this query.

        Notes:
            Sample will put the query into a table variable and select a random sample of rows. The result of this is
            then put into another table var and a select statement is added to it. You can then either send this to
            luminesce or add on further statements such as where.

            You must give either a sample size (n) or a probability of sampling (prob), but not both.

        Args:
            n (Optional[int]): the number of rows to sample.
            prob (Optional[float]): the probability of sampling a given row.

        Returns:
            Select: select instance that represent the sample.

        """
        if (n is None and prob is None) or (n is not None and prob is not None):
            raise ValueError("You must specify either n or frac but not both!")

        if n is not None and (not isinstance(n, int) or n < 1):
            raise ValueError("n must be an integer that is greater than 1. Did you mean to use prob=?")

        if prob is not None and (prob < 0 or prob > 1):
            raise ValueError("Probability (prob) must be a value between 0 and 1.")

        q = self.to_table_var(record.make_name('sample_tv', self)).select('*')

        rand = Column(fn=lambda: '0.5  + random()/CAST(-18446744073709551616 AS REAL)', dtype=DType.Double, label='op')

        if prob is not None:
            sample = q.where(rand <= prob).order_by(rand.asc())
        if n is not None:
            sample = q.order_by(rand.asc()).limit(n)

        return sample.to_table_var(record.make_name('sample_tv', sample)).select('*')


class Select(TableOperation):
    """The Select class represents the select statement in a query. It encapsulates the selected columns and the methods
    (futher statements) that can be applied after.

    """

    label_: Literal['select'] = Field('select', alias='label')

    @input_constraints(..., Is.boolean, name='.where()')
    def where(self, condition: Column) -> Where:
        """Apply a where statement.

        Notes:
            Where is used to filter rows according to some condition.

        Args:
            condition (Column): the where statement filter condition.

        Returns:
            Where: instance representing this where statement
        """
        table = self.content.get_table()
        table._assert_in_table('.where()', condition)
        content = self.content.update_node(where_filter=table._add_prefix(condition))
        return Where(parents=(self, content), client=self.client)

    def group_by(self, *groups: Column, **aliases: Column) -> GroupBy:
        """Apply a group by statement.

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
        return _group_by_make(self, *groups, **aliases)

    def order_by(self, *orders: Ordering) -> OrderBy:
        """Apply an order by statement.

        Notes:
            ORDER BY is used to sort rows according to a given set of orderings.

            Orderings are built by calling .asc() or .desc() on columns in lumipy.

        Args:
            *orders (Ordering): ordering to apply. To be evaluated in left to right order.

        Returns:
            OrderBy: an order by instance that represents this order by statement.
        """
        return _order_by_make(self, *orders)

    def limit(self, limit: Union[int, None], offset: Optional[int] = None) -> Limit:
        """Apply a limit statement.

        Notes:
            LIMIT is used to restrict the number of rows returned by a query. The limit statement can also have an
            offset that discards N-many rows before returning y-many rows of the query.

        Args:
            limit (Union[int, None]): limit value to apply. If None then there is no limit applied (LIMIT -1).
            offset (Optional[int]): offset value to apply, defaults to None. If offset is None then no offset is applied.

        Returns:
            Limit: a limit instance that represents this limit statement.

        """
        return _limit_make(self, limit, offset)

    def union(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply a union statement.

        Notes:
            UNION returns the combined set of rows from both subqueries, but with duplicates filtered out.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the union with.

        Returns:
            SetOperation: instance representing the result of this union.

        """
        return _set_op_make('union', self, other)

    def union_all(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply a union all statement.

        Notes:
            UNION ALL returns the combined set of rows from both subqueries.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the union all with.

        Returns:
            SetOperation: instance representing the result of this union all.

        """
        return _set_op_make('union all', self, other)

    def intersect(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply an intersect statement.

        Notes:
            INTERSECT returns the set of rows that are in both subqueries.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the intersection with.

        Returns:
            SetOperation: instance representing the result of this intersect.

        """
        return _set_op_make('intersect', self, other)

    def exclude(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply an exclude (except) statement.

        Notes:
            EXCEPT returns the rows from the first subquery that are not present in the second.

        Args:
            other (Union[Select, Where, SetOperation]):

        Returns:
            SetOperation: instance representing the result of this exclude (except).

        """
        return _set_op_make('except', self, other)


class Where(TableOperation):
    """The Where class represents the where statement in a query. It encapsulates the where condition and the methods
    (futher statements) that can be applied after.

    """
    label_: Literal['where'] = Field('where', alias='label')

    def group_by(self, *groups: Column, **aliases: Column) -> GroupBy:
        """Apply a group by statement.

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
        return _group_by_make(self, *groups, **aliases)

    def order_by(self, *orders: Ordering) -> OrderBy:
        """Apply an order by statement.

        Notes:
            ORDER BY is used to sort rows according to a given set of orderings.

            Orderings are built by calling .asc() or .desc() on columns in lumipy.

        Args:
            *orders (Ordering): ordering to apply. To be evaluated in left to right order.

        Returns:
            OrderBy: an order by instance that represents this order by statement.
        """
        return _order_by_make(self, *orders)

    def limit(self, limit: Union[int, None], offset: Optional[int] = None) -> Limit:
        """Apply a limit statement.

        Notes:
            LIMIT is used to restrict the number of rows returned by a query. The limit statement can also have an
            offset that discards N-many rows before returning y-many rows of the query.

        Args:
            limit (Union[int, None]): limit value to apply. If None then there is no limit applied (LIMIT -1).
            offset (Optional[int]): offset value to apply, defaults to None. If offset is None then no offset is applied.

        Returns:
            Limit: a limit instance that represents this limit statement.

        """
        return _limit_make(self, limit, offset)

    def union(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply a union statement.

        Notes:
            UNION returns the combined set of rows from both subqueries, but with duplicates filtered out.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the union with.

        Returns:
            SetOperation: instance representing the result of this union.

        """
        return _set_op_make('union', self, other)

    def union_all(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply a union all statement.

        Notes:
            UNION ALL returns the combined set of rows from both subqueries.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the union all with.

        Returns:
            SetOperation: instance representing the result of this union all.

        """
        return _set_op_make('union all', self, other)

    def intersect(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply an intersect statement.

        Notes:
            INTERSECT returns the set of rows that are in both subqueries.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the intersection with.

        Returns:
            SetOperation: instance representing the result of this intersect.

        """
        return _set_op_make('intersect', self, other)

    def exclude(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply an exclude (except) statement.

        Notes:
            EXCEPT returns the rows from the first subquery that are not present in the second.

        Args:
            other (Union[Select, Where, SetOperation]):

        Returns:
            SetOperation: instance representing the result of this exclude (except).

        """
        return _set_op_make('except', self, other)


class GroupBy(TableOperation):
    """The GroupBy class represents the group by statement in a query. It encapsulates the group columns and the methods
    (futher statements) that can be applied after.

    """
    label_: Literal['group_by'] = Field('group_by', alias='label')

    @input_constraints(..., Is.boolean, name='.having()')
    def having(self, condition: Column) -> Having:
        """Apply a having statement.

        Notes:
            HAVING applies a filter condition at the group level.

            The condition must be a condition on a group function such as .sum() or .first()

        Args:
            condition (Column): the having statement filter condition.

        Returns:
            Having: instance representing the result of this having statement.
        """
        return _having_make(self, condition)

    def _aggregate(self, name, *args, **aggs: Column) -> Aggregate:

        if len(args) > 0:
            raise ValueError(
                '.agg() only accepts keyword arguments, this is so they are always given an alias. '
                'Try something like\n'
                '    .agg(MyValue=table.my_col.mean())'
            )

        table = self.content.get_table()
        aggs = table._validate_inputs(name, **aggs)
        bad = []
        for agg in aggs:
            if not any(n.get_label() == 'aggfunc' for n in agg.get_ancestors()):
                bad.append(f'{agg.meta.field_name}: {agg.get_parents()[0].sql}')

        if len(bad) > 0:
            non_aggs = '\n'.join(bad)
            raise ValueError(
                f'{name}() only accepts aggregate expressions (must contain at least one aggregate function such as sum).'
                f'\nThe following inputs resolved to non-aggregate values:\n{indent_str(non_aggs, 4)}'
            )

        content = self.content.update_node(aggregates=tuple(aggs))
        return Aggregate(parents=(self, content), client=self.client)

    def agg(self, *args, **aggs: Column) -> Aggregate:
        """Apply a set of aggregation functions.

        Notes:
            Adds group aggregation functions to the SELECT statement.

        Args:
            **aggs (Column): the aggregations to perform, with their aliases specified at the keyword.

        Returns:

        """
        return self._aggregate('.agg', *args, **aggs)

    def aggregate(self, *args, **aggs: Column) -> Aggregate:
        """Apply a set of aggregation functions.

        Notes:
            Adds group aggregation functions to the SELECT statement.

        Args:
            **aggs (Column): the aggregations to perform, with their aliases specified at the keyword.

        Returns:

        """
        return self._aggregate('.aggregate', *args, **aggs)

    def order_by(self, *orders: Ordering) -> OrderBy:
        """Apply an order by statement.

        Notes:
            ORDER BY is used to sort rows according to a given set of orderings.

            Orderings are built by calling .asc() or .desc() on columns in lumipy.

        Args:
            *orders (Ordering): ordering to apply. To be evaluated in left to right order.

        Returns:
            OrderBy: an order by instance that represents this order by statement.
        """
        return _order_by_make(self, *orders)


def _group_by_make(parent: TableOperation, *groups: Column, **aliases: Column):
    table = parent.content.get_table()
    groups = table._validate_inputs('.group_by()', *groups, **aliases)
    content = parent.content.update_node(group_by_cols=tuple(groups))
    return GroupBy(parents=(parent, content), client=parent.client)


class Aggregate(TableOperation):
    """The Aggregate class represents group aggregations in a query. It encapsulates the group aggregation columns and
    the methods (futher statements) that can be applied after.

    """
#    label_: StrictStr = Field('aggregate', const=True)
    label_: Literal['aggregate'] = Field('aggregate', alias='label')

    @input_constraints(..., Is.boolean, name='.having()')
    def having(self, condition: Column) -> Having:
        """Apply a having statement.

        Notes:
            HAVING applies a filter condition at the group level.

            The condition must be a condition on a group function such as .sum() or .first()

        Args:
            condition (Column): the having statement filter condition.

        Returns:
            Having: instance representing the result of this having statement.
        """
        return _having_make(self, condition)

    def order_by(self, *orders: Ordering) -> OrderBy:
        """Apply an order by statement.

        Notes:
            ORDER BY is used to sort rows according to a given set of orderings.

            Orderings are built by calling .asc() or .desc() on columns in lumipy.

        Args:
            *orders (Ordering): ordering to apply. To be evaluated in left to right order.

        Returns:
            OrderBy: an order by instance that represents this order by statement.
        """
        return _order_by_make(self, *orders)

    def limit(self, limit: Union[int, None], offset: Optional[int] = None) -> Limit:
        """Apply a limit statement.

        Notes:
            LIMIT is used to restrict the number of rows returned by a query. The limit statement can also have an
            offset that discards N-many rows before returning y-many rows of the query.

        Args:
            limit (Union[int, None]): limit value to apply. If None then there is no limit applied (LIMIT -1).
            offset (Optional[int]): offset value to apply, defaults to None. If offset is None then no offset is applied.

        Returns:
            Limit: a limit instance that represents this limit statement.

        """
        return _limit_make(self, limit, offset)


class Having(TableOperation):
    """The Having class represents the having statement in a query. It encapsulates the condition and the methods
    (futher statements) that can be applied after.

    """
#    label_: StrictStr = Field('having', const=True)
    label_: Literal['having'] = Field('having', alias='label')

    def order_by(self, *orders: Ordering) -> OrderBy:
        """Apply an order by statement.

        Notes:
            ORDER BY is used to sort rows according to a given set of orderings.

            Orderings are built by calling .asc() or .desc() on columns in lumipy.

        Args:
            *orders (Ordering): ordering to apply. To be evaluated in left to right order.

        Returns:
            OrderBy: an order by instance that represents this order by statement.
        """
        return _order_by_make(self, *orders)

    def limit(self, limit: Union[int, None], offset: Optional[int] = None) -> Limit:
        """Apply a limit statement.

        Notes:
            LIMIT is used to restrict the number of rows returned by a query. The limit statement can also have an
            offset that discards N-many rows before returning y-many rows of the query.

        Args:
            limit (Union[int, None]): limit value to apply. If None then there is no limit applied (LIMIT -1).
            offset (Optional[int]): offset value to apply, defaults to None. If offset is None then no offset is applied.

        Returns:
            Limit: a limit instance that represents this limit statement.

        """
        return _limit_make(self, limit, offset)


def _having_make(parent: TableOperation, condition: Column):
    table = parent.content.get_table()

    # assert condition is on a group agg value
    if not any(a.get_label() == 'aggfunc' for a in condition.get_ancestors()):
        raise ValueError(
            'The condition given to .having() must depend on group aggregate values (e.g. table.col.mean() > 0).'
        )

    # assert columns are in the table
    table._assert_in_table('.having()', condition)
    condition = table._add_prefix(condition)
    content = parent.content.update_node(having_filter=condition)
    return Having(parents=(parent, content), client=parent.client)


class OrderBy(TableOperation):
    """The OrderBy class represents the order by statement in a query. It encapsulates the content and the methods
    (futher statements) that can be applied after.

    """
#    label_: StrictStr = Field('order_by', const=True)
    label_: Literal['order_by'] = Field('order_by', alias='label')

    def limit(self, limit: Union[int, None], offset: Optional[int] = None) -> Limit:
        """Apply a limit statement.

        Notes:
            LIMIT is used to restrict the number of rows returned by a query. The limit statement can also have an
            offset that discards N-many rows before returning y-many rows of the query.

        Args:
            limit (Union[int, None]): limit value to apply. If None then there is no limit applied (LIMIT -1).
            offset (Optional[int]): offset value to apply, defaults to None. If offset is None then no offset is applied.

        Returns:
            Limit: a limit instance that represents this limit statement.

        """
        return _limit_make(self, limit, offset)


def _order_by_make(parent: TableOperation, *orders: Ordering) -> OrderBy:
    table = parent.content.get_table()

    table._assert_in_table('.order_by()', *orders)

    errs = []
    for i, o in enumerate(orders):
        if not isinstance(o, Ordering):
            errs.append(f"orders[{i}]: SQL='{o.sql}' ({o.get_label()} {type(o).__name__.lower()})")

    if len(errs) > 0:
        raise TypeError(
            f'All positional args (*orders) to .order_by() must be orderings. Some of the input values were not:\n'
            + indent_str('\n'.join(errs))
            + f'\nDid you forget to call .asc() or .desc()?'
        )

    content = parent.content.update_node(order_bys=tuple(table._add_prefix(o) for o in orders))
    return OrderBy(parents=(parent, content), client=parent.client)


class Limit(TableOperation):
    """The Limit class represents the limit statement in a query. It encapsulates the content and the methods
    (futher statements) that can be applied after.

    """
#    label_: StrictStr = Field('limit', const=True, alias='label')
    label_: Literal['limit'] = Field('limit', alias='label')


def _limit_make(parent: TableOperation, limit: int, offset: int) -> Limit:
    limit_dtype = DType.to_dtype(type(limit))
    offset_dtype = DType.to_dtype(type(offset))

    if (limit_dtype not in [DType.Null, DType.Int]) or (limit_dtype == DType.Int and limit <= 0):
        raise ValueError(f'limit value must be None, or an integer > 0. Was \'{limit}\' ({type(limit).__name__}).')
    if (offset_dtype != DType.Null) and (offset_dtype != DType.Int or offset < 0):
        raise ValueError(f'offset value must be None, or an integer >= 0. Was \'{offset}\' ({type(offset).__name__}).')
    content = parent.content.update_node(limit=limit, offset=offset)
    return Limit(parents=(parent, content), client=parent.client)


class SetOperation(TableOperation):
    """The SetOperation class represents the row set operations (union, union all, except, intersect) in a query. It
    encapsulates the content and the methods (futher statements) that can be applied after.

    """
    label_: Literal['row set op'] = Field('row set op', alias='label')

    def union(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply a union all statement.

        Notes:
            UNION ALL returns the combined set of rows from both subqueries.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the union all with.

        Returns:
            SetOperation: instance representing the result of this union all.

        """
        return _set_op_make('union', self, other)

    def union_all(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply a union all statement.

        Notes:
            UNION ALL returns the combined set of rows from both subqueries.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the union all with.

        Returns:
            SetOperation: instance representing the result of this union all.

        """
        return _set_op_make('union all', self, other)

    def intersect(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply an intersect statement.

        Notes:
            INTERSECT returns the set of rows that are in both subqueries.

        Args:
            other (Union[Select, Where, SetOperation]): the other subquery to take the intersection with.

        Returns:
            SetOperation: instance representing the result of this intersect.

        """
        return _set_op_make('intersect', self, other)

    def exclude(self, other: Union[Select, Where, SetOperation]) -> SetOperation:
        """Apply an exclude (except) statement.

        Notes:
            EXCEPT returns the rows from the first subquery that are not present in the second.

        Args:
            other (Union[Select, Where, SetOperation]):

        Returns:
            SetOperation: instance representing the result of this exclude (except).

        """
        return _set_op_make('except', self, other)

    def order_by(self, *orders) -> OrderBy:
        """Apply an order by statement.

        Notes:
            ORDER BY is used to sort rows according to a given set of orderings.

            Orderings are built by calling .asc() or .desc() on columns in lumipy.

        Args:
            *orders (Ordering): ordering to apply. To be evaluated in left to right order.

        Returns:
            OrderBy: an order by instance that represents this order by statement.
        """
        return _order_by_make(self, *orders)

    def limit(self, limit: Union[int, None], offset: Optional[int] = None) -> Limit:
        """Apply a limit statement.

        Notes:
            LIMIT is used to restrict the number of rows returned by a query. The limit statement can also have an
            offset that discards N-many rows before returning y-many rows of the query.

        Args:
            limit (Union[int, None]): limit value to apply. If None then there is no limit applied (LIMIT -1).
            offset (Optional[int]): offset value to apply, defaults to None. If offset is None then no offset is applied.

        Returns:
            Limit: a limit instance that represents this limit statement.

        """
        return _limit_make(self, limit, offset)


def _set_op_make(label: str, arg1: TableOperation, arg2: TableOperation) -> SetOperation:
    if not isinstance(arg2, (Select, Where, SetOperation)):
        raise TypeError(
            f'The input to a row set operation (compound SELECT) must be a result of select(), where(), union(), '
            f'union_all(), exclude() or intersect() but was a {to_snake_case(type(arg2).__name__)}() result.'
        )

    content = CompoundContent(label=label, parents=(arg1.content, arg2.content))
    return SetOperation(parents=(arg1, arg2, content), client=arg1.client)


def dependency_sql(node):

    from lumipy.lumiflex._table.variable import BaseVarDef

    def make_def_sql(v: BaseVarDef) -> str:
        return f'@{v.name} = {v.table_sql().strip()};\n'

    def node_filter(t: Node) -> bool:
        return isinstance(t, BaseVarDef) and hash(t) != hash(node)

    output = [make_def_sql(n) for n in node.topological_sort() if node_filter(n)]

    sql = f'--{" -" * 46}-\n'.join(output)
    if sql != '':
        return sql + f'--{"=" * 91}--\n\n'
    else:
        return sql
