import os
import unittest
from pathlib import Path

import pandas as pd
import requests as r

from lumipy.provider import PandasProvider
from lumipy.provider.api_server import ApiServer
from lumipy.provider.implementation.test_providers import ParameterAndLimitTestProvider


class TestProviderApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        test = ParameterAndLimitTestProvider()

        file_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = Path(file_dir + '/../../data/context_examples')
        cls.data_dir = data_dir

        prices_df = pd.read_csv(data_dir / '..' / 'prices.csv')
        prices_df['Date'] = pd.to_datetime(prices_df.Date).dt.tz_localize(tz='utc')
        prices = PandasProvider(prices_df, 'prices')

        cls.pset = [test, prices]

    def test_provider_api_ctor_happy(self):
        api = ApiServer(*self.pset, host='127.0.0.1', port=5007)

        self.assertEqual(2, len(api.providers))
        self.assertEqual('127.0.0.1', api.host)
        self.assertEqual(5007, api.port)
        self.assertIsNone(api.thread)

        self.assertEqual('http://127.0.0.1:5007', api.base_url)

        roots = api.provider_roots

        self.assertEqual(2, len(api.provider_roots))
        # names
        self.assertSequenceEqual(['test.pyprovider.paramsandlimit', 'Pandas.prices'], [x['Name'] for x in roots])
        # api paths
        self.assertSequenceEqual(
            ['http://127.0.0.1:5007/api/v1/test-pyprovider-paramsandlimit/',  'http://127.0.0.1:5007/api/v1/pandas-prices/'],
            [x['ApiPath'] for x in roots]
        )
        # types
        self.assertSequenceEqual(['ParameterAndLimitTestProvider', 'PandasProvider'], [x['Type'] for x in roots])

    def test_provider_api_ctor_unhappy(self):
        with self.assertRaises(ValueError):
            ApiServer(host='127.0.0.1', port=5007)

        with self.assertRaises(TypeError):
            ApiServer('a', 'b', 'c', host='127.0.0.1', port=5007)

        with self.assertRaises(ValueError):
            ApiServer(*self.pset, host='A_bad_example,$', port=5000)

        with self.assertRaises(ValueError):
            ApiServer(*self.pset, host='127.0.0.1', port='abc')

    def test_provider_start_stop_and_index_endpoint(self):
        api = ApiServer(*self.pset, host='127.0.0.1', port=5007)

        api.start()

        res = r.get(api.base_url + '/api/v1/index')
        idx = res.json()

        self.assertEqual(2, len(idx))
        # names
        self.assertSequenceEqual(['test.pyprovider.paramsandlimit', 'Pandas.prices'], [x['Name'] for x in idx])
        # api paths
        self.assertSequenceEqual(
            ['http://127.0.0.1:5007/api/v1/test-pyprovider-paramsandlimit/',  'http://127.0.0.1:5007/api/v1/pandas-prices/'],
            [x['ApiPath'] for x in idx]
        )
        # types
        self.assertSequenceEqual(['ParameterAndLimitTestProvider', 'PandasProvider'], [x['Type'] for x in idx])

        api.stop()
