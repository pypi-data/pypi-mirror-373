from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.operation import Having, _having_make


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestHaving(SqlTestCase):

    def make_vars(self, name='my.table.one'):
        table = self.make_table(name)
        return table, table.select('*').group_by(table.col4, TestGroup=table.col0 % 3).having(table.col0.mean() > 0)

    def test_having_creation(self):
        table = self.make_table()
        group_by = table.group_by(Groups=table.col0 % 3)

        content = group_by.content.update_node(having_filter=table.col1.mean() > 0)

        having = Having(parents=(group_by, content), client=table.client_)

        self.assertEqual('having', having.get_label())

        sql = having.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               ([Col0] % 3) AS [Groups]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               ([Col0] % 3)
            HAVING
               avg([Col1]) > 0
            """,
            sql
        )

    def test_having_make_validation(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')
        group_by = table1.group_by(Groups=table1.col0 % 3)

        # assert agg check
        self.assertErrorsWithMessage(
            lambda: _having_make(group_by, table1.col0 > 0),
            ValueError,
            "The condition given to .having() must depend on group aggregate values (e.g. table.col.mean() > 0)."
        )

        # assert membership check
        self.assertErrorsWithMessage(
            lambda: _having_make(group_by, table2.col0.count() > 2),
            ValueError,
            """
            There are columns in the input to .having() that do not belong to the table (my.table.one):
            count([Col0]) > 2 has dependence on my.table.two
            The column may be from the same provider but a with a different set of parameter values and therefore constitutes a different table.
            """
        )

    def test_having_order_by(self):
        table, having = self.make_vars()
        q = having.order_by(table.col0.asc(), table.col1.desc())
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [TestGroup]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col4], ([Col0] % 3)
            HAVING
               (avg([Col0]) > 0)
            ORDER BY
               [Col0] ASC, [Col1] DESC
            """,
            sql
        )

    def test_having_limit(self):
        table, having = self.make_vars()
        q = having.limit(1000, 33)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [TestGroup]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col4], ([Col0] % 3)
            HAVING
               (avg([Col0]) > 0)
            LIMIT 1000 OFFSET 33            
            """,
            sql
        )

    def test_having_to_table_var(self):
        table, having = self.make_vars()

        q = having.to_table_var('TEST_VAR').select('*')
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            @TEST_VAR = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [TestGroup]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            GROUP BY
               [Col4], ([Col0] % 3)
            HAVING
               (avg([Col0]) > 0);
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], [TestGroup]
            FROM
               @TEST_VAR
            """,
            sql
        )
