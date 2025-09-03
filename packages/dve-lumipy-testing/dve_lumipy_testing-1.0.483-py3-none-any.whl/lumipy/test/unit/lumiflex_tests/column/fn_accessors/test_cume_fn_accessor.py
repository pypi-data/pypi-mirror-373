from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestCumeFnColumnAccessor(SqlTestCase):

    def test_cume_function_accessor_errors_with_non_numeric_col(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('a').cume,
            AttributeError,
            "To use .cume accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_cume_function_accessor_prod(self):
        table = self.make_table()

        c1 = table.col0.cume.prod()
        c2 = table.col0.cume.prod(order=table.col1.asc())

        sql1 = c1.sql
        self.assertSqlEqual(
            """
            cumeprod([Col0]) OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            sql1
        )

        sql2 = c2.sql
        self.assertSqlEqual(
            """
            cumeprod([Col0]) OVER(
                ORDER BY [Col1] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
            )
            """,
            sql2
        )

    def test_cume_function_accessor_sum(self):
        table = self.make_table()

        c1 = table.col0.cume.sum()
        c2 = table.col0.cume.sum(order=table.col1.asc())

        sql1 = c1.sql
        self.assertSqlEqual(
            """
            sum([Col0]) OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            sql1
        )

        sql2 = c2.sql
        self.assertSqlEqual(
            """
            sum([Col0]) OVER(
                ORDER BY [Col1] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
            )
            """,
            sql2
        )

    def test_cume_function_accessor_min(self):
        table = self.make_table()

        c1 = table.col0.cume.min()
        c2 = table.col0.cume.min(order=table.col1.asc())

        sql1 = c1.sql
        self.assertSqlEqual(
            """
            min([Col0]) OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            sql1
        )

        sql2 = c2.sql
        self.assertSqlEqual(
            """
            min([Col0]) OVER(
                ORDER BY [Col1] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
            )
            """,
            sql2
        )

    def test_cume_function_accessor_max(self):
        table = self.make_table()

        c1 = table.col0.cume.max()
        c2 = table.col0.cume.max(order=table.col1.asc())

        sql1 = c1.sql
        self.assertSqlEqual(
            """
            max([Col0]) OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            sql1
        )

        sql2 = c2.sql
        self.assertSqlEqual(
            """
            max([Col0]) OVER(
                ORDER BY [Col1] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
            )
            """,
            sql2
        )

    def test_cume_function_accessor_dist(self):
        table = self.make_table()

        c1 = table.col0.cume.dist()

        sql1 = c1.sql
        self.assertSqlEqual(
            """
            cume_dist() OVER(
                ORDER BY [Col0] ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            sql1
        )
