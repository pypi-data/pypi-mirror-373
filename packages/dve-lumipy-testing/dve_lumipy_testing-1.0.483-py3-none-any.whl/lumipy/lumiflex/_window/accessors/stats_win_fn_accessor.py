from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints, block_node_type
from lumipy.lumiflex._window.window import WindowColumn
from lumipy.lumiflex.column import Column
from .base_win_fn_accessor import BaseWinFnAccessor


class StatsWinFnAccessor(BaseWinFnAccessor):

    @block_node_type(label='aggfunc', name='stats.covariance()')
    @input_constraints(..., Is.numeric, Is.numeric, Is.integer, name='stats.covariance()')
    def covariance(self, x: Column, y: Column, ddof: int = 1) -> WindowColumn:
        """Apply a covariance calculation between two series in this window.

        Notes:
            Covariance is a statistical measure of the joint variability of two random variables. See
                https://en.wikipedia.org/wiki/Covariance

        Args:
            x (Column): the first column/function of columns to calculate over.
            y (Column): the second column/function of columns to calculate over.
            ddof (Optional[int]): delta degrees of freedom, use 0 for population covariance or 1 for sample covariance.
            Defaults to 1.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2, a3: f'covariance({a1.sql}, {a2.sql}, {a3.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y, ddof), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.empirical_cdf()')
    @input_constraints(..., Is.numeric, Is.numeric, name='empirical_cdf()')
    def empirical_cdf(self, x: Column, value: float) -> WindowColumn:
        """Apply an empirical cumulative distribution function calculation in this window.

        Args:
            x (Column): the column/function of columns to calculate over.
            value (float): the point at which to evaluate the empirical CDF.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, v: f'empirical_cume_dist_function({a1.sql}, {v.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, value), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.pearson_r()')
    @input_constraints(..., Is.numeric, Is.numeric, name='pearson_r()')
    def pearson_r(self, x: Column, y: Column) -> WindowColumn:
        """Apply a Pearson's correlation coefficient calculation between two series in this window.

        Args:
            x (Column): the first column/function of columns to calculate over.
            y (Column): the second column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'pearson_correlation({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.spearman_r()')
    @input_constraints(..., Is.numeric, Is.numeric, name='spearman_r()')
    def spearman_r(self, x: Column, y: Column) -> WindowColumn:
        """Apply a Spearman's rank correlation coefficient between two values in this window.

        Args:
            x (Column): the first column/function of columns to calculate over.
            y (Column): the second column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'spearman_correlation({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.median_abs_deviation()')
    @input_constraints(..., Is.numeric, name='median_abs_deviation()')
    def median_abs_deviation(self, x: Column) -> WindowColumn:
        """Apply a median absolute deviation calculation between two series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'median_absolute_deviation({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.skewness()')
    @input_constraints(..., Is.numeric, name='skewness()')
    def skewness(self, x: Column) -> WindowColumn:
        """Apply a skewness calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'skewness({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.kurtosis()')
    @input_constraints(..., Is.numeric, name='kurtosis()')
    def kurtosis(self, x: Column) -> WindowColumn:
        """Apply a kurtosis calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'kurtosis({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.root_mean_square()')
    @input_constraints(..., Is.numeric, name='root_mean_square()')
    def root_mean_square(self, x: Column) -> WindowColumn:
        """Apply a root mean square calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'root_mean_square({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.harmonic_mean()')
    @input_constraints(..., Is.numeric, name='harmonic_mean()')
    def harmonic_mean(self, x: Column) -> WindowColumn:
        """Apply a harmonic mean calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'harmonic_mean({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.geometric_mean()')
    @input_constraints(..., Is.numeric, name='geometric_mean()')
    def geometric_mean(self, x: Column) -> WindowColumn:
        """Apply a geometric mean calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'geometric_mean({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.geometric_stdev()')
    @input_constraints(..., Is.numeric, name='geometric_stdev()')
    def geometric_stdev(self, x: Column) -> WindowColumn:
        """Apply a geometric standard deviation calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        return self._window.stats.stdev(x.log()).exp()

    @block_node_type(label='aggfunc', name='stats.entropy()')
    @input_constraints(..., Is.any, name='entropy()')
    def entropy(self, x: Column) -> WindowColumn:
        """Apply an entropy calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'entropy({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.interquartile_range()')
    @input_constraints(..., Is.numeric, name='interquartile_range()')
    def interquartile_range(self, x: Column) -> WindowColumn:
        """Apply an interquartile range calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'interquartile_range({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.interquantile_range()')
    @input_constraints(..., Is.numeric, Is.double, Is.double, name='interquantile_range()')
    def interquantile_range(self, x: Column, q1: float, q2: float) -> WindowColumn:
        """Apply an interquantile range calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.
            q1 (float): the lower quantile value.
            q2 (float): the upper quantile value.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2, a3: f'interquantile_range({a1.sql}, {a2.sql}, {a3.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, q1, q2), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.coef_of_variation()')
    @input_constraints(..., Is.numeric, name='coef_of_variation()')
    def coef_of_variation(self, x: Column) -> WindowColumn:
        """Apply a coefficient of variation calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'coefficient_of_variation({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.mean_stdev_ratio()')
    @input_constraints(..., Is.numeric, name='mean_stdev_ratio()')
    def mean_stdev_ratio(self, x: Column) -> WindowColumn:
        """Apply a mean/std deviation variation calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'mean_stdev_ratio({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.median()')
    @input_constraints(..., Is.numeric, name='median()')
    def median(self, x: Column) -> WindowColumn:
        """Apply a median calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'quantile({a.sql}, 0.5)'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.lower_quartile()')
    @input_constraints(..., Is.numeric, name='lower_quartile()')
    def lower_quartile(self, x: Column) -> WindowColumn:
        """Apply a lower quartile calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'lower_quartile({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.upper_quartile()')
    @input_constraints(..., Is.numeric, name='upper_quartile()')
    def upper_quartile(self, x: Column) -> WindowColumn:
        """Apply an upper quartile calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'upper_quartile({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.quantile()')
    @input_constraints(..., Is.numeric, Is.double, name='quantile()')
    def quantile(self, x: Column, q: float) -> WindowColumn:
        """Apply a quantile calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.
            q (float): the quantile value to use.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'quantile({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, q), dtype=DType.Double)

    @block_node_type(label='aggfunc', name='stats.stdev()')
    @input_constraints(..., Is.numeric, name='stdev()')
    def stdev(self, x: Column) -> WindowColumn:
        """Apply a standard deviation calculation to a series in this window.

        Args:
            x (Column): the column/function of columns to calculate over.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a: f'window_stdev({a.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x), dtype=DType.Double)
