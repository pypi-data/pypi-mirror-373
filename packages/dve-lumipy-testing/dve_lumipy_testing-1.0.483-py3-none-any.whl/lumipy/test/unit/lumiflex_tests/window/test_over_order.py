from lumipy.lumiflex._window.window import OverOrder
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestOverOrder(SqlTestCase):

    def test_over_order_empty(self):
        order = OverOrder()
        self.assertFalse(order.has_content())

    def test_over_order_create(self):

        table = self.make_table()
        orderings = [c.asc() for c in table.get_columns()[:3]]
        order = OverOrder(parents=orderings)
        self.assertSequenceHashEqual(orderings, order.get_parents())
        self.assertTrue(order.has_content())

    def test_over_order_validation(self):

        table = self.make_table()

        self.assertErrorsWithMessage(
            lambda: OverOrder(parents=(table.col0, table.col1)),
            ValueError,
            """
            1 validation error for OverOrder
            parents
              Value error, Over ordering values must be column orderings. Received Column, Column [type=value_error, input_value=(Column(
               label_: 'data...se )
               sql: '[Col1]'
            )), input_type=tuple]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [6]
        )

    def test_over_order_add_prefix(self):

        table = self.make_table()
        order = self.make_over_order()
        table_a = table.with_alias('ABC')

        part_prfx = table_a._add_prefix(order)
        sql = part_prfx.get_sql()
        self.assertSqlEqual("ORDER BY ABC.[Col0] ASC, ABC.[Col1] ASC", sql)
