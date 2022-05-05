import click

from renderer.renderer import Renderer
from tracker.tracker import Tracker
import config.config as config


def execute(config_path: str):
    '''
    Run debug tracking only.

    Parameters
    ----------
    config_path : str
        Path to the TOML config file
    '''
    cfg, err = config.read(config_path)
    if err != None:
        click.echo(f'Error while reading config: {err.message}')
        return

    click.echo('Tracking running in debug mode...')

    # Create tracker, force debugging
    t = Tracker(cfg['tracker'], cfg['capture'], True)
    err = t.start()
    if err != None:
        click.echo(err.message)
