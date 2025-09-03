from lumipy.lumiflex._table.operation import SetOperation, _set_op_make
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.content import CompoundContent


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestSetOperationCreation(SqlTestCase):

    def test_set_operation_methods_exclude(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        exclude = table1.select('*').exclude(table2.select('*'))

        sql = exclude.get_sql()
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
            EXCEPT
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14          
            """,
            sql
        )

    def test_set_operation_methods_intersect(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        exclude = table1.select('*').intersect(table2.select('*'))

        sql = exclude.get_sql()
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
           INTERSECT 
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14          
            """,
            sql
        )

    def test_set_operation_methods_union_all(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        exclude = table1.select('*').union_all(table2.select('*'))

        sql = exclude.get_sql()
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
            UNION ALL
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14          
            """,
            sql
        )

    def test_set_operation_methods_union(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        exclude = table1.select('*').union(table2.select('*'))

        sql = exclude.get_sql()
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
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14          
            """,
            sql
        )

    def test_set_operation_methods_order_by(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        exclude = table1.select('*').union(table2.select('*')).order_by(table1.col0.asc(), table1.col1.desc())

        sql = exclude.get_sql()
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
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14          
            ORDER BY
               [Col0] ASC, [Col1] DESC
            """,
            sql
        )

    def test_set_operation_methods_limit(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        exclude = table1.select('*').union(table2.select('*')).limit(1000, 100)

        sql = exclude.get_sql()
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
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14          
            LIMIT 1000 OFFSET 100
            """,
            sql
        )

    def test_set_operation_methods_order_by_and_limit(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        exclude = table1.select('*').union(table2.select('*')).order_by(table1.col0.asc(), table1.col1.desc()).limit(1000, 100)

        sql = exclude.get_sql()
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
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14          
            ORDER BY
               [Col0] ASC, [Col1] DESC
            LIMIT 1000 OFFSET 100
            """,
            sql
        )

    def test_set_operation_methods_to_table_var(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        tv = table1.select('*').union(table2.select('*')).to_table_var('test_var')

        q = tv.select('*')

        sql = q.get_sql()

        self.assertSqlEqual(
            """
            @test_var = SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.one]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               @test_var            
            """,
            sql
        )

    def test_set_operation_methods_chaining(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')
        table3 = self.make_table('my.table.three')
        table4 = self.make_table('my.table.four')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)
        sq3 = table3.select('*').where(table3.col0 > 0)
        sq4 = table4.select('*').where(table4.col0 > 0)

        content = CompoundContent(label='union', parents=(sq1.content, sq2.content))
        union = SetOperation(parents=(sq1, sq2, content), client=table1.client_).union(sq3).union(sq4)

        sql = union.get_sql()

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
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.three]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))
            UNION
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.four]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))            
            """,
            sql,
        )

    def test_set_operation_methods_mixed_chaining(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')
        table3 = self.make_table('my.table.three')
        table4 = self.make_table('my.table.four')
        table5 = self.make_table('my.table.five')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)
        sq3 = table3.select('*').where(table3.col0 > 0)
        sq4 = table4.select('*').where(table4.col0 > 0)
        sq5 = table5.select('*').where(table5.col0 > 0)

        exclude = sq1.union(sq2).intersect(sq3.union(sq4)).exclude(sq5)

        sql = exclude.get_sql()

        self.assertSqlEqual(
            """
                (
                    (
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
                    )
                INTERSECT
                    (
                        SELECT
                           [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                        FROM
                           [my.table.three]
                        WHERE
                           ([Param0] = 123
                           and [Param1] = 1727364939238612
                           and [Param2] = 3.14)
                           and (([Col0] > 0))
                    UNION
                        SELECT
                           [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                        FROM
                           [my.table.four]
                        WHERE
                           ([Param0] = 123
                           and [Param1] = 1727364939238612
                           and [Param2] = 3.14)
                           and (([Col0] > 0))
                    )
                )
            EXCEPT
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.five]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))
            """,
            sql
        )

    def test_set_operation_creation(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        content = CompoundContent(label='union', parents=(sq1.content, sq2.content))
        union = SetOperation(parents=(sq1, sq2, content), client=table1.client_)

        self.assertEqual('row set op', union.get_label())
        self.assertHashEqual(sq1, union.get_parents()[0])
        self.assertHashEqual(sq2, union.get_parents()[1])

        sql = union.content.get_sql()

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

    def test_set_operation_make_function(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        set_op = _set_op_make('except', sq1, sq2)

        self.assertIsInstance(set_op, SetOperation)
        self.assertEqual('except', set_op.content.get_label())
        self.assertHashEqual(sq1, set_op.get_parents()[0])
        self.assertHashEqual(sq2, set_op.get_parents()[1])

        sql = set_op.get_sql()
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

    def test_set_operation_make_function_validation(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        bad = sq2.group_by(table2.col0)
        self.assertErrorsWithMessage(
            lambda: _set_op_make('except', sq1, bad),
            TypeError,
            "The input to a row set operation (compound SELECT) must be a result of select(), where(), union(), "
            "union_all(), exclude() or intersect() but was a group_by() result."
        )

        bad = bad.agg(Mean=table2.col0.mean())
        self.assertErrorsWithMessage(
            lambda: _set_op_make('except', sq1, bad),
            TypeError,
            "The input to a row set operation (compound SELECT) must be a result of select(), where(), union(), "
            "union_all(), exclude() or intersect() but was a aggregate() result."
        )

        bad = bad.having(table2.col0.count() > 10)
        self.assertErrorsWithMessage(
            lambda: _set_op_make('except', sq1, bad),
            TypeError,
            "The input to a row set operation (compound SELECT) must be a result of select(), where(), union(), "
            "union_all(), exclude() or intersect() but was a having() result."
        )

        bad = bad.order_by(table2.col1.asc())
        self.assertErrorsWithMessage(
            lambda: _set_op_make('except', sq1, bad),
            TypeError,
            "The input to a row set operation (compound SELECT) must be a result of select(), where(), union(), "
            "union_all(), exclude() or intersect() but was a order_by() result."
        )

        bad = bad.limit(100, 10)
        self.assertErrorsWithMessage(
            lambda: _set_op_make('except', sq1, bad),
            TypeError,
            "The input to a row set operation (compound SELECT) must be a result of select(), where(), union(), "
            "union_all(), exclude() or intersect() but was a limit() result."
        )
