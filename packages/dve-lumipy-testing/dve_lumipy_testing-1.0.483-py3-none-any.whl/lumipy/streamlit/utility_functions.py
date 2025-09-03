from typing import NoReturn, Union

import streamlit as st
from pandas import DataFrame

from lumipy.client import Client
from lumipy.lumiflex._atlas.atlas import Atlas
from lumipy.lumiflex._atlas.query import atlas_queries
from lumipy.lumiflex._metadata.table import TableMeta
from lumipy.lumiflex._table.operation import TableOperation
from lumipy.streamlit.reporter import Reporter


def get_atlas(container, **kwargs) -> Atlas:
    """Get luminesce data provider atlas instance.

    Args:
        container: streamlit container to display running query information in.

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
        Atlas: the atlas instance.

    """
    log = container.empty()

    report = Reporter(log)

    client = Client(**kwargs)

    def _print(x, end='\n'):
        report.update(x + end)

    # Note: can't store the atlas itself because object isinstance checks fail between runtimes
    # This leads to type checking failing when you use fluent syntax from an atlas generated in a different runtime.
    # We have to store the data it's built from and rebuild from that. Thankfully the querying is the slow bit.

    _print("Getting Atlas🌏")

    if 'atlas_dfs' not in st.session_state:
        data_df, direct_df = atlas_queries(client)
        st.session_state['atlas_dfs'] = (data_df, direct_df)

    data_df, direct_df = st.session_state['atlas_dfs']

    data_metas = [TableMeta.data_provider_from_df(gdf) for _, gdf in data_df.groupby('TableName')]
    direct_metas = [TableMeta.direct_provider_from_row(row) for _, row in direct_df.iterrows()]
    _print(f"Contents: \n  • {len(data_metas)} data providers\n  • {len(direct_metas)} direct providers")
    atlas = Atlas(data_metas + direct_metas, client)

    report.empty()

    return atlas


def run_and_report(container, query: Union[str, TableOperation], client=None) -> DataFrame:
    """Runs lumipy query and publishes the progress information to a given container in your streamlit app. Also
    implements a cancel button that will stop the monitoring process and delete the running query.

    Args:
        query (TableOperation): lumipy query expression object to run.
        container: streamlit container to display running query information in.

    Returns:
        DataFrame: dataframe containing the result of the query.
    """

    title = container.empty()
    cancel = container.empty()
    log = container.empty()

    report = Reporter(log)

    title.subheader('[lumipy] executing query')

    if isinstance(query, str):
        job = client.run(query, return_job=True)
    else:
        job = query.go_async(_print_fn=lambda x: report.update(x + '\n'))

    stop = cancel.button(key=job.ex_id, label='Cancel Query', on_click=job.delete)

    job.monitor(stop_trigger=lambda: stop)

    if stop:
        report.empty()
        cancel.empty()
        title.empty()
        return DataFrame()

    report.update("\n\nFetching results... ")
    df = job.get_result()
    report.update("done!\n")

    report.empty()
    cancel.empty()
    title.empty()

    return df


def use_full_width() -> NoReturn:
    """Make streamlit use the full width of the screen.

    Use by calling this function at the top of your application.

    """

    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )
