from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.operation import Select, Where
from lumipy.lumiflex._table.content import CoreContent


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestWhere(SqlTestCase):

    def make_vars(self, name='My.Test.Table'):
        table = self.make_table(name)
        return table, table.select('*').where(table.col0 > 0)

    def test_where_creation(self):
        table = self.make_table()
        cols = table.get_columns()
        content = CoreContent(select_cols=cols, parents=(table,), table=table)

        select = Select(parents=(table, content), client=table.client_)
        content = content.update_node(where_filter=table.col0 > 0)

        where = Where(parents=(select, content), client=table.client_)

        self.assertEqual('where', where.get_label())

        sql = where.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and ([Col0] > 0)
            """,
            sql
        )

    def test_where_methods_group_by(self):
        table, where = self.make_vars()
        q = where.group_by(table.col4, table.col5, ModTest=table.col0 % 3)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], ([Col0] % 3) AS [ModTest]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            GROUP BY
               [Col4], [Col5], ([Col0] % 3)            
            """,
            sql
        )

    def test_where_methods_order_by(self):
        table, where = self.make_vars()
        q = where.order_by(table.col0.asc(), table.col1.desc())
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            ORDER BY
               [Col0] ASC, [Col1] DESC            
            """,
            sql
        )

    def test_where_methods_limit(self):
        table, where = self.make_vars()
        q = where.limit(1000, 25)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            LIMIT 1000 OFFSET 25
            """,
            sql
        )

    def test_where_methods_union(self):
        table1, where1 = self.make_vars('my.table.one')
        table2, where2 = self.make_vars('my.table.two')

        q = where1.union(where2)
        sql = q.get_sql()
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
                   and (([Col0] > 0))
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))            
            """,
            sql
        )

    def test_where_methods_union_all(self):
        table1, where1 = self.make_vars('my.table.one')
        table2, where2 = self.make_vars('my.table.two')

        q = where1.union_all(where2)
        sql = q.get_sql()
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
                   and (([Col0] > 0))
            UNION ALL
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))            
            """,
            sql
        )

    def test_where_methods_intersect(self):
        table1, where1 = self.make_vars('my.table.one')
        table2, where2 = self.make_vars('my.table.two')

        q = where1.intersect(where2)
        sql = q.get_sql()
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
                   and (([Col0] > 0))
            INTERSECT
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))            
            """,
            sql
        )

    def test_where_methods_exclude(self):
        table1, where1 = self.make_vars('my.table.one')
        table2, where2 = self.make_vars('my.table.two')

        q = where1.exclude(where2)
        sql = q.get_sql()
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
                   and (([Col0] > 0))
            EXCEPT 
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))            
            """,
            sql
        )

    def test_where_methods_to_table_var(self):
        table, where = self.make_vars()

        q = where.to_table_var('TEST_VAR').select('*')
        sql = q.get_sql()

        self.assertSqlEqual(
            """
            @TEST_VAR = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0));
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               @TEST_VAR
            """,
            sql
        )
