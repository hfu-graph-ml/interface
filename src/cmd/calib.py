import click
import os

import capture.calibration as calib
import config.config as config

import utils.input as inp


def execute(config_path: str, verbose: bool):
    ''''''
    cfg, err = config.read_config(config_path)
    if err != None:
        click.echo(f'Error while reading config: {err.message}')
        return

    file_path = os.path.join(cfg['capture']['path'], 'calib.json')

    # Check if we already have a calib.json file
    if os.path.exists(file_path):
        if not inp.confirmation_prompt('A calibration file already exists. Overide?'):
            return

    c = calib.Calibration(cfg, verbose)

    result, err = c._calibrate_auto()
    if err != None:
        click.echo(err.message)
        return

    json_string = calib.dump_calibration_result(result)

    file = open(file_path, 'w')
    file.write(json_string)
    file.close()
