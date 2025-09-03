from __future__ import annotations

import re
from fnmatch import fnmatch
from typing import Optional, Literal, Union

import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel, StrictStr, model_validator, ValidationError

from lumipy.lumiflex._atlas.widgets import provider_widget
from lumipy.lumiflex._common.str_utils import model_repr
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._metadata.field import ColumnMeta, ParamMeta, TableParamMeta

import logging
from functools import wraps

logger = logging.getLogger(__name__)


def handle_validation_errors(fn):
    @wraps(fn)
    def wrapper(meta):
        try:
            return fn(meta)
        except ValidationError:
            if isinstance(meta, DataFrame) and len(meta) > 0:
                logger.warning(
                    '%s: data provider failed validation and will not be added to your atlas.',
                    meta.iloc[0].TableName)
            elif isinstance(meta, pd.Series):
                logger.warning(
                    '%s: direct provider failed validation and will not be added to your atlas.',
                    meta.TableName)
            else:
                logger.warning(f"A provider's metadata was empty! This should not happen.")
            return None

    return wrapper


class TableMeta(BaseModel):
    name: StrictStr
    columns: Union[tuple, None]
    parameters: tuple = tuple()
    table_parameters: tuple = tuple()
    category: StrictStr
    documentation_link: Optional[StrictStr] = 'No documentation link available'
    description: Optional[StrictStr] = 'No description available'
    type: Literal['DataProvider', 'DirectProvider', 'TableVar']
    namespace_level: Optional[int] = None
    attributes: Union[str, None] = None
    alias: Union[str, None] = None

    class Config:
        frozen = True
        extra = 'forbid'

    def update(self, **kwargs) -> TableMeta:
        return self.model_copy(update=kwargs)

    def __repr__(self):
        return model_repr(self)

    def python_name(self):
        return self.name.replace('.', '_').lower()

    def find_body_field(self):
        body = [p for p in self.parameters if p.is_body]
        if len(body) == 1:
            return body[0]
        return None

    # noinspection PyMethodParameters
    @model_validator(mode='before')
    def validate_fields(self):

        if 'name' not in self or 'columns' not in self:
            return self

        name = self['name']

        if len(name) == 0:
            raise ValueError()

        ok_chars = ['_', '.', '-']
        if not name[0].isalpha() or not all(c.isalnum() or c in ok_chars for c in name):
            ok_chars_str = ', '.join(f"'{s}'" for s in ok_chars)
            raise ValueError(
                f'Invalid table name: \'{name}\'. Must not start with a number, '
                f'and contain only alphanumeric chars + {ok_chars_str}.'
            )

        cols = self.get('columns')
        if cols is not None and len(cols) == 0:
            raise ValueError()

        if cols is not None and not all(isinstance(c, ColumnMeta) for c in cols):
            clss_str = ', '.join(type(c).__name__ for c in cols)
            raise TypeError(f'Columns must all be ColumnMeta objects but were ({clss_str}).')

        params = self.get('parameters', [])
        if not all(isinstance(c, ParamMeta) for c in params):
            clss_str = ', '.join(type(c).__name__ for c in params)
            raise TypeError(f'Parameters must all be ParamMeta objects but were ({clss_str}).')

        t_params = self.get('table_parameters', [])
        if not all(isinstance(c, TableParamMeta) for c in t_params):
            clss_str = ', '.join(type(c).__name__ for c in t_params)
            raise TypeError(f'Table parameters must all be TableParamMeta objects but were ({clss_str}).')

        if cols is not None and not all(c.table_name == name for c in cols):
            raise ValueError(f'There are columns given as input that do not belong to the table {name}.')
        if not all(c.table_name == name for c in params):
            raise ValueError(f'There are params given as input that do not belong to the table {name}.')
        if not all(c.table_name == name for c in t_params):
            raise ValueError(f'There are table params given as input that do not belong to the table {name}.')

        return self

    def update_fields(self, **kwargs) -> TableMeta:
        return self.model_copy(update=kwargs)

    @staticmethod
    @handle_validation_errors
    def data_provider_from_df(df):
        cols, params, tparams = [], [], []
        for _, row in df.iterrows():
            if row.FieldType == 'Column':
                cols.append(ColumnMeta.from_row(row))
            elif row.FieldType == 'Parameter' and row.DataType != 'Table':
                params.append(ParamMeta.from_row(row))
            elif row.FieldType == 'Parameter' and row.DataType == 'Table':
                tparams.append(TableParamMeta.from_row(row))
            else:
                raise ValueError(f'Unrecognised field type: {row.FieldType}.')
        doc_link = df.iloc[0].DocumentationLink
        descr_link = df.iloc[0].Description
        attrs = df.iloc[0].ProvAttributes
        return TableMeta(
            name=df.iloc[0].TableName,
            columns=cols,
            parameters=params,
            table_parameters=tparams,
            category=df.iloc[0].Category,
            documentation_link=doc_link if isinstance(doc_link, str) else None,
            description=descr_link if isinstance(descr_link, str) else None,
            type='DataProvider',
            namespace_level=df.iloc[0].NamespaceLevel,
            attributes=None if pd.isna(attrs) else None
        )

    @staticmethod
    @handle_validation_errors
    def direct_provider_from_row(row):

        t_name = row.TableName
        columns = None

        def make_column(name, dtype, description):
            return ColumnMeta(field_name=name, dtype=dtype, description=description, table_name=t_name, is_main=True)

        if fnmatch(t_name, '*.RawText*'):
            columns = [make_column('Content', DType.Text, 'The raw text from the target file.')]

        if fnmatch(t_name, '*.SaveAs*'):
            columns = [
                make_column('VariableName', DType.Text, 'Name of the @variable saved to a file.'),
                make_column('FileName', DType.Text, 'The file name.'),
                make_column('RowCount', DType.Int, 'The row count of the the @variable saved to a file.'),
                make_column('Skipped', DType.Boolean, 'Whether the @variable was skipped over.'),
            ]

        if t_name in ['Dev.Slack.Send', 'Email.Send']:
            columns = [
                make_column('Ok', DType.Text, 'Not available'),
                make_column('Request', DType.Text, 'Not available'),
                make_column('Result', DType.Text, 'Not available'),
            ]

        p_df = parse_direct_provider_help_table(row.ParamTable)

        params = []
        for _, p in p_df.iterrows():
            p = ParamMeta(
                field_name=p.Name,
                description=p.Description,
                dtype=DType.to_dtype(p.Type),
                table_name=t_name,
            )
            p = p.update(is_body=p.python_name() in row.BodyStrNames)
            params.append(p)

        p_names = [p.python_name() for p in params]
        for bstr_name in row.BodyStrNames:
            if bstr_name in p_names:
                continue
            params.append(ParamMeta(
                field_name=bstr_name,
                description=f'The body string that goes under "----" corresponding to {bstr_name}.',
                dtype=DType.Text,
                table_name=t_name,
                is_body=True
            ))

        return TableMeta(
            name=t_name,
            columns=tuple(columns) if columns is not None else columns,
            parameters=tuple(params),
            category=row.Category,
            documentation_link=row.DocumentationLink,
            description=row.Description,
            type='DirectProvider',
            namespace_level=row.NamespaceLevel,
            attributes=str(row.ProvAttributes)
        )

    def widget(self, opened=False):
        return provider_widget(self, opened)


def parse_direct_provider_help_table(text: str) -> DataFrame:
    df = DataFrame(
        [[c.strip() for c in line.split('│')] for line in text.split('\n')],
        columns=['Argument', 'Description']
    )
    df['Name'] = df.Argument.apply(
        lambda x: x if x != '' else None
    ).ffill().apply(
        lambda x: x.split()[0]
    )

    df = df.groupby('Name', sort=False, as_index=False).agg(
        Description=('Description', 'sum')
    )
    df['Type'] = df.Description.apply(
        lambda x: re.findall('\[.*\]', x)[-1] if 'Regex' in x else re.findall('\[.*?\]', x)[-1]
    ).apply(
        lambda x: x.replace('[', '').replace(']', '')
    ).apply(
        lambda x: x.split('Default:')[0].strip().strip(',')
    ).apply(
        lambda x: 'String' if len(x.split(',')) > 1 else x
    )

    df['DefaultValue'] = df.Description.apply(
        lambda x: re.findall('\[.*\]', x)[-1]
    ).apply(
        lambda x: x.replace('[', '').replace(']', '')
    ).apply(
        lambda x: x.split('Default:')[-1] if 'Default:' in x else None
    )
    return df
