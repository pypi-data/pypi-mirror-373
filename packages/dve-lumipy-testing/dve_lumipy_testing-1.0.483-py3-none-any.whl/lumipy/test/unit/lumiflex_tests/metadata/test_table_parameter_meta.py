from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._metadata import TableParamMeta
from pydantic import ValidationError


class TestTableParamMeta(SqlTestCase):

    def test_table_param_meta_ctor(self):
        table_name = 'Test.Table.Writer'
        field_name = 'ToWrite'
        cols = [self.make_col_meta(i, True, field_name) for i in range(8)]
        t_param = TableParamMeta(field_name=field_name, table_name=table_name, columns=cols)
        self.assertEqual(table_name, t_param.table_name)
        self.assertEqual(field_name, t_param.field_name)
        self.assertEqual('to_write', t_param.python_name())
        self.assertSequenceEqual(t_param.columns, cols)

    def test_table_param_meta_ctor_defaults(self):
        t_param = TableParamMeta(field_name='ToWrite', table_name='Test.Table.Writer')
        self.assertEqual('Test.Table.Writer', t_param.table_name)
        self.assertEqual('ToWrite', t_param.field_name)
        self.assertEqual('to_write', t_param.python_name())
        self.assertEqual(t_param.columns, tuple())

    def test_table_param_meta_columns_field_validation(self):
        field_name = 'ToWrite'
        table_name = 'Test.Table.Writer'

        cols = [self.make_col_meta(i, True, 'wrong' if i % 2 == 0 else field_name) for i in range(3)]
        self.assertErrorsWithMessage(
            lambda: TableParamMeta(field_name=field_name, table_name=table_name, columns=cols),
            ValueError,
            """
            1 validation error for TableParamMeta
  Value error, There are column metadata objects that don't belong to this table parameter metadata object (ToWrite)
	Col0: wrong
	Col2: wrong [type=value_error, input_value={'field_name': 'ToWrite',... wrong, Double, True )]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [4]
        )

        cols = [(i, 'wrong' if i % 2 == 0 else field_name) for i in range(3)]
        self.assertErrorsWithMessage(
            lambda: TableParamMeta(field_name=field_name, table_name=table_name, columns=cols),
            TypeError,
            "All table param metadata columns must all be Column objects but were (tuple, tuple, tuple)."
        )

    def test_table_parameter_extras_error(self):
        self.assertErrorsWithMessage(
            lambda: TableParamMeta(field_name='ToWrite', table_name='Test.Table.Writer', bad_field=True),
            ValidationError,
            """
            1 validation error for TableParamMeta
bad_field
  Extra inputs are not permitted [type=extra_forbidden, input_value=True, input_type=bool]
    For further information visit https://errors.pydantic.dev/xxx/v/extra_forbidden
            """,
            [3]
        )
