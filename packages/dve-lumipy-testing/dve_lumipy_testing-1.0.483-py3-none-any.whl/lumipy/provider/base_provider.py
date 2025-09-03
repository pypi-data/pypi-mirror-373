import csv
import re
import sys
import traceback
import warnings
from abc import ABC, abstractmethod
from enum import Enum
from math import ceil
from typing import List, Optional, Dict, Union, Any, Type, Iterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pandas import DataFrame

from lumipy.provider.context import Context
from lumipy.provider.metadata import (
    ColumnMeta, ParamMeta, TableParam,
    RegistrationType, RegistrationCategory, RegistrationAttributes, LifeCycleStage
)
from lumipy.provider.metadata import DType


class BaseProvider(ABC):
    """Abstract base class for local python luminesce providers.

    All local provider classes must inherit from this class, call super().__init__() and implement the _get_data method.

    """

    __chunk_size = 10000
    __csv_args = {'index': False, 'header': False, 'na_rep': 'NULL', 'quoting': csv.QUOTE_ALL}

    @abstractmethod
    def __init__(
            self,
            name: str,
            columns: List[ColumnMeta],
            parameters: Optional[List[ParamMeta]] = None,
            table_parameters: Optional[List[TableParam]] = None,
            description: Optional[str] = None,
            documentation_link: Optional[str] = None,
            license_code: Optional[str] = None,
            registration_category: Optional[RegistrationCategory] = RegistrationCategory.OtherData,
            registration_attributes: Optional[RegistrationAttributes] = RegistrationAttributes.none,
            lifecycle_stage: Optional[LifeCycleStage] = LifeCycleStage.Experimental,
            verbose: Optional[bool] = False
    ):
        """Constructor of the BaseProvider class.

        Args:
            name (str): name to give the provider (e.g. Example.Local.Provider).
            columns (List[ColumnMeta]): list of columns metadata objects that define the parameter's columns.
            parameters (Optional[List[ParamMeta]]): optional list of parameter metadata objects that define the
            provider's parameters. If no values are supplied then the provider will be parameterless.
            description (Optional[str]): description of the provider.
            documentation_link (Optional[str]): the url linking to the provider documentation.
            license_code (Optional[str]): the license code of this provider.
            registration_category (Optional[RegistrationCategory]): registration category of the provider.
            registration_attributes (Optional[RegistrationAttributes]): registration attributes of the provider.
            lifecycle_stage (Optional[LifeCycleStage]): stage of the development lifecycle of the provider.
            verbose (Optional[bool]): whether the provider should show informational messages.

        """

        self._metadata_type_check('name', str, name)
        self._metadata_type_check('description', str, description)
        self._metadata_type_check('documentation_link', str, documentation_link)
        if license_code is not None:
            self._metadata_type_check('license_code', str, license_code)

        if (name is None) or re.match('^[a-zA-Z0-9.]+$', name) is None:
            raise ValueError("Provider name must be a non-empty string containing only '.' and alphanumeric chars. "
                             f"Was {name}")

        if (len(columns) == 0) or any(not isinstance(c, ColumnMeta) for c in columns):
            raise TypeError(f"Provider columns input must be a non-empty list of {ColumnMeta.__name__}.")

        self._metadata_type_check('parameters', ParamMeta, parameters)
        self._metadata_type_check('table_parameters', TableParam, table_parameters)
        self._metadata_type_check('registration_category', RegistrationCategory, registration_category)
        self._metadata_type_check('registration_attributes', RegistrationAttributes, registration_attributes)
        self._metadata_type_check('lifecycle_stage', LifeCycleStage, lifecycle_stage)

        self.name = name
        self.description = description
        self.documentation_link = documentation_link
        self.license_code = license_code
        self.registration_type = RegistrationType.DataProvider
        self.registration_category = registration_category
        self.registration_attributes = registration_attributes
        self.lifecycle_stage = lifecycle_stage

        self.path_name = name.replace('.', '-').lower()

        self.columns = {c.name: c for c in columns}
        self.parameters = {p.name: p for p in parameters} if parameters is not None else {}
        self.table_parameters = {p.name: p for p in table_parameters} if table_parameters is not None else {}
        self.verbose = verbose

    def _metadata_type_check(self, name: str, target_type: Type, values: Union[str, Enum, Iterator]):
        if not hasattr(values, '__len__'):
            values = [values]

        if len(values) == 1 and values[0] is None:
            return

        for value in values:
            if value is not None and not isinstance(value, target_type):
                raise TypeError(
                    f"{type(self).__name__} {name} must be type {target_type.__name__} but was {type(value).__name__}."
                )

    def shutdown(self) -> None:
        """Method that is called whenever the provider needs to be shut down. By default, this is a no-op, but if your
        provider needs to clean up after itself it should do it by overloading this method.

        """
        pass

    @abstractmethod
    def get_data(self, context: Context) -> Union[DataFrame, Iterator[DataFrame]]:
        """Abstract method that represents getting and then returning data from the provider given a data filter
        dictionary, an optional limit value, and a set of named parameter values. Overriding this method implements the
        core behaviour of the provider when its associated /api/v1/provider-name/data/ endpoint is called.

        Args:
            context (Context): the query context containing info on the where clause, params, limit etc.

        Returns:
            Union[DataFrame, Iterator[DataFrame]]: either a single dataframe, or an iterable of dataframes.
        """
        raise NotImplementedError("super()._get_data() does not do anything and shouldn't be called.")

    def sys_info_line(self, message: str) -> DataFrame:
        """Create a log line df that will be streamed back and displayed in the provider STDOUT.
        This will not be visible in query progress logs seen by the user. Use progress_line() for that.

        Use this method with the yield keyword like in this example

        (inside get_data)
            rows = []
            for i in range(10):

                rows.append(row_building_fn())

                if i % 2:
                    yield self.sys_info_line(f'Built {i+1} rows!')

            return DataFrame(rows)

        Args:
            message (str): the message you want to send back to the logger.

        Returns:
            DataFrame: the dataframe containing the log message + dummy columns.

        """
        return self._msg_line(message, 'sys_info')

    def progress_line(self, message: str) -> DataFrame:
        """Create a log line df that will be streamed back and displayed in the progress log.
        This will be visible in query progress logs seen by the user. For sys-level info use sys_info_line.

        Use this method with the yield keyword like in this example

        (inside get_data)
            rows = []
            for i in range(10):

                rows.append(row_building_fn())

                if i % 2:
                    yield self.progress_line(f'Built {i+1} rows!')

            return DataFrame(rows)

        Args:
            message (str): the message you want to send back to the query progress log.

        Returns:
            DataFrame: the dataframe containing the log message + dummy columns.

        """
        return self._msg_line(message, 'progress')

    def router(self) -> APIRouter:
        """Create a FastAPI APIRouter object that implements a chunk of the API for this local provider instance.

        Returns:
            APIRouter: FastAPI APIRouter object representing the API routes for this instance.
        """

        router = APIRouter(tags=[self.name])

        @router.get(f'/api/v1/{self.path_name}/metadata')
        async def provider_metadata():
            return {
                "Name": self.name,
                "Description": self.description,
                "DocumentationLink": self.documentation_link,
                'LicenseCode': self.license_code,
                'RegistrationType': self.registration_type.name,
                'RegistrationCategory': self.registration_category.name,
                'RegistrationAttributes': self.registration_attributes.name,
                'LifecycleStage': self.lifecycle_stage.name if self.lifecycle_stage else None,
                "Columns": [c.to_dict() for c in self.columns.values()],
                "Params": [p.to_dict() for p in self.parameters.values()],
                "TableParams": [t.to_dict() for t in self.table_parameters.values()],
                "Verbose": self.verbose,
            }

        @router.post(f'/api/v1/{self.path_name}/data')
        async def provider_data(request: Request):
            return StreamingResponse(self._pipeline(await request.json()))

        return router

    def _pipeline(self, request: Dict) -> Iterator[str]:
        context = Context.model_validate(request, strict=False)
        data = self._data_iterator(context)
        data = self._detect_empty_generator(data)
        data = self._check_data_content(data, context)
        data = self._cast_column_types(data, context)
        data = self._insert_context_signals(data, context)
        csvs = self._chunked_csv_iterator(data)
        csvs = self._catch_and_report_errors(csvs)
        return csvs

    def _msg_line(self, message: str, msg_type: str) -> DataFrame:
        row = {c: None for c in self.columns.keys()}
        row['__line_type'] = msg_type
        row['__content'] = message
        return DataFrame([row])

    def empty_row(self) -> DataFrame:
        return DataFrame(columns=list(self.columns.keys()))

    def _data_iterator(self, context: Context) -> Iterator[DataFrame]:
        # noinspection PyBroadException
        try:
            data = self.get_data(context)

            if isinstance(data, DataFrame):
                return [data]
            elif isinstance(data, Iterator):
                return data
            else:
                msg = f'{type(self).__name__}.get_data must be a dataframe or iterator. Was {type(data).__name__}.'
                raise TypeError(msg)

        except Exception:
            return [self._msg_line(''.join(traceback.format_exception(*sys.exc_info())), 'error')]

    def _check_data_content(self, dfs: Iterator[DataFrame], context: Context) -> Iterator[DataFrame]:
        for df in dfs:
            if not isinstance(df, DataFrame):
                raise TypeError(f'{type(self).__name__}.get_data did not yield a DataFrame. Was {type(df).__name__}')

            if '__line_type' in df.columns:
                # This is a message line - pass through
                yield df
            elif context.is_agg and set(df.columns) != set(context.groupby_agg.get_names()):
                exp_col_str = ', '.join(sorted(context.groupby_agg.get_names()))
                obs_col_str = ', '.join(sorted(df.columns))
                raise ValueError(
                    f'DataFrame column content from {type(self).__name__}.get_data does not match group agg request.\n'
                    f'  Expected: {exp_col_str}\n'
                    f'    Actual: {obs_col_str}'
                )
            elif not context.is_agg and set(df.columns) != set(self.columns.keys()):
                exp_col_str = ', '.join(sorted([c for c in self.columns.keys()]))
                obs_col_str = ', '.join(sorted(df.columns))
                raise ValueError(
                    f'DataFrame column content from {type(self).__name__}.get_data does not match provider spec.\n'
                    f'  Expected: {exp_col_str}\n'
                    f'    Actual: {obs_col_str}'
                )
            else:
                # Make a 'slice' that contains the whole df. This will stop columns being added to the original which
                # ends up in here as a reference. The next lines can accidentally mutate the original df in a
                # PandasProvider for example. We don't want to copy - will save on memory.
                if context.is_agg:
                    names = context.groupby_agg.get_names()
                else:
                    names = self.columns.keys()
                df = df[names]

                # Now add the extra metadata cols for the data response lines
                with warnings.catch_warnings():
                    # because it moans about setting values on a slice. It's fine here.
                    warnings.simplefilter("ignore")
                    df['__line_type'] = 'data'
                    df['__content'] = None
                yield df

    def _cast_column_types(self, dfs: Iterator[DataFrame], context: Context) -> Iterator[DataFrame]:

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for df in dfs:
                if not context.is_agg:
                    for k, v in self.columns.items():
                        df[k] = v.data_type.col_type_map()(df[k])
                yield df

    def _insert_context_signals(self, dfs: Iterator[DataFrame], context: Context) -> Iterator[DataFrame]:

        df = next(iter(dfs))

        # Put msgs on front of the stream to inform the dotnet side about agg/ordering/offset implementation
        yield self._msg_line(str(context.is_agg), 'is_agg')
        yield self._msg_line(str(context.is_ordered), 'is_ord')
        yield self._msg_line(str(context.is_offset), 'is_offset')

        cols = df.columns
        row = {c: DType.to_dtype(df[c]).name for c in cols}
        row['__line_type'] = 'dtypes'
        row['__content'] = ','.join(df.dtypes.index[:-2])
        yield DataFrame([row])
        yield df

        while True:
            try:
                yield next(dfs)

            except StopIteration:
                return

            except Exception as e:
                raise e

    def _chunked_csv_iterator(self, dfs: Iterator[DataFrame]) -> Iterator[str]:
        for df in dfs:
            n_chunks = ceil(df.shape[0] / self.__chunk_size)
            for i in range(n_chunks):
                chunk = df.iloc[i * self.__chunk_size: (i + 1) * self.__chunk_size]
                yield chunk.to_csv(**self.__csv_args)

    def _detect_empty_generator(self, it: Iterator[Any]) -> Iterator[Any]:

        # because lists aren't iterators
        it = iter(it)
        # First entry or None if it doesn't exist
        el = next(it, None)

        if el is None:
            raise ValueError(
                f'Generator from {type(self).__name__}.get_data did not yield any results!\n'
                'Check whether you\'re trying to use return to return a result in a method that also uses yield.\n'
                'In this case the return value ends up in the StopIteration object and is not returned by the method\n'
                'https://docs.python.org/3/reference/simple_stmts.html#the-return-statement\n'
                'Consider changing to use just the yield keyword.\n'
                f'If you want to return an empty result try\n'
                f'\tyield self.empty_row()'
            )

        yield el

        # After first
        while True:
            try:
                yield next(it)

            except StopIteration:
                return

            except Exception as e:
                raise e

    def _catch_and_report_errors(self, csv_strs: Iterator[str]) -> Iterator[str]:

        # noinspection PyBroadException
        try:
            for csv_str in csv_strs:
                yield csv_str

        except Exception:
            err = ''.join(traceback.format_exception(*sys.exc_info()))
            yield self._msg_line(err, 'error').to_csv(**self.__csv_args)
