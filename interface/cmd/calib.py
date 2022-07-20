import click
import os

from capture.calibration import Calibration, dump_calibration_result
from utils.input import confirmation_prompt
from config.config import read_config


def execute(config_path: str, verbose: bool):
    config_result = read_config(config_path)
    if config_result.is_err():
        click.echo(f'Error while reading config: {err.message}')
        return

    cfg = config_result.unwrap()
    file_path = os.path.join(cfg['capture']['path'], 'calib.pckl')

    # Check if we already have a calib.json file
    if os.path.exists(file_path):
        if not confirmation_prompt('A calibration file already exists. Overide?'):
            return

    c = Calibration(cfg, verbose)

    calib_result = c.calibrate()
    if calib_result.is_err():
        click.echo(calib_result.error().string())
        return

    err = dump_calibration_result(file_path, calib_result.unwrap())
    if err != None:
        click.echo(err.string())
