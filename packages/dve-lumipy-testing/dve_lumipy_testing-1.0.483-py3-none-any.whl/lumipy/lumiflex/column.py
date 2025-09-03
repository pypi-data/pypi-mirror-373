from __future__ import annotations

import typing
from datetime import datetime, date
from typing import Union, Type, Callable, Literal, Optional, List, Tuple, Set

from pandas import Series
from pydantic import StrictStr, Field, model_validator

from lumipy.lumiflex._column.widgets import column_object_widget
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._common.str_utils import model_repr
from lumipy.lumiflex._common.widgets import display
from lumipy.lumiflex._metadata import ColumnMeta
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._method_tools.constraints import Is, Are
from lumipy.lumiflex._method_tools.decorator import input_constraints, preprocess_collection, block_node_type

if typing.TYPE_CHECKING:
    from lumipy.lumiflex._column.ordering import Ordering
    from lumipy.lumiflex._column.accessors import *
    from lumipy.lumiflex._table.operation import Select, Where


class Column(Node):
    """Represents columns and column-derived values in SQL query.

    Contains methods and accessors for yet more methods that transform, aggregate and combine data.

    """

    fn: Callable
    dtype: DType
    label_: Literal["data", "op", "func", "aggfunc", "const", "alias", "prefix"] = Field(alias='label')
    meta: Union[ColumnMeta, float, int, bool, StrictStr, datetime, date, None] = None
    sql: Optional[StrictStr] = None

    # noinspection PyMethodParameters
    @model_validator(mode='before')
    def _compute_val(self):
        fn = self['fn']
        if not callable(fn):
            raise ValueError(f'{fn} is not a callable. fn input must be a function.')

        args = self.get('parents', [])
        if not all(isinstance(a, Node) for a in args):
            types_str = '(' + ', '.join(type(a).__name__ for a in args) + ')'
            raise TypeError(f"Parents must all be Node or a subclass of Node but were {types_str}.")

        sql = fn(*args)
        if not isinstance(sql, str):
            raise TypeError(
                f"Column.fn must be a callable that returns str, but returned {type(sql).__name__} "
                f"({sql})."
            )
        self['sql'] = sql
        return self

    def _repr_mimebundle_(self, *args, **kwargs):
        return display(column_object_widget(self, True), *args, **kwargs)

    def get_name(self) -> str:
        """Get the pythonic name of this column.

        Returns:
            str: pythonic name of this column
        """
        return self.meta.python_name()

    def __hash__(self) -> int:
        return hash((self.dtype, self.label_, self.meta, self.sql, self.parents_))

    def __repr__(self):
        return model_repr(self, 'fn')

    @property
    def str(self) -> StrFnAccessor:
        """Column str function accessor property. Encapsulates the set of str methods.

        You can chain methods on the accessor property. For example, to make a column all upper case.
            my_str_col.str.upper()

        If this column is not dtype Text an error will be thrown.

        Returns:
            StrFnAccessor: the str function accessor instance.
        """
        from lumipy.lumiflex._column.accessors.str_fn_accessor import StrFnAccessor
        return StrFnAccessor(self)

    @property
    def dt(self) -> DtFnAccessor:
        """Column date/datetime function accessor property. Encapsulates the set of date/datetime methods.

        You can chain methods on the accessor property. For example, to convert a date to a str in some format
            my_date_col.dt.strftime(fmt_str)

        If this column is not dtype Date or DateTime an error will be thrown.

        Returns:
            DtFunctionAccessor: the date/datetime function accessor instance.
        """
        from lumipy.lumiflex._column.accessors.dt_fn_accessor import DtFnAccessor
        return DtFnAccessor(self)

    @property
    def cume(self) -> CumeFnAccessor:
        """Column cumulative function accessor property. Encapsulates the set of cumulative function methods.

        You can chain methods on the accessor property. For example, to compute a cumulative sum
            my_num_col.cume.sum()

        If this column is not a numeric dtype an error will be thrown.

        Returns:
            CumeFnAccessor: the cume function accessor instance.
        """
        from lumipy.lumiflex._column.accessors import CumeFnAccessor
        return CumeFnAccessor(self)

    @property
    def finance(self) -> FinanceFnAccessor:
        """Column finance function accessor property. Encapsulates the set of finance function methods.

        You can chain methods on the accessor property. For example, to compute the max drawdown for a price series
            prices.finance.max_drawdown()

        If this column is not a numeric dtype an error will be thrown.

        Returns:
            FinanceFnAccessor: the finance function accessor instance.
        """
        from lumipy.lumiflex._column.accessors import FinanceFnAccessor
        return FinanceFnAccessor(self)

    @property
    def linreg(self) -> LinregFnAccessor:
        """Column linear regression function accessor property. Encapsulates the set of linear regression function methods.

        You can chain methods on the accessor property. For example, to compute the alpha (gradient) between this column
        and another
            x.linreg.alpha(y)

        If this column is not a numeric dtype an error will be thrown.

        Returns:
            LinregFnAccessor: the linreg function accessor instance.
        """
        from lumipy.lumiflex._column.accessors import LinregFnAccessor
        return LinregFnAccessor(self)

    @property
    def metric(self) -> MetricFnAccessor:
        """Column metric (i.e. distance and similarity measures) function accessor property. Encapsulates the set of
        metric function methods.

        You can chain methods on the accessor property. For example, to compute the manhattan distance between this column
        and another
            x.metric.manhattan_distance(y)

        If this column is not a numeric dtype an error will be thrown.

        Returns:
            MetricFnAccessor: the metric function accessor instance.
        """
        from lumipy.lumiflex._column.accessors import MetricFnAccessor
        return MetricFnAccessor(self)

    @property
    def stats(self) -> StatsFnAccessor:
        """Column statistical function accessor property. Encapsulates the set of statistical function methods.

        You can chain methods on the accessor property. For example, to compute the skewness of this column
            x.stats.skewness()

        If this column is not a numeric dtype an error will be thrown.

        Returns:
            StatsFnAccessor: the stats function accessor instance.
        """
        from lumipy.lumiflex._column.accessors import StatsFnAccessor
        return StatsFnAccessor(self)

    @property
    def json(self) -> JsonFnAccessor:
        """Column json function accessor property. Encapsulates the set of json function methods.
        See https://www.sqlite.org/json1.html

        You can chain methods on the accessor property or use square brackets with a path string. For example
            x.json['$.A.B[2]']
        or
            x.json.patch('{"A": 2}')

        Returns:
            JsonFnAccessor: the stats function accessor instance.
        """
        from lumipy.lumiflex._column.accessors import JsonFnAccessor
        return JsonFnAccessor(self)

    @input_constraints(Is.not_timelike, Is.not_timelike, name='+ (addition)')
    def __add__(self, other: Union[Column, int, float, str]) -> Column:
        if Is.text(self) and Is.text(other):
            return self.str.concat(other)
        return self.__num_add(other)

    @input_constraints(Is.numeric, Is.numeric, name='+ (addition)')
    def __num_add(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} + {y.sql}'
        dtype = self.dtype.num_priority(other.dtype)
        return Column(fn=fn, parents=(self, other), dtype=dtype, label='op')

    @input_constraints(Is.not_timelike, Is.not_timelike, name='+ (addition)')
    def __radd__(self, other: Union[Column, int, float, str]) -> Column:
        return other + self

    @input_constraints(Is.numeric, Is.numeric, name='* (multiplication)')
    def __mul__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} * {y.sql}'
        dtype = self.dtype.num_priority(other.dtype)
        return Column(fn=fn, parents=(self, other), dtype=dtype, label='op')

    @input_constraints(Is.numeric, Is.numeric, name='* (multiplication)')
    def __rmul__(self, other) -> Column:
        return other * self

    @input_constraints(Is.not_text, Is.not_text, name='- (subtraction)')
    def __sub__(self, other) -> Column:
        if Is.timelike(self) and Is.timelike(other):
            delta = self.dt.julian_day() - other.dt.julian_day()
            return delta * 3600 * 24
        return self.__num_diff(other)

    @input_constraints(Is.numeric, Is.numeric, name='- (subtraction)')
    def __num_diff(self, other: Column) -> Column:
        fn = lambda x, y: f'{x.sql} - {y.sql}'
        dtype = self.dtype.num_priority(other.dtype)
        return Column(fn=fn, parents=(self, other), dtype=dtype, label='op')

    @input_constraints(Is.not_text, Is.not_text, name='- (subtraction)')
    def __rsub__(self, other) -> Column:
        return other - self

    @input_constraints(Is.numeric, Is.numeric, name='/ (division)')
    def __truediv__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} / {y.sql}'
        return Column(fn=fn, parents=(self, other.cast(float)), dtype=DType.Double, label='op')

    @input_constraints(Is.numeric, Is.numeric, name='/ (division)')
    def __rtruediv__(self, other) -> Column:
        return other / self

    @input_constraints(Is.numeric, Is.numeric, name='// (floor division)')
    def __floordiv__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} / {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=other.dtype, label='op')

    @input_constraints(Is.numeric, Is.numeric, name='// (floor division)')
    def __rfloordiv__(self, other) -> Column:
        return other // self

    @input_constraints(Are.comparable, name='= (equal)')
    def __eq__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} = {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Boolean, label='op')

    @input_constraints(Are.comparable, name='!= (not equal)')
    def __ne__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} != {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Boolean, label='op')

    @input_constraints(Is.numeric, name='- (negative)')
    def __neg__(self) -> Column:
        fn = lambda x: f'-{x.sql}'
        return Column(fn=fn, parents=(self,), dtype=DType.Boolean, label='op')

    @input_constraints(Is.boolean, name='~ (not)')
    def __invert__(self) -> Column:
        fn = lambda x: f'NOT {x.sql}'
        return Column(fn=fn, parents=(self,), dtype=DType.Boolean, label='op')

    @input_constraints(Are.comparable, name='< (less than)')
    def __lt__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} < {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Boolean, label='op')

    @input_constraints(Are.comparable, name='<= (less than or equal)')
    def __le__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} <= {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Boolean, label='op')

    @input_constraints(Are.comparable, name='> (greater than)')
    def __gt__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} > {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Boolean, label='op')

    @input_constraints(Are.comparable, name='>= (greater that or equal)')
    def __ge__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} >= {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Boolean, label='op')

    @input_constraints(Is.numeric, Is.numeric, name='** (power)')
    def __pow__(self, power, modulo=None) -> Column:
        fn = lambda x, y: f'power({x.sql}, {y.sql})'
        dtype = self.dtype.num_priority(power.dtype)
        return Column(fn=fn, parents=(self, power), dtype=dtype, label='func')

    @input_constraints(Is.numeric, Is.numeric, name='** (power)')
    def __rpow__(self, other) -> Column:
        return other ** self

    @input_constraints(Is.numeric, Is.integer, name='% (modulus)')
    def __mod__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} % {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Int, label='op')

    @input_constraints(Is.integer, Is.numeric, name='% (modulus)')
    def __rmod__(self, other) -> Column:
        return other % self

    @input_constraints(Is.boolean, Is.boolean, name='& (and)')
    def __and__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} AND {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Boolean, label='op')

    @input_constraints(Is.boolean, Is.boolean, name='& (and)')
    def __rand__(self, other) -> Column:
        return other & self

    @input_constraints(Is.boolean, Is.boolean, name='| (or)')
    def __or__(self, other) -> Column:
        fn = lambda x, y: f'{x.sql} OR {y.sql}'
        return Column(fn=fn, parents=(self, other), dtype=DType.Boolean, label='op')

    @input_constraints(Is.boolean, Is.boolean, name='| (or)')
    def __ror__(self, other) -> Column:
        return other | self

    @input_constraints(Is.numeric, name='abs()')
    def __abs__(self) -> Column:
        fn = lambda x: f'abs({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=self.dtype, label='func')

    @input_constraints(Is.numeric, name='ceil()')
    def __ceil__(self) -> Column:
        # noinspection PyArgumentList
        return self.ceil()

    @input_constraints(Is.numeric, name='floor()')
    def __floor__(self) -> Column:
        # noinspection PyArgumentList
        return self.floor()

    @input_constraints(Is.numeric, Is.integer, name='round()')
    def __round__(self, n: Union[Column, int] = 0) -> Column:
        # noinspection PyArgumentList
        return self.round(n)

    @input_constraints(Is.numeric, name='.abs()')
    def abs(self) -> Column:
        """Apply an abs (absolute value) function to this value.

        Returns:
            Column: column instance representing this calculation.
        """
        return abs(self)

    @input_constraints(Is.numeric, name='.ceil()')
    def ceil(self) -> Column:
        """Apply a ceil function to this value.

        Returns:
            Column: column instance representing this calculation.
        """
        fn = lambda x: f'ceil({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Int, label='func')

    @input_constraints(Is.numeric, name='.floor()')
    def floor(self) -> Column:
        """Apply a floor function to this value.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'floor({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Int, label='func')

    @input_constraints(Is.numeric, Is.integer, name='.round()')
    def round(self, n: Union[int, Column] = 0) -> Column:
        """Apply a round function to this value.

        Args:
            n (Union[int, Column]): the number of decimal places to round to.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'round({x.sql}, {y.sql})'
        dtype = DType.Int if n.meta == 0 else DType.Double
        return Column(fn=fn, parents=(self, n), dtype=dtype, label='func')

    def is_null(self) -> Column:
        """Apply an is null condition to this value.

        Returns:
            Column: boolean value column instance representing this condition.

        """
        fn = lambda x: f'{x.sql} IS NULL'
        return Column(fn=fn, parents=(self,), dtype=DType.Boolean, label='op')

    def is_not_null(self) -> Column:
        """Apply an is not null condition to this value.

        Returns:
            Column: boolean value column instance representing this condition.

        """
        fn = lambda x: f'{x.sql} IS NOT NULL'
        return Column(fn=fn, parents=(self,), dtype=DType.Boolean, label='op')

    @input_constraints(Is.numeric, name='.exp()')
    def exp(self) -> Column:
        """Apply an exp (exponential) function to this value.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'exp({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Double, label='func')

    @input_constraints(Is.numeric, name='.log()')
    def log(self) -> Column:
        """Apply a log function (natural base) to this value.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'log({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Double, label='func')

    @input_constraints(Is.numeric, name='.log10()')
    def log10(self) -> Column:
        """Apply a log function (base 10) to this value.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'log10({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Double, label='func')

    @input_constraints(Is.numeric, name='.sign()')
    def sign(self) -> Column:
        """Apply a sign function to this value.

        sign(x) will give -1, 0, or 1 if x is negative, zero or positive > 0.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'sign({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Int, label='func')

    @preprocess_collection
    @input_constraints(Are.comparable, name='.is_in()')
    def is_in(self, *args: Union[List, Tuple, Set, Series, Select, Where]) -> Column:
        """Apply an is in condition. This tests whether values are in a given set of values. This set can be a
        list/tuple/set of values, a pandas Series or even a subquery with a single column.

        Args:
            *args (Union[List, Tuple, Set, Series, Select, Where]): the set of values to use in the condition.

        Returns:
            Column: boolean value column instance representing this condition.

        """
        fn = lambda *xs: f'{xs[0].sql} IN ({", ".join(v.sql for v in xs[1:])})'
        return Column(fn=fn, parents=(self,) + args, dtype=DType.Boolean, label='op')

    @preprocess_collection
    @input_constraints(Are.comparable, name='not_in()')
    def not_in(self, *args: Union[List, Tuple, Set, Series, Select, Where]) -> Column:
        """Apply a not in condition. This tests whether values are in a given set of values. This set can be a
        list/tuple/set of values, a pandas Series or even a subquery with a single column.

        Args:
            *args (Union[List, Tuple, Set, Series, Select, Where]): the set of values to use in the condition.

        Returns:
            Column: boolean value column instance representing this condition.

        """
        fn = lambda *xs: f'{xs[0].sql} NOT IN ({", ".join(v.sql for v in xs[1:])})'
        return Column(fn=fn, parents=(self,) + args, dtype=DType.Boolean, label='op')

    @input_constraints(Are.comparable, name='.between()')
    def between(self, lower, upper) -> Column:
        """Apply a between condition. This tests whether a value is between two test values.

        Args:
            lower: the lower bound of the interval.
            upper: the upper bound of the interval.

        Returns:
            Column: boolean value column instance representing this condition.

        """
        fn = lambda x, y, z: f'{x.sql} BETWEEN {y.sql} AND {z.sql}'
        return Column(fn=fn, parents=(self, lower, upper), dtype=DType.Boolean, label='op')

    @input_constraints(Are.comparable, name='.not_between()')
    def not_between(self, lower, upper) -> Column:
        """Apply a not between condition. This tests whether a value is not between two test values.

        Args:
            lower: the lower bound of the interval.
            upper: the upper bound of the interval.

        Returns:
            Column: boolean value column instance representing this condition.

        """
        fn = lambda x, y, z: f'{x.sql} NOT BETWEEN {y.sql} AND {z.sql}'
        return Column(fn=fn, parents=(self, lower, upper), dtype=DType.Boolean, label='op')

    @input_constraints(Are.comparable, name='coalesce')
    def coalesce(self, *values) -> Column:
        """Apply a coalesce function to this value. Coalesce will return the first non-null value in a list of values
        and calculations.

        Args:
            *values:

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda *xs: f'coalesce({", ".join(v.sql for v in xs)})'
        return Column(fn=fn, parents=(self,) + values, dtype=self.dtype, label='func')

    def _with_alias(self, alias: str) -> Column:

        if not isinstance(alias, str):
            raise TypeError(f'The alias must be specified as a string, but was {alias.__class__.__name__}.')
        if self.label_ == 'alias':
            raise ValueError(f'This expression already has an alias ({self.meta.field_name}).')

        fn = lambda x: f'{x.sql} AS [{alias}]'
        table_name = self.meta.table_name if isinstance(self.meta, ColumnMeta) else None
        meta = ColumnMeta(field_name=alias, dtype=self.dtype, table_name=table_name)
        return Column(fn=fn, parents=(self,), meta=meta, dtype=self.dtype, label='alias')

    def cast(self, dtype: Union[Type, DType]) -> Column:
        """Apply a cast function to this value. Cast will cast the values to another given type.

        Args:
            dtype Union[Type, DType]: the type to case to.

        Returns:
            Column: column instance representing this operation.

        """
        dtype = DType.to_dtype(dtype)

        if dtype in [DType.Date, DType.DateTime]:
            raise TypeError("Can't cast to Date or DateTime. Try using to_date")

        if self.dtype == dtype:
            return self

        fn = lambda x: f'cast({x.sql} AS {dtype.name})'
        return Column(fn=fn, dtype=dtype, parents=(self,), label='func')

    @block_node_type(label='aggfunc', name='.sum()')
    @input_constraints(Is.numeric, name='.sum()')
    def sum(self) -> Column:
        """Apply a sum function to this value. Sum will add all the values together whilst treating nulls as zeros.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'total({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=self.dtype, label='aggfunc')

    @block_node_type(label='aggfunc', name='.count()')
    @input_constraints(Is.any, name='.count()')
    def count(self) -> Column:
        """Apply a count function to this value. Count will count how many values there are in a column or group.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'count({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Int, label='aggfunc')

    @block_node_type(label='aggfunc', name='.mean()')
    @input_constraints(Is.numeric, name='.mean()')
    def mean(self) -> Column:
        """Apply a mean function to this value. Mean will compute the arithmetic mean of a column or group.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'avg({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.min()')
    @input_constraints(Is.any, name='.min()')
    def min(self) -> Column:
        """Apply a min function to this value. Min will return the minimum value of a column or group.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'min({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=self.dtype, label='aggfunc')

    @block_node_type(label='aggfunc', name='.max()')
    @input_constraints(Is.any, name='.max()')
    def max(self) -> Column:
        """Apply a max function to this value. Max will return the maximum value of a column or group.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'max({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=self.dtype, label='aggfunc')

    @block_node_type(label='aggfunc', name='.median()')
    @input_constraints(Is.numeric, name='.median()')
    def median(self) -> Column:
        """Apply a median function to this value. Median will calculate the 'middle value' that separates the top
        half of an ordered set of values from the lower half.


        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'median({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.stdev()')
    @input_constraints(Is.numeric, name='.stdev()')
    def stdev(self) -> Column:
        """Apply a standard deviation function to this value. The standard deviation is a measure of the dispersion of
        a set of values (https://en.wikipedia.org/wiki/Standard_deviation).

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'stdev({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.quantile()')
    @input_constraints(Is.numeric, Is.numeric, name='.quantile()')
    def quantile(self, q: Union[float, Column]) -> Column:
        """Apply a quantile function to this value. This function computes the value of a given quantile of the input
        (the value that bounds this fraction of the data). For example a quantile of 0.9 will be the value that 90% of
        the data is below.

        Args:
            q: (Union[float, Column]) the quantile value to compute.

        Returns:
            Column: column instance representing this calculation.

        """
        if q.label_ == 'const' and q.meta is not None:
            if q.meta > 1 or q.meta < 0:
                raise ValueError(f'The quantile value q must be between 0 and 1. Was {q.meta}.')

        fn = lambda x, y: f'quantile({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self, q), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.prod()')
    @input_constraints(Is.numeric, name='.prod()')
    def prod(self) -> Column:
        """Apply a product function to this value. The product function will take the product of every value in a column
        or group.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'cumeprod({x.sql})'
        return Column(fn=fn, parents=(self,), dtype=self.dtype, label='aggfunc')

    @block_node_type(label='aggfunc', name='.diff()')
    @block_node_type(label='windowfunc', name='.diff()')
    @input_constraints(Is.numeric, ..., ..., name='.diff()')
    def diff(self, sort_by=None, offset: int = 1) -> Column:
        """Apply an elementwise difference function to this value. This function will compute the arithmetic difference
        between an element in a column and another element in the column offset by a given number of rows.

        Args:
            sort_by (Optional[Column]): optional column to order by.
            offset (int): offset value to use (defaults to 1).

        Returns:
            Column: column instance representing this calculation.

        """
        from lumipy.lumiflex.window import window
        w = window(orders=sort_by, lower=offset)
        return self - w.lag(self, offset)

    @block_node_type(label='aggfunc', name='.frac_diff()')
    @block_node_type(label='windowfunc', name='.frac_diff()')
    @input_constraints(Is.numeric, ..., ..., name='.frac_diff()')
    def frac_diff(self, sort_by=None, offset: int = 1) -> Column:
        """Apply an elementwise fractional difference function to this value. This function will compute the fractional
        difference between an element in a column and another element in the column offset by a given number of rows.

        Args:
            sort_by (Optional[Column]): optional column to order by.
            offset (int): offset value to use (defaults to 1).

        Returns:
            Column: column instance representing this calculation.

        """
        from lumipy.lumiflex.window import window
        w = window(orders=sort_by, lower=offset)
        prev = w.lag(self, offset)
        return (self - prev) / prev

    def ascending(self) -> Ordering:
        """Create an ascending ordering from this column.

        Returns:
            Ordering: instance that represents ordering by this column in ascending order.

        """
        from lumipy.lumiflex._column.ordering import Ordering
        return Ordering(label='asc', parents=(self,))

    def asc(self) -> Ordering:
        """Create an ascending ordering from this column.

        Returns:
            Ordering: instance that represents ordering by this column in ascending order.

        """
        return self.ascending()

    def descending(self) -> Ordering:
        """Create a descending ordering from this column.

        Returns:
            Ordering: instance that represents ordering by this column in descending order.

        """
        from lumipy.lumiflex._column.ordering import Ordering
        return Ordering(label='desc', parents=(self,))

    def desc(self) -> Ordering:
        """Create a descending ordering from this column.

        Returns:
            Ordering: instance that represents ordering by this column in descending order.

        """
        return self.descending()

    def _get_data_col_dependencies(self) -> List[Column]:
        if self.label_ == 'data':
            return [self]
        return [c for c in self.get_ancestors() if isinstance(c, Column) and c.label_ == 'data']
