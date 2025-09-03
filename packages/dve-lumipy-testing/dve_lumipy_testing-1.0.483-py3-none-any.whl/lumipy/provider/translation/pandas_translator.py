import warnings
from typing import Union, Tuple

import pandas as pd
from pandas import DataFrame, Series, merge
from pandas.core.groupby.generic import DataFrameGroupBy

from lumipy.common import table_spec_to_df
from lumipy.provider.context import Context
from lumipy.provider.context import Expression
from lumipy.provider.translation.pandas_map import pandas_map


def pass_none(fn):

    def wrapper(*args):
        if args[1] is None:
            return None
        return fn(*args)

    return wrapper


def _apply_restriction_table(df, meta, content) -> Series:
    # Parse restriction table into a dataframe and then build a filter for which columns pass
    res_df = table_spec_to_df(meta, content)
    merge_df = merge(df, res_df, how='left', on=res_df.columns.tolist(), indicator=True)
    return merge_df['_merge'] == 'both'


def _translate(expression, df, fill_na=None) -> Tuple[Union[Series, None], bool]:
    if expression is None:
        return None, False

    def walk(ex: Expression, is_partial: bool) -> Tuple[Union[Series, None, float, str, bool], bool]:

        if ex.op == 'ColValue':
            fn = lambda x: df[x]
        elif ex.op == 'RestrictionTable':
            fn = lambda x: _apply_restriction_table(df, *x)
        elif ex.op in pandas_map:
            fn = pandas_map[ex.op]
        else:
            # Otherwise, can't be translated. Set value to None so the associated bit of the filter isn't applied.
            warnings.warn(f'No mapping for op={ex.op}')
            return None, True

        translations = [(a, False) if ex.is_leaf() else walk(a, is_partial) for a in ex.args]

        # All inputs are available
        if not any([t[1] for t in translations]):
            return fn(*[t[0] for t in translations]), False

        # Handle partial application here...
        # If it's a logic function return all True series, if it's any other function type return None
        output = Series([True] * df.shape[0]) if ex.is_logic_op() else None
        return output, True

    result, flag = walk(expression, False)
    if isinstance(result, pd.Series) and fill_na is not None:
        return result.fillna(fill_na), flag

    return result, flag


class PandasTranslator:

    def __init__(self, context: Context):
        self.context = context
        self.partial_where = False

    def apply(self, df: DataFrame, yield_mode: bool) -> DataFrame:
        """Apply operations specified in the context to the input pandas DataFrame (filter, groups, aggregates etc.)

        Args:
            df (DataFrame): The dataframe to apply expressions to.
            yield_mode (bool): Whether this is being used in get_data method that yields dataframe chunks. This will
            switch off application of everything except the where filter.

        Returns:
            DataFrame: the dataframe result with the expressions applied.

        """

        df = self._apply_where(df)

        if not yield_mode:
            x = self._apply_group_by(df)
            x = self._apply_aggregation(x)
            x = self._apply_ordering(x)
            x = self._apply_limit(x)
            if x is not None:
                return x

        return df

    def _apply_where(self, df: DataFrame) -> DataFrame:
        where_filter, self.partial_where = _translate(self.context.where_clause, df, False)

        if where_filter is None:
            return df

        return df[where_filter]

    def _apply_group_by(self, df: DataFrame) -> Union[DataFrame, DataFrameGroupBy, None]:

        if self.context.no_groupby():
            return df

        if self.partial_where:
            return None

        groups = [_translate(g, df) for g in self.context.groupby_agg.groups]

        if any(t[1] for t in groups):
            return None

        return df.groupby([g[0] for g in groups], dropna=False)

    @pass_none
    def _apply_aggregation(self, df: Union[DataFrame, DataFrameGroupBy, None]) -> Union[DataFrame, None]:

        if self.context.no_aggregation():
            return df

        # If we have to aggregate but where filter has not been fully applied we can't continue
        if self.partial_where:
            return None

        gb_agg = self.context.groupby_agg

        # Try to translate and apply the col/agg expressions
        def apply_expressions(data):
            expressions = [_translate(ex, data) for ex in gb_agg.expressions]

            # If any of the col/agg expressions are partially translated return None
            # This will cause the groupby.apply to return an empty DF.
            if any(t[1] for t in expressions):
                return None

            vals = [t[0].iloc[0] if isinstance(t[0], Series) else t[0] for t in expressions]
            return Series({ex.get_alias(): v for v, ex in zip(vals, gb_agg.expressions)})

        # Switch behaviour depending on whether there is a group by or just an aggregate in the SELECT.
        if isinstance(df, DataFrameGroupBy):
            a_df = df.apply(apply_expressions).reset_index(drop=True)
        elif isinstance(df, DataFrame):
            a_df = pd.DataFrame(apply_expressions(df)).T
        else:
            raise TypeError(f'Bad input to apply_aggregation: type = {type(df).__name__}')

        # If not all the columns are present we have a partial translation.
        # Return None so the other translation steps are skipped
        if a_df.shape[1] != len(gb_agg.expressions):
            return None

        # Sort the group by columns so the nulls are first (matches Sqlite order).
        # Set the is_agg flag to true and return the aggregated DF.
        self.context.is_agg = True
        return a_df.sort_values(gb_agg.get_groups(), na_position='first')

    @pass_none
    def _apply_ordering(self, df: Union[DataFrame, None]) -> Union[DataFrame, None]:

        ords = self.context.orderby_clause

        if ords is None or len(ords) == 0:
            return df

        gb_agg = self.context.groupby_agg
        if gb_agg is not None and gb_agg.has_groups():
            return self._apply_ordering_agg(ords, df)
        else:
            return self._apply_ordering_cols(ords, df)

    @pass_none
    def _apply_ordering_agg(self, ords, df: Union[DataFrame, None]) -> Union[DataFrame, None]:

        e_hashes = {hash(e): e.get_alias() for e in self.context.groupby_agg.expressions}
        o_hashes = {hash(o.args[0]): o.op for o in ords}

        if any(h not in e_hashes for h in o_hashes):
            return None

        self.context.is_ordered = True
        cols = [e_hashes[k] for k in o_hashes.keys()]
        ascs = [v == 'Asc' for v in o_hashes.values()]
        return df.sort_values(cols, ascending=ascs, na_position='first')

    @pass_none
    def _apply_ordering_cols(self, ords, df: Union[DataFrame, None]) -> Union[DataFrame, None]:

        def make(pos, ex, direction):

            if ex.op == 'ColValue':
                return ex.args[0], None, False, direction == 'Asc'

            series, partial = _translate(ex, df)
            return f'__AuxOrdCol{pos}', series, partial, direction == 'Asc'

        series_ords = [make(i, o.args[0], o.op) for i, o in enumerate(ords)]

        if any(o[2] for o in series_ords):
            return None

        aux_cols = []
        for o in series_ords:
            if o[1] is None:
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df[o[0]] = o[1]

            aux_cols.append(o[0])

        self.context.is_ordered = True
        df = df.sort_values([o[0] for o in series_ords], ascending=[o[3] for o in series_ords], na_position='first')
        return df[[c for c in df.columns if c not in aux_cols]]

    @pass_none
    def _apply_limit(self, df: Union[DataFrame, None]) -> Union[DataFrame, None]:

        lim = self.context.limit_clause

        if not lim.has_requirements():
            self.context.is_offset = lim.has_offset()
            return df.iloc[lim.offset:lim.limit]
        elif lim.requires_filter_only() and not self.partial_where:
            self.context.is_offset = lim.has_offset()
            return df.iloc[lim.offset:lim.limit]
        elif lim.requires_filter_and_order() and not self.partial_where and self.context.is_ordered:
            self.context.is_offset = lim.has_offset()
            return df.iloc[lim.offset:lim.limit]

        return df
