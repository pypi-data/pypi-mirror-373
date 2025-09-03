import importlib
from importlib.util import spec_from_file_location
from pathlib import Path
from typing import Union, Literal

import click

import lumipy.provider as lp
from lumipy.common import emph, red_print

char_map = str.maketrans("_-", "..")


def from_module(target: Path):
    module_name = target.stem
    spec = spec_from_file_location(module_name, target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    objs = [getattr(module, name) for name in dir(module)]
    return [obj for obj in objs if isinstance(obj, lp.BaseProvider)]


def from_csv(target: Union[str, Path], name: Union[str, None]):

    if name is None:
        f_name = Path(target).stem
        name = 'csv.' + f_name.translate(char_map)
        red_print(f'⚠️  No name supplied. CSV is running as {emph(name)}.')

    if len(name) == 0:
        raise ValueError(
            f'Provider names must be non-empty strings.\n'
            '  For example:\n'
            '    lumipy run /path/to/data.csv ' + emph('--name=my.test.csv\n')
        )
    return lp.PandasProvider(target, name, None)


def main(target: str, name: str, user: str, run_type: Literal['normal', 'python_only', 'dotnet_only'], port: int, domain: str, whitelist_me: bool, dev_dll_path: str, via_proxy: bool, fbn_run: bool):

    fpath = Path(target)

    from lumipy.provider.provider_sets import provider_sets

    if target in provider_sets:
        providers = provider_sets[target]()
    elif fpath.suffix == '.py':
        providers = from_module(fpath)
    elif fpath.suffix == '.csv':
        fpath = target if target.startswith('http') else fpath
        providers = [from_csv(fpath, name)]
    elif fpath.is_dir():

        providers = [from_csv(csv, None) for csv in fpath.glob('*.csv')]

        pys = fpath.glob('*.py')
        for py in pys:
            providers += from_module(py)

        if len(providers) == 0:
            raise ValueError(f'The directory {fpath} contained no providers (*.csv or *.py).')
    else:
        available = ', '.join(emph(k) for k in provider_sets.keys())
        raise ValueError(
            f'Unsupported file format or provider set: {emph(target)}. '
            f'Supported sets are {available}.'
        )

    lp.ProviderManager(*providers, user=user, port=port, domain=domain, whitelist_me=whitelist_me, via_proxy=via_proxy, run_type=run_type, _fbn_run=fbn_run, _dev_dll_path=dev_dll_path).run()


@click.command(no_args_is_help=True)
@click.argument('target', metavar='TARGET')
@click.option('--name', help='the name to give the provider')
@click.option('--user', help='the user to run with. Can be a user ID or "global". If this argument is not specified a login window will be opened.')
@click.option('--port', help='the port that the python provider API should run at. It defaults to 5001. If the default port is unavailable, the system will try the next available port, incrementing one at a time. This process will repeat up to 25 times to find an available port.', default=None, type=int)
@click.option('--domain', help='the client domain to run the providers in.')
@click.option('--whitelist-me', help='Whitelist your machine name. Required when running globally.', type=bool, is_flag=True)
@click.option('--run-type', help='Whether to run normally, or with just the python/dotnet side of the pyproviders (for developers).', default='normal')
@click.option('--dev-dll-path', help='Manually specify the location of the factory dlls (for developers).')
@click.option('--via-proxy', help='Execute all queries via AMQP but over the Hutch-Proxy.', type=bool, is_flag=True)
@click.option('--fbn-run', help='Internal Finbourne option to be used when running Python Providers in our infrastructure', type=bool, is_flag=True)
def run(target: str, name: str, user: str, port: int, domain: str, whitelist_me: bool, run_type: Literal['normal', 'python_only', 'dotnet_only'], dev_dll_path, via_proxy: bool, fbn_run: bool):
    """Run one or more providers.

    TARGET can be one of the following

    A .py file:

        This will import the module and extract all the objects that inherit from lumipy's BaseProvider class and then start a manager that contains them.

        For example:

            $ lumipy run path/to/my_providers.py

    A .csv file:

        This will load the CSV into a pandas provider and start it in a manager. You must supply a name in this case.

        For example:

            $ lumipy run path/to/my_data.csv --name=my.data.csv

        Note: this can be a URL as well.

    A directory:

        This will check the directory for CSV and PY files. It will spin a provider up for each CSV and spin up each
        provider contained in the PY files.

        For example:

            $ lumipy run path/to/files/

    A named built-in provider set:

        For example:

            $ lumipy run demo

    """
    main(target, name, user, run_type, port, domain, whitelist_me, dev_dll_path, via_proxy, fbn_run)
