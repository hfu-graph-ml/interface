import click

import cmd.track as track
import cmd.gen as gen
import cmd.run as run


@click.group()
def cli():
    pass


@cli.group('gen')
def gen_group():
    pass


@gen_group.command('markers')
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
@click.option('-n', '--number', default=10, help='Number of ArUco markers to generate', type=int, show_default=True)
@click.option('-r', '--res', default=300, help='Size of the ArUco marker in pixels', type=int, show_default=True)
def gen_markers(config_path: str, number: int, res: int):
    gen.markers(config_path, number, res)


@gen_group.command('board')
@click.option('-p', '--path', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
@click.option('-c', '--cols', default=7, help='Number of board columns', type=int, show_default=True)
@click.option('-r', '--rows', default=5, help='Number of board rows', type=int, show_default=True)
@click.option('-w', '--width', default=1920, help='Width of board in pixels', type=int, show_default=True)
@click.option('-h', '--height', default=1080, help='Height of board in pixels', type=int, show_default=True)
def gen_board(config_path: str, cols: int, rows: int, width, height):
    gen.board(config_path, cols, rows, width, height)


@cli.command('run')
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
def run_cmd(config_path: str):
    run.execute(config_path)


@cli.command('track')
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
def track_cmd(config_path: str):
    track.execute(config_path)


def execute():
    cli()
