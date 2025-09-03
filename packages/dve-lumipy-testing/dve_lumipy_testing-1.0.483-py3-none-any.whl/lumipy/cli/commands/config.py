from typing import Optional

import click

import lumipy as lm
from lumipy.common import emph

action_types = ['set', 'add', 'show', 'delete', 'deactivate']


def main(action, domain, token, overwrite):

    if action is None:
        lm.config.show()
    elif action == 'add':
        lm.config.add(domain, token, overwrite)
    elif action == 'show':
        lm.config.show()
    elif action == 'delete':
        lm.config.delete(domain)
    elif action == 'set':
        lm.config.set(domain)
    elif action == 'deactivate':
        lm.config.deactivate()
    else:
        raise ValueError(f'Unrecognised lumipy config action: {emph(action)}.')


config_args = click.Choice(action_types, case_sensitive=False)


@click.command()
@click.argument('action', required=False, type=config_args)
@click.option('--domain', help='the domain to target during add, set and delete actions.')
@click.option('--token', help='the token value to add to the config.')
@click.option('--overwrite', help='Whether to overwrite an existing token.', type=bool, is_flag=True)
def config(action: Optional[str], domain: str, token: str, overwrite: bool):
    """Manage your Lumipy config.

    Running just 'lumipy config' will show your current config.

    You may specify one of: set, add, show, delete, deactivate.

    set: set a domain to active.

        $ lumipy config set --domain=my-domain

    add: add a new domain and PAT.

        $ lumipy config add --domain=my-domain --token=<my token> (--overwrite)

    show: show currently configured domains.

        $ lumipy config show

    delete: delete a domain and its PAT from config.

        $ lumipy config delete --domain=my-domain

    deactivate: deactivate all domains, so they aren't automatically used in the lumipy client or atlas.

        $ lumipy config deactivate

    """
    main(action, domain, token, overwrite)
