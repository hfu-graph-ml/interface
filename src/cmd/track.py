import click

from tracker.tracker import Tracker
import config.config as config


def execute(config_path: str):
    ''''''
    cfg, err = config.read(config_path)
    if err != None:
        click.echo(f'Error while reading config: {err.message}')
        return

    t = Tracker(cfg['tracker'])
    err = t.run(0, 60)
    if err != None:
        click.echo(err.message)
