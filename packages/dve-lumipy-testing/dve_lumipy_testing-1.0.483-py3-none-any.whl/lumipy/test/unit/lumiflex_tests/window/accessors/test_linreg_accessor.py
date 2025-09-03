from lumipy.lumiflex._metadata import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestLinregWindowFnAccessor(SqlTestCase):

    def test_window_linreg_accessor_alpha(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.linreg.alpha(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            linear_regression_alpha(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_linreg_accessor_beta(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.linreg.beta(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            linear_regression_beta(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_linreg_accessor_alpha_str_err(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.linreg.alpha_std_err(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            linear_regression_alpha_error(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )

    def test_window_linreg_accessor_beta_std_err(self):
        table, win = self.make_window_table_pair()
        table_a = table.with_alias('AA')

        x = win.linreg.beta_std_err(table.col0, table.col1)
        x = table_a._add_prefix(x)

        self.assertEqual(DType.Double, x.dtype)
        self.assertSqlEqual(
            """
            linear_regression_beta_error(AA.[Col0], AA.[Col1]) OVER(
                PARTITION BY AA.[Col0], AA.[Col1], AA.[Col2], AA.[Col3]
                ORDER BY AA.[Col0] ASC, AA.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            x.sql
        )
