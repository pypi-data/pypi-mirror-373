from pathlib import Path

import click

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.i18n import gettext as _
from synapse_sdk.plugins.models import PluginRelease
from synapse_sdk.plugins.upload import archive


def _publish(host, access_token, debug, debug_modules=''):
    """
    Publish a plugin release to the Synapse backend.

    :param host: The host URL of the Synapse backend.
    :param access_token: The access token for authentication.
    :param debug_modules: Comma-separated list of debug modules.
    """
    plugin_release = PluginRelease()

    source_path = Path('./')
    archive_path = source_path / 'dist' / 'archive.zip'
    archive(source_path, archive_path)

    data = {'plugin': plugin_release.plugin, 'file': str(archive_path), 'debug': debug}
    if debug:
        modules = debug_modules.split(',') if debug_modules else []
        data['meta'] = {'modules': modules}

    client = BackendClient(host, access_token)
    client.create_plugin_release(data)

    message = _('Successfully published "{}" ({}) to synapse backend!').format(plugin_release.name, plugin_release.code)
    click.secho(message, fg='green', bold=True)
    return plugin_release


@click.command()
@click.option('--host', required=True)
@click.option('--access_token', required=True)
@click.option('--debug_modules', default='', envvar='SYNAPSE_DEBUG_MODULES')
@click.pass_context
def publish(ctx, host, access_token, debug_modules):
    debug = ctx.obj['DEBUG']
    _publish(host, access_token, debug, debug_modules)
