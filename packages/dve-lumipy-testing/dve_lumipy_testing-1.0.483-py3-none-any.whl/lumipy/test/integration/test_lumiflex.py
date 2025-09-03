import datetime as dt
import time

import pandas as pd

import lumipy as lm
from lumipy.test.test_infra import BaseIntTestWithAtlas


class LumiflexTests(BaseIntTestWithAtlas):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.ar = cls.atlas.lusid_logs_apprequest(
            start_at=dt.datetime.utcnow() - dt.timedelta(days=1)
        )

    def test_lumiflex_select_and_limit(self):

        pf = self.atlas.lusid_portfolio(as_at=dt.datetime(2022, 9, 1))
        n_cols = len(pf.get_columns())
        df = pf.select('*').limit(10).go()

        self.assertGreater(df.shape[0], 0)
        self.assertEqual(df.shape[1], n_cols)

    def test_lumiflex_select_new_columns(self):

        pf = self.atlas.lusid_portfolio(as_at=dt.datetime(2022, 9, 1))
        n_pf_cols = len(pf.get_columns(True))
        dt_val = dt.datetime(2022, 1, 1, 13, 45, 2)
        df = pf.select(
            '^',
            LoudNoises=pf.portfolio_code.str.upper(),
            IntVal=7,
            DoubleVal=1.23,
            TextVal='TESTING',
            DatetimeVal=dt_val,
            BoolVal=False,
        ).limit(10).go()

        df['DatetimeVal'] = pd.to_datetime(df.DatetimeVal)

        self.assertTrue((df['PortfolioCode'].str.upper() == df['LoudNoises']).all())
        self.assertTrue((df['IntVal'] == 7).all())
        self.assertTrue((df['DoubleVal'] == 1.23).all())
        self.assertTrue((df['TextVal'] == 'TESTING').all())
        self.assertTrue((df['DatetimeVal'] == dt_val).all())
        self.assertTrue((df['BoolVal'] == False).all())

        self.assertGreater(df.shape[0], 0)
        self.assertEqual(df.shape[1], n_pf_cols + 6)

    def test_lumiflex_where(self):

        pf = self.atlas.lusid_portfolio(as_at=dt.datetime(2022, 9, 1))
        n_cols = len(pf.get_columns())

        example_scope = 'Finbourne-Examples'
        df = pf.select('*').where(pf.portfolio_scope == example_scope).go()

        self.assertGreater(df.shape[0], 0)
        self.assertEqual(df.shape[1], n_cols)
        self.assertTrue((df.PortfolioScope.str.lower() == example_scope.lower()).all())

    def test_lumiflex_order_by(self):

        pf = self.atlas.lusid_portfolio(as_at=dt.datetime(2022, 9, 1))
        n_cols = len(pf.get_columns())

        example_scope = 'Finbourne-Examples'
        df = pf.select('*').where(
            pf.portfolio_scope == example_scope
        ).order_by(
            pf.portfolio_code.ascending()
        ).go()

        self.assertGreater(df.shape[0], 0)
        self.assertEqual(df.shape[1], n_cols)
        self.assertTrue((df.PortfolioScope.str.lower() == example_scope.lower()).all())
        self.assertTrue(
            (df.PortfolioCode.str.lower().sort_values(ascending=True) == df.PortfolioCode.str.lower()).all()
        )

    def test_lumiflex_case_statement_and_group_by_agg(self):

        pf = self.atlas.lusid_portfolio(as_at=dt.datetime(2022, 9, 1))

        example_scope = 'Finbourne-Examples'
        labels = ['GLOBAL', 'US', 'UK']

        region = pf
        for label in labels:
            region = lm.when(pf.portfolio_code.str.contains(label)).then(label)
        region = region.otherwise('OTHER')

        df = pf.select(
            Region=region
        ).where(
            (pf.portfolio_scope == example_scope)
        ).group_by(
            Region=region
        ).aggregate(
            PortfolioCount=pf.portfolio_code.count()
        ).go()

        self.assertGreater(df.shape[0], 0)
        self.assertEqual(df.shape[1], 2)
        self.assertSequenceEqual(df.columns.tolist(), ['Region', 'PortfolioCount'])

    def test_lumiflex_having(self):

        pf = self.atlas.lusid_portfolio(as_at=dt.datetime(2022, 9, 1))

        example_scope = 'Finbourne-Examples'
        labels = ['GLOBAL', 'US', 'UK']

        label = labels[0]
        region = lm.when(pf.portfolio_code.str.contains(label)).then(label)
        for label in labels[1:]:
            region = region.when(pf.portfolio_code.str.contains(label)).then(label)
        region = region.otherwise('OTHER')

        df = pf.select(
            Region=region
        ).where(
            (pf.portfolio_scope == example_scope)
        ).group_by(
            Region=region
        ).aggregate(
            PortfolioCount=pf.portfolio_code.count()
        ).having(
            pf.portfolio_code.count() > 3
        ).go()

        self.assertEqual(df.shape[0], 2)
        self.assertEqual(df.shape[1], 2)
        self.assertSequenceEqual(df.columns.tolist(), ['Region', 'PortfolioCount'])

    def test_lumiflex_table_var_and_left_join(self):

        pf = self.atlas.lusid_portfolio(as_at=dt.datetime(2022, 9, 1))
        hld = self.atlas.lusid_portfolio_holding(as_at=dt.datetime(2022, 9, 1))

        tv = pf.select('^').where(pf.portfolio_scope == 'Finbourne-Examples').to_table_var()

        n_cols_left = len(tv.get_columns())
        n_cols_right = len(hld.get_columns())

        join = tv.left_join(hld, on=tv.portfolio_code == hld.portfolio_code)
        df = join.select('*').go()

        self.assertGreater(df.shape[0], 0)
        self.assertEqual(df.shape[1], n_cols_left + n_cols_right)

    def test_lumiflex_unions(self):

        portfolios = self.atlas.lusid_portfolio(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        )
        pf_codes = portfolios.select(portfolios.portfolio_code).where(
            (portfolios.portfolio_scope == 'Finbourne-Examples') &
            (portfolios.portfolio_code.str.like('%equ%')) &
            (portfolios.portfolio_code.str.not_like('%swap%'))
        ).go().PortfolioCode.tolist()

        holding = self.atlas.lusid_portfolio_holding(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        )

        def subquery(pf_code):
            total_cost = holding.select(
                TotalCost=holding.cost_amount_portfolio_currency.sum()
            ).where(
                (holding.portfolio_code == pf_code) &
                (holding.portfolio_scope == 'Finbourne-Examples')
            ).to_scalar_var(f'cost_total_{abs(hash(pf_code))}')

            return holding.select(
                holding.portfolio_code,
                holding.lusid_instrument_id,
                holding.cost_amount_portfolio_currency,
                CostFractionPc=100 * holding.cost_amount_portfolio_currency / total_cost
            ).where(
                (holding.portfolio_code == pf_code) &
                (holding.portfolio_scope == 'Finbourne-Examples')
            ).order_by(
                (holding.cost_amount_portfolio_currency / total_cost).descending()
            ).limit(5).to_table_var(f"sq_{abs(hash(pf_code))}").select('*')

        qry = lm.concat(map(subquery, pf_codes))
        df = qry.go()

        self.assertEqual(df.shape[0], 10)
        self.assertEqual(df.shape[1], 4)

    def test_sample_table_with_frac(self):

        pf = self.atlas.lusid_instrument()

        # The sampling will be with probability 0.5 from a set of 200
        # The row count of the result will be binomial-distributed with n = 200 and p = 0.5
        # https://en.wikipedia.org/wiki/Binomial_distribution
        n, p = 200, 0.5

        # Given it's going to be a binomial we can compute the std deviation
        sigma = (n * p * (1 - p)) ** 0.5

        # and we can compute the expected value
        exp = n * p

        # Given these we can compute the 4-sigma interval. The count has a 1/15787 chance of being outside.
        # If it's outside this interval there's probably a problem with the sampling.
        lower_lim, upper_lim = exp - 4 * sigma, exp + 4 * sigma

        pfs = pf.select('*').limit(n)
        qry = pfs.sample(prob=p)
        df = qry.go()

        self.assertTrue(lower_lim < df.shape[0] < upper_lim)

    def test_sample_table_with_n(self):

        pf = self.atlas.lusid_instrument().select('*').limit(200)

        # Get the lim 100 of the above as a table var to check against.
        # If the sampling works it should be different to just taking the first 100
        lim_100_df = pf.to_table_var().select('*').limit(100).go()

        qry = pf.sample(100)
        df = qry.go()

        # It should return 100 random samples
        self.assertEqual(df.shape[0], 100)
        # That are definitely different to the first 100
        self.assertFalse((lim_100_df == df).all().all())

    def test_create_query_delete_view(self):

        test_provider_name = "Lumipy.View.Test"

        sys_connection = self.atlas.sys_connection()

        # Create view and verify returns rows
        query = sys_connection.select('*')
        df = query.setup_view(test_provider_name).go()
        self.assertGreater(df.shape[0], 0)

        # Check view has accessible provider in atlas
        time.sleep(5)
        atlas = lm.get_atlas()
        results = atlas.search(test_provider_name).list_providers()
        self.assertEqual(len(results), 1)

        # Check view provider can be queried
        test_provider = results[0]()
        df = test_provider.select('*').go()
        self.assertGreater(df.shape[0], 0)

        # Delete view provider and verify it's removed from atlas
        self.client.delete_view(test_provider_name)
        tries = 0
        while tries < 6:
            time.sleep(15)
            atlas = lm.get_atlas()
            results = atlas.search(test_provider_name).list_providers()
            if len(results) == 0:
                break
            tries += 1

        if tries == 6:
            raise AssertionError('View has not been deleted.')

#     def test_cumulative_fns_match_pandas(self):
#         qry = self.ar.select(
#             self.ar.timestamp, self.ar.duration,
#             CumeSum=self.ar.duration.cume.sum(),
#             CumeMin=self.ar.duration.cume.min(),
#             CumeMax=self.ar.duration.cume.max(),
#         ).where(
#             (self.ar.application == 'lusid')
#             & (self.ar.method == 'UpsertInstruments')
#         ).limit(100)
# 
#         df = qry.go()
# 
#         df['PdCumeSum'] = df.Duration.cumsum()
#         df['PdCumeMax'] = df.Duration.cummax()
#         df['PdCumeMin'] = df.Duration.cummin()
# 
#         self.assertSequenceEqual(df.PdCumeSum.round(9).tolist(), df.CumeSum.round(9).tolist())
#         self.assertSequenceEqual(df.PdCumeMin.round(9).tolist(), df.CumeMin.round(9).tolist())
#         self.assertSequenceEqual(df.PdCumeMax.round(9).tolist(), df.CumeMax.round(9).tolist())
# 
#     def test_frac_diff_matches_pandas(self):
#         qry = self.ar.select(
#             self.ar.timestamp, self.ar.duration,
#             FracDiff=self.ar.duration.frac_diff(),
#             FracDiffN3=self.ar.duration.frac_diff(offset=3),
#         ).where(
#             (self.ar.application == 'lusid')
#             & (self.ar.method == 'UpsertInstruments')
#             & (self.ar.event_type == 'Completed')
#         ).limit(100)
# 
#         df = qry.go()
# 
#         df['PdFracDiff'] = df.Duration.pct_change()
#         df['PdFracDiffN3'] = df.Duration.pct_change(periods=3)
# 
#         self.assertSequenceEqual(
#             df.PdFracDiff.round(9).tolist()[1:],
#             df.FracDiff.round(9).tolist()[1:],
#         )
# 
#         self.assertSequenceEqual(
#             df.PdFracDiffN3.round(9).tolist()[3:],
#             df.FracDiffN3.round(9).tolist()[3:],
#         )
# 
#     def test_drawdown_matches_pandas(self):
#         win = lm.window()
#         qry = self.ar.select(
#             self.ar.timestamp, self.ar.duration,
#             Drawdown=win.finance.drawdown(self.ar.duration)
#         ).where(
#             (self.ar.application == 'lusid')
#             & (self.ar.method == 'UpsertInstruments')
#             & (self.ar.event_type == 'Completed')
#         ).limit(100)
# 
#         df = qry.go()
# 
#         df['PdDrawdown'] = abs(df.Duration - df.Duration.cummax()) / df.Duration.cummax()
#         df = df.iloc[1:]
#         self.assertSequenceEqual(
#             df.PdDrawdown.round(9).tolist(),
#             df.Drawdown.round(9).tolist(),
#         )
# 
#     def test_cume_dist_matches_pandas(self):
#         qry = self.ar.select(
#             self.ar.timestamp, self.ar.duration,
#             CumeDist=self.ar.duration.cume.dist()
#         ).where(
#             (self.ar.application == 'lusid')
#             & (self.ar.method == 'UpsertInstruments')
#             & (self.ar.event_type == 'Completed')
#         ).limit(100)
# 
#         df = qry.go()
#         df['PdCumeDist'] = df.Duration.rank(pct=True, method='max')
# 
#         self.assertSequenceEqual(
#             df.CumeDist.round(9).tolist(),
#             df.PdCumeDist.round(9).tolist(),
#         )
