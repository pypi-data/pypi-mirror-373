import inspect
from abc import ABC, abstractmethod, ABCMeta
from datetime import date, datetime

from lumipy.client import Client
from lumipy.common import indent_str
from lumipy.lumiflex._atlas.widgets import provider_widget
from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._common.widgets import display
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._metadata.field import ParamMeta, TableParamMeta, ColumnMeta
from lumipy.lumiflex._metadata.table import TableMeta
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._method_tools.method_tools import assemble_error
from lumipy.lumiflex._method_tools.method_tools import check_kwargs
from lumipy.lumiflex._table import DirectProviderVar
from lumipy.lumiflex._table.operation import TableOperation, dependency_sql
from lumipy.lumiflex._table.parameter import Parameter
from lumipy.lumiflex.table import Table


def generate_data_call_signature(meta: TableMeta) -> inspect.Signature:

    params = [inspect.Parameter('self', inspect.Parameter.POSITIONAL_ONLY)]
    params += [inspect.Parameter(p.python_name(), inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=DType.to_pytype(p.dtype)) for p in meta.parameters]
    params += [inspect.Parameter(p.python_name(), inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Table) for p in meta.table_parameters]

    return inspect.Signature(params, return_annotation=Table)


def generate_direct_call_signature(meta: TableMeta) -> inspect.Signature:
    params = [inspect.Parameter('self', inspect.Parameter.POSITIONAL_ONLY),
              inspect.Parameter('with_vars', inspect.Parameter.VAR_POSITIONAL, annotation=Table)]
    for p in meta.parameters:
        params.append(inspect.Parameter(p.python_name(), inspect.Parameter.KEYWORD_ONLY, annotation=DType.to_pytype(p.dtype)))

    params.append(inspect.Parameter('apply_limit', inspect.Parameter.KEYWORD_ONLY, annotation=int))

    return inspect.Signature(params, return_annotation=Table)


def generate_call_docstring(meta: TableMeta) -> str:

    def param_line(x: ParamMeta):
        py_type_str = DType.to_pytype(x.dtype).__name__
        return f"{x.python_name()} ({py_type_str}): {x.description}"

    def table_param_line(x: TableParamMeta):
        return f"{x.python_name()} (Table): {x.description}"

    doc = f'Create a Table instance for the {meta.name} provider.\n\n'
    doc += f"Provider Description:\n    {meta.description}\n\n"
    doc += f"Provider Documentation:\n    {meta.documentation_link}\n\n"

    arg_lines = [param_line(p) for p in meta.parameters]
    arg_lines += [table_param_line(p) for p in meta.table_parameters]
    if meta.type == 'DirectProvider':
        arg_lines.append("apply_limit (int): limit to apply to the direct provider call")
        arg_lines.insert(0, "*with_vars (Table): the @/@@ variables to be used with the direct provider call")

    if len(arg_lines) > 0:
        args_str = '\n'.join(arg_lines)
        doc += f"Args: \n{indent_str(args_str, 6)}"

    doc += '\n\n'
    doc += f'Returns:\n'
    doc += f'    Table: the Table instance for querying {meta.name} with the given parameter values.'

    return doc


def get_type_constraint(x: ParamMeta):
    if x.dtype == DType.Double:
        return Is.numeric
    if x.dtype == DType.Int or x.dtype == DType.BigInt:
        return Is.integer
    if x.dtype == DType.Date:
        return Is.timelike
    if x.dtype == DType.DateTime:
        return Is.timelike
    if x.dtype == DType.Decimal:
        return Is.numeric
    if x.dtype == DType.Text:
        return Is.text
    if x.dtype == DType.Boolean:
        return Is.boolean

    raise TypeError(f'Unsupported type for type constraint selection {x.dtype.name}.')


def make_data_provider_call_method(meta, client):

    def __call__(self, *args):
        pmeta = meta.parameters + meta.table_parameters
        params = [Parameter(meta=p, parents=(a,)) for p, a in zip(pmeta, args) if a is not ...]
        return Table(meta=meta, client_=client, parameters=params)

    __call__.__signature__ = generate_data_call_signature(meta)

    constraints = [get_type_constraint(p) for p in meta.parameters]
    constraints += [Is.table_var] * len(meta.table_parameters)
    dec = input_constraints(..., *constraints, name=f'.{meta.python_name()}()', missing='ellipsis')

    output = dec(__call__)
    output.__doc__ = generate_call_docstring(meta)
    output.__signature__ = __call__.__signature__
    return output


def make_direct_provider_call_method(meta, client):

    def __call__validation(name, *args, **kwargs):

        failures = []

        bad_args = [(i, a) for i, a in enumerate(args) if not isinstance(a, Table) or a.meta_.type != 'TableVar']

        def get_type(a):
            if isinstance(a, Table):
                return f'a {a.meta_.type} table. Table vars can be constructed from queries with .to_table_var()'
            elif isinstance(a, TableOperation):
                return f'a {type(a).__name__.lower()} op. Did you need to call .to_table_var()?'
            else:
                return type(a).__name__

        failures += [f'Input to *args[{i}] must be a table var, but was {get_type(a)}.' for i, a in bad_args]

        constraint_dict = {p.python_name(): get_type_constraint(p) for p in meta.parameters}
        constraint_dict['apply_limit'] = Is.integer
        for k, v in kwargs.items():
            a = make(v)
            constr = constraint_dict[k]
            if not constr(a):
                failures.append(constr.make_error_msg(k, a))

        assemble_error(name, failures)

    sig = generate_direct_call_signature(meta)

    def __call__(self, *args, **kwargs):

        name = f'.{meta.python_name()}()'

        check_kwargs(sig, name, kwargs)
        __call__validation(name, *args, **kwargs)

        spec = {p.python_name(): p for p in meta.parameters}

        def val_map(v):
            if isinstance(v, (datetime, date)):
                return v.strftime('%Y-%m-%dT%H:%M:%S')
            return v

        use_params = {spec[k].field_name: val_map(v) for k, v in kwargs.items() if k != 'apply_limit'}

        dp = DirectProviderVar(meta=meta, use_params=use_params, parents=args, client=client, limit=kwargs.get('apply_limit'))

        if meta.columns is None:
            # infer columns by trying a small query
            peek_sql = f'--peek sql\n{dependency_sql(dp)}@x = {dp.update_node(limit=10).table_sql()};\n\nselect * from @x'

            df = client.query_and_fetch(peek_sql)

            # Error if nothing comes back
            if df.shape[0] == 0:
                raise ValueError(
                    f'Direct provider column discover failed. Peek SQL returned no rows:\n{indent_str(peek_sql)}'
                )

            # assemble cols from result
            def make_col(name, val):
                dtype = DType.to_dtype(type(val))
                return ColumnMeta(field_name=name, table_name=meta.name, dtype=dtype)

            columns = tuple(make_col(k, v) for k, v in df.iloc[0].to_dict().items())
            dp = dp.update_node(meta=meta.update_fields(columns=columns))

        out_tv = dp.build()
        return out_tv

    __call__.__signature__ = sig
    __call__.__doc__ = generate_call_docstring(meta)
    return __call__


class Factory(ABC):

    meta: TableMeta

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    def __getattribute__(self, item):
        if item in ['select', 'group_by']:
            # error with help message about how to use the syntax
            raise AttributeError(
                f'\'{type(self).__name__}\' has no attribute \'{item}\'.\n'
                'To start building a query you need to make the provider table object. '
                f'Try calling the atlas attribute and then chaining on .{item}(),\n'
                'for example:\n'
                f'    t = atlas.{self.meta.python_name()}()\n'
                'or\n'
                f'    t = atlas["{self.meta.name}"]()\n'
                f'Then call .{item}() to start building your query\n'
                f'    query = t.{item}("^")\n'
                'and finally call .go() to run the query and get your dataframe back\n'
                '    df = query.go()'
            )
        return super().__getattribute__(item)


def display_fn(self, *args, **kwargs):
    node = provider_widget(self.meta, True)
    return display(node, *args, **kwargs)


class MetaFactory(ABCMeta):

    def __new__(mcs, meta: TableMeta, client: Client):
        name = meta.name.replace('.', '') + 'Factory'

        mcs._name = name

        class_attrs = {
            'meta': meta,
            '__doc__': f'Factory class for making {meta.name} Table instances.'
        }
        if meta.type == 'DataProvider':
            class_attrs['__call__'] = make_data_provider_call_method(meta, client)
        elif meta.type == 'DirectProvider':
            class_attrs['__call__'] = make_direct_provider_call_method(meta, client)
        else:
            ValueError(f'Construction of factory classes not supported for {meta.type} table types.')

        class_attrs['_repr_mimebundle_'] = display_fn

        return super().__new__(mcs, name, (Factory,), class_attrs)

    def __init__(cls, meta: TableMeta, client: Client):
        super().__init__(cls._name, (Factory,), {})


