import os
import click

from utils.input import handle_calibration
from renderer.renderer import Renderer
from config.config import read_config
from capture.tracker import Tracker


def execute(config_path: str, calib_mode: str):
    '''
    Run the interface apppplication.

    Parameters
    ----------
    config_path : str
        Path to the TOML config file
    '''
    # Load config
    config_result = read_config(config_path, True)
    if config_result.is_err():
        click.echo(f'Error while reading config: {config_result.error().string()}')
        return
    cfg = config_result.unwrap()

    # Check if the user already calibrated the camera via the separate command. If yes, we prompt the user to either use
    # the existing data or re-do the calibration. If no, we prompt the user to do the calibration or exit the
    # application.
    calib_result = handle_calibration(cfg, calib_mode)
    if calib_result.is_err():
        click.echo(f'Error while calibration: {calib_result.error().string()}')
        return
    calib_data = calib_result.unwrap()

    # Create tracker
    tracker = Tracker(cfg, calib_data)
    err = tracker.start()
    if err != None:
        click.echo(err.message)

    click.echo('Tracking running...')
    click.echo('Start rendering...')

    # Create renderer
    renderer = Renderer(cfg, calib_data, tracker)
    err = renderer.start()
    if err != None:
        click.echo(err.message)

    # TODO (Techassi): Handle interupts and call t.stop()
