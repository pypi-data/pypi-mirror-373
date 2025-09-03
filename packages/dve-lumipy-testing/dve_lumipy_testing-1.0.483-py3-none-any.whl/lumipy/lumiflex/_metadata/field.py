from __future__ import annotations

from typing import Optional, Union

from pydantic import BaseModel, StrictBool, StrictStr, model_validator

from lumipy.lumiflex._common.str_utils import model_repr
from lumipy.lumiflex._common.str_utils import to_snake_case
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._metadata.widgets import table_parameter_meta_widget, column_meta_widget, parameter_meta_widget


class FieldMeta(BaseModel):

    field_name: StrictStr
    table_name: Union[StrictStr, None]
    prefix: Optional[StrictStr] = None
    description: Optional[str] = 'No description available'

    class Config:
        frozen = True
        extra = 'forbid'

    def update(self, **kwargs) -> FieldMeta:
        return self.model_copy(update=kwargs)

    def python_name(self):
        return to_snake_case(self.field_name)

    def __repr__(self):
        return model_repr(self)


class ColumnMeta(FieldMeta):
    dtype: DType
    is_main: StrictBool = False
    is_primary_key: StrictBool = False
    params_hash: Union[int, None] = None

    @staticmethod
    def from_row(row):
        return ColumnMeta(
            field_name=row.FieldName,
            table_name=row.TableName,
            description=row.Description_fld,
            dtype=DType[row.DataType],
            is_main=bool(row.IsMain),
            is_primary_key=bool(row.IsPrimaryKey),
        )

    def __repr__(self):
        return f'{type(self).__name__}( {self.field_name}, {self.table_name}, {self.dtype.name}, {self.is_main} )'

    def widget(self, opened=False):
        return column_meta_widget(self, opened)


class ParamMeta(FieldMeta):
    dtype: DType
    is_body: StrictBool = False
    default_str: StrictStr = 'None'

    @staticmethod
    def from_row(row):
        return ParamMeta(
            field_name=row.FieldName,
            table_name=row.TableName,
            description=row.Description_fld,
            dtype=DType[row.DataType],
            default_str=str(row.ParamDefaultValue)
        )

    def __repr__(self):
        return f'{type(self).__name__}( {self.field_name}, {self.table_name}, {self.dtype.name}, {self.default_str} )'

    def widget(self, opened=False):
        return parameter_meta_widget(self, opened)


class TableParamMeta(FieldMeta):
    columns: Optional[tuple] = tuple()

    @model_validator(mode='before')
    def validate_columns(self):
        if not isinstance(self, dict):
            return self

        if 'columns' not in self or 'field_name' not in self:
            return self

        # assert columns is a tuple of ColumnMeta
        cols = self['columns']
        if any(not isinstance(c, ColumnMeta) for c in cols):
            clss_str = ', '.join(type(c).__name__ for c in cols)
            raise TypeError(f'All table param metadata columns must all be Column objects but were ({clss_str}).')

        # assert the column.table_name matches
        name = self['field_name']
        if any(c.table_name != name for c in cols):
            token = '\n\t'
            strs = token.join([f'{c.field_name}: {c.table_name}' for c in cols if c.table_name != name])
            raise ValueError(
                f'There are column metadata objects that don\'t belong to this table parameter metadata object ({name})'
                + token + strs
            )

        return self

    @staticmethod
    def from_row(row):
        name = row.FieldName
        table_name = row.TableName

        try:
            defs = [line.split() for line in row.TableParamColumns.split('\n') if line != '' and line != 'No schema']
            cols = [ColumnMeta(field_name=cd[0], table_name=name, dtype=DType[cd[1].strip('()')]) for cd in defs]
            return TableParamMeta(columns=cols, field_name=name, table_name=table_name)

        except KeyError:
            return TableParamMeta(columns=[], field_name=name, table_name=table_name, description=row.TableParamColumns)

    def widget(self, opened=False):
        return table_parameter_meta_widget(self, opened)
