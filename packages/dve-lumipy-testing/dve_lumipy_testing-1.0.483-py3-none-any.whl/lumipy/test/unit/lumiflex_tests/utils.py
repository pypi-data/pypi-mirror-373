import unittest

from lumipy.lumiflex._atlas.atlas import Atlas
from lumipy.lumiflex._atlas.utils import process_direct_provider_metadata
from lumipy.lumiflex._window.window import Window, OverPartition, OverOrder, OverFrame, OverFilter
from lumipy.lumiflex.column import Column
from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._metadata import ColumnMeta, ParamMeta, TableMeta, TableParamMeta
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._table.join import BaseTable
from lumipy.lumiflex.table import Table
from lumipy.lumiflex._table.content import CoreContent
from lumipy.lumiflex._table.parameter import Parameter
from typing import List, Tuple
from datetime import date, datetime
from lumipy.client import Client
from itertools import zip_longest
from functools import reduce
from pandas import DataFrame
import pandas as pd
import os


dtypes = [e for e in DType]
n_types = len(dtypes) - 1  # null type


class DummyClient(Client):

    def __init__(self):
        pass

    def query_and_fetch(self, sql) -> DataFrame:
        vals = [1, 123, 1.5, 1.2, True, 'ABC', date(2022, 1, 1), datetime(2023, 2, 2, 12, 4, 7)]

        def make_val(n):
            return vals[n % 8]

        return DataFrame([{f'Col{i}': make_val(i) for i in range(10)}])

    def get_domain(self):
        return 'nowhere'


class SqlTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        cls.df1 = pd.read_csv(file_dir + '/data/data_providers.csv')
        cls.df2 = pd.read_csv(file_dir + '/data/direct_providers.csv')

    @staticmethod
    def make_dummy_client() -> DummyClient:
        return DummyClient()

    @staticmethod
    def make_double_col(name, table_name='my.test.table') -> Column:
        return make(ColumnMeta(field_name=name, table_name=table_name, dtype=DType.Double))

    @staticmethod
    def make_double_cols(n, table_name='my.test.table') -> List[Column]:
        return [make(ColumnMeta(field_name=f'd{i}', table_name=table_name, dtype=DType.Double)) for i in range(n)]

    @staticmethod
    def make_int_col(name, table_name='my.test.table') -> Column:
        return make(ColumnMeta(field_name=name, table_name=table_name, dtype=DType.Int))

    @staticmethod
    def make_big_int_col(name, table_name='my.test.table') -> Column:
        return make(ColumnMeta(field_name=name, table_name=table_name, dtype=DType.BigInt))

    @staticmethod
    def make_boolean_col(name, table_name='my.test.table') -> Column:
        return make(ColumnMeta(field_name=name, table_name=table_name, dtype=DType.Boolean))

    @staticmethod
    def make_decimal_col(name, table_name='my.test.table') -> Column:
        return make(ColumnMeta(field_name=name, table_name=table_name, dtype=DType.Decimal))

    @staticmethod
    def make_text_col(name, table_name='my.test.table') -> Column:
        return make(ColumnMeta(field_name=name, table_name=table_name, dtype=DType.Text))

    @staticmethod
    def make_date_col(name, table_name='my.test.table') -> Column:
        return make(ColumnMeta(field_name=name, table_name=table_name, dtype=DType.Date))

    @staticmethod
    def make_datetime_col(name, table_name='my.test.table') -> Column:
        return make(ColumnMeta(field_name=name, table_name=table_name, dtype=DType.DateTime))

    @staticmethod
    def make_col_meta(x, is_main=True, table_name='my.test.table') -> ColumnMeta:
        return ColumnMeta(field_name=f'Col{x}', dtype=dtypes[x % n_types], is_main=is_main, table_name=table_name)

    @staticmethod
    def make_param_meta(x, table_name='my.test.table') -> ParamMeta:
        return ParamMeta(
            field_name=f'Param{x}', dtype=dtypes[x % n_types], table_name=table_name
        )

    @staticmethod
    def make_table_param_meta(x, n_cols, table_name='my.test.table') -> TableParamMeta:
        tv_name = f'TableVar_{x}'
        return TableParamMeta(
            field_name=tv_name,
            columns=[SqlTestCase.make_col_meta(i, table_name=tv_name) for i in range(n_cols)],
            table_name=table_name
        )

    @staticmethod
    def make_provider_meta(name='My.Table', n_cols=10, n_params=3, n_tv_params=0, type='DataProvider', alias=None) -> TableMeta:
        return TableMeta(
            name=name,
            columns=[SqlTestCase.make_col_meta(i, i % 2 == 0, name) for i in range(n_cols)],
            parameters=[SqlTestCase.make_param_meta(i, name) for i in range(n_params)],
            table_parameters=[SqlTestCase.make_table_param_meta(i, 5, name) for i in range(n_tv_params)],
            alias=alias,
            category='Testing',
            type=type
        )

    def make_parameters(self, p_metas) -> List[Parameter]:
        test_values = {
            DType.Int: make(123),
            DType.BigInt: make(1727364939238612),
            DType.Double: make(3.14),
            DType.Text: make('ABCDEF'),
            DType.Boolean: make(False),
            DType.Date: make(date(2022, 1, 1)),
            DType.DateTime: make(datetime(2000, 1, 1, 13, 3, 5))
        }
        return [Parameter(meta=p, parents=(test_values[p.dtype],)) for p in p_metas]

    def make_table_parameter(self, meta: TableParamMeta) -> Parameter:
        # make a table variable with the shape of the table parameter
        name = meta.field_name + '.test.table'
        table_meta = TableMeta(
            name=name,
            columns=[c.update(table_name=name) for c in meta.columns],
            category='Testing',
            type='DataProvider'
        )
        table = Table(meta=table_meta, client_=self.make_dummy_client(), parameters=tuple())
        tv = table.select('*').to_table_var(meta.field_name)

        # make table parameter assignment object
        return Parameter(meta=meta, parents=(tv,))

    def make_table(self, name='My.Test.Table', n_cols=10, n_params=3, n_tv_params=0) -> Table:
        meta = self.make_provider_meta(name, n_cols, n_params, n_tv_params)
        parameters = self.make_parameters(meta.parameters)
        table_parameters = [self.make_table_parameter(tpm) for tpm in meta.table_parameters]

        return Table(meta=meta, client_=self.make_dummy_client(), parameters=parameters + table_parameters)

    def make_table_content(self, table: BaseTable = None) -> CoreContent:
        if table is None:
            table = self.make_table()
        return CoreContent(
            table=table,
            parents=(table,),
            select_cols=table.get_columns(True)
        )

    def make_chained_join(self):
        t1 = self.make_table('my.table.one', n_cols=3, n_params=2)
        t2 = self.make_table('my.table.two', n_cols=2, n_params=3)
        t3 = self.make_table('my.table.three', n_cols=5, n_params=2)
        t4 = self.make_table('my.table.four', n_cols=4, n_params=1)

        return t1, t2, t3, t4, t1.inner_join(
            t2, t1.col0 == t2.col0, 'a', 'b'
        ).inner_join(
            t3, t3.col1 == t2.col0, "c"
        ).inner_join(
            t4, t4.col3 == t1.col0, "d"
        )

    def make_over_partition(self, table=None, n=4):
        if table is None:
            table = self.make_table()

        return OverPartition(parents=table.get_columns()[:n])

    def make_over_order(self, table=None, n=2):
        if table is None:
            table = self.make_table()

        return OverOrder(parents=[c.asc() for c in table.get_columns()[:n]])

    def make_over_filter(self, table=None, n=2):
        if table is None:
            table = self.make_table()
        condition = reduce(lambda x, y: x & y, [c > 0 for c in table.get_columns()[:n]])
        return OverFilter(parents=(condition,))

    def make_over_frame(self, lower=None, upper=0, exclude='no others'):
        return OverFrame(lower=lower, upper=upper, exclude=exclude)

    def make_window(self, table):

        partition = self.make_over_partition(table)
        order_by = self.make_over_order(table)
        frame = OverFrame(lower=10, upper=10)
        filter = OverFilter()

        return Window(parents=(partition, order_by, frame, filter))

    def make_window_table_pair(self) -> Tuple[Table, Window]:
        table = self.make_table()
        win = self.make_window(table)
        return table, win

    def make_table_var(self, label='one'):
        return self.make_table(f'my.table.{label}').select('*').to_table_var(f'test_{label}')

    def make_atlas(self, client=None) -> Atlas:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        df1 = pd.read_csv(file_dir + '/data/data_providers.csv')
        df2 = pd.read_csv(file_dir + '/data/direct_providers.csv')
        data_p_metas = [TableMeta.data_provider_from_df(gdf) for _, gdf in df1.groupby('TableName')]
        df = process_direct_provider_metadata(df2).fillna('Not available')
        direct_p_metas = [TableMeta.direct_provider_from_row(row) for _, row in df.iterrows()]

        p_metas = data_p_metas + direct_p_metas
        return Atlas(p_metas, self.make_dummy_client() if client is None else client)

    def assertHashEqual(self, x, y):
        self.assertEqual(hash(x), hash(y), msg=f'Hash missmatch between {x} and {y}')

    def assertSequenceHashEqual(self, x, y):
        _x = [hash(v) for v in x]
        _y = [hash(v) for v in y]
        self.assertSequenceEqual(_x, _y)

    def assertHashNotEqual(self, x, y):
        self.assertNotEqual(hash(x), hash(y))

    def assertErrorsWithMessage(self, fn, err_type, exp, skip_lines=None):
        with self.assertRaises(err_type) as err:
            fn()

        obs = str(err.exception)
        self.assertLineByLineEqual(exp, obs, skip_lines)

    def assertLineByLineEqual(self, exp, obs, skip_lines=None):

        if skip_lines is None:
            skip_lines = []

        # line by line comparison between exp and obs error messages
        obs_lines = obs.strip().split('\n')
        exp_lines = exp.strip().split('\n')

        mismatches = []
        for i, (x, y) in enumerate(zip_longest(exp_lines, obs_lines)):

            if i in skip_lines:
                print(f'Skipping line {i}')
                continue

            x = '[NO LINE]' if x is None else x
            y = '[NO LINE]' if y is None else y

            _x = x.strip().lower()
            _y = y.strip().lower()
            if _x != _y:
                mismatches.append((i, x, y))

        if len(mismatches) > 0:
            msg = lambda f: f'Line {f[0]}:\n     exp "{f[1].strip()}"\n     obs "{f[2].strip()}"'
            point = '\n   '
            mismatches = point + point.join(map(msg, mismatches))
            raise AssertionError(
                f'There are mismatches in the expected and observed SQL strings:{mismatches}\nFull obs error:\n{obs}'
            )

    def assertSqlEqual(self, x: str, y: str):

        x_lines = x.strip().split('\n')
        y_lines = y.strip().split('\n')

        failures = []
        for i, (x_line, y_line) in enumerate(zip_longest(x_lines, y_lines)):

            x_line = '[NO SQL LINE]' if x_line is None else x_line
            y_line = '[NO SQL LINE]' if y_line is None else y_line

            _x_line = x_line.strip().lower()
            _y_line = y_line.strip().lower()
            if _x_line.startswith('--') and _y_line.startswith('--'):
                continue

            if _x_line != _y_line:
                failures.append((i, x_line, y_line))

        if len(failures) > 0:
            msg = lambda f: f'SQL Line {f[0]}:\n     exp "{f[1].strip()}"\n     obs "{f[2].strip()}"'
            point = '\n   '
            mismatches = point + point.join(map(msg, failures))
            raise AssertionError(f'There are mismatches in the expected and observed SQL strings:{mismatches}')

    def assertTableColumnContent(self, table: Table, meta: TableMeta):
        for c_meta in meta.columns:
            self.assertTrue(hasattr(table, c_meta.python_name()))
            self.assertIsInstance(getattr(table, c_meta.python_name()), Column)
