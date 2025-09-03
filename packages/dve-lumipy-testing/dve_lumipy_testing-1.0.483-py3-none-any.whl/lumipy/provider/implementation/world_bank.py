import datetime as dt
from typing import Union, Iterable

import wbgapi as wb
from pandas import DataFrame, merge, concat

from lumipy.lumiflex import DType
from ..base_provider import BaseProvider
from ..context import Context
from ..metadata import ColumnMeta, ParamMeta


class WorldBankDataSources(BaseProvider):

    def __init__(self):

        columns = [
            ColumnMeta('SourceName', DType.Text),
            ColumnMeta('SourceCode', DType.Text),
            ColumnMeta('SeriesName', DType.Text),
            ColumnMeta('SeriesCode', DType.Text),
        ]

        super().__init__(
            'WorldBank.MetaData.Source',
            columns=columns
        )

    def get_data(self, context: Context) -> DataFrame:

        src_df = DataFrame(
            wb.source.info().table()[:-1],
            columns=['ID', 'SourceName', 'SourceCode', 'Concepts', 'LastUpdated']
        )

        src_df = context.pandas.apply(src_df, yield_mode=True)

        for _, row in src_df.iterrows():

            # Looks like a DB sometimes drops but still shows up in the sources list
            try:
                ser = wb.series.info(db=row.ID)
                df = DataFrame(
                    ser.table()[:-1],
                    columns=['SeriesCode', 'SeriesName']
                )
                df['SourceName'] = row.SourceName
                df['SourceCode'] = row.SourceCode

            except Exception as e:
                print(e)
                print(row)
                continue

            yield context.pandas.apply(df, yield_mode=True)


class WorldBankEconomies(BaseProvider):

    def __init__(self):

        columns = [
            ColumnMeta('Code', DType.Text),
            ColumnMeta('Name', DType.Text),
            ColumnMeta('RegionCode', DType.Text),
            ColumnMeta('IncomeLevel', DType.Text),
            ColumnMeta('Type', DType.Text),
            ColumnMeta('RegionName', DType.Text),
        ]

        super().__init__(
            'WorldBank.Metadata.Economy',
            columns=columns
        )

    def get_data(self, context: Context) -> DataFrame:

        econ = wb.economy.info()
        region = wb.region.info()

        edf = DataFrame(econ.table(), columns=['Code', 'Name', 'RegionCode', 'IncomeLevel'])
        edf['Type'] = edf.RegionCode.apply(lambda x: 'Region' if x == '' else 'Country')
        edf = edf.iloc[:-1]

        rdf = DataFrame(region.table(), columns=region.columns)

        mdf = merge(edf, rdf, left_on='RegionCode', right_on='code', how='left')
        mdf['RegionName'] = mdf.apply(lambda x: x['name'] if x.Type == 'Country' else x['Name'], axis=1)
        return mdf.drop(labels=['code', 'name'], axis=1)


class WorldBankSeriesMetadata(BaseProvider):

    def __init__(self):

        columns = [
            ColumnMeta('MetadataLabel', DType.Text),
            ColumnMeta('MetadataValue', DType.Text),
        ]
        params = [
            ParamMeta('SeriesCode', DType.Text, is_required=True)
        ]

        super().__init__(
            'WorldBank.Metadata.Series',
            columns=columns,
            parameters=params,
        )

    def get_data(self, context: Context) -> DataFrame:

        series_code = context.get('SeriesCode')
        sm = wb.series.metadata.get(series_code)
        df = DataFrame([sm.metadata]).T.reset_index()
        df.columns = ['MetadataLabel', 'MetadataValue']
        return df


class WorldBankSeriesData(BaseProvider):

    def __init__(self):

        columns = [
            ColumnMeta('Year', DType.Int),
            ColumnMeta('Value', DType.Double),
            ColumnMeta('EconCode', DType.Text),
            ColumnMeta('Series', DType.Text),
            ColumnMeta('SeriesName', DType.Text),
        ]

        params = [
            ParamMeta('SeriesCode', DType.Text, is_required=True),
            ParamMeta('EconomicRegion', DType.Text),
            ParamMeta('StartYear', DType.Int, default_value=1950),
            ParamMeta('EndYear', DType.Int, default_value=dt.date.today().year + 1),
            ParamMeta('ExpandRegion', DType.Boolean, default_value=True),
        ]

        super().__init__(
            'WorldBank.Data.Series',
            columns=columns,
            parameters=params,
        )

    def get_data(self, context: Context) -> Union[DataFrame, Iterable[DataFrame]]:

        # Handle series code and add human-readable info
        series_code = context.get('SeriesCode')
        series_name = wb.series.info(series_code).table()[0][1]

        # Handle economic region code
        econ_region = context.get('EconomicRegion')

        is_a_country = wb.economy.info(econ_region).table()[0][2] != '' if econ_region is not None else None

        if econ_region is not None and is_a_country:
            # This is a country such as the USA. Can't be split into constituents.
            economic_regions = [econ_region]
        elif econ_region is not None and not is_a_country:
            # This is a region such as south-east asia (SAS). Can be split into constituents.
            economic_regions = [econ_region]
            if context.get('ExpandRegion'):
                economic_regions = sorted(list(wb.region.members(econ_region)))
        else:
            # Otherwise default to global
            economic_regions = 'all'

        vdf = wb.data.DataFrame(
            series_code,
            economy=economic_regions,
            time=range(context.get('StartYear'), context.get('EndYear'))
        ).T

        def make_stack(e):

            _df = DataFrame(vdf[e])
            _df['Series'] = series_code
            _df['SeriesName'] = series_name
            _df['EconCode'] = e
            _df['Year'] = [int(v[2:]) for v in _df.index]

            _df.columns = ['Value', 'Series', 'SeriesName', 'EconCode', 'Year']
            return _df.reset_index(drop=True)

        return concat(map(make_stack, vdf.columns.tolist()))
