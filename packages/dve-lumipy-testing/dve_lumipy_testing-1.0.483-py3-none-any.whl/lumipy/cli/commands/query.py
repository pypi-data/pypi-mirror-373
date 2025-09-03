import datetime as dt
import tempfile
from pathlib import Path
from typing import Optional

import click

import lumipy as lm
from lumipy.common import emph

tmp_dir = Path(tempfile.gettempdir()) / 'lumipy'


def main(sql, domain, save_to):

    if save_to is not None:
        save_to = Path(save_to)
        if save_to.suffix.lower() != '.csv':
            raise ValueError(
                f'Unsupported data file format ({emph(save_to.suffix)}). Only {emph(".csv")} output is supported currently.'
            )

    c = lm.get_client(domain)
    df = c.run(sql)

    if save_to is None:
        print()
        print(df, end='\n\n')
        now_str = dt.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
        tmp_dir.mkdir(parents=True, exist_ok=True)
        save_to = tmp_dir / f'query_{now_str}.csv'

    save_to.parent.mkdir(exist_ok=True, parents=True)
    df.to_csv(save_to, index=False)
    print(f'Query result saved to {emph(str(save_to))}', end='\n\n')


@click.command(no_args_is_help=True)
@click.option('--sql', help='The SQL string to send to Luminesce.')
@click.option('--domain', help='The client domain to run in. If not specified it will fall back to your lumipy config and then the env variables.')
@click.option('--save-to', help='The location to save the query results to. If not specified it will be saved to a system temp directory that will be printed to screen when the query completes.')
def query(sql: str, domain: Optional[str], save_to: Optional[str]):
    """Run a SQL query string in Luminesce.

    This command runs a SQL query, gets the result back, shows it on screen and then saves it as a CSV.

    Example:

        $ lumipy query --sql="select ^ from lusid.instrument limit 5"

    """
    main(sql, domain, save_to)
