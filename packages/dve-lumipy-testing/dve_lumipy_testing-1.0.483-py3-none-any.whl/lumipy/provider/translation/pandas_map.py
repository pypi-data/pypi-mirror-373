import numpy as np
import pandas as pd
from pandas import isna, to_datetime

from lumipy.provider.common import expression_to_table_spec
from lumipy.provider.metadata import DType

_REGEX_ESCAPES = {
    '\\?': 'xxxQUESTIONxxx',
    '\\*': 'xxxSTARxxx',
    '\\_': 'xxxUNDERSCORExxx',
    '\\%': 'xxxPERCENTxxx',
    ' ': 'xxxSPACExxx',
    '\n': 'xxxNEWLINExxx',
    '.': 'xxxDOTxxx',
    '-': 'xxxHYPHENxxx',
    '\\': 'xxxBACKSLASHxxx',
    '|': 'xxxBARxxx',
    '^': 'xxxCARETxxx',
    '$': 'xxxDOLLARxxx',
    '=': 'xxxEQUALSxxx',
    '!': 'xxxEXCLAIMATIONxxx',
    '<': 'xxxLESSTHANxxx',
    '>': 'xxxGREATERTHANxxx',
    ':': 'xxxCOLONxxx',
    '+': 'xxxPLUSxxx',
    '{': 'xxxCURLYLEFTxxx',
    '}': 'xxxCURLYRIGHTxxx',
    '[': 'xxxSQUARELEFTxxx',
    ']': 'xxxSQUARERIGHTxxx',
    '(': 'xxxROUNDLEFTxxx',
    ')': 'xxxROUNDRIGHTxxx',
}

leaves_map = {
    'DateValue': lambda x: to_datetime(x, utc=True),
    'BoolValue': lambda x: bool(x),
    'StrValue': lambda *x: str(x[0]) if len(x) == 1 else 'NULL',
    'NumValue': lambda x: float(x),
    'ListValue': lambda *xs: [x for x in xs],
}

numeric_map = {
    'Add': lambda x, y: x + y,
    'Subtract': lambda x, y: x - y,
    'Divide': lambda x, y: x / y,
    'Multiply': lambda x, y: x * y,
    'Mod': lambda x, m: x % m,
    'Round': lambda x, d: round(x, int(d)),
    'Log': np.log,
    'Log10': np.log10,
    'Abs': np.abs,
    'Exp': np.exp,
    'Power': lambda x, y: x ** y,
    'Sign': np.sign,
    'Sqrt': np.sqrt,
    'Square': np.square,
    'Ceil': np.ceil,
    'Floor': np.floor,
}


def substr(x, start, length):
    start, length = int(start), int(length)

    start -= 1 if start > 0 else 0
    end = start + length
    if start < 0 and end > -1:
        end = None

    if length < 0:
        return x.str.slice(max(end, 0), start)
    return x.str.slice(start, end)


str_map = {
    'Concatenate': lambda x, y: x + y,
    'Like': lambda x, p: _like(x, p),
    'NotLike': lambda x, p: ~_like(x, p) & ~isna(x),
    'Glob': lambda x, p: _glob(x, p),
    'NotGlob': lambda x, p: ~_glob(x, p) & ~isna(x),
    'Regexp': lambda x, p: _regexp(x, p),
    'NotRegexp': lambda x, p: ~_regexp(x, p) & ~isna(x),
    'Upper': lambda x: x.str.upper(),
    'Lower': lambda x: x.str.lower(),
    'Length': lambda x: x.str.len(),
    #todo: ltrim and rtrim are not exactly the same as str.strip()
    'Substr': substr,
    'Replace': lambda x, y, z: x.str.replace(y, z)
}


logical_map = {
    'And': lambda x, y: x & y,
    'Or': lambda x, y: x | y,
    'Lt': lambda x, y: x < y,
    'Lte': lambda x, y: x <= y,
    'Gt': lambda x, y: x > y,
    'Gte': lambda x, y: x >= y,
    'Eq': lambda x, y: x == y,
    'Neq': lambda x, y: x != y,
    'In': lambda x, y: x.isin(y),
    'NotIn': lambda x, y: ~x.isin(y) & ~isna(x),
    'Not': lambda x: ~x,
    'IsNull': lambda x: isna(x),
    'IsNotNull': lambda x: ~isna(x),
    'Between': lambda x, a, b: x.between(a, b, inclusive='both'),
    'NotBetween': lambda x, a, b: ~(x.between(a, b, inclusive='both')) & ~isna(x),
}


def strftime(x, y, *args):
    v = y.dt.strftime(x) if len(args) == 0 else None
    return v


dt_map = {
    'StrFTime': strftime,
    'JulianDay': lambda x: x.apply(pd.Timestamp.to_julian_date),
    'Date': lambda x, *args: strftime('%Y-%m-%d', x, *args)
}


def _cast(x, t):
    if t == 'Int':
        return np.floor(DType.Double.col_type_map()(x))
    return DType[t].col_type_map()(x)


def coalesce(*args):

    n = len(args[0])

    def map_val(v):
        if isinstance(v, pd.Series):
            return v
        else:
            return pd.Series([v] * n)

    vals_df = pd.concat([map_val(a) for a in args], axis=1)
    return vals_df.bfill(axis=1).iloc[:, 0]


def case(*args):
    conditions = [wt[0] for wt in args if isinstance(wt, tuple)]
    values = [wt[1] for wt in args if isinstance(wt, tuple)]
    default = [wt for wt in args if not isinstance(wt, tuple)]
    default = default[0] if len(default) == 1 else pd.NA
    res = np.select(conditions, values, default=default)
    return pd.Series(res)


def when_then(condition, value):
    return condition, value


other = {
    'Cast': lambda x, t: _cast(x, t),
    'Coalesce': lambda *a: coalesce(*a),
    'TableSpec': lambda x, y: expression_to_table_spec(x, y),
    'Case': lambda *args: case(*args),
    'WhenThen': lambda *args: when_then(*args)
}


agg_map = {
    'Min': lambda x: x.min(),
    'Max': lambda x: x.max(),
    'Total': lambda x: x.sum(),
    'Avg': lambda x: x.mean(),
    'Count': lambda x: len(x),
    'Median': lambda x: x.quantile(0.5),
    'Quantile': lambda x, y: x.quantile(y),
    'StDev': lambda x: x.std(),
    'CumeProd': lambda x: x.product(),
    'Covariance': lambda x, y, ddof: x.cov(y, ddof=ddof),
    'Coefficient_Of_Variation': lambda x: x.std() / x.mean(),
    'Group_Concat': lambda x, sep: sep.join(s for s in x if not pd.isna(s)),
}


pandas_map = {**logical_map, **numeric_map, **str_map, **leaves_map, **dt_map, **other, **agg_map}


def _apply_as_regex(char_wildcard, anylen_wildcard, case, series, pattern):
    for k, v in _REGEX_ESCAPES.items():
        pattern = pattern.replace(k, v)

    pattern = pattern.replace(char_wildcard, '(.|\\n)').replace(anylen_wildcard, '(.|\\n)*')

    for k, v in _REGEX_ESCAPES.items():
        pattern = pattern.replace(v, f'\\{k}')

    return series.str.fullmatch(pattern, na=False, case=case)


def _glob(series, pattern):
    return _apply_as_regex('?', '*', True, series, pattern)


def _like(series, pattern):
    v = _apply_as_regex('_', '%', False, series, pattern)
    return v


def _regexp(series, pattern):
    pattern = pattern if pattern.startswith('^') else '.*' + pattern
    return series.str.match(pattern, na=False, case=True)
