import click

from renderer.renderer import Renderer
from capture.tracker import Tracker

import config.config as config


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

    # Create tracker
    t = Tracker(cfg)
    err = t.start()
    if err != None:
        click.echo(err.message)

    click.echo('Tracking running...')
    click.echo('Start rendering...')

    # Create renderer
    r = Renderer(cfg, t)
    err = r.start()
    if err != None:
        click.echo(err.message)

    # TODO (Techassi): Handle interupts and call t.stop()
