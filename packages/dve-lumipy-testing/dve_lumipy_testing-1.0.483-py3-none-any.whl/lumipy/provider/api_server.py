import re
import threading
import time

from fastapi import FastAPI
from uvicorn import Server, Config

from .base_provider import BaseProvider
from ..common import indent_str, emph_print


class ApiServer(Server):
    """A local webserver written with FastAPI that wraps a collection of python providers.

    There is an index endpoint for the api server to report what its provider content is and then there are two
    endpoints per provider. One for getting metadata on the provider and another for getting the data it returns.

    """

    def __init__(self, *providers: BaseProvider, host: str, port: int):
        """Constructor of the ApiServer class.

        Args:
            *providers (BaseProvider): provider objects to be run
            host (str): the host str to use such as 'localhost' or '0.0.0.0'
            port (int): the port to expose the server on

        """

        if re.match('^[\w._-]+$', host) is None:
            raise ValueError(f"Invalid value for host: {host}")

        if not isinstance(port, int):
            raise ValueError(f"Port number must be an integer. Was {type(port).__name__} ({port})")

        if len(providers) == 0:
            raise ValueError(
                "Nothing to run! No providers have been supplied to the provider server constructor"
            )

        self.host = host
        self.port = port
        self.base_url = f'http://{self.host}:{self.port}'
        self.provider_roots = []
        self.providers = providers

        self.thread = None

        app = FastAPI(title='Luminesce Python Providers API')

        @app.get('/api/v1/index', tags=['Global'])
        async def provider_index():
            return self.provider_roots

        for p in self.providers:

            if not isinstance(p, BaseProvider):
                raise TypeError(
                    f"*providers arg was not an inheritor of {BaseProvider.__name__} "
                    f"but was {type(p).__name__}."
                )
            if p.path_name == 'index':
                raise ValueError("Can't have a provider called 'index'.")
            if p.name in [pr["Name"] for pr in self.provider_roots]:
                raise ValueError(f"Can't add a provider to the server under a name that's in use: {p.name}.")

            app.include_router(p.router())
            self.provider_roots.append({
                "Name": p.name,
                "ApiPath": f'{self.base_url}/api/v1/{p.path_name}/',
                "Type": type(p).__name__
            })

        super().__init__(Config(app, self.host, self.port))

    def start(self):
        """Start the server up in a thread. This will be blocking until the server is fully set up and will then hand
        back control.

        """

        maxlen_name = max(len(name['Name']) for name in self.provider_roots)

        def prov_str(pr):
            return f" • {pr['Name'].ljust(maxlen_name)} {pr['Type']}"

        provider_list = '\n'.join(map(prov_str, self.provider_roots))
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        emph_print(f'Starting provider API server at {self.base_url}')
        emph_print(f'API documentation may be found at {self.base_url}/docs')
        while not self.started:
            # block
            pass
        print(f'Hosted data provider APIs:\n{indent_str(provider_list, 2)}\n')

    def stop(self):
        """Shut down the api server and trigger the shutdown method of each provider object.

        """
        emph_print('\nStopping python provider API server.')
        time.sleep(0.5)
        for p in self.providers:
            p.shutdown()
        self.should_exit = True
        self.thread.join()
