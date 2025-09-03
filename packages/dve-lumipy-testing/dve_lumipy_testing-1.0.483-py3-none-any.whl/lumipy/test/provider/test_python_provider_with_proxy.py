import os

import pandas as pd
from time import sleep

import lumipy.provider as lp
from lumipy.provider.provider_sets import int_test_with_proxy
from lumipy.test.test_infra import BaseIntTestWithAtlas, wait_for_providers_to_register


class TestPythonProviderIntegrationWithProxy(BaseIntTestWithAtlas):

    manager_with_proxy = None

    @classmethod
    def setUpClass(cls) -> None:

        user = os.environ.get('LUMIPY_PROVIDER_TESTS_USER')
        domain = os.environ.get('LUMIPY_PROVIDER_TESTS_DOMAIN')
        dll_path = os.environ.get('LUMIPY_PROVIDER_TESTS_DLLS')

        providers_set_with_proxy = int_test_with_proxy()
        cls.manager_with_proxy = lp.ProviderManager(*providers_set_with_proxy, user=user, domain=domain, _dev_dll_path=dll_path, whitelist_me=True, via_proxy=True)
        cls.manager_with_proxy.start()

        ready = wait_for_providers_to_register(providers_set_with_proxy)

        if not ready:
            cls.manager.stop()
            super().tearDownClass()
            raise ValueError(f'Failed, not all providers were ready in time')

        sleep(60)  # Whilst sys.registration thinks we have the providers, we may still get `No provider found` errors
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.manager_with_proxy.stop()

    def _check_provider_attr_exists(self, attr_name):
        self.assertTrue(
            hasattr(self.atlas, attr_name),
            msg=f'The expected provider \'{attr_name}\' was not found in the atlas'
        )

    def test_pandas_provider_with_proxy(self):
        self._check_provider_attr_exists('pandas_titanicproxy')

        pt = self.atlas.pandas_titanicproxy()

        df1 = pt.select('*').go()

        df2 = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv')
        df2 = df2[df1.columns]

        self.assertSequenceEqual(df1.shape, df2.shape)
        comp = df1.fillna('0') == df2.fillna('0')
        self.assertTrue(comp.all().all())

    def test_provider_metadata_base_variant_1_with_proxy(self):

        meta = self.atlas.test_pyprovider_variant1proxy.meta

        self.assertEqual('test.pyprovider.variant1proxy', meta.name.lower())
        self.assertEqual(2, len(meta.columns))
        self.assertEqual(9, len(meta.parameters))
        self.assertEqual(2, len(meta.table_parameters))

        self.assertEqual('Utilities', meta.category)
        self.assertEqual('DataProvider', meta.type)