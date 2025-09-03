import unittest

from lumipy.provider import ProviderManager
from lumipy.provider.implementation.test_providers import TestProvider
from lumipy.provider.metadata import (
    ColumnMeta, ParamMeta, TableParam, DType,
    RegistrationCategory, RegistrationAttributes, LifeCycleStage, RegistrationType
)
import requests as r
import pandas as pd
import io


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


class TestBaseProvider(unittest.TestCase):

    def test_base_provider_base_ctor_defaults(self):

        p = TestProvider()
        self.assertEqual('Test.PyProvider', p.name)
        self.assertEqual(6, len(p.columns))
        self.assertEqual(8, len(p.parameters))
        self.assertEqual(1, len(p.table_parameters))

        self.assertEqual('A test provider to test the base provider class.', p.description)
        self.assertEqual('https://not-the-real-docs.com/docs', p.documentation_link)
        self.assertIsNone(p.license_code)
        self.assertEqual(p.registration_type, RegistrationType.DataProvider)
        self.assertEqual(RegistrationCategory.OtherData, p.registration_category)
        self.assertEqual(RegistrationAttributes.none, p.registration_attributes)
        self.assertEqual(LifeCycleStage.Experimental, p.lifecycle_stage)

    def test_base_provider_base_ctor_happy(self):
        name = 'Test.PyProvider.Variant1'
        descr = 'A new description'
        doclink = 'https://a-new-loc.com/other'
        license_code = 'hc-something'
        reg_cat = RegistrationCategory.Utilities
        reg_att = RegistrationAttributes.Generator
        life_cy = LifeCycleStage.Beta

        p = TestProvider(
            name=name,
            columns=[ColumnMeta('C1', DType.Int), ColumnMeta('C2', DType.Text)],
            parameters=[ParamMeta('Extra', DType.Text)],
            table_parameters=[
                TableParam('TV1', [ColumnMeta('A', DType.Int)]),
                TableParam('TV2', [ColumnMeta('C', DType.Text)])
            ],
            description=descr,
            documentation_link=doclink,
            registration_category=reg_cat,
            registration_attributes=reg_att,
            lifecycle_stage=life_cy,
            license_code=license_code
        )

        self.assertEqual(name, p.name)
        self.assertEqual(2, len(p.columns)),
        self.assertEqual(9, len(p.parameters))
        self.assertEqual(2, len(p.table_parameters))
        self.assertEqual(descr, p.description)
        self.assertEqual(doclink, p.documentation_link)
        self.assertEqual(license_code, p.license_code)
        self.assertEqual(reg_cat, p.registration_category)
        self.assertEqual(reg_att, p.registration_attributes)
        self.assertEqual(life_cy, p.lifecycle_stage)

    def test_base_provider_base_ctor_unhappy(self):

        with self.assertRaises(ValueError):
            TestProvider(name='$$@NOT,Valid')

        with self.assertRaises(TypeError):
            TestProvider(name=3)

        with self.assertRaises(TypeError):
            TestProvider(columns=[])

        with self.assertRaises(TypeError):
            TestProvider(parameters=['Not a param'])

        with self.assertRaises(TypeError):
            TestProvider(table_parameters=['Not a table param'])

        with self.assertRaises(TypeError):
            TestProvider(description=123)

        with self.assertRaises(TypeError):
            TestProvider(documentation_link=123)

        with self.assertRaises(TypeError):
            TestProvider(license_code=123)

        with self.assertRaises(TypeError):
            TestProvider(registration_category='bad')

        with self.assertRaises(TypeError):
            TestProvider(registration_attributes='xyz')

        with self.assertRaises(TypeError):
            TestProvider(lifecycle_stage='ijk')

    def test_base_provider_metadata(self):
        name = 'An.Alt.Name'
        descr = 'A new description'
        doclink = 'https://a-new-loc.com/other'
        license_code = 'hc-something'
        reg_cat = RegistrationCategory.Utilities
        reg_att = RegistrationAttributes.Generator
        life_cy = LifeCycleStage.Beta

        p = TestProvider(
            name=name,
            columns=[ColumnMeta('C1', DType.Int), ColumnMeta('C2', DType.Text)],
            parameters=[ParamMeta('Extra', DType.Text)],
            table_parameters=[
                TableParam('TV1', [ColumnMeta('A', DType.Int)]),
                TableParam('TV2', [ColumnMeta('C', DType.Text)])
            ],
            description=descr,
            documentation_link=doclink,
            license_code=license_code,
            registration_category=reg_cat,
            registration_attributes=reg_att,
            lifecycle_stage=life_cy
        )

        with ProviderManager(p, port=7465, _skip_checks=True, run_type='python_only', domain='test') as m:

            obs = r.get(m.api_server.base_url + '/api/v1/an-alt-name/metadata').json()
            exp = {
                'Name': 'An.Alt.Name',
                'Description': 'A new description',
                'DocumentationLink': 'https://a-new-loc.com/other',
                'LicenseCode': 'hc-something',
                'RegistrationType': 'DataProvider',
                'RegistrationCategory': 'Utilities',
                'RegistrationAttributes': 'Generator',
                'LifecycleStage': 'Beta',
                'Columns': [
                    {'Name': 'C1', 'Type': 'Int', 'Description': '', 'IsMain': False, 'IsPrimaryKey': False},
                    {'Name': 'C2', 'Type': 'Text', 'Description': '', 'IsMain': False, 'IsPrimaryKey': False}],
                'Params': [
                    {'Name': 'Extra', 'Type': 'Text', 'Description': '', 'DefaultValue': None},
                    {'Name': 'ProgressLinePeriod', 'Type': 'Int', 'Description': '', 'DefaultValue': None},
                    {'Name': 'SysInfoLinePeriod', 'Type': 'Int', 'Description': '', 'DefaultValue': None},
                    {'Name': 'ThrowError', 'Type': 'Boolean', 'Description': '', 'DefaultValue': None},
                    {'Name': 'SetIsAgg', 'Type': 'Boolean', 'Description': '', 'DefaultValue': False},
                    {'Name': 'SetIsOrdered', 'Type': 'Boolean', 'Description': '', 'DefaultValue': False},
                    {'Name': 'SetIsOffset', 'Type': 'Boolean', 'Description': '', 'DefaultValue': False},
                    {'Name': 'ReturnBadData', 'Type': 'Boolean', 'Description': '', 'DefaultValue': False},
                    {'Name': 'ReturnNothing', 'Type': 'Boolean', 'Description': '', 'DefaultValue': False}
                ],
                'TableParams': [
                    {'Name': 'TV1', 'Type': 'Table', 'Description': '', 'Columns': [
                        {'Name': 'A', 'Type': 'Int', 'Description': '', 'IsMain': False, 'IsPrimaryKey': False}
                    ]},
                    {'Name': 'TV2', 'Type': 'Table', 'Description': '', 'Columns': [
                        {'Name': 'C', 'Type': 'Text', 'Description': '', 'IsMain': False, 'IsPrimaryKey': False}
                    ]}
                ]
            }

            self.assertEqual(exp['Name'], obs['Name'])
            self.assertEqual(exp['Description'], obs['Description'])
            self.assertEqual(exp['DocumentationLink'], obs['DocumentationLink'])
            self.assertEqual(exp['LicenseCode'], obs['LicenseCode'])
            self.assertEqual(exp['RegistrationType'], obs['RegistrationType'])
            self.assertEqual(exp['RegistrationCategory'], obs['RegistrationCategory'])
            self.assertEqual(exp['RegistrationAttributes'], obs['RegistrationAttributes'])
            self.assertEqual(exp['LifecycleStage'], obs['LifecycleStage'])

            # Columns
            for c1, c2 in zip(exp['Columns'], obs['Columns']):
                self.assertEqual(c1['Name'], c2['Name'])
                self.assertEqual(c1['Type'], c2['Type'])
                self.assertEqual(c1['Description'], c2['Description'])
                self.assertEqual(c1['IsMain'], c2['IsMain'])
                self.assertEqual(c1['IsPrimaryKey'], c2['IsPrimaryKey'])

            # Params
            for p1, p2 in zip(exp['Params'], obs['Params']):
                self.assertEqual(p1['Name'], p2['Name'])
                self.assertEqual(p1['Type'], p2['Type'])
                self.assertEqual(p1['Description'], p2['Description'])
                self.assertEqual(p1['DefaultValue'], p2['DefaultValue'])

            # Table Params
            for tp1, tp2 in zip(exp['TableParams'], obs['TableParams']):

                self.assertEqual(tp1['Name'], tp2['Name'])
                self.assertEqual(tp1['Type'], tp2['Type'])
                self.assertEqual(tp1['Description'], tp2['Description'])

                for c1, c2 in zip(tp1['Columns'], tp2['Columns']):
                    self.assertEqual(c1['Name'], c2['Name'])
                    self.assertEqual(c1['Type'], c2['Type'])
                    self.assertEqual(c1['Description'], c2['Description'])
                    self.assertEqual(c1['IsMain'], c2['IsMain'])
                    self.assertEqual(c1['IsPrimaryKey'], c2['IsPrimaryKey'])

    def test_base_provider_get_data_empty(self):
        p = TestProvider()
        with ProviderManager(p, port=7466, _skip_checks=True, run_type='python_only', domain='test') as m:

            ctx = {
                'param_specs': {
                    'ReturnNothing': {'name': 'ReturnNothing', 'data_type': 'Boolean', 'value': 'true'},
                    'SetIsAgg': {'name': 'SetIsAgg', 'data_type': 'Boolean', 'value': 'false'},
                    'SetIsOrdered': {'name': 'SetIsOrdered', 'data_type': 'Boolean', 'value': 'false'},
                    'SetIsOffset': {'name': 'SetIsOffset', 'data_type': 'Boolean', 'value': 'false'},
                }
            }

            df = get_csv(m.api_server.base_url + '/api/v1/test-pyprovider/data', ctx)
            self.assertSequenceEqual([4, 8], df.shape)

    def test_base_provider_get_data(self):
        p = TestProvider()
        with ProviderManager(p, port=7466, _skip_checks=True, run_type='python_only', domain='test') as m:

            ctx = {
                'param_specs': {
                    'SetIsAgg': {'name': 'SetIsAgg', 'data_type': 'Boolean', 'value': 'false'},
                    'SetIsOrdered': {'name': 'SetIsOrdered', 'data_type': 'Boolean', 'value': 'false'},
                    'SetIsOffset': {'name': 'SetIsOffset', 'data_type': 'Boolean', 'value': 'false'},
                    'ProgressLinePeriod': {'name': 'ProgressLinePeriod', 'data_type': 'Int', 'value': '3'},
                    'SysInfoLinePeriod': {'name': 'SysInfoLinePeriod', 'data_type': 'Int', 'value': '4'},
                }
            }

            obs_df = get_csv(m.api_server.base_url + '/api/v1/test-pyprovider/data', ctx)
            obs_df.columns = [str(c) for c in obs_df.columns]

            exp_csv = '''
0,1,2,3,4,5,6,7
,,,,,,is_agg,False
,,,,,,is_ord,False
,,,,,,is_offset,False
Text,Int,Double,DateTime,DateTime,Boolean,dtypes,"ColA,ColB,ColC,ColD,ColE,ColF"
,,,,,,progress,Test progress 0
,,,,,,sys_info,Test sys info 0
CEEFCDEAAD,-6,-0.4598301026013887,2022-09-28,2022-05-31 22:26:52.758119,False,data,
DFBBACBDDE,1,0.8922475162688099,2022-02-26,2022-02-28 18:21:39.558486,True,data,
EBFBADBBEA,5,-1.3397222765423977,2022-02-13,2022-02-09 20:30:25.632523,False,data,
,,,,,,progress,Test progress 3
BBDBEBABFA,-4,1.0129628256599017,2022-01-19,2022-10-20 17:06:32.686157,True,data,
,,,,,,sys_info,Test sys info 4
BFDEFCCDEC,9,-0.43984813383423416,2022-08-13,2022-11-23 07:30:35.918276,False,data,
            '''

            exp_df = pd.read_csv(io.StringIO(exp_csv))
            exp_df.columns = [str(c) for c in exp_df.columns]

            self.assertSequenceEqual([13, 8], obs_df.shape)

            exp_df = exp_df.fillna(0).round(9)
            obs_df = obs_df.fillna(0).round(9)

            compare = (exp_df == obs_df)
            msg = f'''
Mismatch:

{exp_df}
  
{obs_df}

{compare}          
            '''
            self.assertTrue(compare.all().all(), msg=msg)

    def test_base_provider_get_data_error_on_bad_cols(self):
        p = TestProvider()
        with ProviderManager(p, port=7466, _skip_checks=True, run_type='python_only', domain='test') as m:

            ctx = {
                'param_specs': {
                    'ReturnBadData': {'name': 'ReturnNothing', 'data_type': 'Boolean', 'value': 'true'},
                    'SetIsAgg': {'name': 'SetIsAgg', 'data_type': 'Boolean', 'value': 'false'},
                    'SetIsOrdered': {'name': 'SetIsOrdered', 'data_type': 'Boolean', 'value': 'false'},
                    'SetIsOffset': {'name': 'SetIsOffset', 'data_type': 'Boolean', 'value': 'false'},
                }
            }

            obs_df = get_csv(m.api_server.base_url + '/api/v1/test-pyprovider/data', ctx, False)
            self.assertSequenceEqual([1, 8], obs_df.shape)

            self.assertIn(
                'ValueError: DataFrame column content from TestProvider.get_data does not match provider spec.\n  '
                'Expected: ColA, ColB, ColC, ColD, ColE, ColF\n    '
                'Actual: Bad, Cols, Some\n',
                obs_df.iloc[-1, -1]
            )

    def test_base_provider_get_data_is_agg(self):
        p = TestProvider()
        with ProviderManager(p, port=7466, _skip_checks=True, run_type='python_only', domain='test') as m:

            ctx = {
                'param_specs': {
                    'ReturnBadData': {'name': 'ReturnNothing', 'data_type': 'Boolean', 'value': 'false'},
                    'SetIsAgg': {'name': 'SetIsAgg', 'data_type': 'Boolean', 'value': 'true'},
                    'SetIsOrdered': {'name': 'SetIsOrdered', 'data_type': 'Boolean', 'value': 'false'},
                    'SetIsOffset': {'name': 'SetIsOffset', 'data_type': 'Boolean', 'value': 'false'},
                },
                'groupby_agg': {
                    'expressions': [{'op': 'StrValue', 'args': ['test'], 'alias': f'Agg{i}'} for i in range(3)],
                    'groups': [{'op': 'StrValue', 'args': ['test'], 'alias': f'Agg{i}'} for i in range(3)],
                }

            }

            obs_df = get_csv(m.api_server.base_url + '/api/v1/test-pyprovider/data', ctx, False)

            self.assertSequenceEqual([9, 8], obs_df.shape)

            exp_csv = """
0,1,2,3,4,5,6,7
,,,,,,is_agg,True
,,,,,,is_ord,False
,,,,,,is_offset,False
Double,Int,Text,dtypes,"Agg0,Agg1,Agg2",,,
0.25448229774774667,2,C,data,,,,
0.980830658283356,0,A,data,,,,
0.8214356866397223,8,F,data,,,,
0.9057396475243186,9,D,data,,,,
0.6193427462735202,8,A,data,,,,
"""
            exp_df = pd.read_csv(io.StringIO(exp_csv))
            exp_df.columns = [int(c) for c in obs_df.columns]

            self.assertSequenceEqual(exp_df.shape, obs_df.shape)

            comp = obs_df.fillna(0) == exp_df.fillna(0)
            self.assertTrue(comp.all().all())
