from lumipy.lumiflex._table.content import CoreContent
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from pydantic import ValidationError


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestContentConstruction(SqlTestCase):

    def test_table_content_defaults(self):
        table = self.make_table()
        content = CoreContent(
            table=table,
            parents=(table,),
            select_cols=table.get_columns(main_only=True)
        )

        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            """,
            content.get_sql()
        )

    def test_table_content_ctor(self):
        table = self.make_table()

        in_cols = tuple(table.get_columns()[:4])
        where_filter = table.col1 > 2
        group_by_cols = tuple(table.get_columns()[2:6])
        aggregates = tuple(in_cols[i].sum()._with_alias(f'Agg{i}') for i in range(3))
        having_filter = table.col5.count() > 10
        order_bys = (table.col1.asc(), table.col2.desc())
        limit = 1000

        content = CoreContent(
            table=table,
            parents=(table,),
            select_cols=in_cols,
            where_filter=where_filter,
            group_by_cols=group_by_cols,
            aggregates=aggregates,
            having_filter=having_filter,
            order_bys=order_bys,
            limit=limit
        )

        self.assertEqual(table, content.table)
        self.assertSequenceHashEqual(in_cols, content.select_cols)
        self.assertHashEqual(where_filter, content.where_filter)
        self.assertSequenceHashEqual(group_by_cols, content.group_by_cols)
        self.assertHashEqual(having_filter, content.having_filter)
        self.assertEqual(order_bys, content.order_bys)
        self.assertEqual(limit, content.limit)

        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], total([Col0]) AS [Agg0], total([Col1]) AS [Agg1], total([Col2]) AS [Agg2]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and ([Col1] > 2)
            GROUP BY
               [Col2], [Col3], [Col4], [Col5]
            HAVING
               count([Col5]) > 10
            ORDER BY
               [Col1] ASC, [Col2] DESC
            LIMIT 1000
            """,
            content.get_sql()
        )

    def test_table_content_update_method(self):

        table = self.make_table('My.Test.Table')

        in_cols = tuple(table.get_columns()[:4])
        where_filter = table.col1 > 2

        content1 = CoreContent(table=table, parents=(table,), select_cols=in_cols)
        self.assertIs(content1.where_filter, None)

        content2 = content1.update_node(where_filter=where_filter)
        self.assertNotEqual(content1, content2)
        self.assertHashEqual(where_filter, content2.where_filter)

    def test_table_content_ctor_error_no_select_cols(self):
        table = self.make_table('My.Test.Table')
        self.assertErrorsWithMessage(
            lambda: CoreContent(table=table, parents=(table,), select_cols=tuple()),
            ValueError,
            """1 validation error for CoreContent
  Value error, Content must have at least one select col but was zero. [type=value_error, input_value={'table': Table(
   label...
),), 'select_cols': ()}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error""",
            [4]
        )

    def test_table_content_ctor_error_non_bool_where_filter(self):
        table = self.make_table('My.Test.Table')
        self.assertErrorsWithMessage(
            lambda: CoreContent(table=table, parents=(table,), select_cols=table.get_columns(), where_filter=table.col0),
            ValueError,
            """
            1 validation error for CoreContent
              Value error, Where filter input must resolve to a boolean, but was Int. [type=value_error, input_value={'table': Table(
               label...ue )
               sql: '[Col0]'
            )}, input_type=dict]
            For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [5]
        )
