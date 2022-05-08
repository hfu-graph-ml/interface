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
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
def gen_board(config_path: str):
    gen.board(config_path)


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
