from lumipy.lumiflex._metadata import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestFinanceWindowFnAccessor(SqlTestCase):

    def test_window_finance_accessor_drawdown(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.drawdown(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            drawdown(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_mean_drawdown(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.mean_drawdown(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            mean_drawdown(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_max_drawdown(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.max_drawdown(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            max_drawdown(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_drawdown_length(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.drawdown_length(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            drawdown_length(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_mean_drawdown_length(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.mean_drawdown_length(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            mean_drawdown_length(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_max_drawdown_length(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.max_drawdown_length(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            max_drawdown_length(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_gain_loss_ratio(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.gain_loss_ratio(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            gain_loss_ratio(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_semi_deviation(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.semi_deviation(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            semi_deviation(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_gain_mean(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.gain_mean(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            gain_mean(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_loss_mean(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.finance.loss_mean(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            loss_mean(AA.[Col0]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_gain_stdev(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        win = win.filter(table.col2 == 3)
        x = win.finance.gain_stdev(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            window_stdev(AA.[Col0]) FILTER(WHERE (AA.[Col2] = 3) AND (AA.[Col0] >= 0)) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_loss_stdev(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        win = win.filter(table.col2 == 3)
        x = win.finance.loss_stdev(table.col0)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            window_stdev(AA.[Col0]) FILTER(WHERE (AA.[Col2] = 3) AND (AA.[Col0] < 0)) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_downside_deviation(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        win = win.filter(table.col2 == 3)
        x = win.finance.downside_deviation(table.col0, 0.5)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            window_stdev(AA.[Col0]) FILTER(WHERE (AA.[Col2] = 3) AND (AA.[Col0] < 0.5)) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_information_ratio(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        win = win.filter(table.col2 == 3)
        x = win.finance.information_ratio(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            mean_stdev_ratio((AA.[Col0] - AA.[Col1])) FILTER(WHERE (AA.[Col2] = 3)) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_tracking_error(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        win = win.filter(table.col2 == 3)
        x = win.finance.tracking_error(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            window_stdev((AA.[Col0] - AA.[Col1])) FILTER(WHERE (AA.[Col2] = 3)) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_sharpe_ratio(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        win = win.filter(table.col2 == 3)
        x = win.finance.sharpe_ratio(table.col0, table.col2)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            mean_stdev_ratio((AA.[Col0] - AA.[Col2])) FILTER(WHERE (AA.[Col2] = 3)) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_finance_accessor_volatility(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        win = win.filter(table.col2 == 3)
        x = win.finance.volatility(table.col0, 180)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            window_stdev(AA.[Col0]) FILTER(WHERE (AA.[Col2] = 3)) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
                * power(180, 0.5)
            """,
            x.sql
        )
