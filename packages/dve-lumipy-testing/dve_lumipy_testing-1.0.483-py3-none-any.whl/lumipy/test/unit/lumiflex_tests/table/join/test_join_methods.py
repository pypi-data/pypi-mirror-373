from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestJoinTableMethods(SqlTestCase):

    def test_join_table_contains(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)
        t3 = self.make_table('my.table.three', n_cols=5, n_params=2)
        t4 = self.make_table('my.table.four', n_cols=4, n_params=1)
        t5 = self.make_table('my.table.five', n_cols=5)

        join = t1.inner_join(
            t2, t1.col0 == t2.col0, 'a', 'b'
        ).inner_join(
            t3, t3.col1 == t2.col0, "c"
        ).inner_join(
            t4, t4.col3 == t1.col0, "d"
        )

        self.assertTrue(t1.col0 in join)
        self.assertTrue(t2.col1 in join)
        self.assertTrue(t3.col2 in join)
        self.assertTrue(t4.col3 in join)
        expr = (t1.col0 + t2.col0 + t3.col0 + t4.col0) * 0.25
        self.assertTrue(expr in join)

        self.assertFalse(t5.col0 in join)
        expr = (t1.col0 / t5.col0) + t2.col0 + t3.col0 + t4.col0
        self.assertFalse(expr in join)

    def test_join_table_add_prefix_to_ordering(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)
        t3 = self.make_table('my.table.three', n_cols=5, n_params=2)
        t4 = self.make_table('my.table.four', n_cols=4, n_params=1)

        join = t1.inner_join(
            t2, t1.col0 == t2.col0, 'a', 'b'
        ).inner_join(
            t3, t3.col1 == t2.col0, "c"
        ).inner_join(
            t4, t4.col3 == t1.col0, "d"
        )

        ordering = ((t1.col0 + t2.col0) * (t3.col1 + t4.col1) / 2).asc()
        ordering = join._add_prefix(ordering)
        sql = ordering.sql
        self.assertEqual(
            "(((a.[Col0] + b.[Col0]) * (c.[Col1] + d.[Col1])) / cast(2 AS Double)) ASC",
            sql
        )

    def test_join_table_add_prefix_to_column(self):
        t1, t2, t3, t4, join = self.make_chained_join()

        self.assertEqual("a.[Col0]", join._add_prefix(t1.col0).sql)
        self.assertEqual("b.[Col0]", join._add_prefix(t2.col0).sql)
        self.assertEqual("c.[Col0]", join._add_prefix(t3.col0).sql)
        self.assertEqual("d.[Col0]", join._add_prefix(t4.col0).sql)

    def test_join_table_add_prefix_to_expression(self):
        t1, t2, t3, t4, join = self.make_chained_join()
        self.assertEqual(
            "((a.[Col0] + b.[Col0]) + c.[Col0]) + d.[Col0]",
            join._add_prefix(t1.col0 + t2.col0 + t3.col0 + t4.col0).sql
        )

    def test_join_table_get_param_assignments(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)
        t3 = self.make_table('my.table.three', n_cols=5, n_params=2)
        t4 = self.make_table('my.table.four', n_cols=4, n_params=1)

        join = t1.inner_join(
            t2, t1.col0 == t2.col0, 'a', 'b'
        ).inner_join(
            t3, t3.col1 == t2.col0, "c"
        ).inner_join(
            t4, t4.col3 == t1.col0, "d"
        )

        obs = join._get_param_assignments()
        exp = []
        exp += [t1._add_prefix(c) for c in t1.with_alias('a')._get_param_assignments()]
        exp += [t2._add_prefix(c) for c in t2.with_alias('b')._get_param_assignments()]
        exp += [t3._add_prefix(c) for c in t3.with_alias('c')._get_param_assignments()]
        exp += [t4._add_prefix(c) for c in t4.with_alias('d')._get_param_assignments()]
        self.assertSequenceHashEqual(obs, exp)

    def test_join_table_get_columns(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)
        t3 = self.make_table('my.table.three', n_cols=5, n_params=2)
        t4 = self.make_table('my.table.four', n_cols=4, n_params=1)

        join = t1.inner_join(
            t2, t1.col0 == t2.col0, 'a', 'b'
        ).inner_join(
            t3, t3.col1 == t2.col0, 'c'
        ).inner_join(
            t4, t4.col3 == t1.col0, 'd'
        )

        obs = join.get_columns()
        exp = []
        exp += [t1._add_prefix(c) for c in t1.with_alias('a').get_columns()]
        exp += [t2._add_prefix(c) for c in t2.with_alias('b').get_columns()]
        exp += [t3._add_prefix(c) for c in t3.with_alias('c').get_columns()]
        exp += [t4._add_prefix(c) for c in t4.with_alias('d').get_columns()]
        self.assertSequenceHashEqual(obs, exp)

        obs = join.get_columns(True)
        exp = []
        exp += [t1._add_prefix(c) for c in t1.with_alias('a').get_columns(True)]
        exp += [t2._add_prefix(c) for c in t2.with_alias('b').get_columns(True)]
        exp += [t3._add_prefix(c) for c in t3.with_alias('c').get_columns(True)]
        exp += [t4._add_prefix(c) for c in t4.with_alias('d').get_columns(True)]
        self.assertSequenceHashEqual(obs, exp)

    def test_join_table_select_star(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)

        join = t1.inner_join(t2, t1.col0 == t2.col0)

        q = join.select('*')

        self.assertSqlEqual(
            """
            SELECT
               lhs.[Col0] AS [Col0_lhs], lhs.[Col1] AS [Col1_lhs], lhs.[Col2], rhs.[Col0] AS [Col0_rhs], rhs.[Col1] AS [Col1_rhs]
            FROM
               [my.table.one] AS lhs
                 INNER JOIN
               [my.table.two] AS rhs ON (lhs.[Col0] = rhs.[Col0])
            WHERE
               lhs.[Param0] = 123
               and lhs.[Param1] = 1727364939238612
               and rhs.[Param0] = 123
               and rhs.[Param1] = 1727364939238612
               and rhs.[Param2] = 3.14
            """,
            q.get_sql()
        )

    def test_join_table_select_caret(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)

        join = t1.inner_join(t2, t1.col0 == t2.col0)

        q = join.select('^')

        self.assertSqlEqual(
            """
            SELECT
               lhs.[Col0] AS [Col0_lhs], lhs.[Col2], rhs.[Col0] AS [Col0_rhs]
            FROM
               [my.table.one] AS lhs
                 INNER JOIN
               [my.table.two] AS rhs ON (lhs.[Col0] = rhs.[Col0])
            WHERE
               lhs.[Param0] = 123
               and lhs.[Param1] = 1727364939238612
               and rhs.[Param0] = 123
               and rhs.[Param1] = 1727364939238612
               and rhs.[Param2] = 3.14
            """,
            q.get_sql()
        )

    def test_join_table_select_cols(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)

        join = t1.inner_join(t2, t1.col0 == t2.col0)

        q = join.select(t1.col0, t2.col0, t2.col1, t1.col2)
        self.assertSqlEqual(
            """
            SELECT
               lhs.[Col0] AS [Col0_lhs], rhs.[Col0] AS [Col0_rhs], rhs.[Col1], lhs.[Col2]
            FROM
               [my.table.one] AS lhs
                 INNER JOIN
               [my.table.two] AS rhs ON (lhs.[Col0] = rhs.[Col0])
            WHERE
               lhs.[Param0] = 123
               and lhs.[Param1] = 1727364939238612
               and rhs.[Param0] = 123
               and rhs.[Param1] = 1727364939238612
               and rhs.[Param2] = 3.14
            """,
            q.get_sql()
        )

    def test_join_table_select_aliased_cols(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)

        join = t1.inner_join(t2, t1.col0 == t2.col0)

        q = join.select(
            t1.col0, t2.col0, t2.col1, t1.col2,
            Test1=t1.col0,
            Test2=0.5 * (t2.col0 * t1.col1)
        )

        self.assertSqlEqual(
            """
            SELECT
               lhs.[Col0] AS [Col0_lhs], rhs.[Col0] AS [Col0_rhs], rhs.[Col1], lhs.[Col2], lhs.[Col0] AS [Test1], (0.5 * (rhs.[Col0] * lhs.[Col1])) AS [Test2]
            FROM
               [my.table.one] AS lhs
                 INNER JOIN
               [my.table.two] AS rhs ON (lhs.[Col0] = rhs.[Col0])
            WHERE
               lhs.[Param0] = 123
               and lhs.[Param1] = 1727364939238612
               and rhs.[Param0] = 123
               and rhs.[Param1] = 1727364939238612
               and rhs.[Param2] = 3.14
            """,
            q.get_sql()
        )

    def test_join_table_group_by(self):
        t1, t2, t3, t4, join = self.make_chained_join()

        q = join.group_by(
            t1.col0, t2.col0, t3.col0, t4.col0,
            Test=(t1.col0 + t2.col0 + t3.col0 + t4.col0) > 0
        )

        sql = q.get_sql()

        self.assertSqlEqual(
            """
            SELECT
               a.[Col0] AS [Col0_a], b.[Col0] AS [Col0_b], c.[Col0] AS [Col0_c], d.[Col0] AS [Col0_d], ((((a.[Col0] + b.[Col0]) + c.[Col0]) + d.[Col0]) > 0) AS [Test]
            FROM
               [my.table.one] AS a
                 INNER JOIN
               [my.table.two] AS b ON (a.[Col0] = b.[Col0])
                 INNER JOIN
               [my.table.three] AS c ON (c.[Col1] = b.[Col0])
                 INNER JOIN
               [my.table.four] AS d ON (d.[Col3] = a.[Col0])
            WHERE
               a.[Param0] = 123
               and a.[Param1] = 1727364939238612
               and b.[Param0] = 123
               and b.[Param1] = 1727364939238612
               and b.[Param2] = 3.14
               and c.[Param0] = 123
               and c.[Param1] = 1727364939238612
               and d.[Param0] = 123
            GROUP BY
               a.[Col0], b.[Col0], c.[Col0], d.[Col0], ((((a.[Col0] + b.[Col0]) + c.[Col0]) + d.[Col0]) > 0)            
            """,
            sql
        )

    def test_join_table_hash(self):
        t1 = self.make_table('my.test.one')
        t2 = self.make_table('my.test.two')
        t3 = self.make_table('my.test.three')

        join1 = t1.inner_join(t2, t1.col0 == t2.col0)
        join1b = t1.inner_join(t2, t1.col0 == t2.col0)
        self.assertHashEqual(join1, join1b)

        join2 = t1.inner_join(t2, t1.col0 == t2.col1)
        self.assertHashNotEqual(join1, join2)

        join3 = t1.inner_join(t3, t1.col0 == t3.col0)
        self.assertHashNotEqual(join1, join3)

        join4 = t2.inner_join(t1, t1.col0 == t2.col0)
        self.assertHashNotEqual(join1, join4)

    def test_join_table_add_suffix(self):
        t1, t2, t3, t4, join = self.make_chained_join()

        def fn(x):
            return join._add_suffix(join._add_prefix(x)).sql

        self.assertEqual("a.[Col0] AS [Col0_a]", fn(t1.col0))
        self.assertEqual("b.[Col0] AS [Col0_b]", fn(t2.col0))
        self.assertEqual("c.[Col0] AS [Col0_c]", fn(t3.col0))
        self.assertEqual("d.[Col0] AS [Col0_d]", fn(t4.col0))

    def test_join_table_column_deduplication(self):
        t1, t2, t3, t4, join = self.make_chained_join()

        self.assertEqual({'Col0', 'Col1', 'Col2', 'Col3'}, join.clashes_)

        for alias in ['a', 'b', 'c', 'd']:
            self.assertTrue(hasattr(join, f'col0_{alias}'))
        for alias in ['a', 'b', 'c', 'd']:
            self.assertTrue(hasattr(join, f'col1_{alias}'))
        for alias in ['a', 'c', 'd']:
            self.assertTrue(hasattr(join, f'col2_{alias}'))
        for alias in ['c', 'd']:
            self.assertTrue(hasattr(join, f'col3_{alias}'))

    def test_join_table_get_table_ancestors(self):
        t1, t2, t3, t4, join = self.make_chained_join()

        anc = join._get_table_ancestors()
        self.assertEqual(8, len(anc))

    def test_join_table_self_join(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        join = t1.inner_join(t1, t1.col0 == t1.col2)
        self.assertEqual(len(t1.get_columns()) * 2, len(join.get_columns()))

    def test_join_table_left_join(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)

        join = t1.left_join(t2, t1.col0 == t2.col0)
        sql = join.select('*').get_sql()
        self.assertSqlEqual(
            """
            SELECT
               lhs.[Col0] AS [Col0_lhs], lhs.[Col1] AS [Col1_lhs], lhs.[Col2], rhs.[Col0] AS [Col0_rhs], rhs.[Col1] AS [Col1_rhs]
            FROM
               [my.table.one] AS lhs
                 LEFT JOIN
               [my.table.two] AS rhs ON (lhs.[Col0] = rhs.[Col0])
            WHERE
               lhs.[Param0] = 123
               and lhs.[Param1] = 1727364939238612
               and rhs.[Param0] = 123
               and rhs.[Param1] = 1727364939238612
               and rhs.[Param2] = 3.14            
            """,
            sql
        )

    def test_join_table_left_join_error_with_bad_on_condition(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)
        t3 = self.make_table('my.table.three', n_cols=4, n_params=3)
        t4 = self.make_table('my.table.four', n_cols=5, n_params=3)

        self.assertErrorsWithMessage(
            lambda: t1.left_join(t2, (t1.col0 == t3.col0) & (t2.col0 == t4.col0)),
            ValueError,
            """1 validation error for Join
  Value error, There are columns in the join's on condition that don't belong to any parent table (my.table.one, my.table.two):
    [Col0] (my.table.three)
    [Col0] (my.table.four) [type=value_error, input_value={'join_type': 'left', 'cl... ([Col0] = [Col0]))'
))}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [5]
        )

        self.assertErrorsWithMessage(
            lambda: t1.left_join(t2, t1.col0 == t2.col0).left_join(t3, t2.col0 == t4.col0, 'c'),
            ValueError,
            """1 validation error for Join
  Value error, There are columns in the join's on condition that don't belong to any parent table (my.table.one, my.table.two, my.table.three):
    [Col0] (my.table.four) [type=value_error, input_value={'join_type': 'left', 'cl... '([Col0] = [Col0])'
))}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [4]
        )

    def test_join_table_inner_join(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)

        join = t1.inner_join(t2, t1.col0 == t2.col0)
        sql = join.select('*').get_sql()
        self.assertSqlEqual(
            """
            SELECT
               lhs.[Col0] AS [Col0_lhs], lhs.[Col1] AS [Col1_lhs], lhs.[Col2], rhs.[Col0] AS [Col0_rhs], rhs.[Col1] AS [Col1_rhs]
            FROM
               [my.table.one] AS lhs
                 INNER JOIN
               [my.table.two] AS rhs ON (lhs.[Col0] = rhs.[Col0])
            WHERE
               lhs.[Param0] = 123
               and lhs.[Param1] = 1727364939238612
               and rhs.[Param0] = 123
               and rhs.[Param1] = 1727364939238612
               and rhs.[Param2] = 3.14            
            """,
            sql
        )

    def test_join_table_error_on_duplicate_alias(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)
        t3 = self.make_table('my.table.three', n_cols=4, n_params=3)

        self.assertErrorsWithMessage(
            lambda: t1.inner_join(t2, t1.col0 == t2.col0, left_alias='a', right_alias='a'),
            ValueError,
            """
            1 validation error for Join
              Value error, The two sides of the join must have different aliases, but were both 'a'. [type=value_error, input_value={'join_type': 'inner', 'c... '([Col0] = [Col0])'
            ))}, input_type=dict]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [3]
        )

        self.assertErrorsWithMessage(
            lambda: t1.inner_join(t2, t1.col0 == t2.col0).inner_join(t3, t1.col0 == t3.col0, right_alias='rhs'),
            ValueError,
            """
            1 validation error for Join
              Value error, Right table has an alias ('rhs') that clashes with an existing parent table alias ('lhs', 'rhs'). [type=value_error, input_value={'join_type': 'inner', 'c... '([Col0] = [Col0])'
            ))}, input_type=dict]
                For further information visit https://errors.pydantic.dev/xxx/v/value_error            
            """,
            [3]
        )

    def test_join_table_chained_select_star(self):

        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)
        t3 = self.make_table('my.table.three', n_cols=5, n_params=2)
        t4 = self.make_table('my.table.four', n_cols=4, n_params=1)

        join = t1.inner_join(
            t2, t1.col0 == t2.col0, 'a', 'b'
        ).inner_join(
            t3, t3.col1 == t2.col0, "c"
        ).inner_join(
            t4, t4.col3 == t1.col0, "d"
        )

        q = join.select('*')

        self.assertSqlEqual(
            """
            SELECT
               a.[Col0] AS [Col0_a], a.[Col1] AS [Col1_a], a.[Col2] AS [Col2_a], b.[Col0] AS [Col0_b], b.[Col1] AS [Col1_b], c.[Col0] AS [Col0_c], c.[Col1] AS [Col1_c], c.[Col2] AS [Col2_c], c.[Col3] AS [Col3_c], c.[Col4], d.[Col0] AS [Col0_d], d.[Col1] AS [Col1_d], d.[Col2] AS [Col2_d], d.[Col3] AS [Col3_d]
            FROM
               [my.table.one] AS a
                 INNER JOIN
               [my.table.two] AS b ON (a.[Col0] = b.[Col0])
                 INNER JOIN
               [my.table.three] AS c ON (c.[Col1] = b.[Col0])
                 INNER JOIN
               [my.table.four] AS d ON (d.[Col3] = a.[Col0])
            WHERE
               a.[Param0] = 123
               and a.[Param1] = 1727364939238612
               and b.[Param0] = 123
               and b.[Param1] = 1727364939238612
               and b.[Param2] = 3.14
               and c.[Param0] = 123
               and c.[Param1] = 1727364939238612
               and d.[Param0] = 123
            """,
            q.get_sql()
        )
