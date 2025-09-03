from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.operation import Limit, _limit_make


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestLimit(SqlTestCase):

    def test_limit_creation(self):
        table = self.make_table()
        select = table.select('*')
        content = select.content.update_node(limit=2222, offset=1111)

        limit = Limit(parents=(select, content), client=table.client_)

        self.assertEqual('limit', limit.get_label())
        sql = limit.get_sql()
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
            LIMIT 2222 OFFSET 1111            
            """,
            sql
        )

    def test_limit_make_validation(self):
        table = self.make_table()
        select = table.select('*')

        self.assertErrorsWithMessage(
            lambda: _limit_make(select, 1.2, 0),
            ValueError,
            "limit value must be None, or an integer > 0. Was '1.2' (float)."
        )

        self.assertErrorsWithMessage(
            lambda: _limit_make(select, 1.2, 0.1),
            ValueError,
            "limit value must be None, or an integer > 0. Was '1.2' (float)."
        )

        self.assertErrorsWithMessage(
            lambda: _limit_make(select, 0, 0),
            ValueError,
            "limit value must be None, or an integer > 0. Was '0' (int)."
        )

        self.assertErrorsWithMessage(
            lambda: _limit_make(select, -2, 0),
            ValueError,
            "limit value must be None, or an integer > 0. Was '-2' (int)."
        )

        self.assertErrorsWithMessage(
            lambda: _limit_make(select, 2, -2),
            ValueError,
            "offset value must be None, or an integer >= 0. Was '-2' (int)."
        )

    def test_limit_to_table_var(self):
        table = self.make_table()
        limit = table.select('*').limit(1000, 33)

        q = limit.to_table_var('TEST_VAR').select('*')
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            @TEST_VAR = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            LIMIT 1000 OFFSET 33;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               @TEST_VAR            
            """,
            sql
        )
