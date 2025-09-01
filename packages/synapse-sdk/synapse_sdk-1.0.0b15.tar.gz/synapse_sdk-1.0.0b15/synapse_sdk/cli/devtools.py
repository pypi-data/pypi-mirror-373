import os
import subprocess
import sys
import time

import click

from synapse_sdk.i18n import gettext as _


@click.command()
@click.option('--host', default=None, help='Host to bind the devtools server')
@click.option('--port', default=None, type=int, help='Port to bind the devtools server')
@click.option('--debug', is_flag=True, help='Run in debug mode')
def devtools(host, port, debug):
    """Start the Synapse devtools web interface"""

    try:
        import importlib.util

        if not importlib.util.find_spec('streamlit') or not importlib.util.find_spec('streamlit_ace'):
            raise ImportError('Missing dependencies')
    except ImportError:
        click.echo(
            click.style(
                _('Devtools dependencies not installed. Install with: pip install synapse-sdk[devtools]'), fg='red'
            ),
            err=True,
        )
        click.echo(
            click.style(_('Specifically, you need: pip install streamlit streamlit-ace'), fg='yellow'),
            err=True,
        )
        sys.exit(1)

    click.echo('Starting Synapse DevTools...')

    # Get the path to the streamlit app
    from pathlib import Path

    app_path = Path(__file__).parent.parent / 'devtools' / 'streamlit_app.py'

    if not app_path.exists():
        click.echo(click.style(f'Streamlit app not found at {app_path}', fg='red'), err=True)
        sys.exit(1)

    # Build streamlit command
    cmd = ['streamlit', 'run', str(app_path)]

    # Add host and port if specified
    if host:
        cmd.extend(['--server.address', host])
    else:
        cmd.extend(['--server.address', '0.0.0.0'])

    if port:
        cmd.extend(['--server.port', str(port)])
    else:
        cmd.extend(['--server.port', '8080'])  # Default port

    cmd.extend(['--server.headless', 'false'])

    if debug:
        cmd.extend(['--logger.level', 'debug'])
    else:
        cmd.extend(['--logger.level', 'error'])

    # Set working directory to current directory (plugin directory)
    plugin_directory = os.getcwd()

    try:
        # Add a small delay to ensure clean output
        time.sleep(0.5)

        # Start streamlit
        process = subprocess.Popen(cmd, cwd=plugin_directory, env=os.environ.copy())

        click.echo('Press Ctrl+C to stop')

        # Wait for process
        process.wait()

    except KeyboardInterrupt:
        click.echo(_('\nDevTools stopped.'))
        if process:
            process.terminate()
            process.wait()
    except Exception as e:
        click.echo(click.style(f'Failed to start devtools: {e}', fg='red'), err=True)
        sys.exit(1)
