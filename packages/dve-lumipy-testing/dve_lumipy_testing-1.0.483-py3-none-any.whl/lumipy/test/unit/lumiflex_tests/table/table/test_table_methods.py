from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._column.make import make
from lumipy.lumiflex.table import Table
import datetime as dt


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestTableMethods(SqlTestCase):

    def test_table_hash(self):
        t1a = self.make_table('my.table.one', n_cols=3, n_params=2)
        t1b = self.make_table('my.table.one', n_cols=3, n_params=2)
        t1c = self.make_table('my.table.one', n_cols=2, n_params=2)
        t1d = self.make_table('my.table.one', n_cols=3, n_params=3)

        t2 = self.make_table('my.table.two', n_cols=6)

        self.assertEqual(hash(t1a), hash(t1b))
        self.assertNotEqual(hash(t1a), hash(t2))
        self.assertNotEqual(hash(t1a), hash(t1c))
        self.assertNotEqual(hash(t1a), hash(t1d))
        self.assertNotEqual(hash(t1c), hash(t1d))

    def test_table_inner_join_defaults(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=6)
        join = t1.inner_join(t2, t1.col0 == t2.col1)
        self.assertSqlEqual(
            '''
            [my.table.one] AS lhs
                INNER JOIN
            [my.table.two] AS rhs ON (lhs.[Col0] = rhs.[Col1])
            ''',
            join.from_
        )
        cols = join.get_columns()
        self.assertEqual(
            len(t1.get_columns()) + len(t2.get_columns()),
            len(cols)
        )

    def test_table_get_param_assignments(self):
        table = self.make_table('my.test.table', n_cols=5, n_params=3, n_tv_params=2)
        params = table._get_param_assignments()
        self.assertEqual(len(params), 5)
        sql = '\nand '.join(p.sql for p in params)
        self.assertSqlEqual(
            """
                [Param0] = 123
                and [Param1] = 1727364939238612
                and [Param2] = 3.14
                and [TableVar_0] = @TableVar_0
                and [TableVar_1] = @TableVar_1
            """,
            sql
        )

    def test_table_add_prefix_data_col(self):
        table = self.make_table()
        table_a = table.with_alias('ABC')

        col = table.col1
        prfx = table_a._add_prefix(col)

        self.assertEqual('ABC.[Col1]', prfx.sql)
        self.assertEqual(col.dtype, prfx.dtype)

    def test_table_add_prefix_expression_col(self):
        table = self.make_table().with_alias('ABC')
        r = (table.col0 - table.col1) / 2
        c = table._add_prefix(r)

        self.assertEqual(
            "(ABC.[Col0] - ABC.[Col1]) / cast(2 AS Double)",
            c.sql
        )

    def test_table_add_prefix_prefixed_col(self):
        table = self.make_table()
        table_a = table.with_alias('ABC')

        col = table.col1
        prfx = table_a._add_prefix(col)
        prfx2 = table_a._add_prefix(prfx)
        self.assertEqual("ABC.[Col1]", prfx2.sql)

        r = (table.col0 - table.col1) / 2
        prfx = table._add_prefix(r)
        prfx2 = table_a._add_prefix(prfx)
        self.assertEqual("(ABC.[Col0] - ABC.[Col1]) / cast(2 AS Double)", prfx2.sql)

    def test_table_add_suffix_data_col(self):

        table1 = self.make_table(name='my.table.one').with_alias('ABC')
        table2 = self.make_table(name='my.table.two').with_alias('CBA')

        c = table1.col0
        c_s = table1._add_suffix(c)
        c_s2 = table2._add_suffix(c)

        # test passthrough when from another table
        self.assertEqual('ABC.[Col0] AS [Col0_ABC]', c_s.sql)
        self.assertEqual('Col0_ABC', c_s.meta.field_name)
        self.assertEqual('col0_abc', c_s.meta.python_name())

    def test_table_with_alias_method(self):
        table = self.make_table('my.test.table')
        table_a = table.with_alias('ABC')

        self.assertSequenceHashEqual(
            [table_a._add_prefix(c) for c in table.get_columns()],
            table_a.get_columns()
        )
        self.assertEqual(
            tuple(p.with_prefix('ABC') for p in table._get_param_assignments()),
            table_a._get_param_assignments()
        )
        self.assertEqual(len(table.parameters_), len(table_a.parameters_))
        self.assertIs(table.meta_.alias, None)
        self.assertEqual(table_a.meta_.alias, 'ABC')

    def test_table_get_columns_method(self):
        table = self.make_table()

        exp_cols = [make(c) for c in table.meta_.columns]
        obs_cols = table.get_columns()

        self.assertEqual(len(exp_cols), len(obs_cols))
        for ec, oc in zip(exp_cols, obs_cols):
            self.assertHashEqual(ec, oc)

    def test_table_contains_col_method(self):
        table1 = self.make_table()
        table2 = self.make_table(name='other.table')

        exp_cols = [make(c) for c in table1.meta_.columns]

        for c in exp_cols:
            self.assertTrue(c in table1)

        self.assertFalse(table2.col0 in table1)

        self.assertTrue(0.5 * (table1.col0 / table1.col1) in table1)
        self.assertFalse(0.5 * (table1.col0 / table2.col1) in table1)

    def test_table_from_str_property(self):
        table = self.make_table('My.Test.Provider', n_params=0, n_tv_params=0)
        table_a = table.with_alias('test_alias')

        self.assertEqual('[My.Test.Provider]', table.from_)
        self.assertEqual('[My.Test.Provider] AS test_alias', table_a.from_)

        table_tv = table.select('*').to_table_var('test')
        table_tv_a = table_tv.with_alias('test_alias')
        self.assertEqual('@test', table_tv.from_)
        self.assertEqual('@test AS test_alias', table_tv_a.from_)

    def test_table_inner_join_method(self):
        table1 = self.make_table('My.Test.Provider1', n_params=2, n_tv_params=1)
        table2 = self.make_table('My.Test.Provider2', n_params=3, n_tv_params=0)

        join = table1.inner_join(table2, on=table1.col1 == table2.col1, left_alias='l', right_alias='r')

        self.assertHashEqual(join.parents_[0], table1.with_alias('l'))
        self.assertHashEqual(join.parents_[1], table2.with_alias('r'))
        exp, obs = join.parents_[2].get_parents()[0], table1.col1 == table2.col1
        self.assertHashEqual(exp, obs)

        self.assertSqlEqual(
            """
            [My.Test.Provider1] AS l
                INNER JOIN 
            [My.Test.Provider2] AS r ON (l.[Col1] = r.[Col1])
            """,
            join.from_
        )

        self.assertEqual(20, len(join.get_columns()))
        self.assertEqual(6, len(join._get_param_assignments()))

    def test_table_left_join_method(self):
        table1 = self.make_table('My.Test.Provider1', n_params=2, n_tv_params=1)
        table2 = self.make_table('My.Test.Provider2', n_params=3, n_tv_params=0)

        join = table1.left_join(table2, on=table1.col1 == table2.col1, left_alias='l', right_alias='r')

        self.assertHashEqual(join.parents_[0], table1.with_alias('l'))
        self.assertHashEqual(join.parents_[1], table2.with_alias('r'))
        exp, obs = join.parents_[2].get_parents()[0], table1.col1 == table2.col1
        self.assertHashEqual(exp, obs)

        self.assertSqlEqual(
            """
            [My.Test.Provider1] AS l
                LEFT JOIN 
            [My.Test.Provider2] AS r ON (l.[Col1] = r.[Col1])
            """,
            join.from_
        )

        self.assertEqual(20, len(join.get_columns()))
        self.assertEqual(6, len(join._get_param_assignments()))

    def test_table_select_method(self):
        table = self.make_table('My.Test.Provider1', n_params=0, n_tv_params=0)
        q = table.select('*')
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Test.Provider1]
            """,
            q.get_sql()
        )

    def test_table_select_star(self):
        table = self.make_table('My.Test.Table', n_cols=5, n_params=3)
        sql = table.select('*').get_sql()
        self.assertSqlEqual(
            """
            SELECT
                [Col0], [Col1], [Col2], [Col3], [Col4]
            FROM
                [My.Test.Table]
            WHERE
                [Param0] = 123
                and [Param1] = 1727364939238612
                and [Param2] = 3.14
            """,
            sql
        )

    def test_table_select_caret(self):
        table = self.make_table('My.Test.Table', n_cols=5, n_params=3)
        sql = table.select('^').get_sql()
        self.assertSqlEqual(
            """
            SELECT
                [Col0], [Col2], [Col4]
            FROM
                [My.Test.Table]
            WHERE
                [Param0] = 123
                and [Param1] = 1727364939238612
                and [Param2] = 3.14
            """,
            sql
        )

    def test_table_select_kwargs(self):
        table = self.make_table('My.Test.Table', n_cols=6, n_params=3)
        sql = table.select(A=table.col1, B=table.col4, C=table.col5).get_sql()
        self.assertSqlEqual(
            """
            SELECT
                [Col1] AS [A], [Col4] AS [B], [Col5] AS [C]
            FROM
                [My.Test.Table]
            WHERE
                [Param0] = 123
                and [Param1] = 1727364939238612
                and [Param2] = 3.14
            """,
            sql
        )

    def test_table_select_combined_inputs(self):
        table = self.make_table('My.Test.Table', n_cols=6, n_params=3)

        # star and **aliases
        sql1 = table.select('*', A=table.col1.exp(), Z=table.col0/2).get_sql()
        self.assertSqlEqual(
            """
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], exp([Col1]) AS [A], ([Col0] / cast(2 AS Double)) AS [Z]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            """,
            sql1
        )

        # caret and **aliases
        sql2 = table.select('^', A=table.col1.exp(), Z=table.col0/2).get_sql()
        self.assertSqlEqual(
            """SELECT
                   [Col0], [Col2], [Col4], exp([Col1]) AS [A], ([Col0] / cast(2 AS Double)) AS [Z]
                FROM
                   [My.Test.Table]
                WHERE
                   [Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14
            """,
            sql2
        )

        # caret and *args
        sql3 = table.select('^', table.col1, table.col5).get_sql()
        self.assertSqlEqual(
            """SELECT
                  [Col0], [Col2], [Col4], [Col1], [Col5]
               FROM
                  [My.Test.Table]
               WHERE
                  [Param0] = 123
                  and [Param1] = 1727364939238612
                  and [Param2] = 3.14
               """,
            sql3
        )

        # caret, *args and **aliases
        sql4 = table.select('^', table.col1, table.col5, Test1=table.col0 / 2, Test2=table.col2.exp()).get_sql()
        self.assertSqlEqual(
            """SELECT
                  [Col0], [Col2], [Col4], [Col1], [Col5], ([Col0] / cast(2 AS Double)) AS [Test1], exp([Col2]) AS [Test2]
               FROM
                  [My.Test.Table]
               WHERE
                  [Param0] = 123
                  and [Param1] = 1727364939238612
                  and [Param2] = 3.14
               """,
            sql4
        )

    def test_table_group_by_method(self):
        table = self.make_table('My.Test.Provider1', n_params=0, n_tv_params=0)
        q = table.group_by(table.col3, table.col4, IsPositive=table.col0 >= 0)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
                [Col3], [Col4], ([Col0] >= 0) AS [IsPositive]
            FROM
               [My.Test.Provider1]
            GROUP BY
                [Col3], [Col4], ([Col0] >= 0)
            """,
            sql
        )

    def test_table_select_validation_args_and_aliasing(self):
        t = self.make_table('My.Test.Table', n_cols=5, n_params=3)

        self.assertErrorsWithMessage(
            lambda: t.select(t.col0, t.col1._with_alias('test_alias'), t.col1 * 2, 5),
            ValueError,
            "Inputs to *cols must be original table columns (not calculations or python values), but were\n"
            "  cols[2] = [Col1] * 2 (Column op)\n"
            "  cols[3] = 5 (int)\n"
            "Only table columns can be supplied as unnamed cols. Other columns types such as functions of columns or "
            "python literals must be supplied as keyword args (except '*' and '^').\n"
            "Try something like one of the following:\n"
            "  •Scalar functions of columns: \n"
            "     table.select(col_doubled=provider.col*2)\n"
            "  •Aggregate functions of columns: \n"
            "     table.select(col_sum=provider.col.sum())\n"
            "  •Python literals: \n"
            "     table.select(higgs_mass=125.1)"
        )

    def test_table_select_bug(self):
        table = self.make_table('my.test.table', n_tv_params=2)
        q = table.select('*', table.col0 * 2)

    def test_table_select_with_table_params(self):
        table = self.make_table('my.test.table', n_tv_params=2)

        self.assertEqual(5, len(table._get_param_assignments()))

        q = table.select('*')

        self.assertSqlEqual(
            """
            @TableVar_0 = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4]
            FROM
               [TableVar_0.test.table];
            ------------------------------------------------------------------------------------------------
            @TableVar_1 = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4]
            FROM
               [TableVar_1.test.table];
            ------------------------------------------------------------------------------------------------
            
            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.test.table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
               and [TableVar_0] = @TableVar_0
               and [TableVar_1] = @TableVar_1            
            """,
            q.get_sql()
        )

    def test_table_validate_inputs_prefixing(self):
        table = self.make_table('my.test.table')
        table_a = table.with_alias("ABC")

        q = table_a.select(table.col0, table.col1, Test=table.col0*table.col1)
        sql = q.get_sql()
        self.assertSqlEqual(
            """
            SELECT
               ABC.[Col0], ABC.[Col1], (ABC.[Col0] * ABC.[Col1]) AS [Test]
            FROM
               [my.test.table] AS ABC
            WHERE
               ABC.[Param0] = 123
               and ABC.[Param1] = 1727364939238612
               and ABC.[Param2] = 3.14            
            """,
            sql
        )

    def test_table_validate_inputs_membership_check(self):
        table1 = self.make_table('my.table.one', n_cols=5, n_params=2, n_tv_params=1)
        table2 = self.make_table('my.table.two', n_cols=5)
        self.assertErrorsWithMessage(
            lambda: table1.select(table2.col0, Test=table1.col0 / table2.col0),
            ValueError,
            "There are columns in the input to .select() that do not belong to the table (my.table.one):\n"
            "[Col0] has dependence on my.table.two\n"
            "([Col0] / cast([Col0] AS Double)) AS [Test] has dependence on my.table.one + my.table.two\n"
            "The column may be from the same provider but a with a different set of parameter values and therefore constitutes a different table."
        )

    def test_table_get_table_ancestors(self):

        table = self.make_table('my.test.table', n_tv_params=3)
        obs = table._get_table_ancestors()
        exp = [p for p in table._get_table_ancestors() if isinstance(p, Table)]

        self.assertEqual(6, len(obs))
        self.assertSequenceHashEqual(exp, obs)

        tv = table.select('*').to_table_var()
        obs = tv._get_table_ancestors()
        exp = [p for p in tv._get_table_ancestors() if isinstance(p, Table)]
        self.assertEqual(7, len(obs))
        self.assertSequenceHashEqual(exp, obs)

    def test_table_getitem(self):

        table = self.make_table()
        c1 = table['Col1']
        self.assertEqual('[Col1]', c1.sql)

        c1 = table['col1']
        self.assertEqual('[Col1]', c1.sql)

        self.assertErrorsWithMessage(
            lambda: table['bol3'],
            AttributeError,
            "My.Test.Table has no column called \'bol3\'.\n"
            "Did you mean to use one of:\n"
            "   table.col3 / table[\"Col3\"]\n"
            "   table.col0 / table[\"Col0\"]\n"
            "   table.col1 / table[\"Col1\"]"
        )

    def test_table_self_inner_join(self):

        table = self.make_table()

        ta = table.with_alias('A')
        tb = table.with_alias('B')

        join = ta.inner_join(tb, ta.col0 == tb.col0)

        q = join.select('^')

        sql = q.get_sql()

        self.assertSqlEqual(
            """
            SELECT
               A.[Col0] AS [Col0_A], A.[Col2] AS [Col2_A], A.[Col4] AS [Col4_A], A.[Col6] AS [Col6_A], A.[Col8] AS [Col8_A], B.[Col0] AS [Col0_B], B.[Col2] AS [Col2_B], B.[Col4] AS [Col4_B], B.[Col6] AS [Col6_B], B.[Col8] AS [Col8_B]
            FROM
               [My.Test.Table] AS A
                 INNER JOIN
               [My.Test.Table] AS B ON (A.[Col0] = B.[Col0])
            WHERE
               A.[Param0] = 123
               and A.[Param1] = 1727364939238612
               and A.[Param2] = 3.14
               and B.[Param0] = 123
               and B.[Param1] = 1727364939238612
               and B.[Param2] = 3.14
            """,
            sql
        )

    def test_table_join_same_provider_different_params(self):

        atlas = self.make_atlas(None)

        i1 = atlas.lusid_instrument(as_at=dt.datetime(2022, 1, 1))
        i2 = atlas.lusid_instrument(as_at=dt.datetime(2023, 1, 1))

        join = i1.inner_join(i2, i1.lusid_instrument_id == i2.lusid_instrument_id, 'A', 'B')
        cols = i1.get_columns()[:3] + i2.get_columns()[:3]
        q = join.select(*cols).where(i2.is_active)

        self.assertSqlEqual(
            """
            SELECT
                A.[ClientInternal] AS [ClientInternal_A], A.[CompositeFigi] AS [CompositeFigi_A], A.[Cusip] AS [Cusip_A], B.[ClientInternal] AS [ClientInternal_B], B.[CompositeFigi] AS [CompositeFigi_B], B.[Cusip] AS [Cusip_B]
            FROM
               [Lusid.Instrument] AS A
                 INNER JOIN
               [Lusid.Instrument] AS B ON (A.[LusidInstrumentId] = B.[LusidInstrumentId])
            WHERE
               (A.[AsAt] = #2022-01-01 00:00:00.000000#
               and B.[AsAt] = #2023-01-01 00:00:00.000000#)
               and (B.[IsActive])
            """,
            q.get_sql()
        )
