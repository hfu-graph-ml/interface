import click

from tracker.generator import Generator
import config.config as config


def markers(config_path: str, number: int, res: int):
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

    gen = Generator(cfg['tracker'])

    click.echo(f'Generating 4 corner and \'{number}\' node markers with {res}x{res} pixels')

    err = gen.generate(number, res)
    if err != None:
        click.echo(f'Error while generating markers: {err.message}')
        return

    click.echo('Saved markers in \'{}\''.format(cfg['tracker']['path']))


def board(config_path: str):
    ''''''
