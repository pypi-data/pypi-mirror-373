import click

from lumipy.cli.commands.config import config
from lumipy.cli.commands.query import query
from lumipy.cli.commands.run import run
from lumipy.cli.commands.setup import setup
from lumipy.cli.commands.test import test


@click.group(no_args_is_help=True)
def cli():
    """Welcome to the Lumipy CLI which allows you to manage your config, run providers and their setup, run queries and run tests.

    Lumipy is a Python library that integrates Luminesce with the Python Data Science Stack.

    Set up your token config like this

        $ lumipy config add --domain='my-domain' --token='my-token'

    Then try running some providers

        $ lumipy run demo

    Or try running a SQL query

        $ lumipy query --sql="select ^ from lusid.instrument limit 5"

    """
    pass


cli.add_command(config)
cli.add_command(query)
cli.add_command(run)
cli.add_command(setup)
cli.add_command(test)

if __name__ == '__main__':
    cli()
