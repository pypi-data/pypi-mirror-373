from pathlib import Path

import click
from cookiecutter.main import cookiecutter


@click.command()
def create():
    project_root = Path(__file__).parents[2]
    cookiecutter(str(project_root / 'plugins/templates'))
