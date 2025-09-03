from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestFinanceFnAccessor(SqlTestCase):

    def test_finance_function_accessor_errors_with_non_numeric_col(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('a').finance,
            AttributeError,
            "To use .finance accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_finance_function_accessor_drawdown(self):
        table = self.make_table()
        r = table.col0.finance.drawdown()
        self.assertSqlEqual(
            """
            drawdown([Col0]) OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            r.sql
        )
        r = table.col0.finance.drawdown(table.col1.asc())
        self.assertSqlEqual(
            """
            drawdown([Col0]) OVER(
                ORDER BY [Col1] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            r.sql
        )

    def test_finance_function_accessor_max_drawdown(self):
        table = self.make_table()
        r = table.col0.finance.max_drawdown()
        self.assertEqual("max_drawdown([Col0])", r.sql)

    def test_finance_function_accessor_mean_drawdown(self):
        table = self.make_table()
        r = table.col0.finance.mean_drawdown()
        self.assertEqual("mean_drawdown([Col0])", r.sql)

    def test_finance_function_accessor_max_drawdown_length(self):
        table = self.make_table()
        r = table.col0.finance.max_drawdown_length()
        self.assertEqual("max_drawdown_length([Col0])", r.sql)

    def test_finance_function_accessor_mean_drawdown_length(self):
        table = self.make_table()
        r = table.col0.finance.mean_drawdown_length()
        self.assertEqual("mean_drawdown_length([Col0])", r.sql)

    def test_finance_function_accessor_gain_loss_ratio(self):
        table = self.make_table()
        r = table.col0.finance.gain_loss_ratio()
        self.assertEqual("gain_loss_ratio([Col0])", r.sql)

    def test_finance_function_accessor_semi_deviation(self):
        table = self.make_table()
        r = table.col0.finance.semi_deviation()
        self.assertEqual("semi_deviation([Col0])", r.sql)

    def test_finance_function_accessor_information_ratio(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.finance.information_ratio(y)
        self.assertEqual("mean_stdev_ratio([Col0] - [Col1])", r.sql)

    def test_finance_function_accessor_tracking_error(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.finance.tracking_error(y)
        self.assertEqual("window_stdev([Col0] - [Col1])", r.sql)

    def test_finance_function_accessor_sharpe_ratio(self):
        table = self.make_table()
        r = table.col0.finance.sharpe_ratio(0.01)
        self.assertEqual("mean_stdev_ratio([Col0] - 0.01)", r.sql)

    def test_finance_function_accessor_prices_to_returns(self):
        table = self.make_table()
        r = table.col0.finance.prices_to_returns()
        self.assertSqlEqual(
            """
            prices_to_returns([Col0], 1, 1.0, FALSE) OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            r.sql
        )

        r = table.col0.finance.prices_to_returns(interval=5, order=table.col1.asc(), time_factor=10, compound=True)
        self.assertSqlEqual(
            """
            prices_to_returns([Col0], 5, 10, TRUE) OVER(
                ORDER BY [Col1] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            r.sql
        )

    def test_finance_function_accessor_returns_to_prices(self):
        table = self.make_table()
        r = table.col0.finance.returns_to_prices(100)
        self.assertSqlEqual(
            """
            returns_to_prices([Col0], 100, 1.0, FALSE) OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            r.sql
        )

        r = table.col0.finance.returns_to_prices(100, 2.0, True, table.col1.asc())
        self.assertSqlEqual(
            """
            returns_to_prices([Col0], 100, 2.0, TRUE) OVER(
                ORDER BY [Col1] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            r.sql
        )
