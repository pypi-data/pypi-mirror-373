import os

import click
import inquirer
import requests

from .code_server import code_server
from .config import config
from .devtools import devtools
from .plugin import plugin


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def check_backend_status():
    """Check backend connection status and token validity"""
    from synapse_sdk.devtools.config import get_backend_config

    backend_config = get_backend_config()
    if not backend_config:
        return 'not_configured', 'No backend configured'

    try:
        # Try an authenticated endpoint to verify token validity
        # Use /users/me/ which requires authentication
        response = requests.get(
            f'{backend_config["host"]}/users/me/',
            headers={'Synapse-Access-Token': f'Token {backend_config["token"]}'},
            timeout=5,
        )

        if response.status_code == 200:
            return 'healthy', f'Connected to {backend_config["host"]}'
        elif response.status_code == 401:
            return 'auth_error', 'Invalid token (401)'
        elif response.status_code == 403:
            return 'forbidden', 'Access forbidden (403)'
        elif response.status_code == 404:
            # If /users/me/ doesn't exist, try /health as fallback
            try:
                health_response = requests.get(
                    f'{backend_config["host"]}/health',
                    headers={'Synapse-Access-Token': f'Token {backend_config["token"]}'},
                    timeout=3,
                )
                if health_response.status_code == 200:
                    return 'healthy', f'Connected to {backend_config["host"]}'
                elif health_response.status_code == 401:
                    return 'auth_error', 'Invalid token (401)'
                elif health_response.status_code == 403:
                    return 'forbidden', 'Access forbidden (403)'
                else:
                    return 'error', f'HTTP {health_response.status_code}'
            except:  # noqa: E722
                return 'error', 'Endpoint not found (404)'
        else:
            return 'error', f'HTTP {response.status_code}'

    except requests.exceptions.Timeout:
        return 'timeout', 'Connection timeout (>5s)'
    except requests.exceptions.ConnectionError:
        return 'connection_error', 'Connection failed'
    except Exception as e:
        return 'error', f'Connection error: {str(e)}'


def check_agent_status():
    """Check agent configuration status"""
    from synapse_sdk.devtools.config import load_devtools_config

    config = load_devtools_config()
    agent_config = config.get('agent', {})

    if not agent_config.get('id'):
        return 'not_configured', 'No agent selected'

    return 'configured', f'{agent_config.get("name", "")} (ID: {agent_config["id"]})'


def display_connection_status():
    """Display connection status for backend and agent"""
    click.echo(click.style('Connection Status:', fg='white', bold=True))

    # Check backend status (async with timeout)
    backend_status, backend_msg = check_backend_status()

    # Backend status with specific handling for auth errors
    if backend_status == 'healthy':
        click.echo(f'🟢 Backend: {click.style(backend_msg, fg="green")}')
    elif backend_status == 'not_configured':
        click.echo(f'🔴 Backend: {click.style(backend_msg, fg="yellow")}')
    elif backend_status in ['auth_error', 'forbidden']:
        click.echo(f'🔴 Backend: {click.style(backend_msg, fg="red", bold=True)}')
    else:
        click.echo(f'🔴 Backend: {click.style(backend_msg, fg="red")}')

    # Agent status (config check only, no network call)
    agent_status, agent_msg = check_agent_status()
    if agent_status == 'configured':
        click.echo(f'🟢 Agent: {click.style(agent_msg, fg="green")}')
    else:
        click.echo(f'🔴 Agent: {click.style(agent_msg, fg="yellow")}')

    click.echo()  # Empty line for spacing


def run_devtools(build=True):
    """Run devtools with default settings"""
    # Import the devtools command and run it
    from .devtools import devtools

    # Use default settings
    ctx = click.Context(devtools)
    ctx.invoke(devtools, host=None, port=None, debug=False)


# build_frontend function removed - no longer needed with Streamlit


def run_config():
    """Run the configuration menu"""
    from .config import interactive_config

    interactive_config()


def run_plugin_management():
    """Run interactive plugin management"""
    while True:
        clear_screen()
        click.echo(click.style('🔌 Plugin Management', fg='cyan', bold=True))
        click.echo('Manage your Synapse plugins\n')

        questions = [
            inquirer.List(
                'action',
                message='What would you like to do?',
                choices=[
                    ('Create new plugin', 'create'),
                    ('Run plugin locally', 'run'),
                    ('Publish plugin', 'publish'),
                    ('← Back to main menu', 'back'),
                ],
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers or answers['action'] == 'back':
            clear_screen()
            break

        if answers['action'] == 'create':
            click.echo('\nCreating new plugin...')
            from .plugin.create import create

            ctx = click.Context(create)
            ctx.invoke(create)
            click.echo('\nPress Enter to continue...')
            input()

        elif answers['action'] == 'run':
            # Get plugin action and parameters
            run_questions = [
                inquirer.Text('action', message='Plugin action to run'),
                inquirer.Text('params', message='Parameters (JSON format)', default='{}'),
                inquirer.List(
                    'run_by',
                    message='Run by',
                    choices=[
                        ('Script (local)', 'script'),
                        ('Agent', 'agent'),
                        ('Backend', 'backend'),
                    ],
                    default='script',
                ),
            ]

            run_answers = inquirer.prompt(run_questions)
            if run_answers:
                click.echo('\nRunning plugin...')
                from .plugin.run import run

                ctx = click.Context(run)
                ctx.obj = {'DEBUG': False}

                try:
                    if run_answers['run_by'] == 'script':
                        ctx.invoke(
                            run,
                            action=run_answers['action'],
                            params=run_answers['params'],
                            job_id=None,
                            direct=False,
                            run_by='script',
                            agent_host=None,
                            agent_token=None,
                            host=None,
                            agent=None,
                            user_token=None,
                            tenant=None,
                        )
                    else:
                        click.echo(click.style('\nNote: For agent/backend runs, use the command line:', fg='yellow'))
                        cmd = (
                            f"synapse plugin run {run_answers['action']} '{run_answers['params']}' "
                            f'--run-by {run_answers["run_by"]}'
                        )
                        click.echo(cmd)
                except Exception as e:
                    click.echo(click.style(f'\nError: {str(e)}', fg='red'))

                click.echo('\nPress Enter to continue...')
                input()

        elif answers['action'] == 'publish':
            # Get backend configuration
            from synapse_sdk.devtools.config import get_backend_config

            backend_config = get_backend_config()

            if not backend_config:
                click.echo(click.style('\n⚠ No backend configured. Please configure backend first.', fg='yellow'))
                click.echo('\nPress Enter to continue...')
                input()
                continue

            publish_questions = [
                inquirer.Confirm('debug', message='Publish in debug mode?', default=True),
                inquirer.Confirm('confirm', message=f'Publish plugin to {backend_config["host"]}?', default=True),
            ]

            publish_answers = inquirer.prompt(publish_questions)
            if publish_answers and publish_answers['confirm']:
                click.echo('\nPublishing plugin...')
                from .plugin.publish import _publish

                debug_mode = publish_answers.get('debug', True)
                try:
                    _publish(backend_config['host'], backend_config['token'], debug=debug_mode)
                except Exception as e:
                    click.echo(click.style(f'\nError: {str(e)}', fg='red'))
                    click.echo('\nPress Enter to continue...')
                    input()
                else:
                    click.echo('\nPress Enter to continue...')
                    input()


@click.group(invoke_without_command=True)
@click.option('--dev-tools', is_flag=True, help='Start devtools immediately')
@click.pass_context
def cli(ctx, dev_tools):
    """Synapse SDK - Interactive CLI"""

    # Handle --dev-tools flag
    if dev_tools:
        run_devtools()
        return

    if ctx.invoked_subcommand is None:
        while True:
            clear_screen()  # Always clear screen at start of main menu loop
            click.echo(click.style('🚀 Synapse SDK', fg='cyan', bold=True))
            click.echo()

            try:
                questions = [
                    inquirer.List(
                        'choice',
                        message='Select an option:',
                        choices=[
                            ('🌐 Run Dev Tools', 'devtools'),
                            ('💻 Open Code-Server IDE', 'code_server'),
                            ('⚙️  Configuration', 'config'),
                            ('🔌 Plugin Management', 'plugin'),
                            ('🚪 Exit', 'exit'),
                        ],
                    )
                ]

                answers = inquirer.prompt(questions)
                if not answers or answers['choice'] == 'exit':
                    clear_screen()
                    click.echo(click.style('👋 Goodbye!', fg='green'))
                    break

                if answers['choice'] == 'devtools':
                    run_devtools()
                    break  # Exit after devtools finishes
                elif answers['choice'] == 'code_server':
                    from .code_server import code_server

                    ctx.invoke(code_server)
                    click.echo('\nPress Enter to return to main menu...')
                    input()
                    # Continue to main menu loop
                elif answers['choice'] == 'config':
                    run_config()
                    # Config menu returned, continue to main menu loop
                elif answers['choice'] == 'plugin':
                    run_plugin_management()
                    # Don't break - continue to main menu loop

            except (KeyboardInterrupt, EOFError):
                clear_screen()
                click.echo(click.style('👋 Goodbye!', fg='yellow'))
                break


cli.add_command(plugin)
cli.add_command(config)
cli.add_command(devtools)
cli.add_command(code_server)
