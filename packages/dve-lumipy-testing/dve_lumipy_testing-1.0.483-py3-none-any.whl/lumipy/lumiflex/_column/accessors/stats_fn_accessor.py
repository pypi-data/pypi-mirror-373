from typing import Optional, Union

from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints, block_node_type
from lumipy.lumiflex.column import Column
from .base_fn_accessor import BaseFnAccessor


class StatsFnAccessor(BaseFnAccessor):

    @block_node_type(label='aggfunc', name='.stats')
    def __init__(self, column: Column):
        super().__init__('stats', column, Is.numeric)

    @block_node_type(label='aggfunc', name='.stats.covariance()')
    @input_constraints(..., Is.numeric, Is.integer, name='.stats.covariance()')
    def covariance(self, y: Column, ddof: Optional[int] = 1) -> Column:
        """Apply a covariance calculation between two value series.

        Notes:
            Covariance is a statistical measure of the joint variability of two random variables. See
                https://en.wikipedia.org/wiki/Covariance

        Args:
            y (Column): the second series.
            ddof (Optional[int]): delta degrees of freedom, use 0 for population covariance or 1 for sample covariance.
            Defaults to 1.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2, a3: f'covariance({a1.sql}, {a2.sql}, {a3.sql})'
        return Column(fn=fn, parents=(self._column, y, ddof), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.stats.empirical_cdf()')
    @input_constraints(..., Is.numeric, name='.stats.empirical_cdf()')
    def empirical_cdf(self, value: Union[Column, float]) -> Column:
        """Apply an empirical CDF calculation to these values.

        Notes:
            The empirical CDF is the cumulative distribution function of a sample. It is a step function that jumps by
            1/n at each of the n data points. This function returns the value of the empirical CDF at the given value.
            See
                https://en.wikipedia.org/wiki/Empirical_distribution_function

        Args:
            value (Union[Column, float]): location to evaluate the empirical CDF at.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, v: f'empirical_cume_dist_function({a1.sql}, {v.sql})'
        return Column(fn=fn, parents=(self._column, value), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.stats.pearson_r()')
    @input_constraints(..., Is.numeric, name='.stats.pearson_r()')
    def pearson_r(self, y: Column) -> Column:
        """Apply a Pearson's R calculation between two value series.

        Notes:
            Pearson's r is a measure of the linear correlation between two random variables. See
                https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

        Args:
            y (Column): the other series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'pearson_correlation({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.stats.spearman_r()')
    @input_constraints(..., Is.numeric, name='.stats.spearman_r()')
    def spearman_r(self, y: Column) -> Column:
        """Apply a Spearman's R calculation between two value series.

        Notes:
            Spearman's rho measures how monotonic the relationship between two random variables is. See
                https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient

        Args:
            y (Column): the other series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'spearman_correlation({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    def median_abs_deviation(self) -> Column:
        """Apply a median absolute deviation calculation to these values.

        Notes:
            The median absolute deviation is a measure of the variability of a random variable. Unlike the standard
            deviation it is robust to the presence of outliers. See
                https://en.wikipedia.org/wiki/Median_absolute_deviation

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'median_absolute_deviation({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def skewness(self) -> Column:
        """Apply a skewness calculation to these values.

        Notes:
            Skewness measures the degree of asymmetry of a random variable around its mean. See
                https://en.wikipedia.org/wiki/Skewness
            This calculation currently only supports sample skewness.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'skewness({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def kurtosis(self) -> Column:
        """Apply a kurtosis calculation to these values.

        Notes:
            Kurtosis measures how much probability density is in the tails (extremes) of a sample's distribution. See
                https://en.wikipedia.org/wiki/Kurtosis
            This function corresponds to the Pearson Kurtosis measure not the Fisher one.
            This calculation currently only supports sample kurtosis.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'kurtosis({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def root_mean_square(self) -> Column:
        """Apply a root mean square calculation to these values.

        Notes:
            RMS is the square root of the mean of the squared values of a set of values. It is a statistical measure of the
            spead of a random variable. See
                https://en.wikipedia.org/wiki/Root_mean_square

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'root_mean_square({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def harmonic_mean(self) -> Column:
        """Apply a harmonic mean calculation to these values.

        Notes:
            The harmonic mean is the reciprocal of the mean of the individual reciprocals of the values in a set. See
                https://en.wikipedia.org/wiki/Harmonic_mean

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'harmonic_mean({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def geometric_mean(self) -> Column:
        """Apply a geometric mean calculation to these values.

        Notes:
            The geometric mean is the multiplicative equivalent of the normal arithmetic mean. It multiplies a set of n-many
            numbers together and then takes the n-th root of the result. See
                https://en.wikipedia.org/wiki/Geometric_mean

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'geometric_mean({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def geometric_stdev(self) -> Column:
        """Apply a geometric standard deviation calculation to these values.

        Notes:
            The geometric standard deviation measures the variability of a set of numbers where the appropriate mean to use
            is the geometric one (they are more appropriately combined by multiplication rather than addition). See
                https://en.wikipedia.org/wiki/Geometric_standard_deviation

            This is computed as the exponential of the standard deviation of the natural log of each element in the set
                GSD = exp(stdev(log(x)))

        Returns:
            Column: column instance representing this calculation.

        """
        return self._column.log().stats.stdev().exp()

    def entropy(self) -> Column:
        """Apply an entropy calculation to these values.

        Notes:
            The Shannon entropy measures the average amount of "surprise" in a sequence of values. It can be considered a
            measure of variability.
                https://en.wikipedia.org/wiki/Entropy_(information_theory)
            It is calculated as
                S = -sum(p_i * log(p_i))
            where p_i is the probability of the ith value occurring computed from the sample (n occurrences / sample size).

            This function is equivalent to scipy.stats.entropy called with a single series and with the natural base.
                https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'entropy({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def interquartile_range(self) -> Column:
        """Apply an interquartile range calculation to these values.

        Notes:
            The interquartile range is the difference between the upper and lower quartiles. It can be used as a robust
            measure of the variability of a random variable. See
                https://en.wikipedia.org/wiki/Interquartile_range

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'interquartile_range({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.stats.interquantile_range()')
    @input_constraints(..., Is.numeric, Is.numeric, name='.stats.interquantile_range()')
    def interquantile_range(self, q1: Union[Column, float], q2: Union[Column, float]) -> Column:
        """Apply an interquantile range calculation to these values.

        Notes:
            The interquantile range is the difference between two different quantiles. This is a generalisation of the
            interquartile range where q1=0.25 and q2=0.75.
            The upper quantile (q2) value must be greater than the lower quantile (q1) value.

        Args:
            q1 (Union[Column, float]):
            q2 (Union[Column, float]):

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2, a3: f'interquantile_range({a1.sql}, {a2.sql}, {a3.sql})'
        return Column(fn=fn, parents=(self._column, q1, q2), dtype=DType.Double, label='aggfunc')

    def coef_of_variation(self) -> Column:
        """Apply a coefficient of variation calculation to these values.

        Notes:
            The coefficient of variation is the standard deviation scaled by the mean. It is a standardised measure of the
            dispersion of a random variable so distributions of different scale can be compared. See
                https://en.wikipedia.org/wiki/Coefficient_of_variation

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'coefficient_of_variation({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def mean_stdev_ratio(self) -> Column:
        """Apply a mean/stdev ratio calculation to these values.

        Notes:
            This is a convenience function for computing the mean divided by the standard deviation. This is used in
            multiple financial statistics such as the Sharpe ratio and information ratio.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'mean_stdev_ratio({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def median(self) -> Column:
        """Apply a median calculation to these values.

        Notes:
            The median is the value that separates the top and bottom half of a dataset. See
                https://en.wikipedia.org/wiki/Median
            It is equivalent to quantile 0.5, or the 50th percentile.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'quantile({a.sql}, 0.5)'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def lower_quartile(self) -> Column:
        """Apply a lower quartile calculation to these values.

        Notes:
            The lower quartile is the value that bounds the lower quarter of a dataset. See
                https://en.wikipedia.org/wiki/Quartile
            It is equivalent to quantile 0.25 or the 25th percentile.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'lower_quartile({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    def upper_quartile(self) -> Column:
        """Apply an upper quartile calculation to these values.

        Notes:
            The upper quartile is the value that bounds the upper quarter of a dataset. See
                https://en.wikipedia.org/wiki/Quartile
            It is equivalent to quantile 0.75 or the 75th percentile.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'upper_quartile({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.stats.quantile()')
    @input_constraints(..., Is.numeric, name='.stats.quantile()')
    def quantile(self, q: Union[Column, float]) -> Column:
        """Apply a quantile calculation to these values.

        Notes:
            The quantile function of a given random variable and q value finds the value x where the probability of
            observing a value less than or equal to x is equal to q. See
                https://en.wikipedia.org/wiki/Quantile_function

        Args:
            q (Union[Column, float]): the quantile value to compute.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'quantile({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, q), dtype=DType.Double, label='aggfunc')

    def stdev(self) -> Column:
        """Apply a standard deviation calculation to these values.

        Notes:
            The standard deviation measures the dispersion of a set of values around the mean. See
                https://en.wikipedia.org/wiki/Standard_deviation
            This only calculates the sample standard deviation (delta degrees of freedom = 1)

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a: f'window_stdev({a.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Double, label='aggfunc')
