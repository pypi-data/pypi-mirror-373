from lumipy.lumiflex._metadata import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestMetricWindowFnAccessor(SqlTestCase):

    def test_window_metric_accessor_mean_squared_error(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.mean_squared_error(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            mean_squared_error(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_mean_absolute_error(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.mean_absolute_error(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            mean_absolute_error(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_mean_fractional_absolute_error(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.mean_fractional_absolute_error(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            mean_fractional_absolute_error(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_minkowski_distance(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.minkowski_distance(table.col0, table.col1, 3)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            minkowski_distance(AA.[Col0], AA.[Col1], 3) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_chebyshev_distance(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.chebyshev_distance(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            chebyshev_distance(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_braycurtis_distance(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.braycurtis_distance(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            braycurtis_distance(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_cosine_distance(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.cosine_distance(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            cosine_distance(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_precision_score(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.precision_score(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            precision_score(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_recall_score(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.recall_score(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            recall_score(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_f_score(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.f_score(table.col0, table.col1, 0.5)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            fbeta_score(AA.[Col0], AA.[Col1], 0.5) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_r_squared(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.r_squared(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            r_squared(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_metric_accessor_adjusted_r_squared(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.metric.adjusted_r_squared(table.col0, table.col1, 1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            adjusted_r_squared(AA.[Col0], AA.[Col1], 1) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )




