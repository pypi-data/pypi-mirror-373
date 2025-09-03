import unittest
from lumipy.lumiflex._method_tools.constraints import UnaryCheck, Is, VariadicCheck, Are
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._metadata.field import ColumnMeta
from lumipy.lumiflex._column.make import make
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
import numpy as np
import pandas as pd
import datetime as dt


class TestIsConstraint(SqlTestCase):

    def test_is_constraint_ctor(self):
        c1 = UnaryCheck(True, DType.Date, DType.DateTime)
        self.assertTrue(c1.trigger)
        self.assertEqual((DType.Date, DType.DateTime), c1.dtypes)
        self.assertEqual('must be Date/DateTime', c1.msg)

        c2 = UnaryCheck(False, DType.Date, DType.DateTime)
        self.assertFalse(c2.trigger)
        self.assertEqual((DType.Date, DType.DateTime), c2.dtypes)
        self.assertEqual('must not be Date/DateTime', c2.msg)

    def test_is_constraint_call(self):
        d_col = self.make_date_col('d')
        dt_col = self.make_datetime_col('dt')
        txt_col = self.make_text_col('txt')
        c1 = UnaryCheck(True, DType.Date, DType.DateTime)
        self.assertTrue(c1(d_col))
        self.assertTrue(c1(dt_col))
        self.assertFalse(c1(txt_col))

        c2 = UnaryCheck(False, DType.Date, DType.DateTime)
        self.assertFalse(c2(d_col))
        self.assertFalse(c2(dt_col))
        self.assertTrue(c2(txt_col))

    def test_is_static_class(self):

        def run_test(fn_name, fn, passes):
            fails = [t for t in DType if t not in passes]
            for t in passes:
                col = make(ColumnMeta(field_name='test', table_name='test', dtype=t))
                self.assertTrue(fn(col), msg=f'DType {t} did not pass {fn_name} when it should have.')
            for t in fails:
                col = make(ColumnMeta(field_name='test', table_name='test', dtype=t))
                self.assertFalse(fn(col), msg=f'DType {t} did not fail {fn_name} when it should have.')

        # Numeric
        run_test('Is.numeric', Is.numeric, (DType.Int, DType.BigInt, DType.Double, DType.Decimal))

        run_test('Is.text', Is.text, (DType.Text,))
        run_test('Is.not_text', Is.not_text, [t for t in DType if t != DType.Text])

        # Timelike
        run_test('Is.timelike', Is.timelike, (DType.Date, DType.DateTime))

        # Boolean
        run_test('Is.boolean', Is.boolean, (DType.Boolean,))

        # Integer
        run_test('Is.integer', Is.integer, (DType.Int, DType.BigInt))


class TestAreConstraint(SqlTestCase):

    def test_are_constraint_ctor(self):
        c = VariadicCheck(True, lambda *args: all(a == DType.Int for a in args), 'all values must be Text')
        self.assertFalse(c(DType.Int, DType.Int, DType.Text))
        self.assertTrue(c(DType.Int, DType.Int, DType.Int))
        self.assertEqual("all values must be Text", c.msg)
        self.assertTrue(c.trigger)

        c = VariadicCheck(False, lambda *args: all(a == DType.Int for a in args), 'not all values must be Text')
        self.assertTrue(c(DType.Int, DType.Int, DType.Text))
        self.assertFalse(c(DType.Int, DType.Int, DType.Int))
        self.assertEqual("not all values must be Text", c.msg)
        self.assertFalse(c.trigger)

    def test_are_all_text(self):
        cols = [self.make_text_col(f'c{i}') for i in range(3)]
        self.assertTrue(Are.all_text(*cols))
        self.assertFalse(Are.all_text(*cols, self.make_int_col('c3')))
        self.assertEqual('must all be Text', Are.all_text.msg)

    def test_are_comparable(self):

        def make_cols(*dtypes):
            return [make(ColumnMeta(field_name='test', table_name='test', dtype=t)) for t in dtypes]

        self.assertTrue(Are.comparable(*make_cols(DType.Date, DType.DateTime, DType.Date)))
        self.assertFalse(Are.comparable(*make_cols(DType.Date, DType.Text)))

        self.assertTrue(Are.comparable(*make_cols(DType.DateTime, DType.DateTime, DType.Date)))
        self.assertFalse(Are.comparable(*make_cols(DType.DateTime, DType.Text)))

        self.assertTrue(Are.comparable(*make_cols(DType.Boolean, DType.Boolean, DType.Boolean)))
        self.assertFalse(Are.comparable(*make_cols(DType.Boolean, DType.Text)))

        numerics = make_cols(DType.Int, DType.BigInt, DType.Decimal, DType.Double)
        for col in numerics:
            self.assertTrue(Are.comparable(col, *numerics))
            self.assertFalse(Are.comparable(col, *make_cols(DType.Text)))

        self.assertTrue(Are.comparable(self.make_text_col('t'), *make_cols(DType.Text)))
        self.assertFalse(Are.comparable(self.make_text_col('t'), *make_cols(DType.Int)))


class TestDType(unittest.TestCase):

    def test_dtype_fields_exist_and_are_in_correct_order(self):

        exp = ['Int', 'BigInt', 'Double', 'Decimal', 'Boolean', 'Text', 'Date', 'DateTime', 'Null']
        obs = [t.name for t in DType]
        self.assertSequenceEqual(exp, obs)

    def test_dtype_null_field_is_negative999(self):
        self.assertEqual(-999, DType.Null.value)

    def test_to_dtype_method(self):

        test_cases = {
            DType.Int: (int, np.int32, np.int64, pd.Int16Dtype(), pd.Int32Dtype(), pd.Int64Dtype(), 'Int32'),
            DType.Double: (float, np.float32, np.float64, pd.Float32Dtype(), pd.Float64Dtype(), 'Double', 'Float'),
            DType.Boolean: (bool, pd.BooleanDtype(), 'Boolean'),
            DType.Text: (str, pd.StringDtype(), 'Csv', 'String'),
            DType.Date: (dt.date, 'Date'),
            DType.DateTime: (dt.datetime, pd.Timestamp, 'DateTime'),
            DType.Null: (None, type(pd.NA), type(pd.NaT)),
        }

        for target, types in test_cases.items():
            for t in types:
                self.assertEqual(target, DType.to_dtype(t))

    def test_to_pytype_method(self):

        test_cases = {
            DType.Int: int,
            DType.BigInt: int,
            DType.Double: float,
            DType.Text: str,
            DType.Boolean: bool,
            DType.Date: dt.date,
            DType.DateTime: dt.datetime,
            DType.Decimal: float,
        }
        for dtype, py_type in test_cases.items():
            self.assertEqual(py_type, dtype.to_pytype())

    def test_dtype_numeric_priorty(self):

        self.assertEqual(DType.BigInt, DType.Int.num_priority(DType.BigInt))
        self.assertEqual(DType.Double, DType.BigInt.num_priority(DType.Double))
        self.assertEqual(DType.Decimal, DType.Double.num_priority(DType.Decimal))

