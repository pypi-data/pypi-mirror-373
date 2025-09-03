import io
import os
from typing import Optional, Union, Dict

import pandas as pd
from pandas import DataFrame

from lumipy.lumiflex import DType
from lumipy.provider.base_provider import BaseProvider
from lumipy.provider.common import infer_datatype, df_summary_str, clean_colname
from lumipy.provider.context import Context
from lumipy.provider.metadata import (
    ColumnMeta, ParamMeta,
    RegistrationCategory, RegistrationAttributes, LifeCycleStage
)


class PandasProvider(BaseProvider):
    """Provides rows of data from a Pandas DataFrame.

    """

    def __init__(
            self,
            source: Union[DataFrame, str, os.PathLike, io.IOBase],
            name: str,
            name_root: Optional[str] = 'Pandas',
            description: Optional[str] = None,
            read_csv_kw: Dict = None,
            documentation_link: Optional[str] = None,
            license_code: Optional[str] = None,
            registration_category: Optional[RegistrationCategory] = RegistrationCategory.OtherData,
            registration_attributes: Optional[RegistrationAttributes] = RegistrationAttributes.none,
            lifecycle_stage: Optional[LifeCycleStage] = LifeCycleStage.Experimental,
            verbose: Optional[bool] = True
    ):
        """Constructor of the PandasProvider class.

        Args:
            source (Union[DataFrame, str, os.PathLike, io.IOBase]): the dataframe or pd.read_csv-compatible source to
            serve data from. Datetime-valued columns must be timezone-aware.
            See https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            name (str): name to give the provider. The name will be appended to name_root ('Pandas') by default to
            create the full name 'Pandas.(name)' unless the name root is overridden by supplying a value.
            name_root (Optional[str]): optional name_root value. Will override 'Pandas' if not supplied.
            description (Optional[str]): optional description string of the provider.
            read_csv_kw (Dict): optional dictionary of kwargs to pass to pandas.read_csv.
            documentation_link (Optional[str]): the url linking to the provider documentation.
            license_code (Optional[str]): the license code of this provider.
            registration_category (Optional[RegistrationCategory]): registration category of the provider.
            registration_attributes (Optional[RegistrationAttributes]): registration attributes of the provider.
            lifecycle_stage (Optional[LifeCycleStage]): stage of the development lifecycle of the provider.
            verbose (Optional[bool]): whether the provider should show informational messages.

        """

        if name_root:
            name = f'{name_root}.{name}'

        if isinstance(source, DataFrame):
            df = source
        else:
            read_csv_kw = {} if read_csv_kw is None else read_csv_kw
            df = pd.read_csv(source, **read_csv_kw)

        self.df = df.rename({c: clean_colname(c) for c in df.columns}, axis=1)

        cols = [ColumnMeta(c, infer_datatype(self.df[c])) for c in self.df.columns]
        p_desc = "Whether to pushdown where filter, groups, and/or aggregates to the Pandas provider."
        params = [ParamMeta("Pushdown", DType.Boolean, p_desc, default_value=True)]

        if description is None:
            description = f'A provider that serves data from a Pandas dataframe.\n{df_summary_str(self.df)}\n'

        super().__init__(
            name, cols, params,
            description=description,
            documentation_link=documentation_link,
            license_code=license_code,
            registration_category=registration_category,
            registration_attributes=registration_attributes,
            lifecycle_stage=lifecycle_stage,
            verbose=verbose,
        )

    def get_data(self, context: Context) -> DataFrame:
        if context.get('Pushdown'):
            return context.pandas.apply(self.df, False)
        return self.df
