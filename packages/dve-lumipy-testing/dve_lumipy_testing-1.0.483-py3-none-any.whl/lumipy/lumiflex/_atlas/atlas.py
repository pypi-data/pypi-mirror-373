from __future__ import annotations

from difflib import SequenceMatcher
from fnmatch import fnmatch
from typing import List
from typing import Optional

import lumipy as lm
from lumipy.client import Client
from lumipy.common import indent_str, e_print, emph
from lumipy.lumiflex._atlas.metafactory import MetaFactory, Factory
from lumipy.lumiflex._atlas.query import atlas_queries
from lumipy.lumiflex._atlas.widgets import CatalogueFactory
from lumipy.lumiflex._common.widgets import display
from lumipy.lumiflex._metadata import TableMeta


class Atlas:
    """The atlas provides functionality to explore available providers and then use them.

    Attributes:
        A dynamic set of table factories, one for each provider. Each of these may be called with a parameter set
        to create a provider table object. This table object is then used to build queries.

    @DynamicAttrs
    """

    def __init__(self, provider_metas: List[TableMeta], client: Client, filter_str: Optional[str] = None):

        self._client = client
        self._filter_str = filter_str
        self._provider_metas = provider_metas

        for p_meta in provider_metas:
            self.__dict__[p_meta.python_name()] = MetaFactory(p_meta, client)()

    def _repr_mimebundle_(self, *args, **kwargs):
        node = CatalogueFactory(self).build()
        return display(node, *args, **kwargs)

    def get_domain(self) -> str:
        """Get the domain this atlas is connected to.

        Returns:
            str: the domain name.
        """
        return self.get_client().get_domain()

    def __repr__(self):
        return f'{type(self).__name__}(domain={self.get_domain()})'

    def get_client(self) -> Client:
        """Get the lumipy client that underlies this atlas.

        Returns:
            Client: the underlying client
        """
        return self._client

    def list_providers(self) -> List[Factory]:
        """Get a list of all provider factories in this atlas

        Returns:
            List[Factory]: list of provider factories
        """
        return [f for f in self.__dict__.values() if isinstance(f, Factory)]

    def search(self, pattern: str) -> Atlas:
        """Search through the atlas for providers whose names match a given pattern.
        Uses the built-in module fnmatch, so patterns are Unix shell style:
            *       matches everything
            ?       matches any single character
            [seq]   matches any character in seq
            [!seq]  matches any char not in seq
        but are case-insensitive. You can also specify the negation of the pattern by having '~' at the start of the
        pattern string.

        Examples:
            Get an atlas with just lusid writers
                atlas.search('lusid.*.writer')
            Get an atlas that has the writers filtered out
                atlas.search('~lusid.*.writer')

        Args:
            pattern (str):  the search pattern str to use.

        Returns:
            Atlas: another atlas containing the providers that pass the pattern.

        """
        if pattern[0] == '~':
            criterion = lambda x: not fnmatch(x.meta.name.lower(), pattern[1:].lower())
        else:
            criterion = lambda x: fnmatch(x.meta.name.lower(), pattern.lower())

        metas = [f.meta for f in self.list_providers() if criterion(f)]
        return Atlas(metas, self._client, filter_str=pattern)

    def __getitem__(self, item):
        d = object.__getattribute__(self, '__dict__')
        key = item.replace('.', '_').lower()
        if key in d:
            return d[key]

        def dist_ordered_suggestions(target, patterns):
            dists = {p: SequenceMatcher(a=target, b=p).ratio() for p in patterns}
            return [k for k, v in sorted(dists.items(), key=lambda x: x[1], reverse=True)]

        available = {p.python_name(): p.name for p in d['_provider_metas']}
        suggestions = dist_ordered_suggestions(key, available.keys())[:4]

        suggestions_str = '\n'.join(f'atlas["{available[s]}"]' for s in suggestions)
        raise AttributeError(
            f"Atlas has no provider called '{item}'."
            f"\nDid you mean (case-insensitive):\n{indent_str(suggestions_str)}"
        )


def get_atlas(domain: Optional[str] = None, **kwargs):
    """Get luminesce provider atlas instance by passing any of the following: a token, api_url and app_name; a path to
       a secrets file via api_secrets_file; or by passing in proxy information. If none of these are provided then
       lumipy will try to find the credentials information as environment variables.

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
        Atlas: the atlas instance.

    """

    c = lm.get_client(domain, **kwargs)

    data_df, direct_df = atlas_queries(c)

    data_metas = [TableMeta.data_provider_from_df(gdf) for _, gdf in data_df.groupby('TableName')]
    direct_metas = [TableMeta.direct_provider_from_row(row) for _, row in direct_df.iterrows()]

    atlas = Atlas([m for m in data_metas + direct_metas if m is not None], c)

    domain = emph(f'[{c.get_domain()}]')
    e_print(f'{domain} Atlas 🌐', end='\n')
    print(f"{emph('Contents')}: \n  • {len(data_metas)} data providers\n  • {len(direct_metas)} direct providers")
    return atlas
