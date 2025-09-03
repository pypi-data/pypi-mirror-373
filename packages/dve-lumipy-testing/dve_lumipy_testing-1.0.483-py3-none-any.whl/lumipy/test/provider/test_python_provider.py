import datetime as dt
import io
import os

import numpy as np
import pandas as pd
from time import sleep

import lumipy as lm
import lumipy.provider as lp
from lumipy.provider.provider_sets import int_test
from lumipy.test.test_infra import BaseIntTestWithAtlas, wait_for_providers_to_register
from lumipy import LumiError


class TestPythonProviderIntegration(BaseIntTestWithAtlas):

    manager = None
    df = None

    @classmethod
    def setUpClass(cls) -> None:

        user = os.environ.get('LUMIPY_PROVIDER_TESTS_USER')
        domain = os.environ.get('LUMIPY_PROVIDER_TESTS_DOMAIN')
        dll_path = os.environ.get('LUMIPY_PROVIDER_TESTS_DLLS')

        providers = int_test()
        cls.manager = lp.ProviderManager(*providers, user=user, domain=domain, _dev_dll_path=dll_path, whitelist_me=True)
        cls.manager.start()

        ready = wait_for_providers_to_register(providers)
            
        if not ready:
            cls.manager.stop()
            super().tearDownClass()
            raise ValueError(f'Failed, not all providers were ready in time')

        sleep(60)  # Whilst sys.registration thinks we have the providers, we may still get `No provider found` errors
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.manager.stop()

    def _check_provider_attr_exists(self, attr_name):
        self.assertTrue(
            hasattr(self.atlas, attr_name),
            msg=f'The expected provider \'{attr_name}\' was not found in the atlas'
        )

    def test_pandas_provider(self):
        self._check_provider_attr_exists('pandas_titanic')

        pt = self.atlas.pandas_titanic()

        df1 = pt.select('*').go()

        df2 = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv')
        df2 = df2[df1.columns]

        self.assertSequenceEqual(df1.shape, df2.shape)
        comp = df1.fillna('0') == df2.fillna('0')
        self.assertTrue(comp.all().all())

    def test_filter_pushdown(self):

        self._check_provider_attr_exists('test_filter_pyprovider')

        f = self.atlas.test_filter_pyprovider()
        df = f.select('*').where(f.node_id * 2 >= 0).go()

        self.assertSequenceEqual(df.shape, [5, 3])
        self.assertSequenceEqual(df.OpName.tolist(), ['Gte', 'Multiply', 'ColValue', 'NumValue', 'NumValue'])

    def _make_tablevar(self, n_rows, n_cols):

        def random_val(i):
            if i % 4 == 0:
                return np.random.uniform()
            elif i % 4 == 1:
                return np.random.choice(list('zyxwv'))
            elif i % 4 == 2:
                return dt.datetime(2020, 1, 1) + dt.timedelta(days=np.random.randint(0, 100))
            elif i % 4 == 3:
                return np.random.randint(100)

        df = pd.DataFrame([
            {f'Col{i}': random_val(i) for i in range(n_cols)}
            for _ in range(n_rows)
        ])
        return lm.from_pandas(df)

#     def test_table_parameter_input(self):
# 
#         self._check_provider_attr_exists('test_tableparam_pyprovider')
# 
#         tv1 = self._make_tablevar(3, 5)
#         tv2 = self._make_tablevar(5, 3)
#         tv3 = self._make_tablevar(2, 9)
# 
#         p = self.atlas.test_tableparam_pyprovider(test_table1=tv1, test_table2=tv2, test_table3=tv3)
# 
#         df1 = p.select('*').go()
# 
#         csv = '''
# TableVarColName,TableVarColType,TableVarName,TableVarNumCols,TableVarNumRows
# Col0,float64,TestTable1,5,3
# Col1,string,TestTable1,5,3
# Col2,datetime64[ns],TestTable1,5,3
# Col3,Int64,TestTable1,5,3
# Col4,float64,TestTable1,5,3
# Col0,float64,TestTable2,3,5
# Col1,string,TestTable2,3,5
# Col2,datetime64[ns],TestTable2,3,5
# Col0,float64,TestTable3,9,2
# Col1,string,TestTable3,9,2
# Col2,datetime64[ns],TestTable3,9,2
# Col3,Int64,TestTable3,9,2
# Col4,float64,TestTable3,9,2
# Col5,string,TestTable3,9,2
# Col6,datetime64[ns],TestTable3,9,2
# Col7,Int64,TestTable3,9,2
# Col8,float64,TestTable3,9,2
#         '''
#         df2 = pd.read_csv(io.StringIO(csv))
# 
#         self.assertSequenceEqual(df1.shape, df2.shape)
# 
#         comp = df1 == df2
#         self.assertTrue(comp.all().all())

    def test_provider_metadata_titanic(self):

        meta = self.atlas.pandas_titanic.meta

        self.assertEqual('pandas.titanic', meta.name.lower())
        self.assertEqual(15, len(meta.columns))
        self.assertEqual(1, len(meta.parameters))
        self.assertEqual(0, len(meta.table_parameters))

        self.assertEqual('OtherData', meta.category)
        self.assertEqual('DataProvider', meta.type)

    def test_provider_metadata_base_variant_1(self):

        meta = self.atlas.test_pyprovider_variant1.meta

        self.assertEqual('test.pyprovider.variant1', meta.name.lower())
        self.assertEqual(2, len(meta.columns))
        self.assertEqual(9, len(meta.parameters))
        self.assertEqual(2, len(meta.table_parameters))

        self.assertEqual('Utilities', meta.category)
        self.assertEqual('DataProvider', meta.type)

    def test_provider_metadata_filter_provider(self):

        meta = self.atlas.test_filter_pyprovider.meta

        self.assertEqual('test.filter.pyprovider', meta.name.lower())
        self.assertEqual(3, len(meta.columns))
        self.assertEqual(0, len(meta.parameters))
        self.assertEqual(0, len(meta.table_parameters))

        self.assertEqual('OtherData', meta.category)
        self.assertEqual('DataProvider', meta.type)

    def test_provider_metadata_tableparam_provider(self):

        meta = self.atlas.test_tableparam_pyprovider.meta

        self.assertEqual('test.tableparam.pyprovider', meta.name.lower())
        self.assertEqual(5, len(meta.columns))
        self.assertEqual(0, len(meta.parameters))
        self.assertEqual(3, len(meta.table_parameters))

        self.assertEqual('OtherData', meta.category)
        self.assertEqual('DataProvider', meta.type)

    def test_provider_get_empty(self):

        p = self.atlas.test_pyprovider_variant1(return_nothing=True)

        df = p.select('*').go()
        self.assertSequenceEqual([0, 2], df.shape)

    def test_provider_get_data_progress_messages_and_data(self):
        p = self.atlas.test_pyprovider_variant1(progress_line_period=2)
        job = p.select('*').go_async()
        job.wait()
        job.get_status()

        lines = [line for line in job._progress_lines if '>> Test progress' in line]
        obs = [line.split('>>')[-1].strip() for line in lines]
        exp = [f'Test progress {i}' for i in range(0, 5, 2)]
        self.assertSequenceEqual(exp, obs)

        df1 = job.get_result()
        self.assertSequenceEqual([5, 2], df1.shape)
        csv = '''
C1,C2
0,EEFCDEAADE
-1,BCDCDFBBAC
-7,DEDAFAEEBF
7,ADBBEADFAD
-4,BBBDBEBABF
        '''
        df2 = pd.read_csv(io.StringIO(csv))
        comp = df1 == df2
        self.assertTrue(comp.all().all())

    def test_provider_error_bad_dataframe_from_get_data(self):

        p = self.atlas.test_pyprovider_variant1(return_bad_data=True)

        with self.assertRaises(LumiError) as le:
            p.select('*').go()
        ex = str(le.exception)
        self.assertIn('does not match provider spec', ex)

    def test_provider_error_thrown_by_get_data(self):

        p = self.atlas.test_pyprovider_variant1(throw_error=True)

        with self.assertRaises(LumiError) as le:
            p.select('*').limit(10).go()

        ex = str(le.exception)
        self.assertIn('test error after 5 steps', ex)

    def test_provider_identity_info_passed_down(self):

        p = self.atlas.test_identity_context()

        df = p.select('*').go()
        self.assertSequenceEqual([9, 2], df.shape)

        df = df.set_index('Name')

        user_id = df.loc['user_id'].iloc[0]
        self.assertFalse(pd.isna(user_id))
        self.assertGreater(len(user_id), 0)

        client_id = df.loc['client_id'].iloc[0]
        self.assertFalse(pd.isna(client_id))
        self.assertGreater(len(client_id), 0)

        client_domain = df.loc['client_domain'].iloc[0]
        self.assertFalse(pd.isna(client_domain))
        self.assertGreater(len(client_domain), 0)

        company_domain = df.loc['company_domain'].iloc[0]
        self.assertFalse(pd.isna(company_domain))
        self.assertGreater(len(company_domain), 0)

        actual_user_id = df.loc['actual_user_id'].iloc[0]
        self.assertFalse(pd.isna(actual_user_id))
        self.assertGreater(len(actual_user_id), 0)

        access_token = df.loc['access_token'].iloc[0]
        self.assertFalse(pd.isna(access_token))
        self.assertGreater(len(access_token), 0)
