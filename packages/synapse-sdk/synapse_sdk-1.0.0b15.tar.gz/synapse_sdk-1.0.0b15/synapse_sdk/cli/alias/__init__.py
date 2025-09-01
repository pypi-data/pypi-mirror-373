import click

from .create import create
from .default import default
from .delete import delete
from .list import list as list_cli
from .read import read
from .update import update


@click.group()
def alias():
    """Manage aliases"""
    pass


alias.add_command(list_cli)
alias.add_command(create)
alias.add_command(read)
alias.add_command(update)
alias.add_command(delete)
alias.add_command(default)
