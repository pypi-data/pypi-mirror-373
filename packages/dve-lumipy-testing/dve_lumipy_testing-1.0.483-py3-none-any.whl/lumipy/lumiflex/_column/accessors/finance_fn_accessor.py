from typing import Union, Optional

from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints, block_node_type
from lumipy.lumiflex._window.window import WindowColumn
from lumipy.lumiflex.column import Column
from .base_fn_accessor import BaseFnAccessor
from ...window import window


class FinanceFnAccessor(BaseFnAccessor):

    @block_node_type(label='aggfunc', name='.finance')
    def __init__(self, column: Column):
        super().__init__('finance', column, Is.numeric)

    def drawdown(self, order: Optional[Ordering] = None) -> WindowColumn:
        """Apply a drawdown calculation to this value.

        Notes:
            Drawdown is calculated from prices as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            This assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.


        Args:
            order (Optional[Ordering]): optional ordering to use in the window.

        Returns:
            Column: column instance representing this calculation.

        """
        return window(orders=order).finance.drawdown(self._column)

    def drawdown_length(self, order: Optional[Ordering] = None):
        """Apply a drawdown length calculation to this value.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the mean_drawdown method to the corresponding column in a .select()
            on the table variable.

        Args:
            order (Optional[Ordering]): optional ordering to use in the window.

        Returns:
            Column: column instance representing this calculation.

        """
        return window(orders=order).finance.drawdown(self._column)

    def max_drawdown(self) -> Column:
        """Apply a max drawdown calculation to this value.

        Notes:
            Drawdown is calculated from prices as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            Max drawdown is then the maximum value of the drawdowns dd_i over the sequence of values.

            This assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.


        Args:
            order (Optional[Ordering]): optional ordering to use in the window.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'max_drawdown({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def mean_drawdown(self) -> Column:
        """Apply a mean drawdown calculation to this value.

        Notes:
            Drawdown is calculated from prices as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            Mean drawdown is then the mean value of the drawdowns dd_i over the sequence of values.

            This assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the method to the corresponding column in a .select()
            on the table variable.


        Args:
            order (Optional[Ordering]): optional ordering to use in the window.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'mean_drawdown({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def max_drawdown_length(self) -> Column:
        """Apply a max drawdown length calculation to this value.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            The max drawdown length is then the maximum value of the drawdown length in the time period.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the mean_drawdown method to the corresponding column in a .select()
            on the table variable.

        Args:
            order (Optional[Ordering]): optional ordering to use in the window.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'max_drawdown_length({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def mean_drawdown_length(self) -> Column:
        """Apply a mean drawdown length calculation to this value.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            The mean drawdown length is then the maximum value of the drawdown length in the time period.

            This aggregation assumes that the column is in time order. This calculation will be applied before ORDER BY in
            SQL syntax, so you should consider turning the table containing the data into a table variable, ordering that by
            the time-equivalent column and then applying the mean_drawdown method to the corresponding column in a .select()
            on the table variable.

        Args:
            order (Optional[Ordering]): optional ordering to use in the window.

        Returns:
            Column: column instance representing this calculation.

        """

        fn = lambda a: f'mean_drawdown_length({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def gain_loss_ratio(self) -> Column:
        """Apply a gain-loss ratio calculation to this value.

        Notes:
            Gain-loss ratio is the mean positive return of the series divided by the mean negative return of the series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'gain_loss_ratio({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def semi_deviation(self) -> Column:
        """Apply a semi-deviation calculation to this value.

        Notes:
            Semi-deviation is the standard deviation of values in a returns series below the mean return value.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'semi_deviation({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.finance.information_ratio()')
    def information_ratio(self, y: Union[float, Column]) -> Column:
        """Apply an information ratio calculation to this value.

        Notes:
            The information ratio is the mean excess return between a return series and a benchmark series divided by the
            standard deviation of the excess return.

        Args:
            y (Union[float, Column]): the benchmark return series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'mean_stdev_ratio({a.sql})'
        return Column(fn=fn, parents=(self._column - y,), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.finance.tracking_error()')
    def tracking_error(self, y: Union[float, Column]) -> Column:
        """Apply a tracking error ratio calculation to this value.

        Notes:
            The tracking error is the standard deviation of the difference between a return series and a benchmark.

        Args:
            y (Union[float, Column]): the benchmark return series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'window_stdev({a.sql})'
        return Column(fn=fn, parents=(self._column - y,), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.finance.sharpe_ratio()')
    def sharpe_ratio(self, risk_free_rate: Union[Column, float]) -> Column:
        """Apply a Sharpe ratio calculation to this value.

        Notes:
            The Sharpe ratio is calculated as the mean excess return over the risk free rate divided by the standard
            deviation of the excess return.

        Args:
            risk_free_rate (Union[Column, float]): the risk-free rate of return. This can be a constant value (float
            input) or a series (column instance input).

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'mean_stdev_ratio({a.sql})'
        return Column(fn=fn, parents=(self._column - risk_free_rate,), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.finance.volatility()')
    def volatility(self, time_factor: float):
        """Apply a volatility calculation to this value. This assumed that this column/calculation is a log-returns series.

        Notes:
            Volatility is calculated as the standard deviation of log returns in a given window.
            https://en.wikipedia.org/wiki/Volatility_(finance)#Mathematical_definition

        Args:
            time_factor (float): an annualisation factor to apply to the volatility value.

        Returns:
            Column: column instance representing this calculation.

        """
        return self._column.stats.stdev() * (time_factor ** 0.5)

    @input_constraints(..., Is.integer, Is.numeric, Is.boolean, ..., name='.finance.prices_to_returns()')
    def prices_to_returns(
            self,
            interval: Optional[int] = 1,
            time_factor: Optional[float] = 1.0,
            compound: Optional[bool] = False,
            order: Optional[Ordering] = None
    ) -> WindowColumn:
        """Apply a prices to returns calculation to this value.

        Args:
            interval (Optional[int]): row spacing to calculate returns between. Defaults to 1.
            time_factor (Optional[float]): a timescale factor to apply (defaults to 1.0).
            compound (Optional[bool]): whether to compound the returns (defaults to false).
            order (Optional[Ordering]): ordering to use, defaults to none (we assume returns are already time-ordered).

        Returns:
            Column: column instance representing this calculation.

        """
        win = window(orders=order)
        return win.finance.prices_to_returns(self._column, interval, time_factor, compound)

    @input_constraints(..., Is.numeric, Is.numeric, Is.boolean, ..., name='.finance.returns_to_prices()')
    def returns_to_prices(
            self,
            initial: float,
            time_factor: Optional[float] = 1.0,
            compound: Optional[bool] = False,
            order: Optional[Ordering] = None
    ) -> WindowColumn:
        """Apply a returns to prices calculation to this value. Starting from an initial value this will generate a
        price series from a returns series.

        Args:
            initial (float): the initial price level.
            time_factor (Optional[float]): a timescale factor to apply (defaults to 1.0).
            compound (Optional[bool]): whether to compound the returns (defaults to false).
            order (Optional[Ordering]): ordering to use, defaults to none (we assume returns are already time-ordered).

        Returns:
            Column: column instance representing this calculation.

        """
        win = window(orders=order)
        return win.finance.returns_to_prices(self._column, initial, time_factor, compound)
