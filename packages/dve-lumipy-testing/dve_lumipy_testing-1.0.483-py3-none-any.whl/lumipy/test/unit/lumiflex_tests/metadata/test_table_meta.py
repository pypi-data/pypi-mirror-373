
from lumipy.lumiflex._atlas.utils import process_direct_provider_metadata
from lumipy.lumiflex._metadata import TableMeta
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestProviderMeta(SqlTestCase):

    def test_table_meta_ctor(self):

        name = 'Test.Table.Meta'
        columns = [SqlTestCase.make_col_meta(i, True, name) for i in range(5)]
        parameters = [SqlTestCase.make_param_meta(i, name) for i in range(2)]
        table_parameters = [SqlTestCase.make_table_param_meta(i, 5, name) for i in range(1)]

        meta = TableMeta(name=name, columns=columns, parameters=parameters, table_parameters=table_parameters, category='Testing', type='DataProvider')

        self.assertEqual(name, meta.name)
        self.assertSequenceEqual(columns, meta.columns)
        self.assertSequenceEqual(parameters, meta.parameters)
        self.assertSequenceEqual(table_parameters, meta.table_parameters)

        self.assertEqual('test_table_meta', meta.python_name())

    def test_table_meta_name_validation(self):

        name = 'Test.Table.Meta'
        columns = [SqlTestCase.make_col_meta(i, True, name) for i in range(5)]

        self.assertErrorsWithMessage(
            lambda: TableMeta(name='123', columns=columns, category='Testing', type='DataProvider'),
            ValueError,
            """
            1 validation error for TableMeta
  Value error, Invalid table name: '123'. Must not start with a number, and contain only alphanumeric chars + '_', '.', '-'. [type=value_error, input_value={'name': '123', 'columns'... 'type': 'DataProvider'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [2]
        )

    def test_table_meta_columns_validation(self):

        name = 'Test.Table.Meta'
        bad_columns = [SqlTestCase.make_col_meta(i, True, 'Wrong' if i % 2 == 0 else name) for i in range(5)]

        self.assertErrorsWithMessage(
            lambda: TableMeta(name=name, columns=bad_columns, category='Testing', type='DataProvider'),
            ValueError,
            """1 validation error for TableMeta
  Value error, There are columns given as input that do not belong to the table Test.Table.Meta. [type=value_error, input_value={'name': 'Test.Table.Meta... 'type': 'DataProvider'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [2]
        )

    def test_table_meta_parameters_validation(self):

        name = 'Test.Table.Meta'
        columns = [SqlTestCase.make_col_meta(i, True, name) for i in range(5)]

        bad_parameters = [SqlTestCase.make_param_meta(i, 'Wrong' if i % 2 == 0 else name) for i in range(6)]
        self.assertErrorsWithMessage(
            lambda: TableMeta(name=name, columns=columns, parameters=bad_parameters, category='Testing', type='DataProvider'),
            ValueError,
            """
            1 validation error for TableMeta
  Value error, There are params given as input that do not belong to the table Test.Table.Meta. [type=value_error, input_value={'name': 'Test.Table.Meta... 'type': 'DataProvider'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [2]
        )

        bad_parameters = [(i, 'Wrong' if i % 2 == 0 else name) for i in range(6)]
        self.assertErrorsWithMessage(
            lambda: TableMeta(name=name, columns=columns, parameters=bad_parameters, category='Testing', type='DataProvider'),
            TypeError,
            "Parameters must all be ParamMeta objects but were (tuple, tuple, tuple, tuple, tuple, tuple)."
        )

    def test_table_meta_table_parameters_validation(self):

        name = 'Test.Table.Meta'
        columns = [SqlTestCase.make_col_meta(i, True, name) for i in range(5)]
        parameters = [SqlTestCase.make_param_meta(i, name) for i in range(2)]

        bad_table_params = [SqlTestCase.make_table_param_meta(i, 5, 'Wrong' if i % 2 == 0 else name) for i in range(4)]
        self.assertErrorsWithMessage(
            lambda: TableMeta(name=name, columns=columns, parameters=parameters, table_parameters=bad_table_params, category='Testing', type='DataProvider'),
            ValueError,
            """
            1 validation error for TableMeta
  Value error, There are table params given as input that do not belong to the table Test.Table.Meta. [type=value_error, input_value={'name': 'Test.Table.Meta... 'type': 'DataProvider'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [2]
        )

        bad_table_params = [(i, 'Wrong' if i % 2 == 0 else name, 5) for i in range(4)]
        self.assertErrorsWithMessage(
            lambda: TableMeta(name=name, columns=columns, parameters=parameters, table_parameters=bad_table_params, category='Testing', type='DataProvider'),
            TypeError,
            "Table parameters must all be TableParamMeta objects but were (tuple, tuple, tuple, tuple)."
        )

    def test_table_meta_hash_function(self):

        name = 'Test.Table.Meta'
        columns = [SqlTestCase.make_col_meta(i, True, name) for i in range(5)]
        parameters = [SqlTestCase.make_param_meta(i, name) for i in range(2)]
        table_parameters = [SqlTestCase.make_table_param_meta(i, 5, name) for i in range(1)]

        meta1 = TableMeta(name=name, columns=columns, parameters=parameters, table_parameters=table_parameters, category='Testing', type='DataProvider')
        meta2 = TableMeta(name=name, columns=columns, parameters=parameters, table_parameters=table_parameters, category='Testing', type='DataProvider')

        self.assertHashEqual(meta1, meta2)

    def test_table_meta_equals_function(self):

        name = 'Test.Table.Meta'
        columns = [SqlTestCase.make_col_meta(i, True, name) for i in range(5)]
        parameters = [SqlTestCase.make_param_meta(i, name) for i in range(2)]
        table_parameters = [SqlTestCase.make_table_param_meta(i, 5, name) for i in range(1)]

        meta1 = TableMeta(name=name, columns=columns, parameters=parameters, table_parameters=table_parameters, category='Testing', type='DataProvider')
        meta2 = TableMeta(name=name, columns=columns, parameters=parameters, table_parameters=table_parameters, category='Testing', type='DataProvider')

        self.assertTrue(meta1, meta2)

    def test_table_meta_from_df_method(self):

        for table, df in self.df1.groupby('TableName'):
            meta = TableMeta.data_provider_from_df(df)

            n_cols = df[df.FieldType == 'Column'].shape[0]
            n_params = df[(df.FieldType == 'Parameter') & (df.DataType != 'Table')].shape[0]
            n_tparams = df[(df.FieldType == 'Parameter') & (df.DataType == 'Table')].shape[0]

            self.assertEqual(df.iloc[0].TableName, meta.name)
            self.assertEqual(df.iloc[0].Category, meta.category)
            doc_link = df.iloc[0].DocumentationLink
            self.assertEqual(doc_link if isinstance(doc_link, str) else None, meta.documentation_link)
            descr_link = df.iloc[0].Description
            self.assertEqual(descr_link if isinstance(descr_link, str) else None, meta.description)
            self.assertEqual(df.iloc[0].Type, meta.type)
            self.assertIsNone(meta.alias)

            name = df.iloc[0].TableName
            self.assertEqual(n_cols, len(meta.columns), msg=f'N columns mismatch for {name} meta object.')
            self.assertEqual(n_params, len(meta.parameters), msg=f'N parameters mismatch for {name} meta object.')
            self.assertEqual(n_tparams, len(meta.table_parameters), msg=f'N table parameters mismatch for {name} meta object.')

    def test_direct_provider_from_row_fixed_content(self):
        df = process_direct_provider_metadata(self.df2).fillna('Not available')
        slack_row = df[df.TableName.str.contains('Slack')].iloc[0]
        slack = TableMeta.direct_provider_from_row(slack_row)

        self.assertEqual(slack_row.TableName, slack.name)
        self.assertEqual(slack_row.Description, slack.description)
        self.assertEqual(slack_row.DocumentationLink, slack.documentation_link)
        self.assertEqual(slack_row.Category, slack.category)
        self.assertEqual('DirectProvider', slack.type)
        self.assertEqual(3, len(slack.columns))
        self.assertEqual(0, len(slack.table_parameters))

        # Check param types and names
        exp_names = ['top_n', 'attach_as', 'attach_as_in_thread', 'attach_as_one_file_name', 'max_width', 'json', 'allow_failure', 'ignore_on_zero_rows', 'channel', 'text', 'json_message']
        obs_names = [p.python_name() for p in slack.parameters]
        self.assertSequenceEqual(exp_names, obs_names)
        exp_dtypes = [DType.Int, DType.Text, DType.Boolean, DType.Text, DType.Int, DType.Boolean, DType.Boolean, DType.Boolean, DType.Text, DType.Text, DType.Text]
        obs_dtypes = [p.dtype for p in slack.parameters]
        self.assertSequenceEqual(exp_dtypes, obs_dtypes)

    def test_direct_provider_from_row_variable_content(self):
        df = process_direct_provider_metadata(self.df2).fillna('Not available')
        loki_row = df[df.TableName.str.contains('Loki')].iloc[0]
        loki = TableMeta.direct_provider_from_row(loki_row)

        self.assertEqual(loki_row.TableName, loki.name)
        self.assertEqual(loki_row.Description, loki.description)
        self.assertEqual(loki_row.DocumentationLink, loki.documentation_link)
        self.assertEqual(loki_row.Category, loki.category)
        self.assertEqual('DirectProvider', loki.type)
        self.assertIsNone(loki.columns)
        self.assertEqual(0, len(loki.table_parameters))

        # Check param types and names
        exp_names = ['log_ql', 'start_at', 'end_at', 'step', 'default_limit', 'direction', 'explicit_label_columns', 'only_explicit_label_columns']
        obs_names = [p.python_name() for p in loki.parameters]
        self.assertSequenceEqual(exp_names, obs_names)
        exp_dtypes = [DType.Text, DType.DateTime, DType.DateTime, DType.Int, DType.Int, DType.Text, DType.Text, DType.Boolean]
        obs_dtypes = [p.dtype for p in loki.parameters]
        self.assertSequenceEqual(exp_dtypes, obs_dtypes)

        # Test body param is picked out and handled
        body = [p for p in loki.parameters if p.is_body]
        self.assertEqual(1, len(body))
        body = body[0]
        self.assertEqual('log_ql', body.python_name())

    def test_data_provider_from_df_with_bad_data(self):

        # get a df that has columns and params
        df = self.df1[self.df1.TableName == 'Lusid.Instrument']
        self.assertGreater(len(df), 0)

        # filter out all the columns
        df = df[df.FieldType != 'Column']
        result = TableMeta.data_provider_from_df(df)
        self.assertIsNone(result)

    def test_direct_provider_from_row_with_bad_data(self):

        df = process_direct_provider_metadata(self.df2[self.df2.TableName == 'Drive.Csv'].copy())
        self.assertGreater(len(df), 0)
        df['Category'] = 123
        result = TableMeta.direct_provider_from_row(df.iloc[0])
        self.assertIsNone(result)
