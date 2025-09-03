from __future__ import annotations

import typing
from datetime import date, datetime
from typing import Optional, Union, Literal, Any

from pydantic import Field, field_validator, StrictInt, model_validator

from lumipy.common import indent_str
from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._common.widgets import display
from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._window.widgets import window_object_widget
from lumipy.lumiflex.column import Column

if typing.TYPE_CHECKING:
    from lumipy.lumiflex._window.accessors.stats_win_fn_accessor import StatsWinFnAccessor
    from lumipy.lumiflex._window.accessors.finance_win_fn_accessor import FinanceWinFnAccessor
    from lumipy.lumiflex._window.accessors.linreg_win_fn_accessor import LinregWinFnAccessor
    from lumipy.lumiflex._window.accessors.metrics_win_fn_accessor import MetricsWinFnAccessor
    from lumipy.lumiflex._window.accessors.str_win_fn_accessor import StrWinFnAccessor


class OverPartition(Node):

    label_: Literal['over partition'] = Field("over partition", alias='label')

    @field_validator('parents_')
    def validate_partition(cls, val):

        if not all(isinstance(v, Column) and not isinstance(v, WindowColumn) for v in val):
            bad_types = ', '.join(type(v).__name__ for v in val)
            raise ValueError(
                "Over partition values must be table data columns or functions of them, but not window functions. "
                f"Received {bad_types}"
            )

        return val

    def has_content(self):
        return len(self.parents_) > 0

    def get_sql(self):
        return f"PARTITION BY {', '.join(p.sql for p in self.get_parents())}"


class OverOrder(Node):
    label_: Literal['over order'] = Field("over order", alias='label')

    @field_validator('parents_')
    def _validate_ordering(cls, val):
        if not all(isinstance(v, Ordering) for v in val):
            bad_types = ', '.join(type(v).__name__ for v in val)
            raise ValueError(
                f"Over ordering values must be column orderings. Received {bad_types}"
            )

        return val

    def has_content(self):
        return len(self.parents_) > 0

    def get_sql(self):
        return f"ORDER BY {', '.join(p.sql for p in self.get_parents())}"


class OverFrame(Node):
    label_: Literal['over frame'] = Field("over frame", alias='label')
    upper: Union[None, StrictInt] = 0
    lower: Union[None, StrictInt] = None
    exclude: Literal['no others', 'group', 'ties'] = Field('no others')

    @field_validator('lower')
    def _validate_lower(cls, val):
        if val is not None and val < 0:
            raise ValueError(f'Value for lower cannot be negative, but was {val}.')
        return val

    @field_validator('upper')
    def _validate_upper(cls, val):
        if val is not None and val < 0:
            raise ValueError(f'Value for upper lower cannot be negative, but was {val}.')
        return val

    def has_content(self):
        return True

    def get_sql(self):
        def bound_str(index, side):
            if index is None:
                return f'UNBOUNDED {side}'
            elif index == 0:
                return 'CURRENT ROW'
            elif index > 0:
                return f'{index} {side}'
            else:
                raise ValueError('Index must be an integer >= 0 or None')

        return f"ROWS BETWEEN {bound_str(self.lower, 'PRECEDING')} AND {bound_str(self.upper, 'FOLLOWING')} EXCLUDE {self.exclude.upper()}"


class OverFilter(Node):
    label_: Literal['over filter'] = Field("over filter", alias='label')
    parents_: tuple = Field(tuple(), alias='parents')

    @field_validator('parents_')
    def _validate_filter(cls, val):
        if len(val) > 1:
            raise ValueError('Filter can either be empty or have exactly one input')

        if len(val) == 1 and val[0].dtype != DType.Boolean:
            raise ValueError(f'Input to over filter must resolve to a boolean, but was {val[0].dtype.name}.')

        return val

    def has_content(self):
        return len(self.parents_) > 0

    def get_sql(self):
        return f'FILTER(WHERE {self.get_parents()[0].sql})'

    def get_filter(self):
        if self.has_content():
            return self.parents_[0]
        raise ValueError("There is no window filter to get!")


class Window(Node):
    """The window class represents OVER in luminesce SQL. It encapsulates the values to use in partitions, ordering and
    the boundaries of the frame. It also contains methods and accessor properties for various different window functions.

    """

    label_: Literal['over'] = Field("over", alias='label')
    parents_: tuple = Field(alias='parents')

    @model_validator(mode='before')
    def _validate_over(self):
        if len(self['parents']) != 4:
            raise ValueError(
                'There are missing inputs. Over must have four parent nodes: partition, order by, frame and filter'
            )

        partition, order_by, frame, filter = self['parents']
        if not isinstance(partition, OverPartition):
            raise TypeError(f'parent[0] (partition) must be an OverPartition instance. Was {type(partition).__name__}')
        if not isinstance(order_by, OverOrder):
            raise TypeError(f'parent[1] (order_by) must be an OverOrder instance. Was {type(order_by).__name__}')
        if not isinstance(frame, OverFrame):
            raise TypeError(f'parent[2] (frame) must be an OverFrame instance. Was {type(frame).__name__}')
        if not isinstance(filter, OverFilter):
            raise TypeError(f'parent[3] (filter) must be an OverFilter instance. Was {type(filter).__name__}')

        return self

    def _repr_mimebundle_(self, *args, **kwargs):
        return display(window_object_widget(self, True), *args, **kwargs)

    def get_sql(self) -> str:
        """Get the Luminesce SQL that this object resolves to.

        Returns:
            str: the underlying SQL string.
        """
        parents = self.get_parents()

        content = '\n'.join(p.get_sql() for p in parents[:-1] if p.has_content())
        content = f"OVER(\n{indent_str(content, 4)}\n    )\n"

        fltr = self.get_parents()[-1]
        if fltr.has_content():
            content = f'{fltr.get_sql()} {content}'
        return content

    @property
    def str(self) -> StrWinFnAccessor:
        """Window string function accessor property. Encapsulates the set of string window function methods.

        You can chain methods on the accessor property. For example, to compute the group concat of strings in a window
            win.str.group_concat(x)

        Returns:
            StrWinFnAccessor: the str window function accessor instance.
        """
        from lumipy.lumiflex._window.accessors.str_win_fn_accessor import StrWinFnAccessor
        return StrWinFnAccessor(self)

    @property
    def stats(self) -> StatsWinFnAccessor:
        """Window statistical function accessor property. Encapsulates the set of statistical function methods.

        You can chain methods on the accessor property. For example, to compute the skewness of a column
            win.stats.skewness(x)

        If this column is not a numeric dtype an error will be thrown.

        Returns:
            StatsWinFnAccessor: the stats window function accessor instance.
        """
        from lumipy.lumiflex._window.accessors.stats_win_fn_accessor import StatsWinFnAccessor
        return StatsWinFnAccessor(self)

    @property
    def finance(self) -> FinanceWinFnAccessor:
        """Window finance function accessor property. Encapsulates the set of finance function methods.

        You can chain methods on the accessor property. For example, to compute the max drawdown for a price series
            window.finance.max_drawdown(prices)

        If this column is not a numeric dtype an error will be thrown.

        Returns:
            FinanceWinFnAccessor: the finance window function accessor instance.
        """
        from lumipy.lumiflex._window.accessors.finance_win_fn_accessor import FinanceWinFnAccessor
        return FinanceWinFnAccessor(self)

    @property
    def linreg(self) -> LinregWinFnAccessor:
        """Window linear regression function accessor property. Encapsulates the set of linear regression function methods.

        You can chain methods on the accessor property. For example, to compute the alpha (gradient) between two columns
            window.linreg.alpha(x, y)

        If these columns are not numeric dtypes an error will be thrown.

        Returns:
            LinregWinFnAccessor: the linreg window function accessor instance.
        """
        from lumipy.lumiflex._window.accessors.linreg_win_fn_accessor import LinregWinFnAccessor
        return LinregWinFnAccessor(self)

    @property
    def metric(self) -> MetricsWinFnAccessor:
        """Metric metric (i.e. distance and similarity measures) function accessor property. Encapsulates the set of
        metric function methods.

        You can chain methods on the accessor property. For example, to compute the manhattan distance between two columns
            window.metric.manhattan_distance(x, yy)

        If these columns are not numeric dtypes an error will be thrown.

        Returns:
            MetricsWinFnAccessor: the metric function accessor instance.
        """
        from lumipy.lumiflex._window.accessors.metrics_win_fn_accessor import MetricsWinFnAccessor
        return MetricsWinFnAccessor(self)

    @input_constraints(..., Is.any, name='first()')
    def first(self, values: Column) -> WindowColumn:
        """Apply a first function in this window.

        Notes:
            first will return the first value in a window.

        Args:
            values (Column): the column or function of columns to return data from.

        Returns:
            WindowColumn: window column instance representing this value.
        """
        return WindowColumn(
            fn=lambda x: f'first_value({x.sql})',
            parents=(self, values),
            dtype=values.dtype,
        )

    @input_constraints(..., Is.any, name='last()')
    def last(self, values: Column) -> WindowColumn:
        """Apply a last function in this window.

        Notes:
            last will return the last value in a window.

        Args:
            values (Column): the column or function of columns to return data from.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return WindowColumn(
            fn=lambda x: f'last_value({x.sql})',
            parents=(self, values),
            dtype=values.dtype,
        )

    @input_constraints(..., Is.any, Is.integer, Is.any, name='lag()')
    def lag(self, values: Column, offset: Optional[int] = 1, default: Union[Column, str, int, float, bool, date, datetime, None] = None) -> WindowColumn:
        """Apply a lag function in this window.

        Notes:
            the lag function returns the value n-many rows after (offset) current row in a window.

            If the size of the lag is outside the size of the window it will evaluate to NULL, or a user-specified
            default value.

        Args:
            values (Column): the column or function of columns to return data from.
            offset (Optional[int]): offset bewteen the lag row and current row. Defaults to 1.
            default (Union[Column, str, int, float, bool, date, datetime, None]): default value to use when lag row is
            out of the bounds of the window. Defaults to None (SQL: NULL)

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return WindowColumn(
            fn=lambda x, y, z: f'lag({x.sql}, {y.sql}, {z.sql})',
            parents=(self, values, offset, default),
            dtype=values.dtype,
        )

    @input_constraints(..., Is.any, Is.integer, Is.any, name='lead()')
    def lead(self, values: Column, offset: Optional[int] = 1, default: Optional[Any] = None) -> WindowColumn:
        """Apply a lead function in this window.

        Args:
            values (Column): the column or function of columns to return data from.
            offset (Optional[int]): offset bewteen the lag row and current row. Defaults to 1.
            default (Union[Column, str, int, float, bool, date, datetime, None]): default value to use when lag row is
            out of the bounds of the window. Defaults to None (SQL: NULL)

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x, y, z: f'lead({x.sql}, {y.sql}, {z.sql})'
        return WindowColumn(fn=fn, parents=(self, values, offset, default), dtype=values.dtype)

    @input_constraints(..., Is.any, Is.integer, name='nth_value()')
    def nth_value(self, values: Column, n: int) -> WindowColumn:
        """Apply an nth value function in this window.

        Notes:
            Gets the value at position n in the window.

        Args:
            values (Column): column/function of columns to get the value from.
            n (int): the position value.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x, y, z: f'nth_value({x.sql}, {y.sql})'
        return WindowColumn(fn=fn, parents=(self, values, n), dtype=values.dtype)

    @input_constraints(..., Is.numeric, name='mean()')
    def mean(self, values: Column) -> WindowColumn:
        """Apply a mean calculation in this window.

        Args:
            values (Column): the values to calculate mean over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'avg({x.sql})'
        return WindowColumn(fn=fn, parents=(self, values), dtype=DType.Double)

    @input_constraints(..., Is.any, name='count()')
    def count(self, value: Optional[Column] = None) -> WindowColumn:
        """Apply a count calculation in this window.

        Args:
            value (Optional[Column]): an optional column to count over. In this case if there are NULL values in the
            column they will not contribute to the final count. Default is None, in this case all rows are counted.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        if value.dtype == DType.Null:
            fn = lambda: 'count()'
            return WindowColumn(fn=fn, parents=(self, ), dtype=DType.Int)
        else:
            fn = lambda x: f'count({x.sql})'
            return WindowColumn(fn=fn, parents=(self, value), dtype=DType.Int)

    @input_constraints(..., Is.numeric, name='max()')
    def max(self, values: Column) -> WindowColumn:
        """Apply a maximum value calculation in this window.

        Args:
            values (Column): values to find the max value over in the window.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'max({x.sql})'
        return WindowColumn(fn=fn, parents=(self, values), dtype=values.dtype)

    @input_constraints(..., Is.numeric, name='min()')
    def min(self, values: Column) -> WindowColumn:
        """Apply a minimum value calculation in this window.

        Args:
            values (Column): values to find the min value over in the window.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'min({x.sql})'
        return WindowColumn(fn=fn, parents=(self, values), dtype=values.dtype)

    @input_constraints(..., Is.numeric, name='sum()')
    def sum(self, values: Column) -> WindowColumn:
        """Apply a sum value calculation in this window.

        Args:
            values (Column): values to calculate the window sum over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'sum({x.sql})'
        return WindowColumn(fn=fn, parents=(self, values), dtype=values.dtype)

    @input_constraints(..., Is.numeric, name='prod()')
    def prod(self, values: Column) -> WindowColumn:
        """Apply a product calculation in this window.

        Notes:
            the product will multiply together each value in the window.

        Args:
            values (Column): values to calculate the window product over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'cumeprod({x.sql})'
        return WindowColumn(fn=fn, parents=(self, values), dtype=values.dtype)

    def cume_dist(self) -> WindowColumn:
        """Apply a cumulative distribution ranking function.

        Notes:
            this is the position of an expression's value in the cumulative distribution of the expression normalised
            between 0 and 1.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda: 'cume_dist()'
        return WindowColumn(fn=fn, parents=(self,), dtype=DType.Double)

    def dense_rank(self) -> WindowColumn:
        """Apply a dense rank function in the window.

        Notes:
            Equal values (in the sort by column(s)) will have the same value, the next value in rank after is not
            skipped in the case of a tie (in contrast to the rank function).

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda: 'dense_rank()'
        return WindowColumn(fn=fn, parents=(self,), dtype=DType.Double)

    @input_constraints(..., Is.integer, name='ntile()')
    def ntile(self, n: int) -> WindowColumn:
        """Apply an N tile function in the window.

        Notes:
            This will assign in integer label to each row in the window such that the window is partitioned into n-many
            groups in a tiling fashion.

        Args:
            n (int): the number of groups.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'ntile({x.sql})'
        return WindowColumn(fn=fn, parents=(self, n), dtype=DType.Int)

    def rank(self) -> WindowColumn:
        """Apply a rank function in this window.

        Notes:
             Equal values (in the sort by column(s)) will have the same value, the next value in rank after is skipped
             in the case of a tie.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda: 'rank()'
        return WindowColumn(fn=fn, parents=(self,), dtype=DType.Int)

    def row_number(self) -> WindowColumn:
        """Apply a row number function in this window.

        Notes:
            Row number will enumerate the rows within a window.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda: 'row_number()'
        return WindowColumn(fn=fn, parents=(self,), dtype=DType.Int)

    def percent_rank(self) -> WindowColumn:
        """Apply a percent rank function in this window.

        Notes:
            This will return the rank of a row as a number between 0 and 1.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda: 'percent_rank()'
        return WindowColumn(fn=fn, parents=(self,), dtype=DType.Double)

    @input_constraints(..., Is.boolean, name='filter()')
    def filter(self, condition: Column) -> Window:
        """Add a filter condition to the window.

        Notes:
            This will remove rows that evaluate as false before they enter any associated window functions.

        Args:
            condition (Column):the filter condition to apply. Must be a column/function of columns that resolves to a
            boolean.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        parents = list(self.get_parents())

        # Allow for piecemeal filter construction b/c some window functions will want to add additional filter logic.
        # For example, loss stdev will need to filter for returns < 0.
        extant = parents[-1]
        if extant.has_content():
            condition = extant.get_filter() & condition

        parents[-1] = OverFilter(parents=(condition,))
        return self.update_node(parents=parents)


class WindowColumn(Column):

    label_: Literal['windowfunc'] = Field('windowfunc', alias='label')

    @model_validator(mode='before')
    def _compute_val(self):
        fn = self['fn']
        if not callable(fn):
            raise ValueError(f'{fn} is not a callable. fn input must be a function.')

        over = self['parents'][0]
        if not isinstance(over, Window):
            raise TypeError(f'First parent must be an Over instance, but was {type(over).__name__}')

        args = self['parents'][1:]

        sql = fn(*args)
        if not isinstance(sql, str):
            raise TypeError(
                f"Column.fn must be a callable that returns str, but returned {type(sql).__name__} "
                f"({sql})."
            )

        self['sql'] = sql + ' ' + over.get_sql()

        return self
