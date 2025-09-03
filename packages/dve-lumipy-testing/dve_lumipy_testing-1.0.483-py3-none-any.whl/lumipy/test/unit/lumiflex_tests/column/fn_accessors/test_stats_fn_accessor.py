from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestStatsFnAccessor(SqlTestCase):

    def test_stats_function_accessor_errors_with_non_numeric_col(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('a').stats,
            AttributeError,
            "To use .stats accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_stats_function_accessor_covariance(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.covariance(y, 0)
        self.assertEqual("covariance([Col0], [Col1], 0)", r.sql)
        r = x.stats.covariance(y)
        self.assertEqual("covariance([Col0], [Col1], 1)", r.sql)

    def test_stats_function_accessor_empirical_cdf(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.empirical_cdf(51)
        self.assertEqual("empirical_cume_dist_function([Col0], 51)", r.sql)

    def test_stats_function_accessor_pearson_r(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.pearson_r(y)
        self.assertEqual("pearson_correlation([Col0], [Col1])", r.sql)

    def test_stats_function_accessor_spearman_r(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.spearman_r(y)
        self.assertEqual("spearman_correlation([Col0], [Col1])", r.sql)

    def test_stats_function_accessor_median_abs_deviation(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.median_abs_deviation()
        self.assertEqual("median_absolute_deviation([Col0])", r.sql)

    def test_stats_function_accessor_skewness(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.skewness()
        self.assertEqual("skewness([Col0])", r.sql)

    def test_stats_function_accessor_kurtosis(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.kurtosis()
        self.assertEqual("kurtosis([Col0])", r.sql)

    def test_stats_function_accessor_root_mean_square(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.root_mean_square()
        self.assertEqual("root_mean_square([Col0])", r.sql)

    def test_stats_function_accessor_harmonic_mean(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.harmonic_mean()
        self.assertEqual("harmonic_mean([Col0])", r.sql)

    def test_stats_function_accessor_geometric_mean(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.geometric_mean()
        self.assertEqual("geometric_mean([Col0])", r.sql)

    def test_stats_function_accessor_geometric_stdev(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.geometric_stdev()
        self.assertEqual("exp(window_stdev(log([Col0])))", r.sql)

    def test_stats_function_accessor_entropy(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.entropy()
        self.assertEqual("entropy([Col0])", r.sql)

    def test_stats_function_accessor_interquartile_range(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.interquartile_range()
        self.assertEqual("interquartile_range([Col0])", r.sql)

    def test_stats_function_accessor_interquantile_range(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.interquantile_range(0.05, 0.95)
        self.assertEqual("interquantile_range([Col0], 0.05, 0.95)", r.sql)

    def test_stats_function_accessor_coef_of_variation(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.coef_of_variation()
        self.assertEqual("coefficient_of_variation([Col0])", r.sql)

    def test_stats_function_accessor_mean_stdev_ratio(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.mean_stdev_ratio()
        self.assertEqual("mean_stdev_ratio([Col0])", r.sql)

    def test_stats_function_accessor_median(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.median()
        self.assertEqual("quantile([Col0], 0.5)", r.sql)

    def test_stats_function_accessor_lower_quartile(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.lower_quartile()
        self.assertEqual("lower_quartile([Col0])", r.sql)

    def test_stats_function_accessor_upper_quartile(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.upper_quartile()
        self.assertEqual("upper_quartile([Col0])", r.sql)

    def test_stats_function_accessor_quantile(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.quantile(0.99)
        self.assertEqual("quantile([Col0], 0.99)", r.sql)

    def test_stats_function_accessor_stdev(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.stats.stdev()
        self.assertEqual("window_stdev([Col0])", r.sql)
