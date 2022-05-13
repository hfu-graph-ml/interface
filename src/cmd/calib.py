import click

import capture.calibration as calib
import config.config as config


def execute(config_path: str):
    ''''''
    cfg, err = config.read(config_path)
    if err != None:
        click.echo(f'Error while reading config: {err.message}')
        return

    c = calib.Calibration(cfg)
    c.calibrate_manual()
