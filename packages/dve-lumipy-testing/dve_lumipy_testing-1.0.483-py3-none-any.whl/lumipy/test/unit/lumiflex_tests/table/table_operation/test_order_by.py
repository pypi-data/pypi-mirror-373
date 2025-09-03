from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.operation import OrderBy


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestOrderBy(SqlTestCase):

    def make_vars(self, name='my.table.one'):
        table = self.make_table(name)
        return table, table.select('*').order_by(table.col0.asc(), (table.col1**0.5).desc())

    def test_order_by_creation(self):
        table = self.make_table()
        select = table.select('*')

        content = select.content.update_node(order_bys=[table.col0.asc(), table.col1.desc()])
        order_by = OrderBy(parents=(select, content), client=table.client_)

        self.assertEqual('order_by', order_by.get_label())

        sql = order_by.get_sql()
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
            ORDER BY
               [Col0] ASC, [Col1] DESC           
            """,
            sql
        )

    def test_order_by_limit(self):
        table, order_by = self.make_vars()
        q = order_by.limit(10000, 45)
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
            ORDER BY
               [Col0] ASC, power([Col1], 0.5) DESC
            LIMIT 10000 OFFSET 45            
            """,
            sql
        )

    def test_order_by_to_table_var(self):
        table, order_by = self.make_vars()

        q = order_by.to_table_var('TEST_VAR').select('*')
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            @TEST_VAR = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            ORDER BY
               [Col0] ASC, power([Col1], 0.5) DESC;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               @TEST_VAR            
            """,
            sql
        )

    def test_order_by_make_function_validation(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        self.assertErrorsWithMessage(
            lambda: table1.select('*').order_by(table1.col0, table1.col2.asc(), table1.col1.mean()),
            TypeError,
            "All positional args (*orders) to .order_by() must be orderings. Some of the input values were not:\n"
            "   orders[0]: SQL='[Col0]' (data column)\n"
            "   orders[2]: SQL='avg([Col1])' (aggfunc column)\n"
            "Did you forget to call .asc() or .desc()?"
        )
        self.assertErrorsWithMessage(
            lambda: table1.select('*').order_by(((table1.col0 + table2.col0) / 2).asc()),
            ValueError,
            """
            There are columns in the input to .order_by() that do not belong to the table (my.table.one):
            (([Col0] + [Col0]) / cast(2 AS Double)) ASC has dependence on my.table.one + my.table.two
            The column may be from the same provider but a with a different set of parameter values and therefore constitutes a different table.
            """
        )
