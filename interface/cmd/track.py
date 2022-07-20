import click

from utils.input import handle_calibration
from renderer.debug import DebugRenderer
from config.config import read_config
from capture.tracker import Tracker


def execute(config_path: str, calib_mode: str, use_color: bool):
    click.echo('Reading TOML config file...')

    config_result = read_config(config_path, True)
    if config_result.is_err():
        click.echo(f'Error while reading config: {config_result.error().string()}')
        return
    cfg = config_result.unwrap()

    click.echo('Reading / capturing calibration data...')

    calib_result = handle_calibration(cfg, calib_mode)
    if calib_result.is_err():
        click.echo(f'Error while calibration: {calib_result.error().string()}')
        return
    calib_data = calib_result.unwrap()

    click.echo('Tracking running in debug mode...')

    # Create tracker, force debugging
    tracker = Tracker(cfg, calib_data)
    err = tracker.start()
    if err != None:
        click.echo(err.string())

    renderer = DebugRenderer(cfg, tracker, use_color)
    err = renderer.start()
    if err != None:
        click.echo(err.string())
