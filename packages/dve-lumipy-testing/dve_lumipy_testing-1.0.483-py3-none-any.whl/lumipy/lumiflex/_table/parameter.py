from __future__ import annotations

from typing import Optional, Union, Literal

from pydantic import StrictStr, Field, model_validator

from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._metadata import ParamMeta, TableParamMeta


class Parameter(Node):

    meta: Union[ParamMeta, TableParamMeta]
    label_: Literal['parameter'] = Field('parameter', alias='label')
    sql: Optional[StrictStr] = None

    class Config:
        frozen = True
        extra = 'forbid'
        arbitrary_types_allowed = True

    @model_validator(mode='before')
    def validate_parameter(self):

        if 'meta' not in self:
            return self

        parents = self.get('parents', [])
        if len(parents) != 1:
            if len(parents) > 1:
                detail = f'Too many parent nodes ({", ".join(type(p).__name__ for p in  parents)}).'
            else:
                detail = f'Parents tuple was empty.'
            raise ValueError(
                'Parameter can only have a single parent Node which must be a Column or Table Var. ' + detail
            )

        in_val = parents[0]
        if not isinstance(in_val, Node):
            return self

        meta = self['meta']
        if isinstance(meta, ParamMeta):
            str_val = f'[{meta.field_name}] = {in_val.sql}'
        elif isinstance(meta, TableParamMeta):
            str_val = f'[{meta.field_name}] = {in_val.from_}'
        else:
            return self

        if meta.prefix is not None:
            str_val = f'{meta.prefix}.{str_val}'
        self['sql'] = str_val

        return self

    def with_prefix(self, prefix: str) -> Parameter:
        meta = self.meta.update(prefix=prefix)
        return Parameter(meta=meta, parents=self.get_parents())
