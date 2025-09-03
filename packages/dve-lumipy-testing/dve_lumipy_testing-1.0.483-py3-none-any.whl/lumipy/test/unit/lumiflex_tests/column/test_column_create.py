from datetime import datetime, date

from pydantic import ValidationError

from lumipy.lumiflex.column import Column
from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._metadata import ColumnMeta
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestSqlColumnCreation(SqlTestCase):

    def test_column_ctor(self):
        col1 = Column(fn=lambda: f'[Col1]', dtype=DType.Double, label='data')
        col2 = Column(fn=lambda: f'[Col2]', dtype=DType.Double, label='data')
        col3 = Column(fn=lambda x, y: f'{x.sql} OP {y.sql}', dtype=DType.Date, parents=(col1, col2), label='op')

        self.assertEqual('[Col1] OP [Col2]', col3.sql)
        self.assertEqual(DType.Date, col3.dtype)
        self.assertEqual((col1, col2), col3.get_parents())
        self.assertEqual('data', col1.get_label())
        self.assertEqual('data', col2.get_label())
        self.assertEqual('op', col3.get_label())

    def test_column_ctor_still_errors_on_non_node_parents(self):
        p1 = self.make_double_col('p1')
        fn = lambda x, y: f'{x.sql} TEST_OP {y.sql}'
        self.assertErrorsWithMessage(
            lambda: Column(fn=fn, parents=(p1, 123), dtype=DType.Double, label='op'),
            TypeError,
            "Parents must all be Node or a subclass of Node but were (Column, int)."
        )

    def test_make_from_field_meta(self):
        meta = ColumnMeta(field_name='MyCol', table_name='MyTable', dtype=DType.Int)
        col = make(meta)

        self.assertEqual(meta, col.meta)
        self.assertEqual('[MyCol]', col.sql)
        self.assertEqual(DType.Int, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

    def test_make_from_python_int(self):
        col = make(2)
        self.assertEqual(2, col.meta)
        self.assertEqual('2', col.sql)
        self.assertEqual(DType.Int, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

    def test_make_from_python_float(self):
        col = make(3.14)
        self.assertEqual(3.14, col.meta)
        self.assertEqual('3.14', col.sql)
        self.assertEqual(DType.Double, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

        # Make sure it doesn't end up as '3.1e9'
        col = make(3.1e9)
        self.assertEqual(3.1e9, col.meta)
        self.assertEqual('3100000000.0', col.sql)
        self.assertEqual(DType.Double, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

    def test_make_from_python_bool(self):
        col = make(False)
        self.assertEqual(False, col.meta)
        self.assertEqual('FALSE', col.sql)
        self.assertEqual(DType.Boolean, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

        col = make(True)
        self.assertEqual(True, col.meta)
        self.assertEqual('TRUE', col.sql)
        self.assertEqual(DType.Boolean, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

    def test_make_from_python_str(self):
        col = make('ABC')
        self.assertEqual('ABC', col.meta)
        self.assertEqual("'ABC'", col.sql)
        self.assertEqual(DType.Text, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

    def test_make_from_python_datetime(self):
        x = datetime(2023, 1, 1, 13, 49, 1, 123)
        col = make(x)
        self.assertEqual(x, col.meta)
        self.assertEqual("#2023-01-01 13:49:01.000123#", col.sql)
        self.assertEqual(DType.DateTime, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

    def test_make_from_python_date(self):
        x = date(2023, 1, 1)
        col = make(x)
        self.assertEqual(x, col.meta)
        self.assertEqual("#2023-01-01#", col.sql)
        self.assertEqual(DType.Date, col.dtype)
        self.assertEqual(tuple(), col.get_parents())

    def test_make_errors_when_bad_type_object(self):
        self.assertErrorsWithMessage(
            lambda: make({}),
            TypeError,
            "Unsupported type! Can't make Column object for object of type 'dict', (value={})"
        )

    def test_column_ctor_errors_when_fn_not_callable(self):
        self.assertErrorsWithMessage(
            lambda: Column(fn=123, dtype=DType.Int, label='data'),
            ValidationError,
            "1 validation error for Column\n"
            "Value error, 123 is not a callable. fn input must be a function. [type=value_error, input_value={'fn': 123, 'dtype': <DTy...nt: 0>, 'label': 'data'}, input_type=dict]\n"
            "For further information visit https://errors.pydantic.dev/xxx/v/value_error",
            [2]
        )

    def test_column_val_errors_when_fn_returns_non_string_object(self):
        self.assertErrorsWithMessage(
            lambda: Column(fn=lambda: 123, dtype=DType.Int, label='data'),
            TypeError,
            "Column.fn must be a callable that returns str, but returned int (123).",
        )

    def test_data_column_hash_function(self):
        d1 = self.make_double_col('d1')
        d2 = self.make_double_col('d1')
        self.assertHashEqual(d1, d2)

        d1 = self.make_double_col('d1')
        d2 = self.make_double_col('d2')
        self.assertHashNotEqual(d1, d2)

    def test_literal_column_hash_function(self):
        test_literals = {
            DType.Double: 1.2,
            DType.Int: 2,
            DType.BigInt: 22222222222222222,
            DType.Boolean: True,
            DType.Decimal: 1e-9,
            DType.Text: 'ABCDEFG',
            DType.Date: date(1940, 1, 2),
            DType.DateTime: datetime(2023, 1, 9, 14),
        }

        for name, value in test_literals.items():
            v1, v2 = make(value), make(value)
            self.assertHashEqual(v1, v2)

    def test_column_parents_validation_inherits_from_node(self):
        meta = self.make_col_meta(0, True, 'My.Test.Table')
        self.assertErrorsWithMessage(
            lambda: Column(fn=lambda x: f'{x}', meta=meta, parents=(2.0, ), label='data', dtype=DType.Double),
            TypeError,
            """
              Parents must all be Node or a subclass of Node but were (float).
            """
        )
