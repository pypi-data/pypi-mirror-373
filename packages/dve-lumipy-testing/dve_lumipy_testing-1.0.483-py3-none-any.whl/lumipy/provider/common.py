import re
import subprocess
from importlib.util import find_spec
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError
from typing import Union

import numpy as np
import pandas as pd
import logging
from pandas import CategoricalDtype, Series
from semver import Version

from lumipy.common import indent_str
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.provider.max_version import max_version_str

_min_version_dotnet_6 = Version.parse('1.17.340')
_max_version_dotnet_6 = Version.parse('1.17.375')  # Final published binary that runs .NET 6, soon to be totally invalid already no longer downloadable.

_min_version_dotnet_8 = Version.parse('1.18.531')  # First published binary that uses DirectReplyToFeedback + Streams for cancellation
_max_version_dotnet_8 = Version.parse(max_version_str)

_dotnet8_status = None

logger = logging.getLogger(__name__)

def infer_datatype(col: Series) -> DType:
    """Map the type of pandas Series to its corresponding SQL column type.

    Args:
        col (Series): the input series to infer the type of.

    Returns:
        DType: the SQL column type.
    """
    pd_dtype = col.dtype

    if pd_dtype == int:
        return DType.Int
    elif pd_dtype == float:
        return DType.Double
    elif pd_dtype == bool:
        return DType.Boolean
    elif isinstance(pd_dtype, CategoricalDtype):
        return DType.Text
    elif isinstance(pd_dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
        return DType.DateTime
    elif np.issubdtype(pd_dtype, np.datetime64):
        raise ValueError(
            f"The pandas DataFrame column '{col.name}' used to build the provider was not tz-aware. "
            f"Datetime values in pandas providers must be tz-aware.\n"
            "  Consider using the following (e.g. for the UTC timezone)\n"
            "    df['column'] = df['column'].dt.tz_localize(tz='utc')\n"
            "  to convert an existing DataFrame datetime column."
        )
    else:
        return DType.Text


def df_summary_str(d):
    mem_use = pd.DataFrame.memory_usage(d, deep=True)
    max_col_len = max(len(k) for k in mem_use.keys())
    divider = '―' * (max_col_len + 11)

    def format_size(x):

        units = [['TB😱', 1e12], ['GB', 1e9], ['MB', 1e6], ['KB', 1e3], ['B ', 1e0]]

        for upper, lower in zip(units[:-1], units[1:]):
            if upper[1] > x >= lower[1]:
                vstr = f'{x / lower[1]:6.1f}'
                return f'{vstr:6} {lower[0]}'

    strs = [divider]
    for k, v in mem_use.items():
        strs.append(f'{k:{max_col_len}}  {format_size(v)}')

    strs.append(divider)
    strs.append(f'{"Total":{max_col_len}}  {format_size(mem_use.sum())}')
    strs.append(divider)

    table_str = '\n'.join(map(lambda x: f'| {x} |', strs))

    return '\n'.join([
        '\n',
        'DataFrame Stats',
        f'    Number of rows: {d.shape[0]}',
        f'    Number of cols: {d.shape[1]}',
        '    Memory Usage:',
        f'{indent_str(table_str, 6)}',
        '',
    ])


def clean_colname(c_str):
    return str(c_str).replace('.', '_').replace("'", "").strip().strip('_')


def available(*args):
    return all(find_spec(name) is not None for name in args)


def get_dll_path(sdk_version) -> Path:
    return Path.home() / '.lumipy' / 'python_providers' / sdk_version.replace('.', '_')

def get_dll_path(ver, fbn_run = False) -> Path:
    if fbn_run:
        return Path.home() / 'PythonProviders'

    if ver is not None and semver_has_dll(ver):
        return Path.home() / '.lumipy' / 'python_providers' / ver.replace('.', '_') / 'tools' / _dotnet_string() / 'any'

    raise ValueError("No valid Python provider dlls were found.")

def get_certs_path(domain) -> Path:
    return Path.home() / '.lumipy' / 'certs' / domain


def get_latest_local_python_provider_semver() -> Union[None, str]:
    lm_path = Path.home() / '.lumipy' / 'python_providers'
    folders = [f.parts[-1].replace('_', '.') for f in lm_path.glob('*_*_*')]
    sem_vers = sorted([Version.parse(f) for f in folders if Version.is_valid(f)])
    sem_vers = [sv for sv in sem_vers if min_version() <= sv <= max_version()]
    if len(sem_vers) == 0:
        return None
    return str(sem_vers[-1])


def _dotnet_string():
    return 'net8.0' if _has_dotnet8() else 'net6.0'


def semver_has_dll(semver) -> bool:
    path = Path.home() / '.lumipy' / 'python_providers' / semver.replace('.', '_') / 'tools' / _dotnet_string() / 'any' / 'Finbourne.Honeycomb.Host.dll'
    return path.exists()


def expression_to_table_spec(meta, content):
    _meta = [{'name': a.args[0], 'type': a.args[1]} for a in meta.args]
    _content = content.args[0]
    return _meta, _content


def strtobool(val) -> int:
    val = val.lower()

    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


def _get_latest_major_semver(semvers: list[str]) -> Union[int, None]:
    valid_dotnet_major_versions = [int(x.split('.')[0]) for x in semvers]

    if len(valid_dotnet_major_versions) == 0:
        return None

    valid_dotnet_major_versions.sort(reverse=True)

    return valid_dotnet_major_versions[0]


def _has_dotnet8() -> bool:
    """
    Lazily sets the _dotnet8_status when we use the min_version() or max_version() funcs

    Sets _dotnet8_status to True if .NET 8 is installed
    Sets _dotnet8_status to False if .Net 8 is NOT installed

    Raises a ValueError if:
      - No .NET runtime is detected, or
      - Neither .NET 8 nor .NET 6 is installed.
    """
    global _dotnet8_status
    
    if _dotnet8_status is not None:
        return _dotnet8_status

    semver_regex_dotnet_6_8 = r'([68]\.\d+\.\d+)'
    instruction = "Please install .NET 8.0."

    if which('dotnet') is None:
        raise ValueError(f".NET runtime not found. {instruction}")

    try:
        result = subprocess.run(["dotnet", "--list-sdks"], capture_output=True, text=True, check=True)
    except CalledProcessError:
        raise ValueError(f"Error when trying to list .NET SDKs. {instruction}")

    valid_semvers = re.findall(semver_regex_dotnet_6_8, result.stdout)

    if len(valid_semvers) == 0:
        raise ValueError(f"You must install the .NET 8 SDK. The .NET 6 SDK will also work but its associated binaries are no longer maintained")

    _dotnet8_status = _get_latest_major_semver(valid_semvers) == 8

    if not _dotnet8_status:
        logger.warning(".NET 8 SDK not found, using .NET 6 instead. Please upgrade to .NET 8 to use newer Python Provider binaries (1.18.0+)")

    return _dotnet8_status

def min_version() -> Version:
    if _has_dotnet8():
        return _min_version_dotnet_8
    else:
        return _min_version_dotnet_6

def max_version() -> Version:
    if _has_dotnet8():
        return _max_version_dotnet_8
    else:
        return _max_version_dotnet_6
