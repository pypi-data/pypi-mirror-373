from lumipy.lumiflex._metadata import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestStatsWindowFnAccessor(SqlTestCase):

    def test_window_stats_accessor_covariance(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.covariance(table.col0, table.col1, 0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            covariance(AA.[Col0], AA.[Col1], 0) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_empirical_cdf(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.empirical_cdf(table.col0, 100)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            empirical_cume_dist_function(AA.[Col0], 100) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_pearson_r(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        res = win.stats.pearson_r(table.col0, table.col1)
        res = table_a._add_prefix(res)

        self.assertEqual(DType.Double, res.dtype)
        self.assertSqlEqual(
            """
            pearson_correlation(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            res.sql
        )

    def test_window_stats_accessor_spearman_r(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.spearman_r(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            spearman_correlation(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_median_abs_deviation(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.median_abs_deviation(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            median_absolute_deviation(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_skewness(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.skewness(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            skewness(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_kurtosis(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.kurtosis(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            kurtosis(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_root_mean_square(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.root_mean_square(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            root_mean_square(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_harmonic_mean(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.harmonic_mean(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            harmonic_mean(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_geometric_mean(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.geometric_mean(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            geometric_mean(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_geometric_stdev(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.geometric_stdev(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            exp(window_stdev(log(AA.[Col0])) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            )
            """,
            x.sql
        )

    def test_window_stats_accessor_entropy(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.entropy(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            entropy(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_interquartile_range(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.interquartile_range(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            interquartile_range(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_interquantile_range(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.interquantile_range(table.col0, 0.025, 0.975)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            interquantile_range(AA.[Col0], 0.025, 0.975) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_coef_of_variation(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.coef_of_variation(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            coefficient_of_variation(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_mean_stdev_ratio(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.mean_stdev_ratio(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            mean_stdev_ratio(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_median(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.median(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            quantile(AA.[Col0], 0.5) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_lower_quartile(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.lower_quartile(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            lower_quartile(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_upper_quartile(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.upper_quartile(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            upper_quartile(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_quantile(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.quantile(table.col0, 0.333)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            quantile(AA.[Col0], 0.333) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_stats_accessor_stdev(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.stats.stdev(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            window_stdev(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )
