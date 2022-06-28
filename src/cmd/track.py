import click

from capture.tracker import Tracker
import config.config as config
import utils.input as inp


def execute(config_path: str, calib_mode: str):
    '''
    Run debug tracking only.

    Parameters
    ----------
    config_path : str
        Path to the TOML config file
    '''
    click.echo('Reading TOML config file...')

    config_result = config.read(config_path, True)
    if config_result.is_err():
        click.echo(f'Error while reading config: {config_result.error().string()}')
        return

    click.echo('Reading / capturing calibration data...')

    calib_result = inp.handle_calibration(config_result.unpack(), calib_mode)
    if calib_result.is_err():
        click.echo(f'Error while calibration: {calib_result.error().string()}')
        return

    click.echo('Tracking running in debug mode...')

    # Create tracker, force debugging
    t = Tracker(config_result.unpack(), calib_result.unpack(), True)
    err = t.start()
    if err != None:
        click.echo(err.string())
