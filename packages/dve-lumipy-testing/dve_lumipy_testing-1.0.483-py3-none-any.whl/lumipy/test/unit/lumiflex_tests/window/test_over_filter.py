from lumipy.lumiflex._window.window import OverFilter
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestOverFilter(SqlTestCase):

    def test_over_filter_empty(self):
        of = OverFilter()
        self.assertFalse(of.has_content())

    def test_over_filter_create(self):
        table = self.make_table()
        cond = table.col0 > 0
        of = OverFilter(parents=(cond,))
        self.assertHashEqual(cond, of.get_parents()[0])
        self.assertTrue(of.has_content())

    def test_over_filter_get_sql(self):
        table = self.make_table()
        cond = table.col0 > 0
        of = OverFilter(parents=(cond,))
        self.assertEqual("FILTER(WHERE [Col0] > 0)", of.get_sql())

    def test_over_filter_add_prefix(self):
        table = self.make_table()
        cond = ((table.col0 - table.col1) / table.col1) > 0
        over_filter = OverFilter(parents=(cond,))

        table_a = table.with_alias('ABC')
        over_filter_p = table_a._add_prefix(over_filter)
        self.assertSqlEqual(
            "FILTER(WHERE ((ABC.[Col0] - ABC.[Col1]) / cast(ABC.[Col1] AS Double)) > 0)",
            over_filter_p.get_sql()
        )

    def test_over_filter_validation(self):

        table = self.make_table()

        self.assertErrorsWithMessage(
            lambda: OverFilter(parents=(table.col0,)),
            ValueError,
            """
            1 validation error for OverFilter
            parents
              Value error, Input to over filter must resolve to a boolean, but was Int. [type=value_error, input_value=(Column(
               label_: 'data...e )
               sql: '[Col0]'
            ),), input_type=tuple]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [6]
        )

        self.assertErrorsWithMessage(
            lambda: OverFilter(parents=(table.col0 > 0, table.col1 > 0)),
            ValueError,
            """
            1 validation error for OverFilter
            parents
              Value error, Filter can either be empty or have exactly one input [type=value_error, input_value=(Column(
               label_: 'op'
            ...
               sql: '[Col1] > 0'
            )), input_type=tuple]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [7]
        )
