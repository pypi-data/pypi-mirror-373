import unittest
from lumipy.provider import ProviderManager, PandasProvider
from lumipy.provider.factory import Factory
from lumipy.provider.implementation.test_providers import ParameterAndLimitTestProvider
import os
import socket
import pandas as pd
from pathlib import Path
import requests as r
import io
import datetime as dt


def get_csv(url, context, throw_on_err=True):

    sess = r.Session()
    with sess.post(url, json=context) as res:
        res.raise_for_status()
        csv_str = '\n'.join(map(lambda x: x.decode('utf-8'), res.iter_lines()))
        sio = io.StringIO(csv_str)
        df = pd.read_csv(sio, header=None)

        err_df = df[df.iloc[:, -2] == 'error']
        if throw_on_err and err_df.shape[0] > 0:
            err = err_df.iloc[0, -1]
            raise ValueError(f'There was an error line in the data stream: {err}')

        return df


class TestProviderManager(unittest.TestCase):

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

    def test_provider_manager_ctor_defaults(self):
        mgr = ProviderManager(*self.pset, _skip_checks=True, domain='test')

        self.assertEqual('normal', mgr.run_type)

        self.assertEqual('127.0.0.1', mgr.api_server.host)
        self.assertEqual(5001, mgr.api_server.port)
        self.assertEqual(2, len(mgr.api_server.providers))

        self.assertIsInstance(mgr.factory, Factory)
        self.assertIn('127.0.0.1', mgr.factory.cmd)
        self.assertIn('5001', mgr.factory.cmd)

    def test_provider_manager_ctor_happy(self):
        mgr = ProviderManager(
            *self.pset,
            host='localhost',
            port=5050,
            run_type='python_only',
            user='007e8wfUSER',
            domain='fbn-test',
            _skip_checks=True
        )

        self.assertEqual('python_only', mgr.run_type)

        self.assertEqual('localhost', mgr.api_server.host)
        self.assertEqual(5050, mgr.api_server.port)
        self.assertEqual(2, len(mgr.api_server.providers))

        self.assertIsInstance(mgr.factory, Factory)
        self.assertIn('localhost:5050', mgr.factory.cmd)
        self.assertIn('--localRoutingUserId "007e8wfUSER"', mgr.factory.cmd)
        self.assertIn('--authClientDomain=fbn-test', mgr.factory.cmd)

    def test_provider_manager_ctor_unhappy(self):

        with self.assertRaises(ValueError):
            ProviderManager()

        with self.assertRaises(ValueError):
            ProviderManager(*self.pset, host='$(bad stuff)')

        with self.assertRaises(ValueError):
            ProviderManager(*self.pset, port='abc')

        with self.assertRaises(ValueError):
            ProviderManager(*self.pset, user='$ABC,,')

        with self.assertRaises(ValueError):
            ProviderManager(*self.pset, domain='$(bad stuff)')

        with self.assertRaises(ValueError):
            ProviderManager(*self.pset, run_type='not_a_run_type')

    def _test_pandas_provider_endpoints(self, base):
        meta = r.get(base + '/api/v1/pandas-prices/metadata').json()

        self.assertSequenceEqual(['Symbol', 'Date', 'Price', 'LogRet'], [c['Name'] for c in meta['Columns']])
        self.assertSequenceEqual(['Text', 'DateTime', 'Double', 'Double'], [c['Type'] for c in meta['Columns']])
        self.assertSequenceEqual(['', '', '', ''], [c['Description'] for c in meta['Columns']])
        self.assertSequenceEqual([False, False, False, False], [c['IsMain'] for c in meta['Columns']])
        self.assertSequenceEqual([False, False, False, False], [c['IsPrimaryKey'] for c in meta['Columns']])

        context = {
            'param_specs': {
                'Pushdown': {'name': 'Pushdown', 'data_type': 'Boolean', 'value': True}
            },
            'limit_clause': {
                'limit': 170,
                'offset': 120,
                'limitType': 'NoFilteringRequired'
            }
        }
        obs_df = get_csv(base + '/api/v1/pandas-prices/data', context, True).iloc[:-1]
        obs_df.columns = [str(c) for c in obs_df.columns]
        obs_df['5'] = obs_df['5'].astype(str)

        exp_csv = '''
0,1,2,3,4,5
,,,,is_agg,False
,,,,is_ord,False
,,,,is_offset,True
Text,DateTime,Double,Double,dtypes,"Symbol,Date,Price,LogRet"
AAPL,2022-05-30 23:00:00+00:00,147.56259155273438,-0.0053604202586763,data,
AAPL,2022-05-31 23:00:00+00:00,147.43370056152344,-0.0008738482676449,data,
AAPL,2022-06-01 23:00:00+00:00,149.9122314453125,0.0166714121351594,data,
AAPL,2022-06-02 23:00:00+00:00,144.13229370117188,-0.0393184150648275,data,
AAPL,2022-06-05 23:00:00+00:00,144.88575744628906,0.0052139681176557,data,
AAPL,2022-06-06 23:00:00+00:00,147.43370056152344,0.0174330348120124,data,
AAPL,2022-06-07 23:00:00+00:00,146.6901397705078,-0.0050561176831367,data,
AAPL,2022-06-08 23:00:00+00:00,141.41580200195312,-0.0366179682064089,data,
AAPL,2022-06-09 23:00:00+00:00,135.95309448242188,-0.0393945683869549,data,
AAPL,2022-06-12 23:00:00+00:00,130.7481689453125,-0.0390368341303828,data,
AAPL,2022-06-13 23:00:00+00:00,131.62057495117188,0.0066502526798197,data,
AAPL,2022-06-14 23:00:00+00:00,134.26766967773438,0.0199119911549265,data,
AAPL,2022-06-15 23:00:00+00:00,128.94375610351562,-0.040459032350534,data,
AAPL,2022-06-16 23:00:00+00:00,130.430908203125,0.0114673374150573,data,
AAPL,2022-06-20 23:00:00+00:00,134.7039031982422,0.0322354124654493,data,
AAPL,2022-06-21 23:00:00+00:00,134.18836975097656,-0.0038345027418316,data,
AAPL,2022-06-22 23:00:00+00:00,137.08331298828125,0.0213443077701995,data,
AAPL,2022-06-23 23:00:00+00:00,140.4442138671875,0.024221490603085,data,
AAPL,2022-06-26 23:00:00+00:00,140.4442138671875,0.0,data,
AAPL,2022-06-27 23:00:00+00:00,136.2604217529297,-0.0302424350528847,data,
AAPL,2022-06-28 23:00:00+00:00,138.0350341796875,0.0129396032568429,data,
AAPL,2022-06-29 23:00:00+00:00,135.54660034179688,-0.0181920286482446,data,
AAPL,2022-06-30 23:00:00+00:00,137.73764038085938,0.0160352238481538,data,
AAPL,2022-07-04 23:00:00+00:00,140.34506225585938,0.0187534015374559,data,
AAPL,2022-07-05 23:00:00+00:00,141.6934051513672,0.0095614841495601,data,
AAPL,2022-07-06 23:00:00+00:00,145.09396362304688,0.0237159528379029,data,
AAPL,2022-07-07 23:00:00+00:00,145.7780303955078,0.0047035675327489,data,
AAPL,2022-07-10 23:00:00+00:00,143.62667846679688,-0.0148677025087993,data,
AAPL,2022-07-11 23:00:00+00:00,144.608154296875,0.0068102776757328,data,
AAPL,2022-07-12 23:00:00+00:00,144.24136352539062,-0.0025396682078415,data,
AAPL,2022-07-13 23:00:00+00:00,147.1957550048828,0.0202753355754792,data,
AAPL,2022-07-14 23:00:00+00:00,148.88116455078125,0.0113850667832187,data,
AAPL,2022-07-17 23:00:00+00:00,145.80776977539062,-0.0208593255849161,data,
AAPL,2022-07-18 23:00:00+00:00,149.70404052734375,0.0263711730967548,data,
AAPL,2022-07-19 23:00:00+00:00,151.7265167236328,0.0134193863107796,data,
AAPL,2022-07-20 23:00:00+00:00,154.01670837402344,0.0149814242608528,data,
AAPL,2022-07-21 23:00:00+00:00,152.7675323486328,-0.0081437229385921,data,
AAPL,2022-07-24 23:00:00+00:00,151.63729858398438,-0.0074258937019635,data,
AAPL,2022-07-25 23:00:00+00:00,150.2989044189453,-0.0088654683857782,data,
AAPL,2022-07-26 23:00:00+00:00,155.4443359375,0.0336616918485184,data,
AAPL,2022-07-27 23:00:00+00:00,155.99954223632812,0.0035653735769471,data,
AAPL,2022-07-28 23:00:00+00:00,161.11526489257812,0.0322669669751922,data,
AAPL,2022-07-31 23:00:00+00:00,160.12384033203125,-0.0061725219140233,data,
AAPL,2022-08-01 23:00:00+00:00,158.63671875,-0.0093307175495551,data,
AAPL,2022-08-02 23:00:00+00:00,164.70419311523438,0.0375342955940745,data,
AAPL,2022-08-03 23:00:00+00:00,164.38694763183594,-0.0019280104651313,data,
AAPL,2022-08-04 23:00:00+00:00,164.15859985351562,-0.0013900527146795,data,
AAPL,2022-08-07 23:00:00+00:00,163.6820526123047,-0.0029071902661552,data,
AAPL,2022-08-08 23:00:00+00:00,163.731689453125,0.0003032056069942,data,
AAPL,2022-08-09 23:00:00+00:00,168.0205841064453,0.0258574482114433,data,        

'''

        exp_df = pd.read_csv(io.StringIO(exp_csv)).iloc[:-1]
        exp_df.columns = [str(c) for c in exp_df.columns]
        exp_df['5'] = exp_df['5'].astype(str)

        self.assertSequenceEqual([53, 6], obs_df.shape)

        compare = exp_df.fillna('NAN') == obs_df.fillna('NAN')
        self.assertTrue(compare.all().all())

    def _test_params_test_provider_endpoints(self, base):
        # test params provider
        meta = r.get(base + '/api/v1/test-pyprovider-paramsandlimit/metadata').json()
        self.assertSequenceEqual(['Name', 'StrValue', 'Type'], [c['Name'] for c in meta['Columns']])
        self.assertSequenceEqual(['Text', 'Text', 'Text'], [c['Type'] for c in meta['Columns']])
        self.assertSequenceEqual(['', '', ''], [c['Description'] for c in meta['Columns']])
        self.assertSequenceEqual([False, False, False], [c['IsMain'] for c in meta['Columns']])
        self.assertSequenceEqual([False, False, False], [c['IsPrimaryKey'] for c in meta['Columns']])

        self.assertSequenceEqual([f'Param{i}' for i in range(1, 7)], [p['Name'] for p in meta['Params']])
        self.assertSequenceEqual(['Int', 'Text', 'Double', 'Date', 'DateTime', 'Boolean'],
                                 [p['Type'] for p in meta['Params']])
        self.assertSequenceEqual([''] * 6, [p['Description'] for p in meta['Params']])
        self.assertSequenceEqual([0, 'ABC', 3.1415, '2022-01-01T13:15:02', None, False],
                                 [p['DefaultValue'] for p in meta['Params']])

        context = {
            'param_specs': {
                'Param1': {'name': 'Param1', 'data_type': 'Int', 'value': 12},
                'Param2': {'name': 'Param2', 'data_type': 'Text', 'value': 'ZYX'},
                'Param3': {'name': 'Param3', 'data_type': 'Double', 'value': '1.234'},
                'Param4': {'name': 'Param4', 'data_type': 'Date', 'value': dt.date(2023, 1, 1).isoformat()},
                'Param5': {'name': 'Param5', 'data_type': 'DateTime', 'value': dt.datetime(2023, 4, 1, 12, 5, 7).isoformat()},
                'Param6': {'name': 'Param6', 'data_type': 'Boolean', 'value': False},
            },
            'limit_clause': {
                'limit': 100,
                'offset': 10,
                'limitType': 'NoFilteringRequired'
            }
        }
        obs_df = get_csv(base + '/api/v1/test-pyprovider-paramsandlimit/data', context, True)
        obs_df.columns = [str(c) for c in obs_df.columns]

        exp_csv = '''
0,1,2,3,4
,,,is_agg,False
,,,is_ord,False
,,,is_offset,True
Text,Text,Text,dtypes,"Name,StrValue,Type"
Param1,12,int,data,
Param2,ZYX,str,data,
Param3,1.234,float,data,
Param4,2023-01-01 00:00:00,Timestamp,data,
Param5,2023-04-01 12:05:07,Timestamp,data,
Param6,False,bool,data,
limit,100,int,data,
offset,10,int,data,
        '''
        exp_df = pd.read_csv(io.StringIO(exp_csv))
        exp_df.columns = [str(c) for c in exp_df.columns]
        self.assertSequenceEqual([12, 5], obs_df.shape)

        compare = exp_df.fillna('NAN') == obs_df.fillna('NAN')
        self.assertTrue(compare.all().all())

    def test_provider_manager_run_python_only(self):
        mgr = ProviderManager(*self.pset, run_type='python_only', _skip_checks=True, port=5076, domain='test')

        base = mgr.api_server.base_url
        with mgr:
            res = r.get(base + '/api/v1/index')
            res.raise_for_status()
            idx = res.json()

            self.assertEqual(2, len(idx))

            # For each provider in the index test the metadata and data endpoints
            self._test_params_test_provider_endpoints(base)

            # pandas provider
            self._test_pandas_provider_endpoints(base)

            self.assertEqual(mgr.port, 5076)

    def test_provider_manager_with_in_use_port_finds_an_available_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
            test_socket.bind(('127.0.0.1', 5001))
            test_socket.listen(1)

            mgr = ProviderManager(*self.pset, run_type='python_only', _skip_checks=True, domain='test')

            base = mgr.api_server.base_url
            with mgr:
                res = r.get(base + '/api/v1/index')
                res.raise_for_status()
                idx = res.json()

                self.assertEqual(2, len(idx))

                self._test_params_test_provider_endpoints(base)

                self._test_pandas_provider_endpoints(base)

                self.assertEqual(mgr.port, 5002)

            if test_socket:
                test_socket.close()

    def test_provider_manager_with_in_use_port_and_specify_port_number_raises(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
            test_socket.bind(('127.0.0.1', 5001))
            test_socket.listen(1)

            with self.assertRaises(ValueError):
                mgr = ProviderManager(*self.pset, run_type='python_only', port=5001, _skip_checks=True, domain='test')

            if test_socket:
                test_socket.close()
