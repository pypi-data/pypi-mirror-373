from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from math import ceil, floor
from lumipy.lumiflex._column.accessors import *
import pandas as pd
import numpy as np


class TestSqlColumnMethods(SqlTestCase):

    def test_column_method_hash(self):
        d1a = self.make_double_col('d1')
        d1b = self.make_double_col('d1')
        self.assertEqual(hash(d1a), hash(d1b))
        self.assertEqual(hash(d1a + d1b), hash(d1b + d1a))

        d1c = self.make_int_col('d1')
        self.assertNotEqual(hash(d1a), d1c)

    def test_column_str_accessor_property(self):
        s = self.make_text_col('t')
        acc = s.str
        self.assertIsInstance(acc, StrFnAccessor)

        self.assertErrorsWithMessage(
            lambda: self.make_double_col('d').str,
            AttributeError,
            "To use .str accessor the column must be Text type, but was Double."
        )

    def test_column_dt_accessor_property(self):
        s = self.make_datetime_col('dt')
        acc = s.dt
        self.assertIsInstance(acc, DtFnAccessor)

        self.assertErrorsWithMessage(
            lambda: self.make_double_col('d').dt,
            AttributeError,
            "To use .dt accessor the column must be Date/DateTime type, but was Double."
        )

    def test_column_cume_accessor_property(self):
        s = self.make_double_col('d')
        acc = s.cume
        self.assertIsInstance(acc, CumeFnAccessor)

        self.assertErrorsWithMessage(
            lambda: self.make_text_col('d').cume,
            AttributeError,
            "To use .cume accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_column_stats_accessor_property(self):
        s = self.make_double_col('d')
        acc = s.stats
        self.assertIsInstance(acc, StatsFnAccessor)

        self.assertErrorsWithMessage(
            lambda: self.make_text_col('d').stats,
            AttributeError,
            "To use .stats accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_column_metric_accessor_property(self):
        s = self.make_double_col('d')
        acc = s.metric
        self.assertIsInstance(acc, MetricFnAccessor)

        self.assertErrorsWithMessage(
            lambda: self.make_text_col('d').metric,
            AttributeError,
            "To use .metric accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_column_linreg_accessor_property(self):
        s = self.make_double_col('d')
        acc = s.linreg
        self.assertIsInstance(acc, LinregFnAccessor)

        self.assertErrorsWithMessage(
            lambda: self.make_text_col('d').linreg,
            AttributeError,
            "To use .linreg accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_column_finance_accessor_property(self):
        s = self.make_double_col('d')
        acc = s.finance
        self.assertIsInstance(acc, FinanceFnAccessor)

        self.assertErrorsWithMessage(
            lambda: self.make_text_col('d').finance,
            AttributeError,
            "To use .finance accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_column_method_with_alias(self):
        d1 = self.make_double_col('d1')
        d1_alias = d1._with_alias('TestAlias')

        self.assertEqual('[d1] AS [TestAlias]', d1_alias.sql)
        self.assertHashEqual(d1, d1_alias.get_parents()[0])
        self.assertEqual('alias', d1_alias.get_label())
        self.assertEqual('TestAlias', d1_alias.meta.field_name)
        self.assertEqual(d1.meta.table_name, d1_alias.meta.table_name)

    def test_error_when_aliasing_an_aliased_column(self):
        d1 = self.make_double_col('d1')
        d1_alias = d1._with_alias('TestAlias')
        with self.assertRaises(ValueError) as ve:
            d1_alias._with_alias('errors')

        self.assertIn(
            "This expression already has an alias (TestAlias).",
            str(ve.exception)
        )

    def test_column_round_method(self):
        d = self.make_double_col('d')
        r = d.round()
        self.assertEqual('round([d], 0)', r.sql)
        self.assertEqual(DType.Int, r.dtype)
        r = d.round(2)
        self.assertEqual('round([d], 2)', r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_round_function(self):
        d = self.make_double_col('d')
        r = round(d)
        self.assertEqual('round([d], 0)', r.sql)
        self.assertEqual(DType.Int, r.dtype)
        r = round(d, 2)
        self.assertEqual('round([d], 2)', r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_abs_method(self):
        d = self.make_double_col('d')
        r = d.abs()
        self.assertEqual('abs([d])', r.sql)
        self.assertEqual(DType.Double, r.dtype)
        d = self.make_int_col('d')
        r = d.abs()
        self.assertEqual('abs([d])', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_abs_function(self):
        d = self.make_double_col('d')
        r = abs(d)
        self.assertEqual('abs([d])', r.sql)
        self.assertEqual(DType.Double, r.dtype)
        d = self.make_int_col('d')
        r = abs(d)
        self.assertEqual('abs([d])', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_ceil_method(self):
        d = self.make_double_col('d')
        r = d.ceil()
        self.assertEqual('ceil([d])', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_ceil_function(self):
        d = self.make_double_col('d')
        r = ceil(d)
        self.assertEqual('ceil([d])', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_floor_method(self):
        d = self.make_double_col('d')
        r = d.floor()
        self.assertEqual('floor([d])', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_floor_function(self):
        d = self.make_double_col('d')
        r = floor(d)
        self.assertEqual('floor([d])', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_exp_method(self):
        r = self.make_double_col('d').exp()
        self.assertEqual('exp([d])', r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_log_method(self):
        r = self.make_double_col('d').log()
        self.assertEqual('log([d])', r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_log10_method(self):
        r = self.make_double_col('d').log10()
        self.assertEqual('log10([d])', r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_sign_method(self):
        r = self.make_double_col('d').sign()
        self.assertEqual('sign([d])', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_is_in_method(self):
        c = self.make_text_col('c')

        # *args input
        r = c.is_in('a', 'b', 'c')
        self.assertEqual("[c] IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # list input
        r = c.is_in(['a', 'b', 'c'])
        self.assertEqual("[c] IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # tuple input
        r = c.is_in(('a', 'b', 'c'))
        self.assertEqual("[c] IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # np.array input
        r = c.is_in(np.array(['a', 'b', 'c']))
        self.assertEqual("[c] IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # pd.Series input
        r = c.is_in(pd.Series(('a', 'b', 'c')))
        self.assertEqual("[c] IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_columns_is_in_method_with_subquery(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq = table2.select(table2.col0).where(table2.col2 > 3)
        r = table1.col0.is_in(sq)
        self.assertEqual(DType.Boolean, r.dtype)
        self.assertSqlEqual(
            """
            [Col0] IN (
                SELECT
                   [Col0]
                FROM
                   [my.table.two]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col2] > 3))
               )            
            """,
            r.sql
        )

    def test_columns_not_in_method_with_subquery(self):
        table1 = self.make_table('my.table.one')
        table2 = self.make_table('my.table.two')

        sq = table2.select(table2.col0).where(table2.col2 > 3)
        r = table1.col0.not_in(sq)
        self.assertEqual(DType.Boolean, r.dtype)
        self.assertSqlEqual(
            """
            [Col0] NOT IN (
                SELECT
                   [Col0]
                FROM
                   [my.table.two]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col2] > 3))
               )            
            """,
            r.sql
        )

    def test_column_not_in_method(self):
        c = self.make_text_col('c')

        # *args input
        r = c.not_in('a', 'b', 'c')
        self.assertEqual("[c] NOT IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # list input
        r = c.not_in(['a', 'b', 'c'])
        self.assertEqual("[c] NOT IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # tuple input
        r = c.not_in(('a', 'b', 'c'))
        self.assertEqual("[c] NOT IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # np.array input
        r = c.not_in(np.array(['a', 'b', 'c']))
        self.assertEqual("[c] NOT IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # pd.Series input
        r = c.not_in(pd.Series(('a', 'b', 'c')))
        self.assertEqual("[c] NOT IN ('a', 'b', 'c')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_column_between_method(self):
        d = self.make_double_col('d')

        r = d.between(upper=2, lower=1)
        self.assertEqual('[d] BETWEEN 1 AND 2', r.sql)

        r = d.between(3, 4)
        self.assertEqual('[d] BETWEEN 3 AND 4', r.sql)

        r = d.between(2, upper=3)
        self.assertEqual('[d] BETWEEN 2 AND 3', r.sql)

        r = d.between(lower=1, upper=4)
        self.assertEqual('[d] BETWEEN 1 AND 4', r.sql)

    def test_column_not_between_method(self):
        d = self.make_double_col('d')

        r = d.not_between(upper=2, lower=1)
        self.assertEqual('[d] NOT BETWEEN 1 AND 2', r.sql)

        r = d.not_between(3, 4)
        self.assertEqual('[d] NOT BETWEEN 3 AND 4', r.sql)

        r = d.not_between(2, upper=3)
        self.assertEqual('[d] NOT BETWEEN 2 AND 3', r.sql)

        r = d.not_between(lower=1, upper=4)
        self.assertEqual('[d] NOT BETWEEN 1 AND 4', r.sql)

    def test_column_is_null_method(self):
        r = self.make_double_col('d').is_null()
        self.assertEqual('[d] IS NULL', r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_column_is_not_null_method(self):
        r = self.make_double_col('d').is_not_null()
        self.assertEqual('[d] IS NOT NULL', r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_column_coalesce_method(self):
        d1, d2, d3 = self.make_double_cols(3)
        r = d1.coalesce(d2, d3 / 2, 89)
        self.assertEqual("coalesce([d0], [d1], ([d2] / cast(2 AS Double)), 89)", r.sql)
        self.assertEqual(d1.dtype, r.dtype)

    def test_column_cast_method_pytypes(self):
        c = self.make_double_col('c')

        # Cast to self type is no-op
        r = c.cast(float)
        self.assertEqual("[c]", r.sql)
        self.assertEqual(DType.Double, r.dtype)

        # Cast to Int
        r = c.cast(int)
        self.assertEqual("cast([c] AS Int)", r.sql)
        self.assertEqual(DType.Int, r.dtype)

        # Cast to Text
        r = c.cast(str)
        self.assertEqual("cast([c] AS Text)", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        # Cast to Boolean
        r = c.cast(bool)
        self.assertEqual("cast([c] AS Boolean)", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # Cast to Double
        c = self.make_text_col('s')
        r = c.cast(float)
        self.assertEqual("cast([s] AS Double)", r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_cast_method_dtypes(self):
        c = self.make_double_col('c')

        # Cast to self type is no-op
        r = c.cast(DType.Double)
        self.assertEqual("[c]", r.sql)
        self.assertEqual(DType.Double, r.dtype)

        # Cast to Int
        r = c.cast(DType.Int)
        self.assertEqual("cast([c] AS Int)", r.sql)
        self.assertEqual(DType.Int, r.dtype)

        # Cast to Text
        r = c.cast(DType.Text)
        self.assertEqual("cast([c] AS Text)", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        # Cast to Boolean
        r = c.cast(DType.Boolean)
        self.assertEqual("cast([c] AS Boolean)", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # Cast to Double
        c = self.make_text_col('s')
        r = c.cast(DType.Double)
        self.assertEqual("cast([s] AS Double)", r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_sum_method(self):
        d = self.make_double_col('d')
        s = d.sum()
        self.assertEqual('total([d])', s.sql)
        self.assertEqual(DType.Double, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

    def test_column_count(self):
        d = self.make_double_col('d')
        s = d.count()
        self.assertEqual('count([d])', s.sql)
        self.assertEqual(DType.Int, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

    def test_column_mean_method(self):
        d = self.make_double_col('d')
        s = d.mean()
        self.assertEqual('avg([d])', s.sql)
        self.assertEqual(DType.Double, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

        d = self.make_int_col('d')
        s = d.mean()
        self.assertEqual('avg([d])', s.sql)
        self.assertEqual(DType.Double, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

    def test_column_min_method(self):
        d = self.make_double_col('d')
        s = d.min()
        self.assertEqual('min([d])', s.sql)
        self.assertEqual(DType.Double, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

        d = self.make_int_col('d')
        s = d.min()
        self.assertEqual('min([d])', s.sql)
        self.assertEqual(DType.Int, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

    def test_column_max_method(self):
        d = self.make_double_col('d')
        s = d.max()
        self.assertEqual('max([d])', s.sql)
        self.assertEqual(DType.Double, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

        d = self.make_int_col('d')
        s = d.max()
        self.assertEqual('max([d])', s.sql)
        self.assertEqual(DType.Int, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

    def test_column_median_method(self):
        d = self.make_double_col('d')
        s = d.median()
        self.assertEqual('median([d])', s.sql)
        self.assertEqual(DType.Double, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

    def test_column_stdev_method(self):
        d = self.make_double_col('d')
        s = d.stdev()
        self.assertEqual('stdev([d])', s.sql)
        self.assertEqual(DType.Double, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

    def test_column_quantile(self):
        d = self.make_double_col('d')
        q = d.quantile(0.2)
        self.assertEqual("quantile([d], 0.2)", q.sql)
        self.assertEqual(DType.Double, q.dtype)

    def test_column_prod_method(self):
        d = self.make_double_col('d')
        s = d.prod()
        self.assertEqual('cumeprod([d])', s.sql)
        self.assertEqual(DType.Double, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

        d = self.make_int_col('d')
        s = d.prod()
        self.assertEqual('cumeprod([d])', s.sql)
        self.assertEqual(DType.Int, s.dtype)
        self.assertEqual('aggfunc', s.get_label())

    def test_get_data_col_dependencies(self):

        d1 = self.make_double_col('d1')
        d2 = self.make_double_col('d2')
        i = self.make_int_col('i')

        r = round(100 * (d1 - d2) / i, 2)

        data_cols = r._get_data_col_dependencies()
        self.assertSequenceHashEqual([d1, d2, i], data_cols)

    def test_column_update_field(self):

        d1 = self.make_double_col('d1')
        d2 = self.make_double_col('d2')
        i = self.make_int_col('i')

        expr = (d1 + i) / d2

        target = (d1 + i) / 2.0

        expr_update = expr.update_node(parents=[expr.parents_[0], make(2.0)])

        self.assertHashEqual(target, expr_update)

    def test_block_node_type_agg_of_agg(self):

        d1 = self.make_double_col('d1')

        self.assertErrorsWithMessage(
            lambda: d1.sum().sum(),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d1.sum().sum(),\n"
            "There was 1 failed constraint on .sum():\n"
            "   • Can't use an aggregate function inside .sum()!"
        )

    def test_column_method_diff(self):
        d1 = self.make_double_col('d1')
        sql = d1.diff().sql
        self.assertSqlEqual(
            """
            [d1] - lag([d1], 1, NULL) OVER(
                ROWS BETWEEN 1 PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_column_method_frac_diff(self):
        d1 = self.make_double_col('d1')
        sql = d1.frac_diff().sql
        self.assertSqlEqual(
            """
            ([d1] - lag([d1], 1, NULL) OVER(
                ROWS BETWEEN 1 PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            ) / lag([d1], 1, NULL) OVER(
                ROWS BETWEEN 1 PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
                )
            """,
            sql
        )

    def test_column_diff_block_node_type(self):
        d1 = self.make_double_col('d1')
        self.assertErrorsWithMessage(
            lambda: d1.diff().diff(),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d1.diff().diff(),\n"
            "There was 1 failed constraint on .diff():\n"
            "   • Can't use a window function inside .diff()!"
        )

        self.assertErrorsWithMessage(
            lambda: d1.sum().diff(),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d1.sum().diff(),\n"
            "There was 1 failed constraint on .diff():\n"
            "   • Can't use an aggregate function inside .diff()!"
        )

    def test_column_frac_diff_block_node_type(self):
        d1 = self.make_double_col('d1')
        self.assertErrorsWithMessage(
            lambda: d1.diff().frac_diff(),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d1.diff().frac_diff(),\n"
            "There was 1 failed constraint on .frac_diff():\n"
            "   • Can't use a window function inside .frac_diff()!"
        )

        self.assertErrorsWithMessage(
            lambda: d1.sum().frac_diff(),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d1.sum().frac_diff(),\n"
            "There was 1 failed constraint on .frac_diff():\n"
            "   • Can't use an aggregate function inside .frac_diff()!"
        )

    def test_column_asc_method(self):
        c = self.make_double_col('c')
        ordering = c.asc()
        self.assertIsInstance(ordering, Ordering)
        self.assertEqual("[c] ASC", ordering.sql)
        ordering = c.ascending()
        self.assertIsInstance(ordering, Ordering)
        self.assertEqual("[c] ASC", ordering.sql)

    def test_column_desc_method(self):
        c = self.make_double_col('c')
        ordering = c.desc()
        self.assertIsInstance(ordering, Ordering)
        self.assertEqual("[c] DESC", ordering.sql)
        ordering = c.descending()
        self.assertIsInstance(ordering, Ordering)
        self.assertEqual("[c] DESC", ordering.sql)
