from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestLinregFnAccessor(SqlTestCase):

    def test_linreg_function_accessor_errors_with_non_numeric_col(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('a').linreg,
            AttributeError,
            "To use .linreg accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_linreg_function_accessor_alpha(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.linreg.alpha(y)
        sql = r.sql
        self.assertEqual("linear_regression_alpha([Col0], [Col1])", sql)

    def test_linreg_function_accessor_beta(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.linreg.beta(y)
        sql = r.sql
        self.assertEqual("linear_regression_beta([Col0], [Col1])", sql)

    def test_linreg_function_accessor_alpha_std_err(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.linreg.alpha_std_err(y)
        sql = r.sql
        self.assertEqual("linear_regression_alpha_error([Col0], [Col1])", sql)

    def test_linreg_function_accessor_beta_std_err(self):
        table = self.make_table()
        x, y = table.col0, table.col1
        r = x.linreg.beta_std_err(y)
        sql = r.sql
        self.assertEqual("linear_regression_beta_error([Col0], [Col1])", sql)
