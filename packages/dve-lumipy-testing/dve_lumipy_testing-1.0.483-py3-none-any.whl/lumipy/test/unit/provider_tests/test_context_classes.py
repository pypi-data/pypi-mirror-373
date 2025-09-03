import unittest

import pandas as pd

from lumipy.common import table_spec_to_df
from lumipy.provider.common import expression_to_table_spec
from lumipy.provider.context import Context, Expression, ParamVal, Limit

table_spec_str = '''{
    "op": "TableSpec",
    "args": [
      {
        "op": "TableMeta",
        "args": [
          {
            "op": "ColSpec",
            "args": [
              "species",
              "Text"
            ]
          },
          {
            "op": "ColSpec",
            "args": [
              "petal_length",
              "Double"
            ]
          }
        ]
      },
      {
        "op": "TableContent",
        "args": [
          "species,petal_length\\nvirginica,6\\nvirginica,5.1\\nvirginica,5.9\\nvirginica,5.6\\nvirginica,5.8\\nvirginica,6.6\\nvirginica,4.5\\nvirginica,6.3\\nvirginica,6.1\\nvirginica,5.3\\nvirginica,5.5\\nvirginica,5\\nvirginica,6.7\\nvirginica,6.9\\nvirginica,5.7\\nvirginica,4.9\\nvirginica,4.8\\nvirginica,6.4\\nvirginica,5.4\\nvirginica,5.2\\n"
        ]
      }
    ]
  }'''


class TestExpression(unittest.TestCase):

    def test_expression_string_literal(self):
        expr = Expression.parse_raw('{"op": "StrValue", "args": ["-10"]}')

        self.assertEqual("StrValue", expr.op)
        self.assertEqual("-10", expr.args[0])
        self.assertTrue(expr.is_leaf())
        self.assertFalse(expr.is_logic_op())

    def test_expression_date_literal(self):
        expr = Expression.parse_raw('{"op": "DateValue", "args": ["2022-05-05T00:00:00Z"]}')

        self.assertEqual("DateValue", expr.op)
        self.assertEqual("2022-05-05T00:00:00Z", expr.args[0])
        self.assertTrue(expr.is_leaf())
        self.assertFalse(expr.is_logic_op())

    def test_expression_bool_literal(self):
        expr = Expression.parse_raw('{"op": "BoolValue", "args": [true]}')

        self.assertEqual("BoolValue", expr.op)
        self.assertTrue(expr.args[0])
        self.assertTrue(expr.is_leaf())
        self.assertFalse(expr.is_logic_op())

    def test_expression_num_literal(self):
        expr = Expression.parse_raw('{"op": "NumValue", "args": [9]}')

        self.assertEqual("NumValue", expr.op)
        self.assertEqual(9, expr.args[0])
        self.assertTrue(expr.is_leaf())
        self.assertFalse(expr.is_logic_op())

        expr = Expression.parse_raw('{"op": "NumValue", "args": [3.14]}')

        self.assertEqual("NumValue", expr.op)
        self.assertEqual(3.14, expr.args[0])
        self.assertTrue(expr.is_leaf())
        self.assertFalse(expr.is_logic_op())

    def test_expression_table_spec_and_expression_args(self):
        expr = Expression.parse_raw(table_spec_str)

        spec = expression_to_table_spec(*expr.args)
        df = table_spec_to_df(*spec)

        self.assertSequenceEqual([20, 2], df.shape)
        self.assertSequenceEqual(['string', 'float64'], [str(t) for t in df.dtypes.tolist()])
        self.assertTrue(expr.is_leaf())
        self.assertFalse(expr.is_logic_op())

    def test_expression_column_value(self):
        jstr = '{"op": "ColValue", "args": ["age"]}'
        expr = Expression.parse_raw(jstr)

        self.assertEqual("ColValue", expr.op)
        self.assertEqual('age', expr.args[0])
        self.assertTrue(expr.is_leaf())
        self.assertFalse(expr.is_logic_op())

    def test_expression_is_logic_op(self):
        ops = [
            'And', 'Or',
            'Gt', 'Lt', 'Gte', 'Lte',
            'Eq', 'Neq',
            'In', 'NotIn',
            'Between', 'NotBetween',
            'Like', 'NotLike', 'Glob', 'NotGlob',
            'Regexp', 'NotRegexp',
        ]
        for op in ops:
            expr = Expression.parse_obj({'op': op, 'args': ['testing']})
            self.assertTrue(expr.is_logic_op())
            self.assertFalse(expr.is_leaf())


class TestParamVal(unittest.TestCase):

    def test_param_val_int(self):
        expr = ParamVal.parse_obj({'name': 'MyIntParam', 'data_type': 'Int', 'value': '1989'})
        self.assertEqual('MyIntParam', expr.name)
        self.assertEqual('Int', expr.data_type)
        self.assertEqual('1989', expr.value)
        self.assertEqual(1989, expr.get())

    def test_param_val_float(self):
        expr = ParamVal.parse_obj({'name': 'MyFloatParam', 'data_type': 'Double', 'value': '1.128963'})
        self.assertEqual('MyFloatParam', expr.name)
        self.assertEqual('Double', expr.data_type)
        self.assertEqual('1.128963', expr.value)
        self.assertEqual(1.128963, expr.get())

    def test_param_val_string(self):
        expr = ParamVal.parse_obj({'name': 'MyTextParam', 'data_type': 'Text', 'value': 'ABC'})
        self.assertEqual('MyTextParam', expr.name)
        self.assertEqual('Text', expr.data_type)
        self.assertEqual('ABC', expr.value)
        self.assertEqual('ABC', expr.get())

    def test_param_val_bool(self):
        expr = ParamVal.parse_obj({'name': 'MyBoolParam', 'data_type': 'Boolean', 'value': 'TRUE'})
        self.assertEqual('MyBoolParam', expr.name)
        self.assertEqual('Boolean', expr.data_type)
        self.assertEqual('TRUE', expr.value)
        self.assertEqual(True, expr.get())

    def test_param_val_date(self):
        expr = ParamVal.parse_obj({'name': 'MyDateParam', 'data_type': 'Date', 'value': '2022-01-12'})
        self.assertEqual('MyDateParam', expr.name)
        self.assertEqual('Date', expr.data_type)
        self.assertEqual('2022-01-12', expr.value)
        self.assertEqual(pd.to_datetime('2022-01-12'), expr.get())

    def test_param_val_datetime(self):
        expr = ParamVal.parse_obj({'name': 'MyDateTimeParam', 'data_type': 'DateTime', 'value': '2022-01-12T13:24:11'})
        self.assertEqual('MyDateTimeParam', expr.name)
        self.assertEqual('DateTime', expr.data_type)
        self.assertEqual('2022-01-12T13:24:11', expr.value)
        self.assertEqual(pd.to_datetime('2022-01-12T13:24:11'), expr.get())

    def test_param_val_table(self):
        expr = ParamVal(
            name='MyTableParam',
            data_type='Table',
            value=Expression.parse_raw(table_spec_str)
        )
        self.assertEqual('MyTableParam', expr.name)
        self.assertEqual('Table', expr.data_type)

        df = expr.get()
        self.assertSequenceEqual([20, 2], df.shape)


class TestLimit(unittest.TestCase):

    def test_limit_limit_type_validation(self):
        with self.assertRaises(ValueError):
            Limit(limit=10, offset=10, limitType='bad')

    def test_limit_requirement_methods(self):

        lim = Limit(limit=10, offset=10, limitType='NoFilteringRequired')
        self.assertFalse(lim.requires_filter_only())
        self.assertFalse(lim.requires_filter_and_order())
        self.assertFalse(lim.has_requirements())

        lim = Limit(limit=10, offset=10, limitType='FilteringRequired')
        self.assertTrue(lim.requires_filter_only())
        self.assertFalse(lim.requires_filter_and_order())
        self.assertTrue(lim.has_requirements())

        lim = Limit(limit=10, offset=10, limitType='FilteringAndOrderingRequired')
        self.assertFalse(lim.requires_filter_only())
        self.assertTrue(lim.requires_filter_and_order())
        self.assertTrue(lim.has_requirements())


ctx_json = '''{
  "where_clause": {
    "op": "Gt",
    "args": [
      {
        "op": "ColValue",
        "args": [
          "Date"
        ]
      },
      {
        "op": "DateValue",
        "args": [
          "2022-05-05T00:00:00Z"
        ]
      }
    ]
  },
  "param_specs": {
    "TestCaseName": {
      "name": "TestCaseName",
      "data_type": "Text",
      "value": "literal_date"
    },
    "UsePandasFilter": {
      "name": "UsePandasFilter",
      "data_type": "Boolean",
      "value": "True"
    }
  },
  "limit_clause": {
    "limit": null,
    "offset": null,
    "limitType": "NoFilteringRequired"
  },
  "is_agg": false,
  "is_ordered": false,
  "is_offset": false
}'''


class TestContext(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = Context.parse_raw(ctx_json)

    def test_context_get_method(self):

        upf = self.ctx.get('UsePandasFilter')
        self.assertTrue(upf)

        name = self.ctx.get('TestCaseName')
        self.assertEqual('literal_date', name)

    def test_context_limit_method(self):

        self.assertIsNone(self.ctx.limit())
        self.assertIsNone(self.ctx.offset())

        self.ctx.limit_clause.limit = 100
        self.ctx.limit_clause.offset = 50
        self.assertEqual(100, self.ctx.limit())
        self.assertEqual(50, self.ctx.offset())

    def test_context_can_set_flags(self):
        # Assert defaults
        ctx = Context.parse_raw(ctx_json)
        self.assertFalse(ctx.is_agg)
        self.assertFalse(ctx.is_ordered)
        self.assertFalse(ctx.is_offset)

        # Can be set to true
        ctx.is_agg = True
        self.assertTrue(ctx.is_agg)
        ctx.is_ordered = True
        self.assertTrue(ctx.is_ordered)
        ctx.is_offset = True
        self.assertTrue(ctx.is_offset)


