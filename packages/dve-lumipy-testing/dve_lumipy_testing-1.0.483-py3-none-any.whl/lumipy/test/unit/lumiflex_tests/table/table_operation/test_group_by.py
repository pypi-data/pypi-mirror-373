from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.operation import Select, GroupBy, _group_by_make
from lumipy.lumiflex._table.content import CoreContent


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestGroupBy(SqlTestCase):

    def make_vars(self, name='My.Test.Table'):
        table = self.make_table(name)
        return table, table.select('*').where(table.col0 > 0).group_by(table.col4, TestGroup=table.col0 % 3)

    def test_group_by_creation(self):
        table = self.make_table()
        cols = table.get_columns()
        content = CoreContent(select_cols=cols, parents=(table,), table=table)

        select = Select(parents=(table, content), client=table.client_)
        content = content.update_node(group_by_cols=[table.col0, table.col1])
        group_by = GroupBy(parents=(select, content), client=table.client_)

        self.assertEqual('group_by', group_by.get_label())

        sql = group_by.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col0], [Col1]
            """,
            sql
        )

    def test_group_by_make_validation(self):
        table = self.make_table()
        bad_table = self.make_table('my.other.table')
        select = table.select('*')

        self.assertErrorsWithMessage(
            lambda: _group_by_make(select, table.col1.exp(), table.col3, table.col0.mean(), 3),
            ValueError,
            "Inputs to *cols must be original table columns (not calculations or python values), but were\n"
            "  cols[0] = exp([Col1]) (Column func)\n"
            "  cols[2] = avg([Col0]) (Column aggfunc)\n"
            "  cols[3] = 3 (int)\n"
            "Only table columns can be supplied as unnamed cols. Other columns types such as functions of columns or "
            "python literals must be supplied as keyword args (except '*' and '^').\n"
            "Try something like one of the following:\n"
            "  •Scalar functions of columns: \n"
            "     table.select(col_doubled=provider.col*2)\n"
            "  •Aggregate functions of columns: \n"
            "     table.select(col_sum=provider.col.sum())\n"
            "  •Python literals: \n"
            "     table.select(higgs_mass=125.1)\n"
        )

        self.assertErrorsWithMessage(
            lambda: _group_by_make(select, bad_table.col0, BadExp=bad_table.col0.exp()),
            ValueError,
            """
            There are columns in the input to .group_by() that do not belong to the table (My.Test.Table):
            [Col0] has dependence on my.other.table
            exp([Col0]) AS [BadExp] has dependence on my.other.table
            The column may be from the same provider but a with a different set of parameter values and therefore constitutes a different table.
            """
        )

    def test_group_by_aggregate(self):
        table, group_by = self.make_vars()
        agg = group_by.aggregate(Agg1=table.col0.mean(), Agg2=(table.col1.sum())/3)
        sql = agg.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [TestGroup], avg([Col0]) AS [Agg1], (total([Col1]) / cast(3 AS Double)) AS [Agg2]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            GROUP BY
               [Col4], ([Col0] % 3)            
            """,
            sql
        )

    def test_group_by_agg(self):
        table, group_by = self.make_vars()
        agg = group_by.agg(Agg1=table.col0.mean(), Agg2=(table.col1.sum())/3)
        sql = agg.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [TestGroup], avg([Col0]) AS [Agg1], (total([Col1]) / cast(3 AS Double)) AS [Agg2]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            GROUP BY
               [Col4], ([Col0] % 3)            
            """,
            sql
        )

    def test_group_by_aggregate_validation(self):
        table, group_by = self.make_vars()

        self.assertErrorsWithMessage(
            lambda: group_by.agg(table.col0),
            ValueError,
            ".agg() only accepts keyword arguments, this is so they are always given an alias. "
            "Try something like\n    .agg(MyValue=table.my_col.mean())"
            )

        self.assertErrorsWithMessage(
            lambda: group_by.agg(Test1=table.col0, Test2=table.col1.exp()),
            ValueError,
            ".agg() only accepts aggregate expressions (must contain at least one aggregate function such as sum).\n"
            "The following inputs resolved to non-aggregate values:\n"
            "    Test1: [Col0]\n"
            "    Test2: exp([Col1])"
        )

        table2 = self.make_table('my.table.two')
        self.assertErrorsWithMessage(
            lambda: group_by.agg(Test1=table.col0, Test2=table2.col1.exp()),
            ValueError,
            "There are columns in the input to .agg that do not belong to the table (My.Test.Table):\n"
            "exp([Col1]) AS [Test2] has dependence on my.table.two\n"
            "The column may be from the same provider but a with a different set of parameter values and therefore constitutes a different table."
        )

    def test_group_by_having(self):
        table, group_by = self.make_vars()
        q = group_by.having(table.col0.mean() > 0.0)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [TestGroup]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            GROUP BY
               [Col4], ([Col0] % 3)
            HAVING
               (avg([Col0]) > 0.0)
            """,
            sql
        )

    def test_group_by_order_by(self):
        table, group_by = self.make_vars()
        q = group_by.order_by(table.col0.asc(), table.col1.desc())
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [TestGroup]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            GROUP BY
               [Col4], ([Col0] % 3)
            ORDER BY
               [Col0] ASC, [Col1] DESC            
            """,
            sql
        )

    def test_group_by_to_table_var(self):
        table, group_by = self.make_vars()

        q = group_by.to_table_var('TEST_VAR').select('*')
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            @TEST_VAR = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [TestGroup]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            GROUP BY
               [Col4], ([Col0] % 3);
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], [TestGroup]
            FROM
               @TEST_VAR
            """,
            sql
        )
