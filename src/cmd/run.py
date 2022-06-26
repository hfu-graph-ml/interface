import os
import click

from capture.calibration import Calibration, read_calibration_result
from renderer.renderer import Renderer
from capture.tracker import Tracker

import config.config as config
import utils.input as inp


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
        return

    # Check if the user already calibrated the camera via the separate command. If yes, we prompt the user to either use
    # the existing data or re-do the calibration. If no, we prompt the user to do the calibration or exit the
    # application.
    result = inp.handle_calibration(cfg)
    if result.is_err():
        click.echo(err.message)
        return

    # Create tracker
    trk = Tracker(cfg, result.unpack())
    err = trk.start()
    if err != None:
        click.echo(err.message)

    click.echo('Tracking running...')
    click.echo('Start rendering...')

    # Create renderer
    rdr = Renderer(cfg, trk)
    err = rdr.start()
    if err != None:
        click.echo(err.message)

    # TODO (Techassi): Handle interupts and call t.stop()
