from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._metadata.table import TableMeta
from lumipy.lumiflex._atlas.atlas import Atlas
from lumipy.lumiflex._atlas.utils import process_direct_provider_metadata
from lumipy.lumiflex._atlas.metafactory import Factory


class TestAtlas(SqlTestCase):

    def test_atlas_construction(self):

        data_p_metas = [TableMeta.data_provider_from_df(gdf) for _, gdf in self.df1.groupby('TableName')]
        df = process_direct_provider_metadata(self.df2).fillna('Not available')
        direct_p_metas = [TableMeta.direct_provider_from_row(row) for _, row in df.iterrows()]

        p_metas = data_p_metas + direct_p_metas
        atlas = Atlas(p_metas, self.make_dummy_client())

        pf = atlas.lusid_portfolio()
        tv = pf.select('*').limit(100).to_table_var('PFS')
        slack = atlas.dev_slack_send(tv, channel='@test_channel', text='This is a test message', attach_as='excel')
        q = slack.select('*')

        sql = q.get_sql()
        self.assertSqlEqual(
            """
            @PFS = SELECT
               [AccountingMethod], [BaseCurrency], [ChildPortfolioIds], [CorporateActionSourceId], [CorporateActionSourceScope], [Created], [Description], [DisplayName], [InstrumentScopes], [OriginPortfolioCode], [OriginPortfolioScope], [ParentPortfolioCode], [ParentPortfolioScope], [PortfolioCode], [PortfolioLocation], [PortfolioScope], [PortfolioType], [SubHoldingKeys]
            FROM
               [Lusid.Portfolio]
            LIMIT 100;
            -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - --
            @dev_slack_send_1 = use Dev.Slack.Send with @PFS 
                  --channel=@test_channel
                  --text=This is a test message
                  --attachAs=excel
               enduse;
            --===========================================================================================--

            SELECT
               [Ok], [Request], [Result]
            FROM
               @dev_slack_send_1            
            """,
            sql
        )

    def test_atlas_get_item(self):

        atlas = self.make_atlas()
        pf = atlas.lusid_portfolio
        pf1 = atlas['lusid.portfolio']
        pf2 = atlas['Lusid.Portfolio']
        pf3 = atlas['lusid_portfolio']
        self.assertEqual(pf, pf1)
        self.assertEqual(pf, pf2)
        self.assertEqual(pf, pf3)

    def test_atlas_get_item_error(self):

        atlas = self.make_atlas()
        self.assertErrorsWithMessage(
            lambda: atlas['lucid.portfolio'],
            AttributeError,
            "Atlas has no provider called \'lucid.portfolio\'.\n"
            "Did you mean (case-insensitive):\n"
            "   atlas[\"Lusid.Portfolio\"]\n"
            "   atlas[\"Lusid.Portfolio.Txn\"]\n"
            "   atlas[\"Lusid.Portfolio.AtoB\"]\n"
            "   atlas[\"Lusid.PortfolioGroup\"]"
        )

    def test_atlas_list_providers(self):
        atlas = self.make_atlas()
        providers = atlas.list_providers()

        self.assertTrue(all(isinstance(p, Factory) for p in providers))
        self.assertEqual(314, len(providers))

    def test_atlas_search_positive_match(self):

        atlas = self.make_atlas()
        sub_atlas = atlas.search('lusid.*.writer')
        writers = sub_atlas.list_providers()
        self.assertEqual(36, len(writers))

        def check(x):
            name = x.meta.name.lower()
            return name.startswith('lusid') and name.endswith('writer')

        self.assertTrue(all(check(w) for w in writers))

    def test_atlas_search_negative_match(self):

        atlas = self.make_atlas()
        sub_atlas = atlas.search('~lusid*')
        writers = sub_atlas.list_providers()
        self.assertEqual(221, len(writers))

        def check(x):
            name = x.meta.name.lower()
            return not name.startswith('lusid')

        self.assertTrue(all(check(w) for w in writers))
