from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Callable
from typing import Union, Type
from warnings import warn

import numpy as np
import pandas as pd
from luminesce.models import DataType

bool_map = {
    '0': False, '1': True,
    'True': True, 'False': False,
    'NULL': pd.NA, '': pd.NA,
    'true': True, 'false': False,
    'TRUE': True, 'FALSE': False
}


class DType(Enum):
    """Enum representing SQLite data types for luminesce columns and scalars.

    """

    Int = 0
    BigInt = 1
    Double = 2
    Decimal = 3
    Boolean = 4
    Text = 5
    Date = 6
    DateTime = 7
    Null = -999

    @staticmethod
    def pd_series_to_dtype(series: pd.Series) -> DType:
        if pd.api.types.is_bool_dtype(series):
            return DType.Boolean
        if pd.api.types.is_datetime64_any_dtype(series):
            return DType.DateTime
        if pd.api.types.is_string_dtype(series):
            return DType.Text
        if pd.api.types.is_float_dtype(series):
            return DType.Double
        if pd.api.types.is_integer_dtype(series):
            return DType.Int

        warn(f"No DType mapping for series dtype {series.dtype}. Defaulting to Text.")
        return DType.Text

    @staticmethod
    def to_dtype(dtype: Union[Type, DType, str]) -> DType:

        if dtype is None:
            return DType.Null

        if isinstance(dtype, DType):
            return dtype

        if isinstance(dtype, pd.Series):
            return DType.pd_series_to_dtype(dtype)

        if dtype in (int, np.int32, np.int64, pd.Int16Dtype(), pd.Int32Dtype(), pd.Int64Dtype(), 'Int32'):
            return DType.Int
        if dtype in (float, np.float32, np.float64, pd.Float32Dtype(), pd.Float64Dtype(), 'Double', 'Float'):
            return DType.Double
        if dtype in (bool, pd.BooleanDtype(), 'Boolean'):
            return DType.Boolean
        if dtype in (str, pd.StringDtype(), 'Csv', 'String'):
            return DType.Text
        if dtype in (datetime, pd.Timestamp, 'DateTime', np.datetime64, pd.DatetimeTZDtype("ns", tz="UTC")):
            return DType.DateTime
        if dtype in (date, 'Date'):
            return DType.Date
        if dtype is None or dtype in (type(pd.NA), type(pd.NaT), type(None)):
            return DType.Null

        warn(f"No DType mapping for type {dtype}. Defaulting to Text.")
        return DType.Text

    @staticmethod
    def datatype_to_dtype(data_type: DataType) -> DType:
        if data_type == DataType.BOOLEAN:
            return DType.Boolean
        if data_type == DataType.DATE:
            return DType.Date
        if data_type == DataType.DATETIME:
            return DType.DateTime
        if data_type == DataType.DECIMAL:
            return DType.Decimal
        if data_type == DataType.DOUBLE:
            return DType.Double
        if data_type == DataType.INT:
            return DType.Int
        if data_type == DataType.BIGINT:
            return DType.BigInt
        if data_type == DataType.TEXT:
            return DType.Text

        raise TypeError(f"No DType mapping for type {data_type}")

    def to_pytype(self) -> Type:

        if self in (DType.Int, DType.BigInt):
            return int
        if self == DType.Double:
            return float
        if self == DType.Text:
            return str
        if self == DType.Boolean:
            return bool
        if self == DType.Date:
            return date
        if self == DType.DateTime:
            return datetime
        if self == DType.Decimal:
            return float

        raise NotImplementedError(self.name)

    def num_priority(self, other: DType):
        if self.value > other.value:
            return self
        else:
            return other

    def col_type_map(self) -> Callable:

        def to_datetime(x):
            try:
                return pd.to_datetime(x)
            except ValueError:
                return pd.to_datetime(x, format='mixed', errors='coerce')

        if self == DType.Text:
            return lambda c: c.astype(pd.StringDtype())
        if self == DType.Int or self == DType.BigInt:
            return lambda c: c.astype(pd.Int64Dtype())
        if self == DType.Double:
            return lambda c: c.astype(np.float64)
        if self == DType.Boolean:
            return lambda c: c.replace(bool_map).astype(pd.BooleanDtype())
        if self == DType.Decimal:
            return lambda c: c.astype(np.float64)
        if self == DType.Date or self == DType.DateTime:
            return to_datetime

        raise TypeError(f'Unrecognised data type in column conversion: {self.name}')
