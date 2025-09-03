from lumipy.lumiflex._window.window import OverPartition
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestOverPartition(SqlTestCase):

    def test_over_partition_empty(self):
        part = OverPartition()
        self.assertFalse(part.has_content())

    def test_over_partition_create(self):

        table = self.make_table()
        partition = (table.col0, table.col1, table.col2)
        part = OverPartition(parents=partition)
        self.assertSequenceHashEqual(partition, part.get_parents())
        self.assertTrue(part.has_content())

    def test_over_partition_get_sql(self):

        table = self.make_table()
        part = OverPartition(parents=(table.col0, table.col1, table.col2))
        sql = part.get_sql()
        self.assertEqual("PARTITION BY [Col0], [Col1], [Col2]", sql)

    def test_over_partition_input_validation(self):

        table = self.make_table()

        self.assertErrorsWithMessage(
            lambda: OverPartition(parents=(table.col0.asc(),)),
            ValueError,
            """
            1 validation error for OverPartition
            parents
              Value error, Over partition values must be table data columns or functions of them, but not window functions. Received Ordering [type=value_error, input_value=(Ordering(
               label_: 'as...[Col0]'
                  )
               )
            ),), input_type=tuple]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [7]
        )

    def test_over_partition_add_prefix(self):

        table = self.make_table()
        part = self.make_over_partition()
        table_a = table.with_alias('ABC')

        part_prfx = table_a._add_prefix(part)
        sql = part_prfx.get_sql()
        self.assertSqlEqual(
            "PARTITION BY ABC.[Col0], ABC.[Col1], ABC.[Col2], ABC.[Col3]",
            sql
        )

    def test_over_partition_test_case_make_method(self):

        table = self.make_table()
        part = self.make_over_partition()
        self.assertSequenceHashEqual(table.get_columns()[:4], part.get_parents())

        table = self.make_table('a.different.table')
        part = self.make_over_partition(table, n=5)
        self.assertSequenceHashEqual(table.get_columns()[:5], part.get_parents())
