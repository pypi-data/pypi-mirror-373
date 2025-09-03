from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex.table import Table


class TestTableConstruction(SqlTestCase):

    def test_table_ctor_data_no_alias(self):
        name = 'My.Test.Table'
        meta = self.make_provider_meta(name=name, n_params=2)
        params = self.make_parameters(meta.parameters)
        table = Table(
            meta=meta,
            parameters=params,
            client_=self.make_dummy_client(),
        )
        self.assertEqual(f'[{name}]', table.from_)
        self.assertEqual('data_table', table.get_label())
        meta = meta.update(columns=table.meta_.columns)
        self.assertEqual(meta, table.meta_)
        self.assertSequenceEqual(params, table.parameters_)
        self.assertTableColumnContent(table, meta)

    def test_table_ctor_data_with_alias(self):
        name = 'My.Test.Table'
        meta = self.make_provider_meta(name=name, n_params=2, alias='ABC')
        params = self.make_parameters(meta.parameters)
        table = Table(
            meta=meta,
            parameters=params,
            client_=self.make_dummy_client(),
        )
        self.assertEqual(f'[{name}] AS ABC', table.from_)
        self.assertEqual('data_table', table.get_label())
        meta = meta.update(columns=table.meta_.columns)
        self.assertEqual(meta, table.meta_)
        exp = [p.with_prefix('ABC') for p in params]
        self.assertSequenceEqual(exp, table.parameters_)
        self.assertTableColumnContent(table, meta)

    def test_table_ctor_variable_no_alias(self):
        name = 'my_test_var'
        meta = self.make_provider_meta(name=name, n_params=2, type='TableVar')
        params = self.make_parameters(meta.parameters)
        table = Table(
            meta=meta,
            parameters=params,
            client_=self.make_dummy_client(),
        )

        self.assertEqual(f'@{name}', table.from_)
        self.assertEqual('data_table', table.get_label())
        meta = meta.update(columns=table.meta_.columns)
        self.assertEqual(meta, table.meta_)
        self.assertSequenceEqual(params, table.parameters_)
        self.assertTableColumnContent(table, meta)

    def test_table_ctor_variable_with_alias(self):
        name = 'my_test_var'
        meta = self.make_provider_meta(name=name, n_params=2, type='TableVar', alias='ABC')
        params = self.make_parameters(meta.parameters)
        table = Table(
            meta=meta,
            parameters=params,
            client_=self.make_dummy_client(),
        )

        self.assertEqual(f'@{name} AS ABC', table.from_)
        self.assertEqual('data_table', table.get_label())
        meta = meta.update(columns=table.meta_.columns)
        self.assertEqual(meta, table.meta_)
        exp = [p.with_prefix('ABC') for p in params]
        self.assertSequenceEqual(exp, table.parameters_)
        self.assertTableColumnContent(table, meta)

    def test_table_built_from_to_table_var(self):

        table = self.make_table('my.test.table', n_cols=6, n_params=3, n_tv_params=1)

        tv = table.select('*', Col1_Test=table.col1).to_table_var('tv_x')

        self.assertEqual(len(table.get_columns()) + 1, len(tv.get_columns()))
        self.assertTrue(all(c.meta.table_name == 'tv_x' for c in tv.get_columns()))
        self.assertTrue(tv.col1_test in tv)
