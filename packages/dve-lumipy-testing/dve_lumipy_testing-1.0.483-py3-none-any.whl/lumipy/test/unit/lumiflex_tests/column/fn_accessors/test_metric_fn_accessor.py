from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestMetricFnAccessor(SqlTestCase):

    def test_metric_function_accessor_errors_with_non_numeric_col(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('a').metric,
            AttributeError,
            "To use .metric accessor the column must be Int/BigInt/Double/Decimal type, but was Text."
        )

    def test_metric_function_accessor_mean_squared_error(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.mean_squared_error(y)
        sql = r.sql
        self.assertEqual("mean_squared_error([Col0], [Col1])", sql)

    def test_metric_function_accessor_mean_absolute_error(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.mean_absolute_error(y)
        sql = r.sql
        self.assertEqual("mean_absolute_error([Col0], [Col1])", sql)

    def test_metric_function_accessor_mean_fractional_absolute_error(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.mean_fractional_absolute_error(y)
        sql = r.sql
        self.assertEqual("mean_fractional_absolute_error([Col0], [Col1])", sql)

    def test_metric_function_accessor_minkowski_distance(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.minkowski_distance(y, 3.0)
        sql = r.sql
        self.assertEqual("minkowski_distance([Col0], [Col1], 3.0)", sql)

    def test_metric_function_accessor_chebyshev_distance(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.chebyshev_distance(y)
        sql = r.sql
        self.assertEqual("chebyshev_distance([Col0], [Col1])", sql)

    def test_metric_function_accessor_manhattan_distance(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.manhattan_distance(y)
        sql = r.sql
        self.assertEqual("manhattan_distance([Col0], [Col1])", sql)

    def test_metric_function_accessor_euclidean_distance(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.euclidean_distance(y)
        sql = r.sql
        self.assertEqual("euclidean_distance([Col0], [Col1])", sql)

    def test_metric_function_accessor_canberra_distance(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.canberra_distance(y)
        sql = r.sql
        self.assertEqual("canberra_distance([Col0], [Col1])", sql)

    def test_metric_function_accessor_braycurtis_distance(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.braycurtis_distance(y)
        sql = r.sql
        self.assertEqual("braycurtis_distance([Col0], [Col1])", sql)

    def test_metric_function_accessor_cosine_distance(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.cosine_distance(y)
        sql = r.sql
        self.assertEqual("cosine_distance([Col0], [Col1])", sql)

    def test_metric_function_accessor_precision_score(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.precision_score(y)
        sql = r.sql
        self.assertEqual("precision_score([Col0], [Col1])", sql)

    def test_metric_function_accessor_recall_score(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.recall_score(y)
        sql = r.sql
        self.assertEqual("recall_score([Col0], [Col1])", sql)

    def test_metric_function_accessor_f_score(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.f_score(y, 1.0)
        sql = r.sql
        self.assertEqual("fbeta_score([Col0], [Col1], 1.0)", sql)

    def test_metric_function_accessor_r_squared(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.r_squared(y)
        sql = r.sql
        self.assertEqual("r_squared([Col0], [Col1])", sql)

    def test_metric_function_accessor_adjusted_r_squared(self):
        table = self.make_table()
        x, y = table.col0, table.col1

        r = x.metric.adjusted_r_squared(y, 1)
        sql = r.sql
        self.assertEqual("adjusted_r_squared([Col0], [Col1], 1)", sql)
