from lumipy.lumiflex._window.window import WindowColumn
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestWindowFunctionCreation(SqlTestCase):

    def test_window_function_create(self):

        table, win = self.make_window_table_pair()

        win = win.filter(table.col0 > 10)
        expr = table.col0

        win_fn = WindowColumn(
            fn=lambda x: f'TEST_FN({x.sql})',
            parents=(win, expr),
            dtype=expr.dtype,
        )
        self.assertEqual("windowfunc", win_fn.get_label())
        sql = win_fn.sql
        self.assertSqlEqual(
            """
            TEST_FN([Col0]) FILTER(WHERE ([Col0] > 10)) OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )          
            """,
            sql
        )

    def test_window_function_with_table_prefixing(self):
        table = self.make_table()
        over = self.make_window(table).filter(table.col2 > 0)

        table_a = table.with_alias('ABC')

        win_fn = over.first(table.col0/table.col1)
        win_fn_p = table_a._add_prefix(win_fn)

        sql_p = win_fn_p.sql

        self.assertSqlEqual(
            """
            first_value((ABC.[Col0] / cast(ABC.[Col1] AS Double))) FILTER(WHERE (ABC.[Col2] > 0)) OVER(
                PARTITION BY ABC.[Col0], ABC.[Col1], ABC.[Col2], ABC.[Col3]
                ORDER BY ABC.[Col0] ASC, ABC.[Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            
            """,
            sql_p
        )
