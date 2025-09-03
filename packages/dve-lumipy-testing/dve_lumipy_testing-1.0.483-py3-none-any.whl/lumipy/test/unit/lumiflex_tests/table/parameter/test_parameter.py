from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.parameter import Parameter
from lumipy.lumiflex._column.make import make


class TestSetParam(SqlTestCase):

    def test_parameter_ctor(self):
        meta = self.make_param_meta(0, 'MyTable')
        param = Parameter(meta=meta, parents=(make(2),))
        self.assertEqual(param.get_label(), 'parameter')
        self.assertEqual(meta, param.meta)
        self.assertIs(param.meta.prefix, None)
        self.assertEqual('[Param0] = 2', param.sql)

    def test_parameter_ctor_table_variable(self):
        meta = self.make_table_param_meta(0, n_cols=5)

        tv = self.make_table_var('A')
        param = Parameter(meta=meta, parents=(tv,))
        self.assertEqual('[TableVar_0] = @test_A', param.sql)
        self.assertHashEqual(tv, param.get_parents()[0])

        prfx = param.with_prefix('ABC')
        self.assertEqual('ABC.[TableVar_0] = @test_A', prfx.sql)
        self.assertHashEqual(tv, prfx.get_parents()[0])

    def test_parameter_with_prefix(self):
        meta = self.make_param_meta(0, 'MyTable')
        param = Parameter(meta=meta, parents=(make(2),)).with_prefix('AB')
        self.assertEqual('AB', param.meta.prefix)
        self.assertEqual('AB.[Param0] = 2', param.sql)

    def test_parameter_meta_field_validation(self):
        # no meta
        self.assertErrorsWithMessage(
            lambda: Parameter(),
            ValueError,
            """
            1 validation error for Parameter
            meta
              Field required [type=missing, input_value={}, input_type=dict]
                For further information visit https://errors.pydantic.dev/xxx/v/missing
            """,
            [3]
        )
        # bad meta type
        self.assertErrorsWithMessage(
            lambda: Parameter(meta=7, parents=(make(1.2),)),
            ValueError,
            """
            2 validation errors for Parameter
meta.ParamMeta
  Input should be a valid dictionary or instance of ParamMeta [type=model_type, input_value=7, input_type=int]
    For further information visit https://errors.pydantic.dev/xxx/v/model_type
meta.TableParamMeta
  Input should be a valid dictionary or instance of TableParamMeta [type=model_type, input_value=7, input_type=int]
    For further information visit https://errors.pydantic.dev/xxx/v/model_type
            """,
            [3, 6]
        )

    def test_parameter_parents_field_validation(self):
        meta = self.make_param_meta(0, 'MyTable')

        # no parents
        self.assertErrorsWithMessage(
            lambda: Parameter(meta=meta),
            ValueError,
            """
            1 validation error for Parameter
  Value error, Parameter can only have a single parent Node which must be a Column or Table Var. Parents tuple was empty. [type=value_error, input_value={'meta': ParamMeta( Param0, MyTable, Int, None )}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [2]
        )

        # too many parents
        self.assertErrorsWithMessage(
            lambda: Parameter(meta=meta, parents=(make(1), make(2))),
            ValueError,
            """
1 validation error for Parameter
  Value error, Parameter can only have a single parent Node which must be a Column or Table Var. Too many parent nodes (Column, Column). [type=value_error, input_value={'meta': ParamMeta( Param... meta: 2
   sql: '2'
))}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error            
            """,
            [4]
        )

        # bad parent type, inherits Node class parents validation
        self.assertErrorsWithMessage(
            lambda: Parameter(meta=meta, parents=('ABC',)),
            TypeError,
            """
            Parents must all be Node or a subclass of Node but were (str).
            """
        )

    def test_parameter_table_parameter(self):
        table = self.make_table('my.test.table', n_cols=5)
        tv = table.select('*').to_table_var('testing')

        meta = self.make_table_param_meta(0, n_cols=5, table_name='my.test.table2')

        p = Parameter(meta=meta, parents=(tv,))
        self.assertEqual('[TableVar_0] = @testing', p.sql)

        p = p.with_prefix('ABC')
        self.assertEqual('ABC.[TableVar_0] = @testing', p.sql)

    def test_param_equals(self):

        meta1 = self.make_param_meta(0)
        meta2 = self.make_param_meta(0)
        p1, p2 = self.make_parameters([meta1, meta2])
        self.assertEqual(p1, p2)

        p1 = p1.with_prefix('abc')
        p2 = p2.with_prefix('abc')
        self.assertEqual(p1, p2)
