from __future__ import annotations

from lumipy.lumiflex._common.str_utils import to_snake_case
from lumipy.lumiflex._metadata import DType


class UnaryCheck:

    def __init__(self, trigger, *dtypes: DType):
        self.trigger = trigger
        self.msg = f"must {'' if self.trigger else 'not '}be {'/'.join(d.name for d in dtypes)}"
        self.dtypes = dtypes

    def __call__(self, x) -> bool:
        from lumipy.lumiflex._table import TableOperation
        from lumipy.lumiflex.table import Table
        if isinstance(x, (Table, TableOperation)):
            return False

        if self.trigger:
            return x.dtype in self.dtypes
        return x.dtype not in self.dtypes

    def make_error_msg(self, name, x) -> str:
        from lumipy.lumiflex._table import TableOperation
        from lumipy.lumiflex.table import Table
        if isinstance(x, (Table, TableOperation)):
            return f'The input to \'{name}\' {self.msg} but was a {type(x).__name__}'

        return f'The input to \'{name}\' {self.msg} but was {x.dtype.name}={x.sql}'


class TableVarCheck:

    msg = "must be a Table"

    def __init__(self, *table_types):
        self.table_types = table_types

    def __call__(self, x) -> bool:
        from lumipy.lumiflex.table import Table
        return isinstance(x, Table) and x.meta_.type in self.table_types

    def make_error_msg(self, name, x) -> str:
        from lumipy.lumiflex._table import TableOperation
        from lumipy.lumiflex.table import Table

        if not isinstance(x, Table) and not isinstance(x, TableOperation):
            return f'The input to \'{name}\' must be Table object but was a {type(x).__name__}'

        if isinstance(x, TableOperation) and 'TableVar' in self.table_types:
            return f'The input to \'{name}\' must be Table object but was a .{to_snake_case(type(x).__name__)}() ' \
                   f'clause object. Did you forget to call .to_table_var()?'

        if isinstance(x, Table) and x.meta_.type in self.table_types:
            types_str = '/'.join(self.table_types)
            output = f'The input to \'{name}\' must be {types_str} but was a {x.meta_.type} table.'
            if 'TableVar' in self.table_types:
                output += f'\nYou may need to construct a query and then call .to_table_var() to make a table variable.'
            return output


class Is:
    any = UnaryCheck(True, *(t for t in DType))
    numeric = UnaryCheck(True, DType.Int, DType.BigInt, DType.Double, DType.Decimal)
    text = UnaryCheck(True, DType.Text)
    not_text = UnaryCheck(False, DType.Text)
    timelike = UnaryCheck(True, DType.Date, DType.DateTime)
    not_timelike = UnaryCheck(False, DType.Date, DType.DateTime)
    boolean = UnaryCheck(True, DType.Boolean)
    integer = UnaryCheck(True, DType.Int, DType.BigInt)
    double = UnaryCheck(True, DType.Double)
    date = UnaryCheck(True, DType.Date)
    not_null = UnaryCheck(False, DType.Null)
    table_var = TableVarCheck("TableVar")
    table = TableVarCheck("DataProvider", "TableVar")


class VariadicCheck:

    def __init__(self, trigger, fn, msg):
        self.trigger = trigger
        self.fn = fn
        self.msg = msg

    def __call__(self, *x) -> bool:
        if self.trigger:
            return self.fn(*x)
        return not self.fn(*x)

    def make_error_msg(self, names, xs) -> str:
        names_str = ", ".join(names)
        dtypes_str = ", ".join(f'{v.dtype.name} {v.sql}' for v in xs)
        error_msg = f'The inputs to ({names_str}) {self.msg} but were ({dtypes_str})'
        return error_msg


class Are:

    def __compare_checks(*args):

        comparable_types = {
            DType.Text: (DType.Text,),
            DType.Int: (DType.Int, DType.BigInt, DType.Double, DType.Decimal),
            DType.Double: (DType.Int, DType.BigInt, DType.Double, DType.Decimal),
            DType.Decimal: (DType.Int, DType.BigInt, DType.Double, DType.Decimal),
            DType.BigInt: (DType.Int, DType.BigInt, DType.Double, DType.Decimal),
            DType.Boolean: (DType.Boolean,),
            DType.Date: (DType.Date, DType.DateTime),
            DType.DateTime: (DType.Date, DType.DateTime),
        }

        return all(a.dtype in comparable_types[args[0].dtype] for a in args[1:])

    comparable = VariadicCheck(True, __compare_checks, 'must all be mutually-comparable types')
    all_text = VariadicCheck(True, lambda *args: all(v.dtype == DType.Text for v in args), 'must all be Text')
    any = VariadicCheck(True, lambda *args: True, 'No op - this should not error')
