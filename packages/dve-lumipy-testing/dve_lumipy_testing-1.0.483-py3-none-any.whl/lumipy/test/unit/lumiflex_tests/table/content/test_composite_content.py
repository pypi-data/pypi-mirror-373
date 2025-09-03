from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.content import CompoundContent


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestCompoundContent(SqlTestCase):

    def test_compound_content_create_simple_union(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        compound = CompoundContent(label='union', parents=(sq1.content, sq2.content))
        self.assertEqual('union', compound.get_label())

        sql = compound.get_sql()

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

    def test_compound_content_with_order_by_and_limit(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        compound = CompoundContent(
            label='union',
            parents=(sq1.content, sq2.content),
            order_bys=[table1.col0.asc()],
            limit=100,
            offset=10
        )

        sql = compound.get_sql()

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
            ORDER BY
               [Col0] ASC
            LIMIT 100 OFFSET 10            
            """,
            sql
        )

    def test_compound_content_create_simple_union_all(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        compound = CompoundContent(label='union all', parents=(sq1.content, sq2.content))
        self.assertEqual('union all', compound.get_label())

        sql = compound.get_sql()

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
            UNION ALL
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

    def test_compound_content_create_simple_except(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        compound = CompoundContent(label='except', parents=(sq1.content, sq2.content))
        self.assertEqual('except', compound.get_label())

        sql = compound.get_sql()

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

    def test_compound_content_create_simple_intersection(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        compound = CompoundContent(label='intersect', parents=(sq1.content, sq2.content))
        self.assertEqual('intersect', compound.get_label())

        sql = compound.get_sql()

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
            INTERSECT
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

    def test_compound_content_create_chained_union(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')
        table3 = self.make_table('my.table.three')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)
        sq3 = table3.select('*').where(table3.col0 > 0)

        compound1 = CompoundContent(label='union', parents=(sq1.content, sq2.content))
        compound2 = CompoundContent(label='union', parents=(compound1, sq3.content))

        sql = compound2.get_sql()
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
            """,
            sql
        )

    def test_compound_content_create_chained_union_all(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')
        table3 = self.make_table('my.table.three')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)
        sq3 = table3.select('*').where(table3.col0 > 0)

        compound1 = CompoundContent(label='union all', parents=(sq1.content, sq2.content))
        compound2 = CompoundContent(label='union all', parents=(compound1, sq3.content))

        sql = compound2.get_sql()
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
            UNION ALL
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.two]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))
            UNION ALL
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.three]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))            
            """,
            sql
        )

    def test_compound_content_create_chained_except(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')
        table3 = self.make_table('my.table.three')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)
        sq3 = table3.select('*').where(table3.col0 > 0)

        compound1 = CompoundContent(label='except', parents=(sq1.content, sq2.content))
        compound2 = CompoundContent(label='except', parents=(compound1, sq3.content))

        sql = compound2.get_sql()
        self.assertSqlEqual(
            """
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
                )
            EXCEPT
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.three]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))           
            """,
            sql
        )

    def test_compound_content_create_chained_intersect(self):

        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')
        table3 = self.make_table('my.table.three')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)
        sq3 = table3.select('*').where(table3.col0 > 0)

        compound1 = CompoundContent(label='intersect', parents=(sq1.content, sq2.content))
        compound2 = CompoundContent(label='intersect', parents=(compound1, sq3.content))

        sql = compound2.get_sql()
        self.assertSqlEqual(
            """
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
               INTERSECT 
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
                SELECT
                   [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
                FROM
                   [my.table.three]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 0))            
            """,
            sql
        )

    def test_compound_content_mixed_chain(self):
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

        union1 = CompoundContent(label='union', parents=(sq1.content, sq2.content))
        union2 = CompoundContent(label='union', parents=(sq3.content, sq4.content))

        intersect = CompoundContent(label='intersect', parents=(union1, union2))
        exclude = CompoundContent(label='except', parents=(intersect, sq5.content))

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

    def test_compound_content_validation(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq1 = table1.select('*').where(table1.col0 > 0)
        sq2 = table2.select('*').where(table2.col0 > 0)

        self.assertErrorsWithMessage(
            lambda: CompoundContent(label='bad', parents=(sq1.content, sq2.content)),
            ValueError,
            """
            1 validation error for CompoundContent
            label
              Input should be 'union', 'union all', 'intersect' or 'except' [type=literal_error, input_value='bad', input_type=str]
                For further information visit https://errors.pydantic.dev/xxx/v/literal_error
            """,
            [3]
        )

        self.assertErrorsWithMessage(
            lambda: CompoundContent(label='union', parents=tuple()),
            ValueError,
            """
            1 validation error for CompoundContent
            parents
              Value error, Compound content must have two parents, but received 0. [type=value_error, input_value=(), input_type=tuple]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [3]
        )
        self.assertErrorsWithMessage(
            lambda: CompoundContent(label='union', parents=tuple([1, 2, 3])),
            ValueError,
            """
            1 validation error for CompoundContent
                parents
                  Value error, Compound content must have two parents, but received 3. [type=value_error, input_value=(1, 2, 3), input_type=tuple]
                    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [3]
        )

        self.assertErrorsWithMessage(
            lambda: CompoundContent(label='union', parents=(sq1.group_by(table1.col4).content, sq2.content)),
            ValueError,
            """
            1 validation error for CompoundContent
            parents
              Value error, One of the compound content inputs wasn't compoundable (a subquery that contains a group by, having, order by or limit clause). [type=value_error, input_value=(CoreContent(
               label_: ...  having_filter: None
            )), input_type=tuple]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [5]
        )
