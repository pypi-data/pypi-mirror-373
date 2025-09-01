import os
import sys

import click
from dotenv import load_dotenv

from synapse_sdk.cli.alias.utils import load_dotenv_default_alias
from synapse_sdk.i18n import gettext as _

from .create import create
from .publish import publish
from .run import run

load_dotenv_default_alias()
load_dotenv(os.path.join(os.getcwd(), '.env'), override=True)
sys.path.append(os.getcwd())


@click.group(context_settings={'obj': {}, 'auto_envvar_prefix': 'SYNAPSE_PLUGIN'})
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def plugin(ctx, debug):
    """Manage Synapse plugins."""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

    if debug:
        click.echo(_('Debug mode is "on"'))


plugin.add_command(create)
plugin.add_command(publish)
plugin.add_command(run)
