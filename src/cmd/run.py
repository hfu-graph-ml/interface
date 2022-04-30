import click

import config.config as config
import client.client as client


def execute(config_path: str):
    '''
    Run the interface apppplication.

    Parameters
    ----------
    config_path : str
        Path to the TOML config file
    '''
    # Load config
    cfg, err = config.read(config_path)
    if err != None:
        click.echo(f'Failed to load config \'{config_path}\': {err}')

    # Create a new HTTP client which talks to the REST API
    c = client.Client(cfg)

    graph, err = c.get_graph()
    if err != None:
        click.echo(f'Error: {err}')
        return

    click.echo(graph)
