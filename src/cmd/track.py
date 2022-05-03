import click

from renderer.renderer import Renderer
from tracker.tracker import Tracker
import config.config as config


def execute(config_path: str, camera_id: int):
    ''''''
    cfg, err = config.read(config_path)
    if err != None:
        click.echo(f'Error while reading config: {err.message}')
        return

    # Create tracker
    t = Tracker(cfg['tracker'])
    err = t.start(camera_id, 60)
    if err != None:
        click.echo(err.message)

    click.echo('Tracking running...')

    # Create renderer
    click.echo('Rendering running...')
    r = Renderer(cfg['renderer'], t)
    err = r.start()
    if err != None:
        click.echo(err.message)

    # TODO (Techassi): Handle interupts and call t.stop()
