from typing import Union, Optional

from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._window.window import WindowColumn
from lumipy.lumiflex.column import Column
from .base_win_fn_accessor import BaseWinFnAccessor


class FinanceWinFnAccessor(BaseWinFnAccessor):

    @input_constraints(..., Is.numeric, name='.finance.drawdown()')
    def drawdown(self, prices: Column) -> WindowColumn:
        """Apply a drawdown calculation in this window.

        Notes:
            Drawdown is calculated from prices as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

        Args:
            prices (Column): the price series column to calculate drawdown from.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'drawdown({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, prices), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.drawdown_length()')
    def drawdown_length(self, prices: Column) -> WindowColumn:
        """Apply a drawdown length calculation in this window.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

        Args:
            prices (Column): the price series column to calculate drawdown length from.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'drawdown_length({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, prices), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.mean_drawdown()')
    def mean_drawdown(self, prices: Column) -> WindowColumn:
        """Apply a mean drawdown calculation in this window.

        Notes:
            Drawdown is calculated from prices as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            Mean drawdown is then the mean value of the drawdowns dd_i over the sequence of values.

        Args:
            prices (Column): the price series column to calculate mean drawdown from.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'mean_drawdown({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, prices), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.max_drawdown()')
    def max_drawdown(self, prices: Column) -> WindowColumn:
        """Apply a maximum drawdown calculation in this window.

        Notes:
            Drawdown is calculated from prices as
                dd_i = (x_h - x_i)/(x_h)
            where x_h is high watermark (max) up to and including the point x_i

            Max drawdown is then the maximum value of the drawdowns dd_i over the sequence of values.

        Args:
            prices (Column): the price series column to calculate max drawdown from.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'max_drawdown({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, prices), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.mean_drawdown_length()')
    def mean_drawdown_length(self, prices: Column) -> WindowColumn:
        """Apply a mean drawdown length in this window.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            The mean drawdown length is then the mean value of the drawdown length in the time period.

        Args:
            prices (Column): the price series column to calculate mean drawdown length from.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'mean_drawdown_length({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, prices), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.max_drawdown_length()')
    def max_drawdown_length(self, prices: Column) -> WindowColumn:
        """Apply a max drawdown length in this window.

        Notes:
            Drawdown length is calculated as the number of rows between the high watermark value and the current row.

            The max drawdown length is then the maximum value of the drawdown length in the time period.

        Args:
            prices (Column): the price series column to calculate max drawdown length from.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'max_drawdown_length({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, prices), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.gain_loss_ratio()')
    def gain_loss_ratio(self, returns: Column) -> WindowColumn:
        """Apply a gain-loss ratio calculation in this window.

        Notes:
            Gain-loss ratio is the mean positive return of the series divided by the mean negative return of the series.

        Args:
            returns (Columns): the returns series to use in the calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'gain_loss_ratio({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, returns), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.semi_deviation()')
    def semi_deviation(self, returns: Column) -> WindowColumn:
        """Apply a semi-deviation calculation in this window.

        Notes:
            Semi-deviation is the standard deviation of values in a returns series below the mean return value.

        Args:
            returns (Columns): the returns series to use in the calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'semi_deviation({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, returns), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.gain_mean()')
    def gain_mean(self, returns: Column) -> WindowColumn:
        """Apply a gain mean calculation in this window.

        Notes:
            Gain mean is the mean value of positive returns.

        Args:
            returns (Columns): the returns series to use in the calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'gain_mean({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, returns), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.loss_mean()')
    def loss_mean(self, returns: Column) -> WindowColumn:
        """Apply a loss mean calculation in this window.

        Notes:
            Loss mean is the mean value of negative returns.

        Args:
            returns (Columns): the returns series to use in the calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda x: f'loss_mean({x.sql})'
        return WindowColumn(fn=fn, parents=(self._window, returns), dtype=DType.Double)

    @input_constraints(..., Is.numeric, name='.finance.gain_stdev()')
    def gain_stdev(self, returns: Column) -> WindowColumn:
        """Apply a gain standard deviation calculation in this window.

        Notes:
            Gain stdev is the standard deviation of positive returns.

        Args:
            returns (Columns): the returns series to use in the calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return self._window.filter(returns >= 0).stats.stdev(returns)

    @input_constraints(..., Is.numeric, name='.finance.loss_stdev()')
    def loss_stdev(self, returns: Column) -> WindowColumn:
        """Apply a loss standard deviation calculation in this window.

        Notes:
            loss stdev is the standard deviation of negative returns.

        Args:
            returns (Columns): the returns series to use in the calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return self._window.filter(returns < 0).stats.stdev(returns)

    @input_constraints(..., Is.numeric, Is.numeric, name='.finance.downside_deviation()')
    def downside_deviation(self, returns: Column, threshold: float) -> WindowColumn:
        """Apply a downside deviation calculation in this window.

        Notes:
            Downside deviation is the standard deviation of returns below a given threshold.

        Args:
            returns (Columns): the returns series to use in the calculation.
            threshold (float): the threshold below which returns enter the standard devation calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return self._window.filter(returns < threshold).stats.stdev(returns)

    @input_constraints(..., Is.numeric, Is.numeric, name='.finance.information_ratio()')
    def information_ratio(self, returns: Column, benchmark: Column) -> WindowColumn:
        """Apply an information ratio calculation in this window.

        Notes:
            The information ratio is the mean excess return between a return series and a benchmark series divided by the
            standard deviation of the excess return.

        Args:
            returns (Columns): the returns series to use in the calculation.
            benchmark (Union[Column, float]): benchmark returns to measure against.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return self._window.stats.mean_stdev_ratio(returns - benchmark)

    @input_constraints(..., Is.numeric, Is.numeric, name='.finance.tracking_error()')
    def tracking_error(self, returns: Column, benchmark: Union[Column, float]) -> WindowColumn:
        """Apply a tracking error calculation in this window.

        Notes:
            The tracking error is the standard deviation of the difference between a return series and a benchmark.

        Args:
            returns (Columns): the returns series to use in the calculation.
            benchmark (Union[Column, float]): benchmark returns to measure against.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return self._window.stats.stdev(returns - benchmark)

    @input_constraints(..., Is.numeric, Is.numeric, name='.finance.sharpe_ratio()')
    def sharpe_ratio(self, returns: Column, risk_free_rate: Union[Column, float]) -> WindowColumn:
        """Apply a Sharpe ratio calculation in this window.

        Notes:
            The Sharpe ratio is calculated as the mean excess return over the risk free rate divided by the standard
            deviation of the excess return.

        Args:
            returns (Columns): the returns series to use in the calculation.
            risk_free_rate (Union[Column, float]): the risk free rate. Can either be a column of values or a python
            value (constant rate).

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return self._window.stats.mean_stdev_ratio(returns - risk_free_rate)

    @input_constraints(..., Is.numeric, Is.numeric, name='.finance.volatility()')
    def volatility(self, log_returns: Column, time_factor: float):
        """Apply a volatility calculation in this window.

        Notes:
            Volatility is calculated as the standard deviation of log returns in a given window.
            https://en.wikipedia.org/wiki/Volatility_(finance)#Mathematical_definition

        Args:
            log_returns (Columns): the log returns series to use in the calculation.
            time_factor (float): the time factor to apply.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return self._window.stats.stdev(log_returns) * (time_factor ** 0.5)

    @input_constraints(..., Is.numeric, Is.integer, Is.numeric, Is.boolean, name='.finance.prices_to_returns()')
    def prices_to_returns(
            self,
            prices: Column,
            interval: Optional[int] = 1,
            time_factor: Optional[float] = 1.0,
            compound: Optional[bool] = False,
    ):
        """Apply a prices to returns calculation in this window.

        Args:
            prices (Column): prices series to calculate returns from.
            interval (Optional[int]): the row interval to calculate returns between. Defaults to 1.
            time_factor (Optional[float]): time factor to apply to return values. Defaults to 1.0.
            compound (Optional[bool]): whether to compute compounded returns. Defaults to False.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda p, i, t, c: f"prices_to_returns({p.sql}, {i.sql}, {t.sql}, {c.sql})"
        return WindowColumn(fn=fn, parents=(self._window, prices, interval, time_factor, compound), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, Is.numeric, Is.boolean, name='.finance.returns_to_prices()')
    def returns_to_prices(
            self,
            returns: Column,
            initial: float,
            time_factor: Optional[float] = 1.0,
            compound: Optional[bool] = False,
    ):
        """Apply a returns to prices calculation in this window.

        Args:
            returns (Columns): the returns series to use in the calculation.
            initial (float): the starting value to compute the price series from.
            time_factor (Optional[float]): the time factor to apply. Defaults to 1.0.
            compound (Optional[bool]): whether the returns are compounded. Defaults to False.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda r, s, t, c: f"returns_to_prices({r.sql}, {s.sql}, {t.sql}, {c.sql})"
        return WindowColumn(fn=fn, parents=(self._window, returns, initial, time_factor, compound), dtype=DType.Double)
