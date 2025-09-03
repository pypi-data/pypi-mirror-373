from lumipy.lumiflex._metadata.table import TableMeta
from lumipy.lumiflex._table import DirectProviderVar
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestDirectProviderDef(SqlTestCase):

    def test_direct_provider_def_creation(self):
        tv1, tv2 = self.make_table_var('one'), self.make_table_var('two')

        name = 'my.direct.provider'
        columns = [self.make_col_meta(i, True, name) for i in range(5)]
        meta = TableMeta(name=name, columns=columns, category='Testing', type='DirectProvider')

        dp = DirectProviderVar(
            meta=meta,
            use_params={
                'number': '123',
                'body': """
                    for thing in things:
                        do stuff
                    """,
                'startAt': '2023-01-31T00:00:00',
                'endAt': '2023-01-31T00:00:00',
            },
            parents=(tv1, tv2),
            client=self.make_dummy_client(),
            limit=10,
        )

        sql = dp.table_sql()

        self.assertSqlEqual(
            """
            use my.direct.provider with @test_one, @test_two limit 10
               --number=123
               --body=
                   for thing in things:
                       do stuff

               --startAt=2023-01-31T00:00:00
               --endAt=2023-01-31T00:00:00
            enduse            
            """,
            sql
        )

    def test_direct_provider_as_table(self):
        tv1, tv2 = self.make_table_var('one'), self.make_table_var('two')

        name = 'my.direct.provider'
        columns = [self.make_col_meta(i, True, name) for i in range(5)]
        meta = TableMeta(name=name, columns=columns, category='Testing', type='DirectProvider')

        dp = DirectProviderVar(
            meta=meta,
            use_params={
                'number': '123',
                'body': """
                    for thing in things:
                        do stuff
                    """,
                'startAt': '2023-01-31T00:00:00',
                'endAt': '2023-01-31T00:00:00',
            },
            parents=(tv1, tv2),
            client=self.make_dummy_client(),
        )

        sql = dp.build().select('*').get_sql()

        self.assertSqlEqual(
            """
            @test_one = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------
            @test_two = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.two]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------
            @my_direct_provider_1 = use my.direct.provider with @test_one, @test_two
                  --number=123
                  --body=
                      for thing in things:
                          do stuff
                                      
                  --startAt=2023-01-31T00:00:00
                  --endAt=2023-01-31T00:00:00
               enduse;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4]
            FROM
               @my_direct_provider_1            
            """,
            sql
        )

    def test_direct_provider_prefixing(self):
        tv1, tv2 = self.make_table_var('one'), self.make_table_var('two')

        name = 'my.direct.provider'
        columns = [self.make_col_meta(i, True, name) for i in range(5)]
        meta = TableMeta(name=name, columns=columns, category='Testing', type='DirectProvider')

        dp = DirectProviderVar(
            meta=meta,
            use_params={
                'number': '123',
                'body': """
                    for thing in things:
                        do stuff
                    """,
                'startAt': '2023-01-31T00:00:00',
                'endAt': '2023-01-31T00:00:00',
            },
            parents=(tv1, tv2),
            client=self.make_dummy_client(),
        )

        table = dp.build()

        condition = table.col0 > 3

        table_a = table.with_alias('ABC')
        prfx_cond = table_a._add_prefix(condition)
        self.assertEqual("ABC.[Col0] > 3", prfx_cond.sql)

    def test_direct_providers_in_a_join(self):
        tv1, tv2 = self.make_table_var('one'), self.make_table_var('two')

        name = 'my.direct.provider1'
        columns = [self.make_col_meta(i, True, name) for i in range(5)]
        meta = TableMeta(name=name, columns=columns, category='Testing', type='DirectProvider')

        dp1 = DirectProviderVar(
            meta=meta,
            use_params={
                'number': '123',
                'body': """
                    for thing in things:
                        do stuff
                    """,
                'startAt': '2023-01-31T00:00:00',
                'endAt': '2023-01-31T00:00:00',
            },
            parents=(tv1, tv2),
            client=self.make_dummy_client(),
        ).build()

        name = 'my.direct.provider2'
        columns = [self.make_col_meta(i, True, name) for i in range(3)]
        meta = TableMeta(name=name, columns=columns, category='Testing', type='DirectProvider')

        dp2 = DirectProviderVar(
            meta=meta,
            use_params={
                'number': '123',
                'body': """
                    for thing in things:
                        do stuff
                    """,
                'startAt': '2023-01-31T00:00:00',
                'endAt': '2023-01-31T00:00:00',
            },
            parents=(tv1, tv2),
            client=self.make_dummy_client(),
        ).build()

        join = dp1.inner_join(dp2, dp1.col0 == dp2.col0)

        q = join.select('*')

        sql = q.get_sql()

        self.assertSqlEqual(
            """
            @test_one = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - --
            @test_two = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.two]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - --
            @my_direct_provider2_1 = use my.direct.provider2 with @test_one, @test_two 
                  --number=123
                  --body=
                                      for thing in things:
                                          do stuff
                                      
                  --startAt=2023-01-31T00:00:00
                  --endAt=2023-01-31T00:00:00
               enduse;
            -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - --
            @my_direct_provider1_1 = use my.direct.provider1 with @test_one, @test_two 
                  --number=123
                  --body=
                                      for thing in things:
                                          do stuff
                                      
                  --startAt=2023-01-31T00:00:00
                  --endAt=2023-01-31T00:00:00
               enduse;
            --===========================================================================================--

            SELECT
               lhs.[Col0] AS [Col0_lhs], lhs.[Col1] AS [Col1_lhs], lhs.[Col2] AS [Col2_lhs], lhs.[Col3], lhs.[Col4], rhs.[Col0] AS [Col0_rhs], rhs.[Col1] AS [Col1_rhs], rhs.[Col2] AS [Col2_rhs]
            FROM
               @my_direct_provider1_1 AS lhs
                 INNER JOIN
               @my_direct_provider2_1 AS rhs ON (lhs.[Col0] = rhs.[Col0])            
            """,
            sql
        )
