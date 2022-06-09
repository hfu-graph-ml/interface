import os
import click

from capture.calibration import Calibration
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

    # Check if the user already calibrated the camera via the separate command. If yes, we prompt the user to either use
    # the existing data or re-do the calibration. If no, we prompt the user to do the calibration or exit the
    # application.
    calib_file_path = os.path.join(cfg['capture']['path'], 'calib.json')
    if not os.path.exists(calib_file_path):
        if inp.confirmation_prompt('No calibration file (.data/calib.json) detected. Run calibration?'):
            c = Calibration(cfg)
            c.calibrate()

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
