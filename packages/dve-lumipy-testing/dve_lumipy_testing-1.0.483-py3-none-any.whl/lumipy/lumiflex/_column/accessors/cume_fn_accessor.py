from typing import Optional

from lumipy.lumiflex._column.ordering import Ordering
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import block_node_type
from lumipy.lumiflex._window.window import WindowColumn
from lumipy.lumiflex.column import Column
from .base_fn_accessor import BaseFnAccessor
from ...window import window


class CumeFnAccessor(BaseFnAccessor):

    @block_node_type(label='aggfunc', name='.cume')
    def __init__(self, column: Column):
        super().__init__('cume', column, Is.numeric)

    def prod(self, order: Optional[Ordering] = None) -> WindowColumn:
        """Apply a cumulative product to this column. This will give the product of all values
        from the start up to current row for each row.

        Args:
            order (Optional[Ordering]): an optional ordering to apply to the column before the op.

        Returns:
            WindowColumn: a window column instance representing this calculation.

        """
        return window(orders=order).prod(self._column)

    def sum(self, order: Optional[Ordering] = None) -> WindowColumn:
        """Apply a cumulative sum to this column.

        Args:
            order (Optional[Ordering]): an optional ordering to apply to the column before the op.

        Returns:
            WindowColumn: a window column instance representing this calculation.

        """
        return window(orders=order).sum(self._column)

    def min(self, order: Optional[Ordering] = None) -> WindowColumn:
        """Apply a cumulative minimum to this column.

        Args:
            order (Optional[Ordering]): an optional ordering to apply to the column before the op.

        Returns:
            WindowColumn: a window column instance representing this calculation.

        """
        return window(orders=order).min(self._column)

    def max(self, order: Optional[Ordering] = None) -> WindowColumn:
        """Apply a cumulative maximum to this column.

        Args:
            order (Optional[Ordering]): an optional ordering to apply to the column before the op.

        Returns:
            WindowColumn: a window column instance representing this calculation.

        """
        return window(orders=order).max(self._column)

    def dist(self) -> WindowColumn:
        """Apply a cumulative distribution (quantile rank) to this column.

        Notes:
            Equivalent to the following in SQL

                CUME_DIST() OVER(
                    ORDER BY <this column> ASC
                    )

            No interpolation is applied when computing the above expression. Each quantile result that comes from the
            cume_dist call is equivalent to percentile rank in pandas computed as follows

                df.column.rank(pct=True, method='first')

        Returns:
            WindowColumn: a window column instance representing this calculation.

        """
        return window(orders=self._column.asc()).cume_dist()
