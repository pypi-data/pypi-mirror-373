from __future__ import annotations

from typing import Dict, Union, Literal, List, Any

import pandas as pd
from pandas import to_datetime
from pydantic import BaseModel, StrictStr, StrictBool

from lumipy.common import table_spec_to_df
from lumipy.provider.common import expression_to_table_spec
from lumipy.provider.common import strtobool


class Expression(BaseModel):

    op: StrictStr
    args: List[Union[Expression, str, int, bool, float]]
    alias: Union[StrictStr, None] = None

    def get_alias(self) -> str:
        if self.op == 'ColValue' and self.alias is None:
            return self.args[0]
        return self.alias

    def is_leaf(self) -> bool:
        return self.op in ['ColValue', 'DateValue', 'BoolValue', 'StrValue', 'NumValue', 'TableSpec']

    def is_logic_op(self) -> bool:
        return self.op in [
            'And', 'Or',
            'Gt', 'Lt', 'Gte', 'Lte',
            'Eq', 'Neq',
            'In', 'NotIn',
            'Between', 'NotBetween',
            'Like', 'NotLike', 'Glob', 'NotGlob',
            'Regexp', 'NotRegexp',
        ]

    def __str__(self) -> str:
        return self.json(indent=2)

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        args_hash = tuple(a for a in self.args)
        return hash((self.op,) + args_hash)


class ParamVal(BaseModel):

    name: StrictStr
    data_type: StrictStr
    value: Union[Expression, Any]

    def get(self) -> Union[pd.DataFrame, int, float, str, pd.Timestamp]:

        if self.data_type == 'Table':
            args = expression_to_table_spec(*self.value.args)
            return table_spec_to_df(*args)

        from lumipy.provider import DType

        t = DType[self.data_type]

        if t == DType.Int:
            return int(self.value)
        if t == DType.Double:
            return float(self.value)
        if t == DType.Text:
            return str(self.value)
        if t == DType.Boolean:
            return bool(strtobool(str(self.value)))
        if t == DType.DateTime or t == DType.Date:
            return to_datetime(self.value, errors='coerce')

        return self.value

    def __str__(self) -> str:
        return self.json(indent=2)

    def __repr__(self) -> str:
        return str(self)


class Limit(BaseModel):

    limit: Union[int, None] = None
    offset: Union[int, None] = None
    limitType: Literal['NoFilteringRequired', 'FilteringRequired', 'FilteringAndOrderingRequired'] = 'NoFilteringRequired'

    def requires_filter_only(self) -> bool:
        return self.limitType == 'FilteringRequired'

    def requires_filter_and_order(self) -> bool:
        return self.limitType == 'FilteringAndOrderingRequired'

    def has_requirements(self) -> bool:
        return self.requires_filter_only() or self.requires_filter_and_order()

    def has_offset(self) -> bool:
        return self.offset is not None and self.offset > 0

    def __str__(self) -> str:
        return self.json(indent=2)

    def __repr__(self) -> str:
        return str(self)


class GroupByAgg(BaseModel):
    expressions: List[Expression] = []
    groups: List[Expression] = []

    def get_names(self) -> List[str]:
        return [ex.get_alias() for ex in self.expressions]

    def get_groups(self) -> List[str]:
        hashes = [hash(g) for g in self.groups]
        return [ex.get_alias() for ex in self.expressions if hash(ex) in hashes]

    def has_groups(self) -> bool:
        return len(self.groups) > 0

    def has_expressions(self) -> bool:
        return len(self.expressions) > 0


class Identity(BaseModel):

    access_token: Union[StrictStr, None] = None
    user_groups: List[StrictStr] = None
    user_id: Union[StrictStr, None] = None
    impersonation_type: Union[StrictStr, None] = None
    company_domain: Union[StrictStr, None] = None
    client_domain: Union[StrictStr, None] = None
    client_id: Union[StrictStr, None] = None
    actual_user_id: Union[StrictStr, None] = None
    email: Union[StrictStr, None] = None


class Context(BaseModel):

    param_specs: Dict[StrictStr, ParamVal] = {}
    distinct: StrictBool = False
    where_clause: Union[Expression, None] = None
    groupby_agg: Union[GroupByAgg, None] = GroupByAgg()
    orderby_clause: Union[List[Expression], None] = None
    limit_clause: Limit = Limit()
    identity: Identity = Identity()

    is_agg: StrictBool = False
    is_ordered: StrictBool = False
    is_offset: StrictBool = False

    def get(self, name) -> Union[pd.DataFrame, int, float, str, pd.Timestamp, None]:
        if name in self.param_specs:
            return self.param_specs[name].get()
        return None

    @property
    def pandas(self):
        from lumipy.provider.translation.pandas_translator import PandasTranslator
        return PandasTranslator(self)

    def no_where(self) -> bool:
        return self.where_clause is None

    def no_groupby(self) -> bool:
        return self.groupby_agg is None or len(self.groupby_agg.groups) == 0

    def no_aggregation(self) -> bool:
        return self.groupby_agg is None or len(self.groupby_agg.expressions) == 0

    def limit(self) -> Union[int, None]:
        return self.limit_clause.limit

    def offset(self) -> Union[int, None]:
        return self.limit_clause.offset

    def __str__(self) -> str:
        return self.json(indent=2)

    def __repr__(self) -> str:
        return str(self)
