from typing import Optional

import click

from lumipy import get_client
from lumipy.provider.common import min_version, max_version


def setup_domain(domain: Optional[str] = None):

    print('Setting up python providers. 🛠')

    c = get_client(domain)
    c.download_certs()
    c.download_binary('Python_Providers', str(max_version()), str(min_version()), get_best_available=True)
    print('Done!')

    print(f"\nTry running the following command in a terminal:")
    cmd = 'lumipy run demo '
    print('  ' + cmd + '\n')
    print('This will open a browser window for you to log in. '
           'Once startup has finished only you will be able to query it.\n')
    print('To run these demo providers so others in your domain can use them:')
    cmd = 'lumipy run demo --user=global --whitelist-me'
    print('  ', cmd + '\n')
    print('In this case it will not open a browser window.')


def main(target, domain):

    if target is None or target == 'pyprovider':
        setup_domain(domain)
    else:
        raise ValueError(f'Invalid setup type: {target}. Currently supports: \'pyprovider\' (default).')


@click.command()
@click.argument('target', required=False, metavar='TARGET')
@click.option(
    '--domain',
    help='The domain to run setup in. Defaults to the active domain is in config, or creds available in the env vars.'
)
def setup(target, domain):
    """Set up provider infrastructure and certificates.

        This will download the associated binaries and pem files then organise things for you, so they're ready to run.

        TARGET: what to set up. This currently only supports pyproviders (the default if not specified).

        Example:

            $ lumipy setup --domain=my-domain

    """
    main(target, domain)
