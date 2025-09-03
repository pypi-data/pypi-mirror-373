import errno
import re
import socket
import time
import traceback
from typing import Optional, Literal

from lumipy._config_manager import config
from .api_server import ApiServer
from .base_provider import BaseProvider
from .factory import Factory
from ..common import indent_str, red_print, emph_print


def find_free_port(starting_port, max_attempts=25) -> int:
    for attempt in range(max_attempts):
        if port_in_use(starting_port):
            print(f"Port {starting_port} already in use, trying port {starting_port + 1}")
            starting_port += 1
        else:
            return int(starting_port)
    raise RuntimeError(f"Failed to find a free port after {max_attempts} attempts. Please specify a port manually.")


def port_in_use(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            s.listen(1)
            s.close()
            return False
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            return True
        else:
            raise

class ProviderManager:
    """Class that manages the configuration and running of python-based Luminesce providers.

    """

    def __init__(
            self,
            *providers: BaseProvider,
            host: Optional[str] = '127.0.0.1',
            port: Optional[int] = None,
            run_type: Literal['normal', 'python_only', 'dotnet_only'] = 'normal',
            user: Optional[str] = None,
            domain: Optional[str] = None,
            whitelist_me: Optional[bool] = False,
            _sdk_version: Optional[str] = None,
            _fbn_run: Optional[bool] = False,
            _skip_checks: Optional[bool] = False,
            _dev_dll_path: Optional[str] = None,
            via_proxy: Optional[bool] = False,

    ):
        """Constructor of the ProviderManager class.

        Args:
            *providers (BaseProvider): local provider instances (classes that inherit from BaseProvider) that
            the server should manage.
            host (Optional[str]): optional server host path. Defaults to localhost.
            port (Optional[int]): optional port for the server to use. Defaults to None.

            user (Optional[str]): optional user id, or 'global' to run the providers for. You can also specify 'global'
            to run the provider globally.
            domain (Optional[str]): lusid environment to run in.
            _sdk_version (Optional[str]): specify a specific py providers version to run with.
            _fbn_run (Optional[bool]): Internal Finbourne option to be used when running Python Providers in our infrastructure.
            Providers will be run using the RabbitMQ password directly. It expects the Python Providers binary to be installed.
            via_proxy: Optional[bool]: execute all queries via AMQP but over the Hutch-Proxy

        """
        if len(providers) == 0:
            raise ValueError(
                "Nothing to run! No providers have been supplied to the provider server constructor"
            )

        if re.match('^[\w._-]+$', host) is None:
            raise ValueError(f"Invalid value for host: {host}")

        self.port = port
        if self.port is None:
            # The user has not provided a port
            self.port = find_free_port(starting_port=5001)
        else:
            # The user has explicitly specified a port
            if not isinstance(self.port, int):
                raise ValueError(f"Port number must be an integer. Was {type(self.port).__name__} ({self.port})")

            if port_in_use(self.port):
                raise ValueError(f"Port number {self.port} is already in use")

        if user is not None and not user.isalnum():
            raise ValueError(f"Invalid user ID ({user}), must be alphanumeric characters only. ")

        if not _fbn_run and domain is None and config.domain is not None:
            domain = config.domain

        if domain is not None and re.match('^[\w_-]+$', domain) is None:
            raise ValueError(f"Invalid value for domain: {domain}")

        valid_run_types = ['normal', 'python_only', 'dotnet_only']
        if run_type not in valid_run_types:
            valid = ','.join(valid_run_types)
            raise ValueError(f'Invalid provider manager run_type value: {run_type}. Must be one of {valid}.')

        self.run_type = run_type
        self.api_server = ApiServer(*providers, host=host, port=self.port)
        self.factory = Factory(host, self.port, user, domain, whitelist_me, _fbn_run, _sdk_version, _skip_checks, _dev_dll_path, via_proxy)

    def start(self):
        emph_print(f'Launching providers! 🚀')

        if self.run_type == 'dotnet_only':
            red_print(f'⚠️  run_type={self.run_type}: only running the dotnet side (provider factory).')

        if self.run_type == 'python_only':
            red_print(f'⚠️  run_type={self.run_type}: only running the python side (py provider API).')

        if self.run_type != 'dotnet_only':
            self.api_server.start()

        if self.run_type != 'python_only':
            self.factory.start()

        if self.run_type != 'python_only' and not self.factory.errored:
            emph_print('\n🟢 Providers are ready to use.')
            emph_print('Use ctrl+c or the stop button in jupyter to shut down\n')

        elif self.factory.errored:
            red_print("\n💥 Provider factory failed to start!")
            if self.run_type != 'dotnet_only':
                self.api_server.stop()
            raise ValueError(
                'Could not start the factory process due to connection/auth issues during startup. '
                'Check your internet connection / config and try again.'
            )

    def stop(self, exc_type=None, exc_val=None, exc_tb=None):

        if exc_type == KeyboardInterrupt:
            red_print("\n⚠️  Received keyboard interrupt.")

        elif exc_type is not None:
            red_print(f"\n💥 An unexpected {exc_type.__name__} occurred: \"{exc_val}\"")
            red_print("  Traceback (most recent call last):")
            red_print(indent_str(''.join(traceback.format_tb(exc_tb))))
            red_print("  Trying to shut down before rethrow...")

        emph_print('\n🟡 Providers are shutting down.')
        if self.run_type != 'python_only':
            self.factory.stop()
        if self.run_type != 'dotnet_only':
            self.api_server.stop()
        emph_print(f'\n🔴 Providers are shut down.\n')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(exc_type, exc_val, exc_tb)

    def run(self):
        """Run the manager instance in the foreground. The manager can be shut down with a KeyboardInterupt (ctrl+C).

        """
        self.start()
        while True:
            try:
                # block
                time.sleep(5)
            except KeyboardInterrupt as ke:
                self.stop(type(ke), None, None)
                raise ke
            except Exception as e:
                self.stop(type(e), str(e), e.__traceback__)
                raise e
