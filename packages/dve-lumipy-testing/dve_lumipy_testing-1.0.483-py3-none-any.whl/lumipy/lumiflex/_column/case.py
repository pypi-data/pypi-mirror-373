from __future__ import annotations

from datetime import date, datetime
from typing import Union, Tuple, Optional, Callable, Literal

from pydantic import Field, field_validator, model_validator

from lumipy.common import indent_str
from lumipy.lumiflex._common.node import Node
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex.column import Column, Is


class When(Node):
    label_: Literal['when'] = Field('when', alias='label')
    parents_: Tuple = Field(alias='parents')

    @field_validator('parents_')
    def _validate_parents(cls, val):
        if len(val) not in (1, 2):
            raise ValueError(
                f'When node must have one or two parents: (condition) or (condition, then), but received {len(val)}.'
            )
        if not isinstance(val[0], Column):
            raise TypeError(f'Condition must be a Column object, but was {type(val[0]).__name__}.')
        if val[0].dtype != DType.Boolean:
            raise TypeError(f'Condition must resolve to a boolean, but was {val[0].dtype.name}.')
        if len(val) == 2 and not isinstance(val[1], Then):
            raise TypeError(f'The second parent of When must be a Then object, but was {type(val[1]).__name__}.')

        return val

    @input_constraints(..., Is.any, name='.then()')
    def then(self, value: Union[Column, int, float, bool, str, date, datetime, None]) -> Then:
        """Add a then clause to this case statement. This is the value to assign when the prior when condition is satisfied.

        Args:
            value (Union[Column, int, float, bool, str, date, datetime, None]): the value to use. None will map to NULL.

        Returns:
            Then: a then instance representing this value.
        """
        return Then(parents=(value, self))

    def get_sql(self) -> str:
        """Get the sql string for this then clause.

        Returns:
            str: the SQL this statement resolves to.
        """
        return f'WHEN {self.get_parents()[0].sql}'


class Then(Node):
    label_: Literal['then'] = Field('then', alias='label')
    parents_: Tuple = Field(alias='parents')

    @field_validator('parents_')
    def _validate_parents(cls, val):
        if len(val) != 2:
            raise ValueError(f'Then node must have two parents: (value, then) but received {len(val)}.')
        if not isinstance(val[0], Column):
            raise TypeError(f'Value must be a Column object, but was {type(val[0]).__name__}.')
        if not isinstance(val[1], When):
            raise TypeError(f'The second parent of a Then must be a When object. Was {type(val[1]).__name__}.')

        return val

    @input_constraints(..., Is.boolean, name='.when()')
    def when(self, condition: Column) -> When:
        """Add a when condition to the case statement.

        Args:
            condition (Column): the condition in the when clause. Must resolve to a boolean type.

        Returns:
            When: a when condition node instance corresponding
        """
        return When(parents=(condition, self))

    @input_constraints(..., Is.any, name='.then()')
    def otherwise(self, value: Union[Column, int, float, bool, str, date, datetime, None] = None) -> CaseColumn:
        """Value to default to at the end of a case statement chain.

        Args:
            value (Union[Column, int, float, bool, str, date, datetime, None]): the default value. None is equivalent
            to NULL in SQL.

        Returns:
            CaseColumn: a column instance that represents the complete case statement.
        """
        return CaseColumn(parents=(value, self))

    def get_sql(self) -> str:
        """Get the sql string for this then clause.

        Returns:
            str: the SQL this statement resolves to.
        """
        return f'  THEN {self.get_parents()[0].sql}'


class CaseColumn(Column):

    label_: Literal['func'] = Field('func', alias='label')
    fn: Optional[Callable] = None
    dtype: Optional[DType] = None

    @model_validator(mode='before')
    def _compute_val(self):

        parents = self.get('parents', [])

        if len(parents) != 2:
            raise ValueError(f'Case must have two parents, but was given {len(parents)}')
        default, then = parents
        if not isinstance(default, Column):
            raise ValueError(f'First parent must be a Column, but was {type(default).__name__}.')
        if not isinstance(then, Then):
            raise ValueError(f'Second parent must be Then, but was {type(then).__name__}.')

        nodes = [n for n in then.topological_sort() if n.get_label() in ['when', 'then']]
        lines = '\n'.join(n.get_sql() for n in nodes)
        val = f'{lines}\nELSE {default.sql}'
        self['sql'] = f'CASE\n{indent_str(val, 4)}\nEND'

        dtypes = [n.get_parents()[0].dtype for n in nodes if n.get_label() == 'then']
        if default.dtype != DType.Null:
            dtypes.append(default.dtype)

        numerics = [DType.Int, DType.BigInt, DType.Double, DType.Decimal]
        if len(set(dtypes)) == 1:
            # All the same dtype
            self['dtype'] = dtypes[0]
        elif all(d in numerics for d in dtypes):
            # Numeric priority
            self['dtype'] = DType(max(d.value for d in dtypes))
        elif all(d in (DType.Date, DType.DateTime) for d in dtypes):
            # Date/Datetime priority
            self['dtype'] = DType(max(d.value for d in dtypes))
        else:
            # Otherwise, it's text
            self['dtype'] = DType.Text

        return self


@input_constraints(..., Is.boolean, name='.when()')
def when(condition):
    """Start building a case statement with the first when condition.

    Args:
        condition (Column): the condition in the when clause. Must resolve to a boolean type.

    Returns:
        When: a when condition node instance corresponding

    """
    return When(parents=(condition,))
