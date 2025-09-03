from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._metadata.dtype import DType
from lumipy import json
import datetime as dt


class TestJsonFnAccessor(SqlTestCase):

    def test_json_function_accessor_json(self):
        table = self.make_table()
        x = table.col5.json.format()
        self.assertEqual('json([Col5])', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor_json_type_errors(self):
        table = self.make_table()
        self.assertErrorsWithMessage(
            lambda: table.col1.json.format(),
            AttributeError,
            "To use .json.format() the column must be Text type, but was BigInt."
        )

    def test_json_function_accessor_array_len(self):
        table = self.make_table()
        x = table.col5.json.array_len('$.A.B[2]')
        self.assertEqual('json_array_length([Col5], \'$.A.B[2]\')', x.sql)
        self.assertEqual(DType.Int, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor_array_len_path_errors(self):
        table = self.make_table()

        self.assertErrorsWithMessage(
            lambda: table.col1.json.format(),
            AttributeError,
            "To use .json.format() the column must be Text type, but was BigInt."
        )

        self.assertErrorsWithMessage(
            lambda: table.col5.json.array_len('A.B[2]'),
            ValueError,
            "json path must start with '$', e.g. '$.A.B[1]'"
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json.array_len(7),
            TypeError,
            """
            Invalid input detected at
               → lambda: table.col5.json.array_len(7),
            There was 1 failed constraint on .json.array_len():
               • The input to 'path' must be Text but was Int=7
            """
        )

    def test_json_function_accessor__getitem__(self):
        table = self.make_table()
        x = table.col5.json['$.A.B[2]']
        self.assertEqual('json_extract([Col5], \'$.A.B[2]\')', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor__getitem__errors(self):

        table = self.make_table()
        self.assertErrorsWithMessage(
            lambda: table.col1.json['$.A.B'],
            AttributeError,
            "To use .json[] the column must be Text type, but was BigInt."
        )

        self.assertErrorsWithMessage(
            lambda: table.col5.json['A.B[2]'],
            ValueError,
            "json path must start with '$', e.g. '$.A.B[1]'"
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json[7],
            TypeError,
            """
            Invalid input detected at
               → lambda: table.col5.json[7],
            There was 1 failed constraint on .json[]:
               • The input to 'path' must be Text but was Int=7
            """
        )

    def test_json_function_accessor_insert(self):
        table = self.make_table()
        x = table.col5.json.insert('$.A.B', 5)
        self.assertEqual('json_insert([Col5], \'$.A.B\', 5)', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor_insert_errors(self):

        table = self.make_table()
        self.assertErrorsWithMessage(
            lambda: table.col1.json.insert('$.A.B', 5),
            AttributeError,
            "To use .json.insert() the column must be Text type, but was BigInt."
        )

        self.assertErrorsWithMessage(
            lambda: table.col5.json.insert('A.B[2]', 5),
            ValueError,
            "json path must start with '$', e.g. '$.A.B[1]'"
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json.insert(7, 5),
            TypeError,
            """
            Invalid input detected at
               → lambda: table.col5.json.insert(7, 5),
            There was 1 failed constraint on .json.insert():
               • The input to 'path' must be Text but was Int=7
            """
        )

    def test_json_function_accessor_patch(self):
        table = self.make_table()
        x = table.col5.json.patch('{"A": 3}')
        self.assertEqual('json_patch([Col5], \'{"A": 3}\')', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor_patch_errors(self):

        table = self.make_table()
        self.assertErrorsWithMessage(
            lambda: table.col1.json.patch('{"a": 1}'),
            AttributeError,
            "To use .json.patch() the column must be Text type, but was BigInt."
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json.patch('{A'),
            ValueError,
            "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json.patch(5),
            TypeError,
            """
            Invalid input detected at
               → lambda: table.col5.json.patch(5),
            There was 1 failed constraint on .json.patch():
               • The input to 'patch' must be Text but was Int=5
            """
        )

    def test_json_function_accessor_quote(self):
        table = self.make_table()
        x = table.col5.json.quote()
        self.assertEqual('json_quote([Col5])', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor_remove(self):
        table = self.make_table()

        x = table.col5.json.remove('$.A.B')
        self.assertEqual('json_remove([Col5], \'$.A.B\')', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

        x = table.col5.json.remove('$.A.B', '$.A.C[1]')
        self.assertEqual('json_remove([Col5], \'$.A.B\', \'$.A.C[1]\')', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor_remove_errors(self):
        table = self.make_table()
        self.assertErrorsWithMessage(
            lambda: table.col1.json.remove('$.A.B'),
            AttributeError,
            "To use .json.remove() the column must be Text type, but was BigInt."
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json.remove('A.B[2]'),
            ValueError,
            "json path must start with '$', e.g. '$.A.B[1]'"
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json.remove(5),
            TypeError,
            """
            Invalid input detected at
               → lambda: table.col5.json.remove(5),
            There was 1 failed constraint on .json.remove():
               • The inputs to (paths[0]) must all be Text but were (Int 5)
            """
        )

    def test_json_function_accessor_type(self):
        table = self.make_table()
        x = table.col5.json.type('$.A.B')
        self.assertEqual('json_type([Col5], \'$.A.B\')', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor_type_errors(self):
        table = self.make_table()
        self.assertErrorsWithMessage(
            lambda: table.col1.json.type('$.A.B'),
            AttributeError,
            "To use .json.type() the column must be Text type, but was BigInt."
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json.type('A.B[2]'),
            ValueError,
            "json path must start with '$', e.g. '$.A.B[1]'"
        )
        self.assertErrorsWithMessage(
            lambda: table.col5.json.type(5),
            TypeError,
            """
            Invalid input detected at
               → lambda: table.col5.json.type(5),
            There was 1 failed constraint on .json.type():
               • The input to 'path' must be Text but was Int=5
            """
        )

    def test_json_function_accessor_valid(self):
        table = self.make_table()
        x = table.col5.json.valid()
        self.assertEqual('json_valid([Col5])', x.sql)
        self.assertEqual(DType.Boolean, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_function_accessor_valid_errors(self):
        table = self.make_table()
        self.assertErrorsWithMessage(
            lambda: table.col1.json.valid(),
            AttributeError,
            "To use .json.valid() the column must be Text type, but was BigInt."
        )

    def test_json_function_accessor_group_array(self):
        table = self.make_table()
        x = table.col5.json.group_array()
        self.assertEqual('json_group_array([Col5])', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('aggfunc', x.get_label())

    def test_json_function_accessor_group_object(self):
        table = self.make_table()
        x = table.col5.json.group_object(table.col1)
        self.assertEqual('json_group_object([Col5], [Col1])', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('aggfunc', x.get_label())

    def test_json_function_accessor_group_object_errors(self):
        table = self.make_table()
        self.assertErrorsWithMessage(
            lambda: table.col1.json.group_object(table.col5),
            AttributeError,
            "To use .json.group_object() the column must be Text type, but was BigInt."
        )


class TestJsonStatic(SqlTestCase):

    def test_json_static_array(self):
        table = self.make_table()
        x = json.array(table.col1, table.col2, table.col3, 'ABC', 123, dt.datetime(2023, 1, 1), True)
        self.assertEqual('json_array([Col1], [Col2], [Col3], \'ABC\', 123, #2023-01-01 00:00:00.000000#, TRUE)', x.sql)
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())

    def test_json_static_object(self):
        table = self.make_table()
        x = json.object(a=table.col1, b=table.col2, c='ABC', d=123, e=dt.datetime(2023, 1, 1), f=True)
        self.assertEqual(
            "json_object('a', [Col1], 'b', [Col2], 'c', 'ABC', 'd', 123, 'e', #2023-01-01 00:00:00.000000#, 'f', TRUE)",
            x.sql
        )
        self.assertEqual(DType.Text, x.dtype)
        self.assertEqual('func', x.get_label())
