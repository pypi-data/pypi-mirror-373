from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.operation import Aggregate


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestAggregate(SqlTestCase):

    def make_vars(self, name='my.test.table'):
        table = self.make_table(name)
        agg = table.group_by(table.col0, table.col4).agg(TestMean=table.col0.mean(), TestCount=table.col1.count())
        return table, agg

    def test_aggregate_creation(self):
        table = self.make_table()
        group_by = table.group_by(table.col0, table.col4)

        aggs = [table.col0.mean()._with_alias('TestMean'), table.col1.count()._with_alias('TestCount')]
        content = group_by.content.update_node(aggregates=aggs)

        agg = Aggregate(parents=(group_by, content), client=table.client_)

        self.assertEqual('aggregate', agg.get_label())

        sql = agg.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col4], avg([Col0]) AS [TestMean], count([Col1]) AS [TestCount]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col0], [Col4]            
            """,
            sql
        )

    def test_aggregate_make_validation(self):
        table = self.make_table()
        bad_table = self.make_table('my.other.table')

        group_by = table.group_by(table.col0, table.col4)

        self.assertErrorsWithMessage(
            lambda: group_by.agg(table.col2.mean()),
            ValueError,
            '.agg() only accepts keyword arguments, this is so they are always given an alias. '
            'Try something like\n'
            '    .agg(MyValue=table.my_col.mean())'
        )

        self.assertErrorsWithMessage(
            lambda: group_by.agg(Mean=table.col1.mean(), Bad=table.col3, AlsoBad=3),
            ValueError,
            '.agg() only accepts aggregate expressions (must contain at least one aggregate function such as sum).\n'
            'The following inputs resolved to non-aggregate values:\n'
            '    Bad: [Col3]\n'
            '    AlsoBad: 3'
        )

        self.assertErrorsWithMessage(
            lambda: group_by.agg(Mean=bad_table.col1.mean(), Num=table.col0.count(), Std=bad_table.col1.stats.stdev()),
            ValueError,
            """
            There are columns in the input to .agg that do not belong to the table (My.Test.Table):
            avg([Col1]) AS [Mean] has dependence on my.other.table
            window_stdev([Col1]) AS [Std] has dependence on my.other.table
            The column may be from the same provider but a with a different set of parameter values and therefore constitutes a different table.
            """
        )

    def test_aggregate_having(self):
        table, agg = self.make_vars()
        having = agg.having(table.col0.mean() > 0)
        sql = having.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col4], avg([Col0]) AS [TestMean], count([Col1]) AS [TestCount]
            FROM
               [my.test.table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col0], [Col4]
            HAVING
               (avg([Col0]) > 0)
            """,
            sql
        )

    def test_aggregate_order_by(self):
        table, agg = self.make_vars()
        order_by = agg.order_by(table.col4.count().desc(), table.col0.mean().asc())
        sql = order_by.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col4], avg([Col0]) AS [TestMean], count([Col1]) AS [TestCount]
            FROM
               [my.test.table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col0], [Col4]
            ORDER BY
               count([Col4]) DESC, avg([Col0]) ASC            
            """,
            sql
        )

    def test_aggregate_limit(self):
        table, agg = self.make_vars()

        limit = agg.limit(1010, 33)
        sql = limit.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col4], avg([Col0]) AS [TestMean], count([Col1]) AS [TestCount]
            FROM
               [my.test.table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col0], [Col4]
            LIMIT 1010 OFFSET 33            
            """,
            sql
        )

        limit = agg.limit(1010)
        sql = limit.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col4], avg([Col0]) AS [TestMean], count([Col1]) AS [TestCount]
            FROM
               [my.test.table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col0], [Col4]
            LIMIT 1010
            """,
            sql
        )

        limit = agg.limit(None, 57)
        sql = limit.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col4], avg([Col0]) AS [TestMean], count([Col1]) AS [TestCount]
            FROM
               [my.test.table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col0], [Col4]
            LIMIT -1 OFFSET 57
            """,
            sql
        )

    def test_aggregate_to_table_var(self):
        table, agg = self.make_vars()

        q = agg.to_table_var('TEST_VAR').select('*')

        sql = q.get_sql()
        self.assertSqlEqual(
            """
            @TEST_VAR = SELECT
               [Col0], [Col4], avg([Col0]) AS [TestMean], count([Col1]) AS [TestCount]
            FROM
               [my.test.table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col0], [Col4];
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col4], [TestMean], [TestCount]
            FROM
               @TEST_VAR
            """,
            sql
        )
