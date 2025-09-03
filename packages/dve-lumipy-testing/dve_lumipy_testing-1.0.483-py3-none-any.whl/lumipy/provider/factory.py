import os
import re
import shutil
import socket
import subprocess as sp
import tempfile
from pathlib import Path
from signal import SIGINT
from threading import Thread
from typing import Union

from lumipy import config, get_client
from lumipy.provider.common import get_dll_path, get_latest_local_python_provider_semver, get_certs_path, semver_has_dll
from lumipy.provider.common import min_version, max_version
from ..common import red_print, emph_print


def ensure_directory(
        domain: str,
        sdk_version: Union[str, None],
        dev_path: Union[str, None],
        skip_checks: bool,
        get_certs: bool = False,
        fbn_run: bool = False
) -> Path:
    # This is a test where the factory is just constructed and not run.
    if skip_checks:
        return Path(tempfile.gettempdir()) / 'test' / 'path'

    # We are developing against a locally-compiled version.
    if dev_path:
        return Path(dev_path)

    """
    Change sdk version to python_provider_binary_version
    """

    if sdk_version is not None:
        binary_version = sdk_version
    else:
        binary_version = get_latest_local_python_provider_semver()

    if fbn_run:
        return get_dll_path(binary_version, fbn_run)

    if not get_certs:
        get_certs = len(list(get_certs_path(domain).glob('*'))) != 2

    get_binaries = binary_version is None or not semver_has_dll(binary_version)

    if get_certs or get_binaries:
        c = get_client(domain)
        print('Setting up python providers. 🛠')

        if get_certs:
            c.download_certs()

        if get_binaries:
            c.download_binary('Python_Providers', str(max_version()), str(min_version()), get_best_available=True)

    # Look for a valid version again now it's downloaded.
    # If it's still none here we can't continue. In a state that shouldn't happen.
    binary_version = get_latest_local_python_provider_semver()

    return get_dll_path(binary_version)

def machine_name():
    if os.name == 'nt':
        return os.environ['COMPUTERNAME']
    else:
        return socket.gethostname().split('.')[0]


def stop_process(process: sp):
    if os.name == 'nt':
        process.terminate()
    else:
        process.send_signal(SIGINT)


class Factory:
    """This class encapsulates a process that manages the python provider factory dotnet application

    """

    def __init__(
            self,
            host: str,
            port: int,
            user: Union[str, None],
            domain: Union[str, None] = None,
            whitelist_me: bool = False,
            _fbn_run: bool = False,
            _sdk_version: str = None,
            _skip_checks: bool = False,
            _dev_dll_path: Union[str, None] = None,
            via_proxy: bool = False,
    ):
        """Constructor of the Factory class

        Args:
            host (str): the host that the target api server is running at
            port (int): the port that the target api server is exposed at
            user (str): who can user the provider. Can be a user ID, 'global' or None (opens a login window).
            domain (str): which finbourne domain to run in such as fbn-ci (internal), fbn-qa (internal) or fbn-prd.
            _fbn_run (bool): finbourne-internal option for an alternative rabbitMQ authentication when running in K8s.
            _sdk_version (str): version number of sdk to use when developing against version other than the default.
            via_proxy: (bool): execute all queries via AMQP but over the Hutch-Proxy

        """
        self._fbn_run = _fbn_run

        if re.match(r'^[\w._-]+$', host) is None:
            raise ValueError(f"Invalid value for host: {host}")

        if not isinstance(port, int):
            raise ValueError(f"Port number must be an integer. Was {type(port).__name__} ({port})")

        if self._fbn_run:
            if domain is not None:
                raise ValueError('Domain cannot be provided when _fbn_run is True')
        else:
            self.domain = config.domain if domain is None else domain
            if self.domain is None:
                raise ValueError(
                    f'Please set the domain by:\n'
                    '  ProviderManager(p, domain="your domain")\n'
                    'or adding it to lumipy config\n'
                    '  import lumipy as lm\n'
                    '  lm.config.add("your domain", "your token")'
                )

            if re.match(r'^[\w_-]+$', domain) is None:
                raise ValueError(f"Invalid value for domain: {domain}")

        self.base_path = ensure_directory(domain, _sdk_version, _dev_dll_path, _skip_checks, False, self._fbn_run )

        self.cmd = f'dotnet {self.base_path / "Finbourne.Honeycomb.Host.dll"} --quiet '
        if not self._fbn_run :
            self.cmd += f'--authClientDomain={domain} '

        if user is not None and user != 'global':
            self.cmd += f'--localRoutingUserId "{user}" '
        elif user == 'global':
            if not whitelist_me and not self._fbn_run :
                raise ValueError('You must whitelist yourself by setting whitelist_me = True')

            if whitelist_me:
                emph_print(f'Machine name "{machine_name()}" is whitelisted')

            red_print(f'Warning: Providers are running globally')

            self.cmd += f'--routeAs:Global '

        if via_proxy:
            self.cmd += '--viaProxy '

        self.cmd += f'--config "PythonProvider:BaseUrl=>http://{host}:{port}/api/v1/" '

        if whitelist_me and user == 'global':
            self.cmd += f'"DataProvider:RoutingTypeGlobalMachineWhitelist=>{machine_name()}" '

        if self._fbn_run :
            self.cmd += '"Metrics:Enabled=>true" '
            self.cmd += '"NameServiceClient:RabbitConfigFile=>honeycomb-rabbit-config-plain.json" '
            self.cmd += '"NameServiceClient:RabbitUserName=>service-main" '
            self.cmd += '"NameServiceClient:RabbitUserPassword->/usr/app/secrets/service-main" '

        self.starting = True
        self.process = None
        self.print_thread: Thread = None
        self.errored = False
        self.expired_certs = False

        self.startup_attempts = 0

    def start(self):
        """Start the factory process. This will block the program while the setup is running.

        """
        self.startup_attempts +=1

        if self._fbn_run:
            emph_print(f'Starting python provider factory globally at the environment level with fbn_run=true')
        else:
            emph_print(f'Starting python provider factory in {self.domain}')

            for cert in self.base_path.glob('*.pem'):
                cert.unlink()

            os.makedirs(self.base_path, exist_ok=True)
            for cert in get_certs_path(self.domain).glob('*.pem'):
                shutil.copy2(cert, self.base_path / cert.parts[-1])

        print(self.cmd, end='\n\n')

        self.process = sp.Popen(self.cmd.split(), shell=False, stdout=sp.PIPE, stderr=sp.PIPE)

        if self.print_thread is None or not self.print_thread.is_alive():
            self.print_thread = Thread(target=self.__print_process_output)
            self.print_thread.start()

        while self.starting:
            self.check_for_expired_certs()

            self.errored = self.process.poll() is not None
            if self.errored:
                break
            pass

        if self.errored:
            self.print_thread.join()

    def check_for_expired_certs(self):
        if not self._fbn_run and self.expired_certs and self.startup_attempts < 2:
            stop_process(self.process)
            emph_print("Expired certificates were found. Minting new certificates...")
            ensure_directory(self.domain, skip_checks=False, sdk_version=None, dev_path=None, get_certs=True)
            self.start()

    def stop(self):
        """Stop the factory process and shut down the providers. This will block the program while the termination is
        completing.

        """
        if self.process.poll() is not None:
            # no-op
            return

        emph_print('\nStopping python provider factory')

        stop_process(self.process)

        while self.process.poll() is None:
            pass

        self.print_thread.join()

    def __print_process_output(self):
        bad_lines = 0
        try:
            for line in iter(self.process.stdout.readline, b''):
                output = line.decode('utf-8', errors="replace").rstrip()
                if output:
                    print(output)

                if 'Running! Hit Ctrl+C to shut down services' in output:
                    self.starting = False

                if not self._fbn_run and 'Client side SSL Certificate is PAST its expiry' in output:
                    self.expired_certs = True

                if 'RemoteCancellation: ResubscribeAsync failed with' in output:
                    bad_lines += 1
                else:
                    # reset count in case it's a blip
                    bad_lines = 0

                if bad_lines > 50:
                    self.errored = True
                    break
        finally:
            self.process.stdout.close()
            self.process.stderr.close()
