import io
import os
import unittest
from json import load
from pathlib import Path

import pandas as pd

from lumipy.provider import PandasProvider, Context


class TestPandasProviders(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = Path(file_dir + '/../../data/context_examples')
        cls.data_dir = data_dir

        cls.iris = PandasProvider('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv', 'iris')
        cls.titanic = PandasProvider('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv', 'titanic')

        prices_df = pd.read_csv(data_dir / '..' / 'prices.csv')
        prices_df['Date'] = pd.to_datetime(prices_df.Date).dt.tz_localize(tz='utc')
        cls.prices = PandasProvider(prices_df, 'prices')

    def get_req(self, name):
        ctx_path = self.data_dir / f'{name}.json'
        with open(ctx_path, 'r') as f:
            req = load(f)
            req['param_specs']['Pushdown'] = {'name': 'Pushdown', 'data_type': 'Boolean', 'value': 'true'}

            return req

    def get_exp(self, name):
        csv_path = self.data_dir / f'{name}.csv'
        return pd.read_csv(csv_path)

    def assertDataMatchesExpected(self, prov, name, is_agg, is_ord, is_offset):
        exp_df = self.get_exp(name)
        if 'Date' in exp_df.columns:
            exp_df['Date'] = pd.to_datetime(exp_df.Date).dt.tz_localize(tz='utc')

        req = self.get_req(name)

        lines = list(prov._pipeline(req))

        sig_csv = io.StringIO('\n'.join(lines[:3]))
        sig_df = pd.read_csv(sig_csv, header=None).iloc[:, -2:]
        sig_df.columns = ['LineType', 'Message']
        sig_df = sig_df.set_index('LineType')

        self.assertEqual(str(is_agg), str(sig_df.loc['is_agg'].Message))
        self.assertEqual(str(is_ord), str(sig_df.loc['is_ord'].Message))
        self.assertEqual(str(is_offset), str(sig_df.loc['is_offset'].Message))

        dtypes_csv = io.StringIO('\n'.join(lines[3:4]))
        dtypes_df = pd.read_csv(dtypes_csv, header=None).iloc[:, -2:]
        dtypes_df.columns = ['LineType', 'Message']
        dtypes_df = dtypes_df.set_index('LineType')

        cols = dtypes_df.loc['dtypes'].Message.split(',')
        obs_csv = io.StringIO(lines[4])
        obs_df = pd.read_csv(obs_csv, header=None).iloc[:, :-2]
        obs_df.columns = cols

        exp_df = exp_df[cols]

        self.assertSequenceEqual(exp_df.shape, obs_df.shape)

        compare = exp_df.round(9).fillna('NA') == obs_df.round(9).fillna('NA')
        self.assertTrue(compare.all().all())

    def test_iris_no_filter(self):
        self.assertDataMatchesExpected(self.iris, 'test_iris_no_filter', False, False, False)

    def test_iris_no_filter_limit(self):
        self.assertDataMatchesExpected(self.iris, 'test_iris_no_filter_limit', False, False, False)

    def test_iris_no_filter_limit_offset(self):
        self.assertDataMatchesExpected(self.iris, 'test_iris_no_filter_limit_offset', False, False, True)

    def test_iris_join_filter(self):
        self.assertDataMatchesExpected(self.iris, 'test_iris_join_filter', False, False, False)

    def test_titanic_op_and(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_and', False, False, False)

    def test_titanic_op_or(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_or', False, False, False)

    def test_titanic_op_concat(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_concat', False, False, False)

    def test_titanic_op_eq(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_eq', False, False, False)

    def test_titanic_op_glob(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_glob', False, False, False)

    def test_titanic_op_gt(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_gt', False, False, False)

    def test_titanic_op_gte(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_gte', False, False, False)

    def test_titanic_op_in(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_in', False, False, False)

    def test_titanic_op_is_between(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_is_between', False, False, False)

    def test_titanic_op_is_not_between(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_is_not_between', False, False, False)

    def test_titanic_op_is_not_null(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_is_not_null', False, False, False)

    def test_titanic_op_is_null(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_is_null', False, False, False)

    def test_titanic_op_len(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_len', False, False, False)

    def test_titanic_op_like(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_like', False, False, False)

    def test_titanic_op_lower(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_lower', False, False, False)

    def test_titanic_op_lt(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_lt', False, False, False)

    def test_titanic_op_lte(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_lte', False, False, False)

    def test_titanic_op_neq(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_neq', False, False, False)

    def test_titanic_op_not(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_not', False, False, False)

    def test_titanic_op_not_glob(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_not_glob', False, False, False)

    def test_titanic_op_not_in(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_not_in', False, False, False)

    def test_titanic_op_not_like(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_not_like', False, False, False)

    def test_titanic_op_replace(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_replace', False, False, False)

    def test_titanic_op_substr(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_substr', False, False, False)

    def test_titanic_op_upper(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_op_upper', False, False, False)

    # Boolean column
    def test_titanic_single_bool_column(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_single_bool_column', False, False, False)

    # Numeric functions
    def test_titanic_numeric_abs(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_abs', False, False, False)

    def test_titanic_numeric_add(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_add', False, False, False)

    def test_titanic_numeric_ceil(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_ceil', False, False, False)

    def test_titanic_numeric_exp(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_exp', False, False, False)

    def test_titanic_numeric_floor(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_floor', False, False, False)

    def test_titanic_numeric_flooordiv(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_floordiv', False, False, False)

    def test_titanic_numeric_log(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_log', False, False, False)

    def test_titanic_numeric_log10(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_log10', False, False, False)

    def test_titanic_numeric_mod(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_mod', False, False, False)

    def test_titanic_numeric_multiply(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_multiply', False, False, False)

    def test_titanic_numeric_power(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_power', False, False, False)

    def test_titanic_numeric_round(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_round', False, False, False)

    def test_titanic_numeric_sign(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_sign', False, False, False)

    def test_titanic_numeric_sub(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_sub', False, False, False)

    def test_titanic_numeric_truediv(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_numeric_truediv', False, False, False)

    # Literal values
    def test_titanic_literal_bool(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_literal_bool', False, False, False)

    def test_titanic_literal_float(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_literal_float', False, False, False)

    def test_titanic_literal_int(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_literal_int', False, False, False)

    def test_titanic_literal_list(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_literal_list', False, False, False)

    def test_titanic_literal_str(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_literal_str', False, False, False)

    def test_prices_literal_date(self):
        self.assertDataMatchesExpected(self.prices, 'test_prices_literal_date', False, False, False)

    # Datetime fns
    def test_prices_dt_date_str(self):
        self.assertDataMatchesExpected(self.prices, 'test_prices_dt_date_str', False, False, False)

    def test_prices_dt_day_name(self):
        self.assertDataMatchesExpected(self.prices, 'test_prices_dt_day_name', False, False, False)

    def test_prices_dt_day_of_month(self):
        self.assertDataMatchesExpected(self.prices, 'test_prices_dt_day_of_month', False, False, False)

    def test_prices_dt_day_of_week(self):
        self.assertDataMatchesExpected(self.prices, 'test_prices_dt_day_of_week', False, False, False)

    def test_prices_dt_day_of_year(self):
        self.assertDataMatchesExpected(self.prices, 'test_prices_dt_day_of_year', False, False, False)

    def test_prices_dt_julian_day(self):
        self.assertDataMatchesExpected(self.prices, 'test_prices_dt_julian_day', False, False, False)

    # Aggregations
    def test_titanic_agg_simple_group_count(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_simple_count', True, False, False)

    def test_titanic_agg_complex_group_count(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_complex_group_count', True, False, False)

    def test_titanic_agg_simple_group_complex_aggs(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_simple_group_complex_aggs', True, False, False)

    def test_titanic_agg_simple_group_mixed_scalars_and_aggs(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_simple_group_mixed_scalars_and_aggs', True, False, False)

    def test_titanic_agg_partial_group_translation_applies_no_aggs(self):
        req = self.get_req('test_titanic_partial_group_translation_applies_no_aggs')
        ctx = Context.parse_obj(req)
        df = ctx.pandas.apply(self.titanic.df, False)
        self.assertSequenceEqual([891, 15], df.shape)

    def test_titanic_agg_partial_agg_translation_applies_no_aggs(self):
        req = self.get_req('test_titanic_partial_agg_translation_applies_no_aggs')
        ctx = Context.parse_obj(req)
        df = ctx.pandas.apply(self.titanic.df, False)
        self.assertSequenceEqual([891, 15], df.shape)

    def test_titanic_agg_partial_where_applies_no_aggs(self):
        json_str = '''
{
  "param_specs": {
    "UsePandasFilter": {
      "name": "UsePandasFilter",
      "data_type": "Boolean",
      "value": "True"
    }
  },
  "distinct": false,
  "where_clause": {
    "op": "IsNotTranslatable",
    "args": [
      {
        "op": "ColValue",
        "args": [
          "deck"
        ],
        "alias": null
      }
    ],
    "alias": null
  },
  "groupby_agg": {
    "expressions": [
      {
        "op": "ColValue",
        "args": [
          "deck"
        ],
        "alias": null
      },
      {
        "op": "ColValue",
        "args": [
          "class"
        ],
        "alias": null
      },
      {
        "op": "ColValue",
        "args": [
          "sex"
        ],
        "alias": null
      },
      {
        "op": "Count",
        "args": [
          {
            "op": "ColValue",
            "args": [
              "deck"
            ],
            "alias": null
          }
        ],
        "alias": "N"
      }
    ],
    "groups": [
      {
        "op": "ColValue",
        "args": [
          "deck"
        ],
        "alias": null
      },
      {
        "op": "ColValue",
        "args": [
          "class"
        ],
        "alias": null
      },
      {
        "op": "ColValue",
        "args": [
          "sex"
        ],
        "alias": null
      }
    ]
  },
  "orderby_clause": [],
  "limit_clause": {
    "limit": null,
    "offset": null,
    "limitType": "NoFilteringRequired"
  },
  "is_agg": false,
  "is_ordered": false,
  "is_offset": false
}        
        '''

        ctx = Context.parse_raw(json_str)
        df = ctx.pandas.apply(self.titanic.df, False)

        self.assertSequenceEqual([891, 15], df.shape)

    def test_titanic_agg_min(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_min', True, False, False)

    def test_titanic_agg_max(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_max', True, False, False)

    def test_titanic_agg_sum(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_sum', True, False, False)

    def test_titanic_agg_count(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_count', True, False, False)

    def test_titanic_agg_median(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_median', True, False, False)

    def test_titanic_agg_quantile(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_quantile', True, False, False)

    def test_titanic_agg_stdev(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_stdev', True, False, False)

    def test_titanic_agg_prod(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_prod', True, False, False)

    def test_titanic_agg_covariance(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_covariance', True, False, False)

    def test_titanic_agg_coef_of_variation(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_coef_of_variation', True, False, False)

    def test_titanic_agg_group_concat(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_agg_group_concat', True, False, False)

    def test_titanic_agg_no_groups(self):
        json_str = '''
{
  "param_specs": {
    "UsePandasFilter": {
      "name": "UsePandasFilter",
      "data_type": "Boolean",
      "value": "True"
    }
  },
  "distinct": false,
  "where_clause": null,
  "groupby_agg": {
    "expressions": [
      {
        "op": "Total",
        "args": [
          {
            "op": "ColValue",
            "args": [
              "fare"
            ],
            "alias": null
          }
        ],
        "alias": "FareSum"
      }
    ],
    "groups": []
  },
  "orderby_clause": [],
  "limit_clause": {
    "limit": null,
    "offset": null,
    "limitType": "NoFilteringRequired"
  },
  "is_agg": false,
  "is_ordered": false,
  "is_offset": false
}        
'''

        ctx = Context.parse_raw(json_str)
        df = ctx.pandas.apply(self.titanic.df, False)

        self.assertSequenceEqual([1, 1], df.shape)

    def test_titanic_order_by_no_aggs_with_limit(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_order_by_no_aggs_with_limit', False, True, False)

    def test_titanic_order_by_aggs_and_groups(self):
        self.assertDataMatchesExpected(self.titanic, 'test_titanic_order_by_aggs_and_groups', True, True, False)

    def test_titanic_order_by_cols_partial_translation(self):

        json_str = '''
             {
              "param_specs": {
                "Pushdown": {
                  "name": "Pushdown",
                  "data_type": "Boolean",
                  "value": "True"
                },
                "TestCaseName": {
                  "name": "TestCaseName",
                  "data_type": "Text",
                  "value": "order_by_no_aggs_with_limit"
                }
              },
              "distinct": false,
              "where_clause": {
                "op": "Lt",
                "args": [
                  {
                    "op": "ColValue",
                    "args": [
                      "age"
                    ],
                    "alias": null
                  },
                  {
                    "op": "NumValue",
                    "args": [
                      "30.0"
                    ],
                    "alias": null
                  }
                ],
                "alias": null
              },
              "groupby_agg": null,
              "orderby_clause": [
                {
                  "op": "Desc",
                  "args": [
                    {
                      "op": "ColValue",
                      "args": [
                        "embark_town"
                      ],
                      "alias": null
                    }
                  ],
                  "alias": null
                },
                {
                  "op": "Asc",
                  "args": [
                    {
                      "op": "ColValue",
                      "args": [
                        "fare"
                      ],
                      "alias": null
                    }
                  ],
                  "alias": null
                },
                {
                  "op": "Asc",
                  "args": [
                    {
                      "op": "NotSupported",
                      "args": [
                        {
                          "op": "ColValue",
                          "args": [
                            "fare"
                          ],
                          "alias": null
                        },
                        {
                          "op": "NumValue",
                          "args": [
                            "2.0"
                          ],
                          "alias": null
                        }
                      ],
                      "alias": null
                    }
                  ],
                  "alias": null
                }
              ],
              "limit_clause": {
                "limit": 20,
                "offset": null,
                "limitType": "FilteringAndOrderingRequired"
              },
              "is_agg": false,
              "is_ordered": false,
              "is_offset": false
            }       
        '''

        ctx = Context.parse_raw(json_str)
        df = ctx.pandas.apply(self.titanic.df, False)

        self.assertSequenceEqual([384, 15], df.shape)

    def test_titanic_order_by_aggs_partial_translation(self):

        json_str = '''
             {
              "param_specs": {
                "Pushdown": {
                  "name": "Pushdown",
                  "data_type": "Boolean",
                  "value": "True"
                },
                "TestCaseName": {
                  "name": "TestCaseName",
                  "data_type": "Text",
                  "value": "order_by_aggs_and_groups"
                }
              },
              "distinct": false,
              "where_clause": null,
              "groupby_agg": {
                "expressions": [
                  {
                    "op": "ColValue",
                    "args": [
                      "embark_town"
                    ],
                    "alias": null
                  },
                  {
                    "op": "ColValue",
                    "args": [
                      "deck"
                    ],
                    "alias": null
                  },
                  {
                    "op": "Count",
                    "args": [
                      {
                        "op": "ColValue",
                        "args": [
                          "fare"
                        ],
                        "alias": null
                      }
                    ],
                    "alias": "NPeople"
                  }
                ],
                "groups": [
                  {
                    "op": "ColValue",
                    "args": [
                      "embark_town"
                    ],
                    "alias": null
                  },
                  {
                    "op": "ColValue",
                    "args": [
                      "deck"
                    ],
                    "alias": null
                  }
                ]
              },
              "orderby_clause": [
                {
                  "op": "Asc",
                  "args": [
                    {
                      "op": "ColValue",
                      "args": [
                        "deck"
                      ],
                      "alias": null
                    }
                  ],
                  "alias": null
                },
                {
                  "op": "Asc",
                  "args": [
                    {
                      "op": "NotAvailable",
                      "args": [
                        {
                          "op": "ColValue",
                          "args": [
                            "fare"
                          ],
                          "alias": null
                        }
                      ],
                      "alias": null
                    }
                  ],
                  "alias": null
                }
              ],
              "limit_clause": {
                "limit": null,
                "offset": null,
                "limitType": "NoFilteringRequired"
              },
              "is_agg": false,
              "is_ordered": false,
              "is_offset": false
            }       
        '''

        ctx = Context.parse_raw(json_str)
        df = ctx.pandas.apply(self.titanic.df, False)

        self.assertSequenceEqual([891, 15], df.shape)
