from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.operation import Select
from lumipy.lumiflex._table.content import CoreContent


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestSelect(SqlTestCase):

    def test_select_creation(self):
        table = self.make_table()
        cols = table.get_columns()
        content = CoreContent(select_cols=cols, parents=(table,), table=table)

        select = Select(parents=(table, content), client=table.client_)

        self.assertEqual('select', select.get_label())
        self.assertHashEqual(content, select.content)
        self.assertSequenceHashEqual([table, content], select.get_parents())

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
            """,
            select.get_sql()
        )

    def test_select_methods_where(self):
        table1 = self.make_table('my.table.one')
        q = table1.select('*').where((table1.col0 + table1.col1)/2 > 0)
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.one]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (((([Col0] + [Col1]) / cast(2 AS Double)) > 0))
            """,
            q.get_sql()
        )

    def test_select_methods_where_validation(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')
        table3 = self.make_table('my.table.three')

        join = table1.inner_join(table2, table1.col0 == table2.col0)
        # Membership
        self.assertErrorsWithMessage(
            lambda: join.select('*').where(table3.col0 > 0),
            ValueError,
            """
            There are columns in the input to .where() that do not belong to the table (my.table.one join my.table.two):
            ([Col0] > 0) has dependence on my.table.three
            The column may be from the same provider but a with a different set of parameter values and therefore constitutes a different table.
            """
        )
        # Boolean constraint
        self.assertErrorsWithMessage(
            lambda: join.select('*').where(table1.col0),
            TypeError,
            """
            Invalid input detected at
               → lambda: join.select('*').where(table1.col0),
            There was 1 failed constraint on .where():
               • The input to 'condition' must be Boolean but was Int=[Col0]
            """
        )

    def test_select_methods_group_by(self):
        table1 = self.make_table('my.table.one')
        pass

    def test_select_methods_order_by(self):
        table1 = self.make_table('my.table.one')
        pass

    def test_select_methods_limit(self):
        table1 = self.make_table('my.table.one')
        pass

    def test_select_methods_union(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*')
        sq2 = table2.select('*')

        q = sq1.union(sq2)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.one]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            """,
            sql
        )

    def test_select_methods_union_all(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*')
        sq2 = table2.select('*')

        q = sq1.union_all(sq2)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.one]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            UNION ALL
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            """,
            sql
        )

    def test_select_methods_intersect(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*')
        sq2 = table2.select('*')

        q = sq1.intersect(sq2)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.one]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            INTERSECT
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            """,
            sql
        )

    def test_select_methods_exclude(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*')
        sq2 = table2.select('*')

        q = sq1.exclude(sq2)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.one]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            EXCEPT
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            """,
            sql
        )

    def test_select_methods_to_table_var(self):
        table1 = self.make_table('my.table.one')

        q = table1.select('*', Test=table1.col0 / 2.0).to_table_var('TEST_VAR').select('*')
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            @TEST_VAR = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] / 2.0) AS [Test]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], [Test]
            FROM
               @TEST_VAR            
            """,
            sql
        )

    def test_select_where_with_is_in_subquery(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        tv = table1.select(table1.col0).limit(100).to_table_var('tv_1')

        q = table2.select(table2.col2).where(table2.col0.is_in(tv.select('*')))

        sql = q.get_sql()
        self.assertSqlEqual(
            """
            @tv_1 = SELECT
               [Col0]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            LIMIT 100;
            --===========================================================================================--

            SELECT
               [Col2]
            FROM
               [my.table.two]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] IN (
                  SELECT
                     [Col0]
                  FROM
                     @tv_1
               )))            
            """,
            sql
        )
