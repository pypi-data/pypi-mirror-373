from lumipy.lumiflex._window.window import (
    Window, OverPartition, OverOrder, OverFrame, OverFilter
)
from lumipy.lumiflex.window import window
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._common.node import Node


class TestSqlWindowCreation(SqlTestCase):

    def test_over_ctor(self):

        table = self.make_table()

        fltr = OverFilter(parents=(table.col0 > 10,))
        partition = OverPartition(parents=(table.col4, table.col5))
        order_by = OverOrder(parents=(table.col0.asc(), table.col1.desc()))
        frame = OverFrame(lower=10, upper=10)

        over = Window(parents=(partition, order_by, frame, fltr))

        self.assertEqual("over", over.get_label())
        self.assertHashEqual(partition, over.get_parents()[0])
        self.assertHashEqual(order_by, over.get_parents()[1])
        self.assertHashEqual(frame, over.get_parents()[2])
        self.assertHashEqual(fltr, over.get_parents()[3])

        self.assertSqlEqual(
            """
            FILTER(WHERE [Col0] > 10) OVER(
               PARTITION BY [Col4], [Col5]
               ORDER BY [Col0] ASC, [Col1] DESC
               ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
            )
            """,
            over.get_sql()
        )

        exp = (partition, order_by, frame, fltr)
        obs = over.get_parents()
        self.assertSequenceHashEqual(exp, obs)

    def test_over_add_prefix(self):

        table = self.make_table()

        fltr = OverFilter(parents=(table.col0 > 10,))
        partition = OverPartition(parents=(table.col4, table.col5))
        order_by = OverOrder(parents=(table.col0.asc(), table.col1.desc()))
        frame = OverFrame(lower=10, upper=10)

        over = Window(parents=(partition, order_by, frame, fltr))

        table_a = table.with_alias('ABC')
        over_prfx = table_a._add_prefix(over)

        sql = over_prfx.get_sql()
        self.assertSqlEqual(
            """
            FILTER(WHERE ABC.[Col0] > 10) OVER(
                PARTITION BY ABC.[Col4], ABC.[Col5]
                ORDER BY ABC.[Col0] ASC, ABC.[Col1] DESC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )            
            """,
            sql
        )

    def test_over_validation_missing_parents(self):
        p = self.make_over_partition()
        self.assertErrorsWithMessage(
            lambda: Window(parents=(p,)),
            ValueError,
            """
            1 validation error for Window
              Value error, There are missing inputs. Over must have four parent nodes: partition, order by, frame and filter [type=value_error, input_value={'parents': (OverPartitio...Col3]'
                  )
               )
            ),)}, input_type=dict]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [5]
        )

    def test_over_validation_incorrect_parent_types(self):
        part = self.make_over_partition()
        order = self.make_over_order()
        frame = self.make_over_frame()
        fltr = self.make_over_filter()

        bad = Node(label='bad value')

        self.assertErrorsWithMessage(
            lambda: Window(parents=(bad, order, frame, fltr)),
            TypeError,
            """
            parent[0] (partition) must be an OverPartition instance. Was Node
            """
        )

        self.assertErrorsWithMessage(
            lambda: Window(parents=(part, bad, frame, fltr)),
            TypeError,
            """
            parent[1] (order_by) must be an OverOrder instance. Was Node
            """
        )

        self.assertErrorsWithMessage(
            lambda: Window(parents=(part, order, bad, fltr)),
            TypeError,
            """
            parent[2] (frame) must be an OverFrame instance. Was Node
            """
        )

        self.assertErrorsWithMessage(
            lambda: Window(parents=(part, order, frame, bad)),
            TypeError,
            """
            parent[3] (filter) must be an OverFilter instance. Was Node
            """
        )

    def test_over_test_case_make_over_method(self):
        table, over = self.make_window_table_pair()
        sql = over.get_sql()
        self.assertSqlEqual(
            """
            OVER(
                PARTITION BY [Col0], [Col1], [Col2], [Col3]
                ORDER BY [Col0] ASC, [Col1] ASC
                ROWS BETWEEN 10 PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_window_creation_helper_function_create_defaults(self):
        win = window()
        sql = win.get_sql()
        self.assertSqlEqual(
            """
            OVER(
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )            
            """,
            sql
        )

    def test_window_creation_helper_function_single_args(self):
        table = self.make_table()
        win = window(table.col2, table.col1.asc(), lower=120, upper=100, exclude='ties')

        self.assertIsInstance(win, Window)

        sql = win.get_sql()

        self.assertSqlEqual(
            """
            OVER(
                PARTITION BY [Col2]
                ORDER BY [Col1] ASC
                ROWS BETWEEN 120 PRECEDING AND 100 FOLLOWING EXCLUDE TIES
                )
            """,
            sql
        )

    def test_window_creation_helper_function_list_args(self):

        table = self.make_table()

        groups = [table.col0, table.col3]
        orders = [table.col1.asc(), table.col2.desc()]
        win = window(groups=groups, orders=orders, lower=10, upper=12, exclude='group')

        self.assertIsInstance(win, Window)

        sql = win.get_sql()

        self.assertSqlEqual(
            """
            OVER(
                PARTITION BY [Col0], [Col3]
                ORDER BY [Col1] ASC, [Col2] DESC
                ROWS BETWEEN 10 PRECEDING AND 12 FOLLOWING EXCLUDE GROUP
                )
            """,
            sql
        )
