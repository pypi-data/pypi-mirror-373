from lumipy.lumiflex._table.join import Join
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestJoinTableConstruction(SqlTestCase):

    def test_join_table_ctor(self):
        table1 = self.make_table('my.table.one', n_cols=2, n_params=3).with_alias('LHS')
        table2 = self.make_table('my.table.two', n_cols=3, n_params=2).with_alias('RHS')
        on = (table1.col0 == table2.col0) & (table1.col1 > table2.col1)
        join = Join(
            join_type='inner',
            client_=self.make_dummy_client(),
            parents=(table1, table2, on),
        )

        p = join.get_parents()
        self.assertHashEqual(p[0], table1)
        self.assertHashEqual(p[1], table2)
        self.assertHashEqual(p[2], on)
        self.assertSqlEqual(
            """
            [my.table.one] AS LHS
              INNER JOIN
            [my.table.two] AS RHS ON (LHS.[Col0] = RHS.[Col0]) AND (LHS.[Col1] > RHS.[Col1])
            """,
            join.from_
        )
