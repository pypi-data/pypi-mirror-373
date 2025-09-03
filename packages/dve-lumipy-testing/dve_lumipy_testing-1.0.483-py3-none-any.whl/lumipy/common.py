import io

import pandas as pd
from pandas import DataFrame
from lumipy.lumiflex._metadata.dtype import DType
from termcolor import colored
from typing import List, Dict


def indent_str(s: str, n: int = 3) -> str:
    """Generate a string that's indented by some number of spaces.

    Args:
        s (str): the input string. Can be a multiline string (contains '\n').
        n (int): in number of spaces to indent. Defaults to 3.

    Returns:
        str: the indented version of the string.
    """
    indent = ' ' * n
    return "\n".join(map(lambda x: f"{indent}{x}", s.split('\n')))


def table_spec_to_df(metadata: List[Dict[str, str]], data: str, **read_csv_params) -> DataFrame:
    """Convert the table dictionary in a restriction table filter to a pandas DataFrame

    Args:
        metadata (List[Dict[str, str]]): a list of dictionaries containing column metadata.
        data (str): the CSV of the table to parse into a dataframe.

    Returns:
        DataFrame: the CSV data parsed as a dataframe

    """

    read_csv_params['encoding'] = 'utf-8'
    read_csv_params['skip_blank_lines'] = False
    read_csv_params['filepath_or_buffer'] = io.StringIO(data)
    read_csv_params['dtype'] = str

    df = pd.read_csv(**read_csv_params)

    for col in metadata:
        name, dtype = col['name'], DType.datatype_to_dtype(col['type'])
        df[name] = DType.col_type_map(dtype)(df[name])

    return df


def emph(s):
    return colored(s, 'cyan', attrs=['bold'])


def red_print(s):
    print(colored(s, color='red', attrs=['bold']))


def emph_print(s):
    print(emph(s))


def e_print(s, end=''):
    eraser = '\r' + ' ' * 64 + '\r'
    print(eraser + s, end=end, flush=True)