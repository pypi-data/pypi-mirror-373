import unittest

import pandas as pd
from lumipy.common import table_spec_to_df


class TestTableSpecToDf(unittest.TestCase):

    def test_table_spec_to_df(self):
        csv = 'Col_A,Col_B,Col_C,Col_D,Col_E\n38,-12.711890610447668,DEEBB,2022-01-11,0\n65,-3.622264732459329,DEADC,2022-04-08,0\n65,-15.693383370248654,ABACE,2022-01-07,1\n14,1.6672276061446991,FACEB,2021-11-13,0\n95,-22.538624549936014,BCADD,2021-12-23,0\n'
        metadata = [
            {'name': 'Col_A', 'type': 'Int'},
            {'name': 'Col_B', 'type': 'Double'},
            {'name': 'Col_C', 'type': 'Text'},
            {'name': 'Col_D', 'type': 'DateTime'},
            {'name': 'Col_E', 'type': 'Boolean'}
        ]
        df = table_spec_to_df(metadata, csv)
        self.assertSequenceEqual(df.shape, [5, 5])
        obs = [str(d) for d in df.dtypes]
        exp = ['Int64', 'float64', 'string', 'datetime64[ns]', 'boolean']
        self.assertSequenceEqual(exp, obs)

    def test_default_pandas_int_conversion_clash_is_fixed(self):

        csv = '''Figi,ClientInternal,LusidInstrumentId
,999999,LUID_00003D63
,123456,LUID_00003D67
0000000000123123123123123,,LUID_00003D6R
,AA0001,LUID_00003D69
,123456,LUID_00003D65
'''

        metadata = [
            {'name': 'Figi', 'type': 'Text'},
            {'name': 'ClientInternal', 'type': 'Text'},
            {'name': 'LusidInstrumentId', 'type': 'Text'},
        ]

        df = table_spec_to_df(metadata, csv)
        self.assertSequenceEqual(df.shape, [5, 3])
        figi = df.iloc[2, 0]
        self.assertEqual('0000000000123123123123123', figi)
        self.assertSequenceEqual(df.dtypes.tolist(), [pd.StringDtype()]*3)
