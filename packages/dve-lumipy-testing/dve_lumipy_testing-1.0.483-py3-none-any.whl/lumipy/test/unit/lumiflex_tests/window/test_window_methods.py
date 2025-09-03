from lumipy.lumiflex._metadata import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestSqlWindowMethods(SqlTestCase):

    def test_window_method_filter(self):
        table, over = self.make_window_table_pair()
        over_f = over.filter(table.col0 > 0)

        sql = over_f.get_sql()
        self.assertSqlEqual(
            """
            FILTER(WHERE ([Col0] > 0)) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_filter_validation(self):
        table, over = self.make_window_table_pair()
        self.assertErrorsWithMessage(
            lambda: over.filter(table.col0),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: over.filter(table.col0),\n"
            "There was 1 failed constraint on filter():\n"
            "   • The input to 'condition' must be Boolean but was Int=[Col0]"
        )

    def test_window_method_first(self):

        table, over = self.make_window_table_pair()

        win_fn = over.first(table.col0)
        sql = win_fn.sql
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            FIRST_VALUE([Col0]) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

        table_a = table.with_alias('ABC')
        win_fn_pfx = table_a._add_prefix(win_fn)
        sql = win_fn_pfx.sql
        self.assertSqlEqual(
            """
            first_value(ABC.[Col0]) OVER(
                PARTITION BY ABC.[Col0], ABC.[Col1], ABC.[Col2], ABC.[Col3]
                ORDER BY ABC.[Col0] ASC, ABC.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )            
            """,
            sql
        )

    def test_window_method_last(self):
        table, over = self.make_window_table_pair()
        win_fn = over.last(table.col0)
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            last_value([Col0]) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            win_fn.sql
        )

    def test_window_method_lag(self):
        table, over = self.make_window_table_pair()

        win_fn = over.lag(table.col0, 3, 999)
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            lag([Col0], 3, 999) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            win_fn.sql
        )

    def test_window_method_lag_defaults(self):
        table, over = self.make_window_table_pair()

        win_fn = over.lag(table.col0)
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            lag([Col0], 1, NULL) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            win_fn.sql
        )

    def test_window_method_lead(self):
        table, over = self.make_window_table_pair()

        win_fn = over.lead(table.col0, 3, 999)
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            lead([Col0], 3, 999) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            win_fn.sql
        )

    def test_window_method_nth_value(self):
        table, over = self.make_window_table_pair()
        win_fn = over.lead(table.col0)
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            lead([Col0], 1, NULL) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            win_fn.sql
        )

    def test_window_method_mean(self):
        table, over = self.make_window_table_pair()
        win_fn = over.mean(table.col0)
        sql = win_fn.sql
        self.assertEqual(DType.Double, win_fn.dtype)
        self.assertSqlEqual(
            """
            AVG([Col0]) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_count(self):
        table, over = self.make_window_table_pair()

        win_fn = over.count(table.col0)
        sql = win_fn.sql
        self.assertEqual(DType.Int, win_fn.dtype)
        self.assertSqlEqual(
            """
            count([Col0]) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_max(self):
        table, over = self.make_window_table_pair()
        win_fn = over.max(table.col0)
        sql = win_fn.sql
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            max([Col0]) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_min(self):
        table, over = self.make_window_table_pair()
        win_fn = over.min(table.col0)
        sql = win_fn.sql
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            min([Col0]) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_sum(self):
        table, over = self.make_window_table_pair()
        win_fn = over.sum(table.col0)
        sql = win_fn.sql
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            sum([Col0]) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_prod(self):
        table, over = self.make_window_table_pair()
        win_fn = over.prod(table.col0)
        sql = win_fn.sql
        self.assertEqual(table.col0.dtype, win_fn.dtype)
        self.assertSqlEqual(
            """
            cumeprod([Col0]) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_cume_dist(self):
        table, over = self.make_window_table_pair()
        win_fn = over.cume_dist()
        sql = win_fn.sql
        self.assertEqual(DType.Double, win_fn.dtype)
        self.assertSqlEqual(
            """
            cume_dist() OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_dense_rank(self):
        table, over = self.make_window_table_pair()
        win_fn = over.dense_rank()
        sql = win_fn.sql
        self.assertEqual(DType.Double, win_fn.dtype)
        self.assertSqlEqual(
            """
            dense_rank() OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_ntile(self):
        table, over = self.make_window_table_pair()
        win_fn = over.ntile(3)
        sql = win_fn.sql
        self.assertEqual(DType.Int, win_fn.dtype)
        self.assertSqlEqual(
            """
            ntile(3) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_rank(self):
        table, over = self.make_window_table_pair()
        win_fn = over.rank()
        sql = win_fn.sql
        self.assertEqual(DType.Int, win_fn.dtype)
        self.assertSqlEqual(
            """
            rank() OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_row_number(self):
        table, over = self.make_window_table_pair()
        win_fn = over.row_number()
        sql = win_fn.sql
        self.assertEqual(DType.Int, win_fn.dtype)
        self.assertSqlEqual(
            """
            row_number() OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_percent_rank(self):
        table, over = self.make_window_table_pair()
        win_fn = over.percent_rank()
        sql = win_fn.sql
        self.assertEqual(DType.Double, win_fn.dtype)
        self.assertSqlEqual(
            """
            percent_rank() OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_method_compose_multiple_filters(self):
        table, over = self.make_window_table_pair()
        win_fn = over.filter(table.col0 > 0).filter(table.col1 < 5).filter(0.5 * (table.col3 - 4) >= 0.5)

        table_a = table.with_alias('AA')
        win_fn = table_a._add_prefix(win_fn)

        sql = win_fn.get_sql()
        self.assertSqlEqual(
            """
            FILTER(WHERE ((AA.[Col0] > 0) AND (AA.[Col1] < 5)) AND ((0.5 * (AA.[Col3] - 4)) >= 0.5)) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )            
            """,
            sql
        )
