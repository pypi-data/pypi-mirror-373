import datetime as dt
from typing import Optional, List, Union, Iterator

import numpy as np
import pandas as pd
from pandas import DataFrame

from lumipy.lumiflex import DType
from lumipy.provider import BaseProvider, ColumnMeta, ParamMeta, TableParam, Context
from lumipy.provider.context import Expression
from lumipy.provider.metadata import RegistrationCategory, RegistrationAttributes, LifeCycleStage


class TestProvider(BaseProvider):

    def __init__(
            self,
            name: Optional[str] = 'Test.PyProvider',
            columns: Optional[List[ColumnMeta]] = None,
            parameters: Optional[List[ParamMeta]] = None,
            table_parameters: Optional[List[TableParam]] = None,
            description: Optional[str] = 'A test provider to test the base provider class.',
            documentation_link: Optional[str] = 'https://not-the-real-docs.com/docs',
            license_code: Optional[str] = None,
            registration_category: Optional[RegistrationCategory] = RegistrationCategory.OtherData,
            registration_attributes: Optional[RegistrationAttributes] = RegistrationAttributes.none,
            lifecycle_stage: Optional[LifeCycleStage] = LifeCycleStage.Experimental,
    ):

        columns = columns if columns is not None else [
            ColumnMeta('ColA', DType.Text, 'Test Col A', True, True),
            ColumnMeta('ColB', DType.Int, 'Test Col B', True, True),
            ColumnMeta('ColC', DType.Double, 'Test Col C'),
            ColumnMeta('ColD', DType.Date, 'Test Col D'),
            ColumnMeta('ColE', DType.DateTime, 'Test Col E'),
            ColumnMeta('ColF', DType.Boolean, 'Test Col F')
        ]
        parameters = parameters if parameters is not None else []
        parameters += [
            ParamMeta('ProgressLinePeriod', DType.Int),
            ParamMeta('SysInfoLinePeriod', DType.Int),
            ParamMeta('ThrowError', DType.Boolean),
            ParamMeta('SetIsAgg', DType.Boolean, default_value=False),
            ParamMeta('SetIsOrdered', DType.Boolean, default_value=False),
            ParamMeta('SetIsOffset', DType.Boolean, default_value=False),
            ParamMeta('ReturnBadData', DType.Boolean, default_value=False),
            ParamMeta('ReturnNothing', DType.Boolean, default_value=False),
        ]
        table_parameters = table_parameters if table_parameters is not None else [
            TableParam('TestTable', columns=[ColumnMeta('TV1', DType.Text), ColumnMeta('TV2', DType.Int)])
        ]
        super().__init__(
            name, columns, parameters, table_parameters,
            description=description,
            documentation_link=documentation_link,
            license_code=license_code,
            registration_category=registration_category,
            registration_attributes=registration_attributes,
            lifecycle_stage=lifecycle_stage,
        )

    def _make_rand_col_values(self) -> DataFrame:

        row = {}

        for name, col in self.columns.items():
            if col.data_type == DType.Text:
                row[name] = ''.join(np.random.choice(list('ABCDEF'), size=10, replace=True))
            elif col.data_type == DType.Int:
                row[name] = np.random.randint(-10, 10)
            elif col.data_type == DType.Double:
                row[name] = np.random.normal()
            elif col.data_type == DType.Date:
                row[name] = dt.date(2022, 1, 1) + dt.timedelta(days=np.random.randint(365))
            elif col.data_type == DType.DateTime:
                row[name] = dt.datetime(2022, 1, 1) + dt.timedelta(days=np.random.uniform(365.24))
            elif col.data_type == DType.Boolean:
                row[name] = np.random.binomial(1, 0.5) == 1
            else:
                raise ValueError(f'Unsupported type: {col.data_type}.')

        return DataFrame([row])

    @staticmethod
    def _make_agg():
        np.random.seed(2121)
        return pd.DataFrame({
            'Agg0': np.random.uniform(size=5),
            'Agg1': np.random.randint(0, 10, size=5),
            'Agg2': np.random.choice(list('ABCDEF'), size=5)
        })

    def get_data(self, context: Context) -> Union[DataFrame, Iterator[DataFrame]]:

        np.random.seed(1989)

        limit = context.limit()
        limit = limit if limit else 5

        context.is_agg = context.get('SetIsAgg')
        context.is_ordered = context.get('SetIsOrdered')
        context.is_offset = context.get('SetIsOffset')

        pl_period = context.get('ProgressLinePeriod')
        si_period = context.get('SysInfoLinePeriod')

        if context.get('ReturnNothing'):
            yield self.empty_row()
        elif context.is_agg:
            yield self._make_agg()
        else:
            for i in range(limit):
                if pl_period and (i % pl_period) == 0:
                    yield self.progress_line(f'Test progress {i}')

                if si_period and (i % si_period) == 0:
                    yield self.sys_info_line(f'Test sys info {i}')

                if context.get('ThrowError') and i == 5:
                    raise ValueError(f"Throwing test error after {i} steps.")

                if context.get('ReturnBadData'):
                    yield DataFrame([{'Some': 10, 'Bad': 'A', 'Cols': True}])

                yield self._make_rand_col_values()

    @staticmethod
    def variant1(name: str = 'Test.PyProvider.Variant1'):

        name = name
        descr = 'A new description'
        doclink = 'https://a-new-loc.com/other'
        reg_cat = RegistrationCategory.Utilities
        reg_att = RegistrationAttributes.Generator
        life_cy = LifeCycleStage.Beta

        return TestProvider(
            name=name,
            columns=[ColumnMeta('C1', DType.Int), ColumnMeta('C2', DType.Text)],
            parameters=[ParamMeta('Extra', DType.Text)],
            table_parameters=[
                TableParam('TV1', [ColumnMeta('A', DType.Int)]),
                TableParam('TV2', [ColumnMeta('C', DType.Text)])
            ],
            description=descr,
            documentation_link=doclink,
            registration_category=reg_cat,
            registration_attributes=reg_att,
            lifecycle_stage=life_cy
        )


class TestFilterProvider(BaseProvider):

    def __init__(self):

        super().__init__(
            'test.filter.pyprovider',
            columns=[
                ColumnMeta('NodeId', DType.Int),
                ColumnMeta('OpName', DType.Text),
                ColumnMeta('Input', DType.Text),
            ]
        )

    def get_data(self, context: Context) -> DataFrame:

        flattened = []

        def flatten(ex: Expression):

            flattened.append({
                'OpName': ex.op,
                'Input': ex.json()
            })

            if ex.op.endswith('Value'):
                return
            else:
                [flatten(a) for a in ex.args]

        flatten(context.where_clause)

        return DataFrame({**{'NodeId': i}, **d} for i, d in enumerate(flattened))


class TestTableParamProvider(BaseProvider):

    def __init__(self):
        columns = [
            ColumnMeta('TableVarName', DType.Text),
            ColumnMeta('TableVarColName', DType.Text),
            ColumnMeta('TableVarColType', DType.Text),
            ColumnMeta('TableVarNumCols', DType.Int),
            ColumnMeta('TableVarNumRows', DType.Int),
        ]
        table_params = [
            TableParam('TestTable1'),
            TableParam('TestTable2'),
            TableParam('TestTable3'),
        ]
        super().__init__('test.tableparam.pyprovider', columns=columns, table_parameters=table_params)

    def get_data(self, context) -> DataFrame:

        def make_cols(name):
            df = context.get(name)
            return DataFrame(
                {
                    'TableVarName': name,
                    'TableVarColName': n,
                    'TableVarColType': t.name,
                    'TableVarNumCols': df.shape[1],
                    'TableVarNumRows': df.shape[0],
                }
                for n, t in df.dtypes.items()
            )

        for i in range(1, 4):
            yield make_cols(f'TestTable{i}')


class ParameterAndLimitTestProvider(BaseProvider):

    def __init__(self):
        columns = [
            ColumnMeta('Name', DType.Text),
            ColumnMeta('StrValue', DType.Text),
            ColumnMeta('Type', DType.Text),
        ]
        params = [
            ParamMeta('Param1', data_type=DType.Int, default_value=0),
            ParamMeta('Param2', data_type=DType.Text, default_value='ABC'),
            ParamMeta('Param3', data_type=DType.Double, default_value=3.1415),
            ParamMeta('Param4', data_type=DType.Date, default_value=dt.datetime(2022, 1, 1, 13, 15, 2)),
            ParamMeta('Param5', data_type=DType.DateTime, is_required=True),
            ParamMeta('Param6', data_type=DType.Boolean, default_value=False),
        ]
        super().__init__('test.pyprovider.paramsandlimit', columns=columns, parameters=params)

    def get_data(self, context: Context) -> DataFrame:
        rows = [
            {
                'Name': name,
                'StrValue': str(context.get(name)),
                'Type': type(context.get(name)).__name__,
            }
            for name in self.parameters.keys()
        ]
        rows.append({'Name': 'limit', 'StrValue': str(context.limit()), 'Type': type(context.limit()).__name__})
        rows.append({'Name': 'offset', 'StrValue': str(context.offset()), 'Type': type(context.offset()).__name__})
        context.is_offset = context.offset() is not None and context.offset() > 0

        return DataFrame(rows)


class IdentityContextTestProvider(BaseProvider):

    def __init__(self):
        super().__init__(
            'test.identity.context',
            columns=[ColumnMeta('Name', DType.Text), ColumnMeta('Value', DType.Text)]
        )

    def get_data(self, context: Context) -> Union[DataFrame, Iterator[DataFrame]]:
        def make_row(name, val):
            if name == 'user_groups' and val is not None:
                val = ','.join(val)
            return {'Name': name, 'Value': val}

        return pd.DataFrame(make_row(k, v) for k, v in context.identity.dict().items())
