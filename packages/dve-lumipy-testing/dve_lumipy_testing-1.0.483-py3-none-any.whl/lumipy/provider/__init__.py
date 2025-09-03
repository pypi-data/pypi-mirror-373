import os
from importlib.util import find_spec

from lumipy.provider.context import Context
from .base_provider import BaseProvider
from .implementation.pandas_provider import PandasProvider
from .manager import ProviderManager
from .metadata import ColumnMeta, ParamMeta, TableParam
from lumipy.lumiflex._metadata.dtype import DType


if os.name == 'nt':
    os.system('color')

if find_spec('cvxopt') is not None:
    from .implementation.index_builder import QuadraticProgram

if find_spec('yfinance') is not None:
    from .implementation.yfinance_provider import YFinanceProvider

if find_spec('wbgapi') is not None:
    from .implementation.world_bank import (
        WorldBankDataSources,
        WorldBankEconomies,
        WorldBankSeriesMetadata,
        WorldBankSeriesData,
    )
