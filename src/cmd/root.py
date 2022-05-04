import click

import cmd.track as track
import cmd.gen as gen
import cmd.run as run


@click.group()
def cli():
    pass


@click.command('gen')
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
@click.option('-n', '--number', default=10, help='Number of ArUco markers to generate', type=int, show_default=True)
@click.option('-r', '--res', default=300, help='Size of the ArUco marker, e.g. 5X5', type=int, show_default=True)
def gen_cmd(config_path: str, number: int, res: int):
    gen.execute(config_path, number, res)


@click.command('run')
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
def run_cmd(config_path: str):
    run.execute(config_path)


@click.command('track')
@click.option('-c', '--config', 'config_path', default='default.toml', help='Path to the TOML config file', type=str, show_default=True)
def track_cmd(config_path: str):
    track.execute(config_path)


cli.add_command(track_cmd)
cli.add_command(gen_cmd)
cli.add_command(run_cmd)


def execute():
    cli()
