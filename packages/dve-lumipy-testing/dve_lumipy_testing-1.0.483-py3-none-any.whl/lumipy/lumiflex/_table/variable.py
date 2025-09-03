from __future__ import annotations

from abc import abstractmethod
from typing import Optional, Dict, Union, Literal

from pandas import DataFrame, isna
from pydantic import StrictStr, Field, StrictInt, model_validator

from lumipy.client import Client
from lumipy.common import indent_str
from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._common.str_utils import model_repr
from lumipy.lumiflex._metadata import TableMeta, ColumnMeta, DType
from lumipy.lumiflex._metadata.var_name import record
from lumipy.lumiflex._table.operation import TableOperation
from lumipy.lumiflex.column import Column
from lumipy.lumiflex.table import Table


class BaseVarDef(Node):

    client: Union[Client, None]
    name: Optional[str] = None

    @model_validator(mode='before')
    def validate_variable(self):
        return self

    @abstractmethod
    def table_sql(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def build(self) -> [Table, Column]:
        raise NotImplementedError()

    def __repr__(self):
        return model_repr(self, 'client', 'meta', 'client_', 'meta_')


class TableVar(BaseVarDef):
    label_: Literal['table_var_def'] = Field('table_var_def', alias='label')

    @model_validator(mode='before')
    def validate_variable(self):
        name = self['name']
        subquery = self['parents'][0]
        self['name'] = name if name is not None else record.make_name('tv', subquery)
        return self

    @property
    def subquery(self) -> TableOperation:
        return self.get_parents()[0]

    def table_sql(self) -> str:
        return self.subquery.content.get_sql()

    def __hash__(self) -> int:
        return hash(self.table_sql()) + hash(self.name)

    def make_meta(self) -> TableMeta:
        columns = [c.meta.update(table_name=self.name) for c in self.subquery.content.get_columns()]
        return TableMeta(name=self.name, columns=columns, category='TableVar', type='TableVar')

    def build(self) -> [Table, Column]:
        return Table(meta=self.make_meta(), client_=self.client, parents=(self,), parameters=tuple())


TableVar.update_forward_refs()


class DirectProviderVar(BaseVarDef):

    label_: Literal['direct_provider_def'] = Field('direct_provider_def', alias='label')
    meta: TableMeta
    use_params: Dict[str, str]
    limit: Union[None, StrictInt] = None

    @model_validator(mode='before')
    def validate_variable(self):
        name = self.get('name')
        meta = self['meta']
        params = self['use_params']

        params = {k: str(v) for k, v in params.items()}

        params_str = ''.join(k + v for k, v in params.items())

        if name is None:
            name = record.make_name(meta.name.replace('.', '_').lower(), hash(meta) + hash(params_str) + hash(self['parents']))

        self['name'] = name
        self['use_params'] = params

        return self

    def __hash__(self):
        return hash(self.meta) + hash(''.join(k + v for k, v in self.use_params.items()))

    def table_sql(self) -> str:

        with_str = ''
        if len(self.parents_):
            with_str = f"with {', '.join(p.from_ for p in self.parents_)}"

        limit_str = ''
        if self.limit is not None:
            limit_str = f'limit {self.limit}'

        body_meta = self.meta.find_body_field()

        content = []
        body = []
        for p, v in self.use_params.items():
            if body_meta is not None and p == body_meta.field_name:
                body.append(f'----\n{v}')
            else:
                content.append(f'--{p}={v}')

        content = indent_str('\n'.join(content + body), 6)

        return f'use {self.meta.name} {with_str} {limit_str}\n{content}\n   enduse'

    def make_meta(self) -> TableMeta:
        columns = [c.update(table_name=self.name) for c in self.meta.columns]
        return self.meta.update_fields(name=self.name, type='TableVar', columns=columns)

    def build(self) -> [Table, Column]:
        return Table(meta=self.make_meta(), client_=self.client, parents=(self,), parameters=tuple())


class TableLiteralVar(BaseVarDef):

    label_: Literal['table_literal_def'] = Field('table_literal_def', alias='label')
    df: DataFrame
    client: Union[Client, None] = None

    def __hash__(self):
        return hash(self.df.to_csv()) + hash(self.name)

    @model_validator(mode='before')
    def validate_variable(cls, values):
        df = values['df']
        name = values.get('name')
        if name is None:
            name = record.make_name('pandas_df', df.to_csv())
        values['name'] = name
        return values

    def table_sql(self) -> str:

        def make_row_str(row):
            def make_val(x):
                if isna(x):
                    return make(None)
                if isinstance(x, str) and "'" in x:
                    return make(x.replace("'", ""))
                if DType.to_dtype(type(x)) == DType.Text:
                    return make(str(x))
                return make(x)

            return f"({', '.join(make_val(v).sql for v in row)})"

        df = self.df

        column_content = [f'[column{i+1}] AS [{c}]' for i, c in enumerate(df.columns)]
        values_content = [make_row_str(row) for _, row in df.iterrows()]

        row_sep = ',\n'
        values = f'(VALUES\n{indent_str(row_sep.join(values_content))}\n)'
        columns = ', '.join(column_content)

        return f'SELECT\n{indent_str(columns)}\nFROM\n{indent_str(values)}'

    def make_meta(self) -> TableMeta:

        def col_meta_from_series(col_name: str) -> ColumnMeta:
            exemplar = self.df[~isna(self.df[col_name])][col_name]
            if len(exemplar) > 0:
                dtype = DType.to_dtype(type(exemplar.iloc[0]))
            else:
                dtype = DType.Text
            cmeta = ColumnMeta(field_name=col_name, table_name=self.name, dtype=dtype)
            return cmeta

        columns = [col_meta_from_series(c) for c in self.df.columns]
        return TableMeta(name=self.name, columns=columns, category='Literal', type='TableVar')

    def build(self) -> [Table, Column]:
        return Table(meta=self.make_meta(), client_=self.client, parents=(self,), parameters=tuple())


class DriveWriteVar(BaseVarDef):

    label_: Literal['drive_write_def'] = Field('drive_write_def', alias='label')
    file_path: StrictStr

    @model_validator(mode='before')
    def validate_variable(self):
        subquery = self['parents'][0]
        self['name'] = record.make_name('drive_write', subquery)
        return self

    def table_sql(self) -> str:

        tv = self.get_parents()[0]

        parts = self.file_path.split('/')

        directory = '/'.join(parts[:-1])
        file_name, file_type = parts[-1].split('.')

        return f'''use Drive.SaveAs with {tv.from_}
          --type={file_type}
          --path={directory}
          --fileNames={file_name}
        enduse'''

    def make_meta(self) -> TableMeta:
        columns = [
            ColumnMeta(field_name='VariableName', table_name=self.name, dtype=DType.Text),
            ColumnMeta(field_name='FileName', table_name=self.name, dtype=DType.Text),
            ColumnMeta(field_name='RowCount', table_name=self.name, dtype=DType.Text),
            ColumnMeta(field_name='Skipped', table_name=self.name, dtype=DType.Boolean),
        ]
        return TableMeta(name=self.name, columns=columns, type='TableVar', category='TableVar')

    def build(self) -> [Table, Column]:
        return Table(meta=self.make_meta(), client_=self.client, parents=(self,), parameters=tuple())


class MakeViewVar(BaseVarDef):

    label_: Literal['make_view_def'] = Field('make_view_def', alias='label')
    view_name: StrictStr
    subquery: TableOperation

    @model_validator(mode='before')
    def validate_variable(self):
        subquery = self['parents'][0]
        self['name'] = record.make_name('make_view', subquery)
        self['subquery'] = subquery
        return self

    @property
    def subquery(self) -> TableOperation:
        return self.get_parents()[0]

    def table_sql(self) -> str:
        content_lines = [
            f'--provider={self.view_name}',
            '-----------',
            indent_str(self.subquery.get_sql(), 4),
        ]
        content = indent_str('\n'.join(content_lines), 4)
        return f'use Sys.Admin.SetupView\n{content}\nenduse'

    def make_meta(self) -> TableMeta:
        tv_meta = self.subquery.to_table_var().meta_
        cols = [c.update(table_name=self.name) for c in tv_meta.columns]
        return tv_meta.update_fields(name=self.name, columns=cols)

    def build(self) -> [Table, Column]:
        return Table(meta=self.make_meta(), client_=self.client, parents=(self,), parameters=tuple())


class ScalarVar(BaseVarDef):

    label_: Literal['scala_var_def'] = Field('scalar_var_def', alias='label')

    @model_validator(mode='before')
    def validate_variable(self):
        name = self['name']
        subquery = self['parents'][0]
        name = name if name is not None else record.make_name('sv', subquery)
        self['name'] = '@' + name
        return self

    @property
    def subquery(self) -> TableOperation:
        return self.get_parents()[0]

    def table_sql(self) -> str:
        return self.subquery.content.get_sql()

    def __hash__(self) -> int:
        return hash(self.table_sql()) + hash(self.name)

    def build(self) -> [Table, Column]:
        column = self.subquery.content.get_columns()[0]
        return Column(fn=lambda x: f'@{self.name}', parents=(self,), dtype=column.dtype, label='const')
