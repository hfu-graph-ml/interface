import click

from tracker.generator import Generator
import config.config as config


def execute(config_path: str, num: int, res: int):
    '''
    Generate a variable amount of ArUco markers and save them to disk.

    Parameters
    ----------
    config_path : str
        Path to the TOML config file
    num : int
        Number of ArUco markers to generate
    res : int
        Width/Height (Resolution) of the ArUco markers in pixels
    '''
    cfg, err = config.read(config_path)
    if err != None:
        click.echo(f'Error while reading config: {err.message}')
        return

    gen = Generator(
        cfg['tracker']['size'],
        cfg['tracker']['uniques'],
        cfg['tracker']['path']
    )

    click.echo(f'Generating 4 calibration and \'{num}\' node markers with {res}x{res} pixels')

    err = gen.generate_combined(num, res)
    if err != None:
        click.echo(f'Error while generating markers: {err.message}')
        return

    click.echo('Saved markers in \'{}\''.format(cfg['tracker']['path']))
