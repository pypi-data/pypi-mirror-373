import asyncio
import io
import json
import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from importlib.util import find_spec
from pathlib import Path
from typing import Callable, Dict, Optional, Literal, Tuple, List
from urllib.parse import urlparse
from zipfile import ZipFile

import luminesce
import pandas as pd
from luminesce import EnvironmentVariablesConfigurationLoader, ArgsConfigurationLoader, \
    SecretsFileConfigurationLoader, ApiException
from luminesce.api import SqlExecutionApi
from luminesce.extensions import ApiClientFactory, SyncApiClientFactory
from luminesce.models import TaskStatus
from pandas import DataFrame
from semver import Version
from tqdm import tqdm

import lumipy
from lumipy._config_manager import config
from lumipy.common import indent_str, table_spec_to_df
from lumipy.query_job import QueryJob

from lumipy.helpers.backoff_handler import BackoffHandler

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if find_spec('IPython') is not None:
    from IPython.display import clear_output


def _add_lumipy_tag(sql: str):
    if hasattr(lumipy, '__version__'):
        version = lumipy.__version__
    else:
        version = ''
    return f'-- lumipy {version}\n{sql}'


class Client:
    """Higher level client that wraps the low-level luminesce python sdk. This client offers a smaller collection of
    methods for starting, monitoring and retrieving queries as Pandas DataFrames.

    """

    def __init__(self, **kwargs):
        """__init__ method of the lumipy client class. It is recommended that you use the lumipy.get_client() function
        at the top of the library.

        Keyword Args (all optional):
            access_token (str): Bearer token (PAT) used to initialise the API
            api_secrets_file (str): Name of secrets file (including full path)
            api_url (str): Luminesce API URL (e.g., 'https://{domain}.lusid.com/honeycomb')
            username (str): The username to use
            password (str): The password to use
            client_id (str): The client id to use
            client_secret (str): The client secret to use
            app_name (str): Application name
            certificate_filename (str): Name of the certificate file (.pem, .cer or .crt)
            proxy_address (str): The url of the proxy to use including the port e.g. http://myproxy.com:8888
            proxy_username (str): The username for the proxy to use
            proxy_password (str): The password for the proxy to use
            token_url (str): The token URL of the identity provider
        """

        api_secrets_file = kwargs.pop('api_secrets_file', None)

        self._config_loaders = [
            EnvironmentVariablesConfigurationLoader(),
            ArgsConfigurationLoader(**kwargs)
        ]

        if api_secrets_file is not None:
            api_secrets_path = Path(api_secrets_file)
            if not api_secrets_path.exists():
                raise ValueError(f"Secrets file: '{api_secrets_path}' does not exist")

            self._config_loaders.insert(0, SecretsFileConfigurationLoader(api_secrets_file=api_secrets_file))

        self._factory = SyncApiClientFactory(config_loaders=self._config_loaders)
        self.backoff_handler = BackoffHandler()
        self._catalog_api = self._factory.build(luminesce.api.CurrentTableFieldCatalogApi)
        self._sql_exec_api = self._factory.build(luminesce.api.SqlExecutionApi)
        self._sql_bkg_exec_api = self._factory.build(luminesce.api.SqlBackgroundExecutionApi)
        self._history_api = self._factory.build(luminesce.api.HistoricallyExecutedQueriesApi)
        self._design_api = self._factory.build(luminesce.api.SqlDesignApi)
        self._certs_management = self._factory.build(luminesce.api.CertificateManagementApi)
        self._binary_download = self._factory.build(luminesce.api.BinaryDownloadingApi)

    def get_domain(self) -> str:
        url = self._factory._SyncApiClientFactory__api_client.configuration._base_path
        return urlparse(url).netloc.split('.')[0]

    def get_token(self) -> str:
        return self._factory._SyncApiClientFactory__api_client.configuration.access_token

    def __repr__(self):
        return f'{type(self).__name__}(domain={self.get_domain()})'

    def _async_to_sync(self, coroutine):
        async def coroutine_with_delay():
            result = await coroutine
            await asyncio.sleep(1)  # Give the resources enough time to dispose (preventing unclosed transport errors)
            return result

        pool = ThreadPoolExecutor()
        result = pool.submit(asyncio.run, coroutine_with_delay()).result()
        return result

    def _get_factory(self) -> ApiClientFactory:
        return ApiClientFactory(config_loaders=self._config_loaders)

    def table_field_catalog(self) -> pd.DataFrame:
        """Get the table field catalog as a DataFrame.

        The table field catalog contains a row describing each field on each provider you have access to.

        Returns:
            DataFrame: dataframe containing table field catalog information.
        """
        return pd.DataFrame(json.loads(self._catalog_api.get_catalog()))

    def query_and_fetch(
            self,
            sql: str,
            name: Optional[str] = 'query',
            timeout: Optional[int] = 175,
            **read_csv_params
    ) -> pd.DataFrame:
        """Send a query to Luminesce and get it back as a pandas dataframe.

        Args:
            sql (str): query sql to be sent to Luminesce
            name (str): name of the query (defaults to just 'query')
            timeout (int): max time for the query to run in seconds (defaults to 175)
            **read_csv_params (Any): keyword arguments to pass down to pandas read_csv. See https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

        Returns:
            DataFrame: result of the query as a pandas dataframe.
        """
        res = self._sql_exec_api.put_by_query_csv(
                body=_add_lumipy_tag(sql),
                query_name=name,
                timeout_seconds=timeout
            )
        buffer_result = io.StringIO(res)
        return pd.read_csv(buffer_result, encoding='utf-8', **read_csv_params)

    def pretty(
            self,
            sql: str,
            **pretty_params
    ) -> pd.DataFrame:
        """Make a sql string pretty using Luminesce pretty method.

        Args:
            sql (str): query sql to be made pretty
            **pretty_params (Any): keyword arguments to be passed down to pretty method.

        Returns:
            str: a pretty sql string
        """
        return self._design_api.put_query_to_format(body=_add_lumipy_tag(sql), **pretty_params)

    def start_query(self, sql: str, name: Optional[str] = "query", timeout: Optional[int] = 3600, keep_for: Optional[int] = 7200) -> str:
        """Send an asynchronous query to Luminesce. Starts the query but does not wait and fetch the result.

        Args:
            sql (str): query sql to be sent to Luminesce
            name (str): name of the query (defaults to just 'query')
            timeout (int): max time for the query to run in seconds (defaults to 3600)
            keep_for (int): time to keep the query result for in seconds (defaults to 7200)

        Returns:
            str: string containing the execution ID

        """
        res = self._sql_bkg_exec_api.start_query(
            body=_add_lumipy_tag(sql),
            query_name=name,
            timeout_seconds=timeout,
            keep_for_seconds=keep_for
        )

        return res.execution_id

    def get_status(self, execution_id: str) -> Dict[str, str]:
        """Get the status of a Luminesce query

        Args:
            execution_id (str): unique execution ID of the query.

        Returns:
            Dict[str, str]: dictionary containing information on the query status.
        """
        res = self._sql_bkg_exec_api.get_progress_of(execution_id)

        return res.dict()

    def delete_query(self, execution_id: str) -> Dict[str, str]:
        return self._sql_bkg_exec_api(execution_id).dict()

    def get_result(
            self,
            execution_id: str,
            sort_by: Optional[str] = None,
            filter_str: Optional[str] = None,
            verbose: bool = False,
            **read_csv_params
    ):
        """Gets the result of a completed luminesce query and returns it as a pandas dataframe.

            Args:
                execution_id (str): execution ID of the query.
                sort_by (Optional[str]): string representing a sort to apply to the result before downloading it.
                filter_str (Optional[str]): optional string representing a filter to apply to the result before downloading it.
                verbose (Optional[bool]): whether to print out information while getting the data.
                **read_csv_params (Any): keyword arguments to pass down to pandas read_csv. See https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

            Returns:
                DataFrame: result of the query as a pandas dataframe.

            """
        status = self.get_status(execution_id)
        row_count = int(status['row_count'])

        while row_count == -1 and status['status'] != TaskStatus.FAULTED:
            status = self.get_status(execution_id)
            row_count = int(status['row_count'])
            if row_count != -1:
                break

            self.backoff_handler.sleep()

        if row_count == -1:
            raise LumiError(execution_id, status)

        fetch_params = {'execution_id': execution_id, 'download': True}
        if sort_by is not None:
            fetch_params['sort_by'] = sort_by
        if filter_str is not None:
            fetch_params['filter'] = filter_str

        if verbose:
            print(f'Downloading {row_count} row{"" if row_count == 1 else "s"} of data... 📡')

        s = time.time()
        csv = self._sql_bkg_exec_api.fetch_query_result_csv(**fetch_params)

        df = table_spec_to_df(status['columns_available'], csv, **read_csv_params)

        if verbose:
            print(f'Done! ({time.time() - s:3.2f}s)')

        return df

    def delete_view(self, name: str):
        """Deletes a Luminesce view provider with the given name.

        Args:
            name (str): name of the view provider to delete.

        """
        self.query_and_fetch(f"""
            @x = use Sys.Admin.SetupView
                --provider={name}
                --deleteProvider
                --------------
                select 1;
                enduse;
            select * from @x;
            """)

    def run(
            self,
            sql: str,
            timeout: Optional[int] = 3600,
            keep_for: Optional[int] = 7200,
            quiet: Optional[bool] = False,
            return_job: Optional[bool] = False,
            _print_fn: Optional[Callable] = None,
            **read_csv_params
    ) -> DataFrame:
        """Run a sql string in Luminesce. This method can either run synchonously which will print query progress to the
         screen and then return the result or return a QueryJob instance that allows you to manage the query job yourself.

        Args:
            sql (str): the sql to run.
            timeout (Optional[int]): max time for the query to run in seconds (defaults to 3600)
            keep_for (Optional[int]): time to keep the query result for in seconds (defaults to 7200)
            quiet (Optional[bool]): whether to print query progress or not
            return_job (Optional[bool]): whether to return a QueryJob instance or to wait until completion and return
            the result as a pandas dataframe
            _print_fn (Optional[Callable]): alternative print function for showing progress. This is mainly for internal use with
            the streamlit utility functions that show query progress in a cell. Defaults to the normal python print() fn.
            **read_csv_params (Any): keyword arguments to pass down to pandas read_csv. See https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

        Returns:
            Union[DataFrame, QueryJob]: either a dataframe containing the query result or a query job object that
            represents the running query.

        """
        ex_id = self.start_query(sql, timeout=timeout, keep_for=keep_for)
        job = QueryJob(ex_id, client=self, _print_fn=_print_fn)
        if return_job:
            return job

        job.interactive_monitor(quiet=quiet)
        result = job.get_result(quiet=quiet, **read_csv_params)
        if find_spec('IPython') is not None and not quiet:
            clear_output(wait=True)

        return result

    def get_binary_versions(self, name: str) -> List[str]:
        """ Gets all available versions of a given binary type (from newest to oldest) This does not mean you are
            entitled to download them (but they will have validated SHAs)

        Args:
            name (str): the name of the binary to download (e.g. Python_Providers).

        Returns:
            List[str]: The available versions ordered from newest to oldest

        """

        return self._binary_download.get_binary_versions(type=name)

    def _get_latest_available_version_in_range(self, name: str, min_version: Optional[str] = None, max_version: Optional[str] = None) -> str:
        min_version_parsed = Version.parse(min_version) if min_version else Version.parse("0.0.0")
        max_version_parsed = Version.parse(max_version) if max_version else Version.parse("999.999.999")

        if min_version_parsed <= max_version_parsed:
            for v in self.get_binary_versions(name):
                version_parsed = Version.parse(v)

                if version_parsed < min_version_parsed:
                    break

                if version_parsed <= max_version_parsed:
                    return v

        raise ValueError(f"Unable to find an available version in the range: {str(min_version_parsed)} (min) - {str(max_version_parsed)} (max)")

    def download_binary(
            self,
            name: str,
            version: Optional[str] = None,
            min_version: Optional[str] = None,
            get_best_available: Optional[bool] = False
    ) -> str:
        """Download a Luminesce binary

        Notes:
            Some newly-published versions may not be immediately available while they are being hashed.
            If `get_best_available` is true, this method will get the latest available binary within the constraints of
            the `version` (maximum, if provided), `min_version` (if provided), and with a valid SHA. If no version is
            provided, the latest available binary with a valid SHA is downloaded. If `version` is provided but
            'get_best_available 'is false, the method will attempt to download that specific version, but it may fail
            if the version does not exist or lacks a validated SHA.

        Args:
            name (str): The name of the binary to download (e.g. Python_Providers).
            version (Optional[str]): The semantic version number to download. When `get_best_available` is True, this
            is used as the maximum version number to download and defaults to "999.999.999" if not provided.
            min_version (Optional[str]): The minimum acceptable semantic version number to download. This is only used
            when `get_best_available` is true and defaults to "0.0.0" when not provided.
            get_best_available (bool): If true, download the latest binary within the range of `min_version` to
            `version` (or the latest if `version` is not specified).

        Returns:
            Version (str): The downloaded binary version

        """

        if min_version and not get_best_available:
            raise ValueError("Cannot set a minimum version to download when 'get_best_available' is False.")

        if (version or min_version) and get_best_available:
            version = self._get_latest_available_version_in_range(name, min_version, version)

        chunk_size = 1024 * 8

        async def download(name: str, version: Optional[str] = None) -> Tuple[Path, str]:

            async with self._get_factory() as f:
                api = f.build(luminesce.BinaryDownloadingApi)

                res = await api.download_binary_with_http_info(type=name, version=version, _preload_content=False)

                if res.status_code != 200:
                    b = []
                    async for data in res.raw_data.content.iter_chunked(chunk_size):
                        b.append(data)
                    d = json.loads(b''.join(b).decode('utf-8'))
                    raise ApiException(status=d['status'], reason=d['detail'])
                else:
                    if version is None:
                        semver_regex = r"(\d+\.\d+\.\d+)\.nupkg"
                        match = re.search(semver_regex, res.headers['content-disposition'])
                        if match is not None:
                            version = match.group(1)
                        else:
                            raise ApiException(status=400, reason='Could not determine version number')

                print_name = name.replace("_", " ").lower()
                print(f'  Downloading  {print_name} binaries ({version})')

                folder = Path.home() / '.lumipy' / name.lower() / version.replace('.', '_')
                if folder.exists():
                    shutil.rmtree(folder)
                folder.mkdir(parents=True)

                zip_path = folder / f'{name}.zip'

                total = int(res.headers['content-length'])
                pbar = tqdm(desc='    Progress', total=total, unit='B', unit_scale=True, ncols=96)

                with open(zip_path, 'wb') as z:
                    async for data in res.raw_data.content.iter_chunked(chunk_size):
                        z.write(data)
                        pbar.update(len(data))

                pbar.close()

                return zip_path, version

        zip_path, version = self._async_to_sync(download(name, version))

        with ZipFile(zip_path, 'r') as zf:
            zf.extractall(zip_path.parent)

        os.remove(zip_path)

        return version

    def download_certs(self, cert_type: Optional[Literal['Domain', 'User']] = 'Domain'):
        """Download the pem files for running providers. This method will download them and move them to the
        expected directory ~/.lumipy/certs/{domain}/

        Args:
            cert_type (Optional[Literal['Domain', 'User']]): the cert type to download pems for. Defaults to 'Domain'
            the certificate for the client domain. For user-level certs specify 'User'.

        """
        print(f'  Downloading {cert_type.lower()} certificates')

        certs_path = Path.home() / '.lumipy' / 'certs' / self.get_domain()
        if certs_path.exists():
            shutil.rmtree(certs_path)
        certs_path.mkdir(parents=True)

        pem_types = [('Private', 'client_key.pem'), ('Public', 'client_cert.pem')]

        async def download():
            async with self._get_factory() as f:
                api = f.build(luminesce.CertificateManagementApi)
                for file_type, file_name in pem_types:
                    res = await api.download_certificate(type=cert_type, file_type=file_type, may_auto_create=True)
                    pem_path = certs_path / file_name
                    with open(pem_path, 'wb') as pf:
                        pf.write(res)

        self._async_to_sync(download())


def get_client(domain: Optional[str] = None, **kwargs) -> Client:
    """Build a lumipy client by passing any of the following: a token, api_url and app_name; a path to a secrets file
       via api_secrets_file; or by passing in proxy information. If none of these are provided then lumipy will try
       to find the credentials information as environment variables.

    Args:
       domain (Optional[str]): specify a domain that's in lumipy.config

    Keyword Args (all optional):
        access_token (str): Bearer token (PAT) used to initialise the API
        api_secrets_file (str): Name of secrets file (including full path)
        api_url (str): Luminesce API URL (e.g., 'https://{domain}.lusid.com/honeycomb')
        username (str): The username to use
        password (str): The password to use
        client_id (str): The client id to use
        client_secret (str): The client secret to use
        app_name (str): Application name
        certificate_filename (str): Name of the certificate file (.pem, .cer or .crt)
        proxy_address (str): The url of the proxy to use including the port e.g. http://myproxy.com:8888
        proxy_username (str): The username for the proxy to use
        proxy_password (str): The password for the proxy to use
        token_url (str): The token URL of the identity provider

    Notes:
        We recommend setting up configuration using the CLI (Lumipy Config) where possible. Once an access token has
        been configured for a domain, this method can be called without manually supplying arguments.

    Returns:
        Client: the lumipy client.

    """
    if domain is not None and len(kwargs) > 0:
        raise ValueError(
            f"You can't specify kwargs and a lumipy.config domain at the same time. Please choose one or the other."
        )

    if len(kwargs) == 0:
        return Client(**config.creds(domain))

    return Client(**kwargs)


class LumiError(Exception):

    def __init__(self, ex_id: str, status: Dict[str, str]):

        self.ex_id = ex_id
        self.status = status['status']

        p = status['progress']

        front_substr1 = 'Query Execution failed.'
        front_substr2 = 'has the following error(s):'

        if front_substr1 in p:
            start = p.find(front_substr1) + len(front_substr1)
            end = p.find('Sql:')
        elif front_substr2 in p:
            start = p.find(front_substr2) + len(front_substr2)
            end = -1
        else:
            start, end = 0, -1

        self.details = p[start:end].strip()

        lines = '\n'.join([
            f'ex id: {self.ex_id}',
            f'status: {self.status}',
            f'details:',
            indent_str(self.details)
        ])
        msg = f'Query results are unavailable.\nInfo:\n{indent_str(lines)}'

        super().__init__(msg)
