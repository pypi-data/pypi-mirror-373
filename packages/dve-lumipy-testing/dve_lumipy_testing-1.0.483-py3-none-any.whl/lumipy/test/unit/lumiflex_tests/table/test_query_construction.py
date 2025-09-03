from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex.window import window


class TestQueryConstruction(SqlTestCase):

    def test_query_construction_with_table_var(self):

        table = self.make_table('Table.Test.One')

        tv = table.select('*').where(
            table.col0 > 0
        ).group_by(
            table.col5
        ).agg(
            MeanCol0=table.col0.mean()
        ).having(
            table.col0.mean() > 0
        ).order_by(
            table.col0.mean().asc()
        ).limit(10).to_table_var('tv')

        q = tv.select('*')

        sql = q.get_sql()

        self.assertSqlEqual(
            """
            @tv = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], avg([Col0]) AS [MeanCol0]
            FROM
               [Table.Test.One]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0))
            GROUP BY
               [Col5]
            HAVING
               (avg([Col0]) > 0)
            ORDER BY
               avg([Col0]) ASC
            LIMIT 10;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], [MeanCol0]
            FROM
               @tv            
            """,
            sql
        )

    def test_query_construction_table_dependency_resolution_spaghetti(self):

        n_cols = 11

        table1 = self.make_table('Table.Test.One', n_cols=n_cols, n_tv_params=3)
        self.assertEqual(n_cols, len(table1.get_columns()))
        tva, _ = [t.get_parents()[0] for t in table1._get_param_assignments()[-2:]]
        self.assertEqual(5, len(tva.get_columns()))

        table2 = self.make_table('Table.Test.Two', n_cols=n_cols)
        self.assertEqual(n_cols, len(table2.get_columns()))
        tvc = table2.select('*').where(table2.col0 > 0).to_table_var('tvc')
        self.assertEqual(n_cols, len(tvc.get_columns()))

        table3 = self.make_table('Table.Test.Three', n_cols=n_cols)
        self.assertEqual(n_cols, len(table3.get_columns()))

        tvd = table3.inner_join(tva, tva.col1 == table3.col1).select('*').to_table_var('tvd')
        self.assertEqual(
            len(table3.get_columns()) + len(tva.get_columns()),
            len(tvd.get_columns())
        )

        join1 = table1.inner_join(
            tvc,
            table1.col1 == tvc.col1,
            left_alias='t1',
            right_alias='c'
        )
        self.assertEqual(
            len(table1.get_columns()) + len(tvc.get_columns()),
            len(join1.get_columns())
        )

        join2 = join1.left_join(
            tvd,
            tvd.col3_lhs == table1.col1,
            right_alias='d'
        )
        self.assertEqual(
            len(join1.get_columns()) + len(tvd.get_columns()),
            len(join2.get_columns())
        )
        join3 = join2.inner_join(
            tva,
            tva.col0 == tvd.col0_rhs,
            right_alias='a'
        )
        self.assertEqual(
            len(join2.get_columns()) + len(tva.get_columns()),
            len(join3.get_columns())
        )

        win = window(groups=tva.col3, orders=table1.col0.asc(), lower=10, upper=11, exclude='group')
        q = join3.select(
            '*',
            AlphaTest=win.linreg.alpha(tvc.col1, tvd.col0_lhs)
        ).where(
            tva.col3 > tvd.col0_lhs
        ).group_by(
            tva.col3
        ).aggregate(
            MeanCol0Sum=(table1.col0 + tvc.col0 + tvd.col0_lhs + tva.col0).mean()
        ).having(
            table1.col1.sum() > 0
        ).order_by(
            table1.col0.desc(), tva.col1.asc()
        ).limit(
            100
        )

        sql = q.get_sql()

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
            @TableVar_2 = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4]
            FROM
               [TableVar_2.test.table];
            ------------------------------------------------------------------------------------------------
            @tvc = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9], [Col10]
            FROM
               [Table.Test.Two]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 0));
            ------------------------------------------------------------------------------------------------
            @tvd = SELECT
               lhs.[Col0] AS [Col0_lhs], lhs.[Col1] AS [Col1_lhs], lhs.[Col2] AS [Col2_lhs], lhs.[Col3] AS [Col3_lhs], lhs.[Col4] AS [Col4_lhs], lhs.[Col5], lhs.[Col6], lhs.[Col7], lhs.[Col8], lhs.[Col9], lhs.[Col10], rhs.[Col0] AS [Col0_rhs], rhs.[Col1] AS [Col1_rhs], rhs.[Col2] AS [Col2_rhs], rhs.[Col3] AS [Col3_rhs], rhs.[Col4] AS [Col4_rhs]
            FROM
               [Table.Test.Three] AS lhs
                 INNER JOIN
               @TableVar_1 AS rhs ON (rhs.[Col1] = lhs.[Col1])
            WHERE
               lhs.[Param0] = 123
               and lhs.[Param1] = 1727364939238612
               and lhs.[Param2] = 3.14;            
            ------------------------------------------------------------------------------------------------

            SELECT
               t1.[Col0] AS [Col0_t1], t1.[Col1] AS [Col1_t1], t1.[Col2] AS [Col2_t1], t1.[Col3] AS [Col3_t1], t1.[Col4] AS [Col4_t1], t1.[Col5] AS [Col5_t1], t1.[Col6] AS [Col6_t1], t1.[Col7] AS [Col7_t1], t1.[Col8] AS [Col8_t1], t1.[Col9] AS [Col9_t1], t1.[Col10] AS [Col10_t1], c.[Col0] AS [Col0_c], c.[Col1] AS [Col1_c], c.[Col2] AS [Col2_c], c.[Col3] AS [Col3_c], c.[Col4] AS [Col4_c], c.[Col5] AS [Col5_c], c.[Col6] AS [Col6_c], c.[Col7] AS [Col7_c], c.[Col8] AS [Col8_c], c.[Col9] AS [Col9_c], c.[Col10] AS [Col10_c], d.[Col0_lhs], d.[Col1_lhs], d.[Col2_lhs], d.[Col3_lhs], d.[Col4_lhs], d.[Col5] AS [Col5_d], d.[Col6] AS [Col6_d], d.[Col7] AS [Col7_d], d.[Col8] AS [Col8_d], d.[Col9] AS [Col9_d], d.[Col10] AS [Col10_d], d.[Col0_rhs], d.[Col1_rhs], d.[Col2_rhs], d.[Col3_rhs], d.[Col4_rhs], a.[Col0] AS [Col0_a], a.[Col1] AS [Col1_a], a.[Col2] AS [Col2_a], a.[Col3] AS [Col3_a], a.[Col4] AS [Col4_a], linear_regression_alpha(c.[Col1], d.[Col0_lhs]) OVER(
                   PARTITION BY a.[Col3]
                   ORDER BY t1.[Col0] ASC
                   ROWS BETWEEN 10 PRECEDING AND 11 FOLLOWING EXCLUDE GROUP
                   )
                AS [AlphaTest], a.[Col3], avg((((t1.[Col0] + c.[Col0]) + d.[Col0_lhs]) + a.[Col0])) AS [MeanCol0Sum]
            FROM
               [Table.Test.One] AS t1
                 INNER JOIN
               @tvc AS c ON (t1.[Col1] = c.[Col1])
                 LEFT JOIN
               @tvd AS d ON (d.[Col3_lhs] = t1.[Col1])
                 INNER JOIN
               @TableVar_1 AS a ON (a.[Col0] = d.[Col0_rhs])
            WHERE
               (t1.[Param0] = 123
               and t1.[Param1] = 1727364939238612
               and t1.[Param2] = 3.14
               and t1.[TableVar_0] = @TableVar_0
               and t1.[TableVar_1] = @TableVar_1
               and t1.[TableVar_2] = @TableVar_2)
               and ((a.[Col3] > d.[Col0_lhs]))
            GROUP BY
               a.[Col3]
            HAVING
               (total(t1.[Col1]) > 0)
            ORDER BY
               t1.[Col0] DESC, a.[Col1] ASC
            LIMIT 100
            """,
            sql
        )
