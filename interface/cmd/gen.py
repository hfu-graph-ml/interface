import click

from capture.generator import BoardGenerator, Generator
from config.config import read_config


def markers(config_path: str, number: int, res: int):
    config_result = read_config(config_path)
    if config_result.is_err():
        click.echo(f'Error while reading config: {config_result.error().string()}')
        return
    cfg = config_result.unwrap()

    gen = Generator(cfg)

    click.echo(f'Generating 4 corner and \'{number - 4}\' node markers with {res}x{res} pixels')

    err = gen.generate(number, res)
    if err != None:
        click.echo(f'Error while generating markers: {err.string()}')
        return

    click.echo('Saved markers in \'{}\''.format(cfg['capture']['path']))


def board(config_path: str, cols: int, rows: int, res_width: int, res_height: int):
    config_result = read_config(config_path)
    if config_result.is_err():
        click.echo(f'Error while reading config: {config_result.error().string()}')
        return
    cfg = config_result.unwrap()

    gen = BoardGenerator(cfg)

    click.echo('Generating ChArUco board')

    err = gen.generate(cols, rows, res_width, res_height)
    if err != None:
        click.echo(f'Error while generating markers: {err.string()}')
        return

    click.echo('Saved board in \'{}\''.format(cfg['capture']['path']))
