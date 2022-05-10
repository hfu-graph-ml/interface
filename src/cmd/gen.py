import click

from capture.generator import BoardGenerator, Generator
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

    gen = Generator(cfg)

    click.echo(f'Generating 4 corner and \'{number - 4}\' node markers with {res}x{res} pixels')

    err = gen.generate(number, res)
    if err != None:
        click.echo(f'Error while generating markers: {err.message}')
        return

    click.echo('Saved markers in \'{}\''.format(cfg['capture']['path']))


def board(config_path: str, cols: int, rows: int, res_width: int, res_height: int):
    ''''''
    cfg, err = config.read(config_path)
    if err != None:
        click.echo(f'Error while reading config: {err.message}')
        return

    gen = BoardGenerator(cfg)

    click.echo('Generating ChArUco board')

    err = gen.generate(cols, rows, res_width, res_height)
    if err != None:
        click.echo(f'Error while generating markers: {err.message}')
        return

    click.echo('Saved board in \'{}\''.format(cfg['capture']['path']))
