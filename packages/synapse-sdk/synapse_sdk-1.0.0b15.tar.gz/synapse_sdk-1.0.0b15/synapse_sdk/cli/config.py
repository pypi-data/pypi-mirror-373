import os

import click
import inquirer
import requests

from synapse_sdk.devtools.config import (
    clear_backend_config,
    get_backend_config,
    load_devtools_config,
    save_devtools_config,
    set_backend_config,
)


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def check_backend_connection(host, token):
    """Test backend connection with given credentials"""
    try:
        # Try an authenticated endpoint to verify token validity
        response = requests.get(
            f'{host}/users/me/',
            headers={'Synapse-Access-Token': f'Token {token}'},
            timeout=5,
        )

        if response.status_code == 200:
            return True, 'Connection successful'
        elif response.status_code == 401:
            return False, 'Invalid token (401)'
        elif response.status_code == 403:
            return False, 'Access forbidden (403)'
        elif response.status_code == 404:
            # If /users/me/ doesn't exist, try /health as fallback
            try:
                health_response = requests.get(
                    f'{host}/health',
                    headers={'Synapse-Access-Token': f'Token {token}'},
                    timeout=3,
                )
                if health_response.status_code == 200:
                    return True, 'Connection successful'
                elif health_response.status_code == 401:
                    return False, 'Invalid token (401)'
                elif health_response.status_code == 403:
                    return False, 'Access forbidden (403)'
                else:
                    return False, f'HTTP {health_response.status_code}'
            except Exception:
                return False, 'Endpoint not found (404)'
        else:
            return False, f'HTTP {response.status_code}'

    except requests.exceptions.Timeout:
        return False, 'Connection timeout (>5s)'
    except requests.exceptions.ConnectionError:
        return False, 'Connection failed'
    except Exception as e:
        return False, f'Connection error: {str(e)}'


def check_agent_connection(agent_url, agent_token):
    """Test agent connection with given credentials"""
    if not agent_url or not agent_token:
        return True, 'Agent configured (no URL/token to test)'

    try:
        # Try to connect to the agent
        response = requests.get(
            f'{agent_url}/health/',
            headers={'Authorization': agent_token},
            timeout=5,
        )

        if response.status_code == 200:
            return True, 'Agent connection successful'
        elif response.status_code == 401:
            return False, 'Invalid agent token (401)'
        elif response.status_code == 403:
            return False, 'Agent access forbidden (403)'
        else:
            return False, f'Agent HTTP {response.status_code}'

    except requests.exceptions.Timeout:
        return False, 'Agent connection timeout (>5s)'
    except requests.exceptions.ConnectionError:
        return False, 'Agent connection failed'
    except Exception as e:
        return False, f'Agent error: {str(e)}'


def get_agent_config():
    """Get current agent configuration"""
    config = load_devtools_config()
    return config.get('agent', {})


def get_tenant_config():
    """Get current tenant configuration"""
    config = load_devtools_config()
    return config.get('tenant', {})


def set_tenant_config(tenant_code: str, tenant_name: str = None):
    """Set tenant configuration"""
    config = load_devtools_config()
    config['tenant'] = {'code': tenant_code}
    if tenant_name:
        config['tenant']['name'] = tenant_name
    save_devtools_config(config)


def clear_tenant_config():
    """Clear tenant configuration"""
    config = load_devtools_config()
    if 'tenant' in config:
        del config['tenant']
    save_devtools_config(config)


def set_agent_config(agent_id: str, agent_name: str = None, agent_url: str = None, agent_token: str = None):
    """Set agent configuration"""
    config = load_devtools_config()
    config['agent'] = {'id': agent_id}
    if agent_name:
        config['agent']['name'] = agent_name
    if agent_url:
        config['agent']['url'] = agent_url
    if agent_token:
        config['agent']['token'] = agent_token

    save_devtools_config(config)


def clear_agent_config():
    """Clear agent configuration"""
    config = load_devtools_config()
    if 'agent' in config:
        del config['agent']
    save_devtools_config(config)


def fetch_agents_from_backend():
    """Fetch available agents from the backend"""
    backend_config = get_backend_config()
    if not backend_config:
        return None, 'No backend configuration found. Configure backend first.'

    def extract_uuid(string):
        import re

        """Extract UUID between 'agents/' and '/node_install_script' from a string."""
        pattern = r'agents/([a-f0-9]{40})/node_install_script'
        match = re.search(pattern, string)
        return match.group(1) if match else None

    try:
        response = requests.get(
            f'{backend_config["host"]}/agents/',
            headers={'Synapse-Access-Token': f'Token {backend_config["token"]}'},
            timeout=10,
        )
        if response.status_code == 200:
            try:
                data = response.json()
                results = data.get('results', [])
                for result in results:
                    _node_install_script = result.get('node_install_script')
                    if _node_install_script:
                        result['token'] = extract_uuid(_node_install_script)
                return results, None
            except ValueError:
                return None, 'Invalid JSON response from server'
        elif response.status_code == 401:
            return None, 'Authentication failed. Check your backend token.'
        elif response.status_code == 403:
            return None, 'Access forbidden. Check your permissions.'
        else:
            return None, f'Failed to fetch agents: HTTP {response.status_code}'

    except requests.exceptions.Timeout:
        return None, 'Request timeout. Check your network connection.'
    except requests.exceptions.ConnectionError:
        return None, 'Connection failed. Check backend host URL.'
    except Exception as e:
        return None, f'Error fetching agents: {str(e)}'


def configure_backend():
    """Interactive backend configuration"""
    backend_config = get_backend_config()

    if backend_config:
        click.echo(f'Current backend: {backend_config["host"]}')
        click.echo(f'Token: {backend_config["token"]}')
        click.echo()

    questions = [
        inquirer.List(
            'action',
            message='What would you like to do?',
            choices=[
                ('Configure new backend', 'configure'),
                ('Show current configuration', 'show'),
                ('Clear configuration', 'clear'),
                ('← Back to main menu', 'back'),
            ],
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers or answers['action'] == 'back':
        return

    if answers['action'] == 'show':
        if backend_config:
            click.echo(click.style('\n✓ Backend Configuration:', fg='green'))
            click.echo(f'  Host: {backend_config["host"]}')
            click.echo(f'  Token: {backend_config["token"]}')
        else:
            click.echo(click.style('\n⚠ No backend configuration found.', fg='yellow'))
        return

    if answers['action'] == 'clear':
        confirm = inquirer.confirm('Are you sure you want to clear the backend configuration?')
        if confirm:
            clear_backend_config()
            click.echo(click.style('\n✓ Backend configuration cleared.', fg='yellow'))
        return

    if answers['action'] == 'configure':
        config_questions = [
            inquirer.Text(
                'host',
                message='Backend host URL',
                default=backend_config['host'] if backend_config else 'https://api.synapse.sh',
            ),
            inquirer.Text('token', default=backend_config['token'] if backend_config else '', message='API token'),
        ]

        config_answers = inquirer.prompt(config_questions)
        if config_answers and config_answers['token']:
            set_backend_config(config_answers['host'], config_answers['token'])
            click.echo(click.style('\n✓ Backend configuration saved!', fg='green'))
            click.echo(f'Host: {config_answers["host"]}')
            click.echo(f'Token: {config_answers["token"]}')

            # Test the connection
            click.echo('\nTesting connection...')
            success, message = check_backend_connection(config_answers['host'], config_answers['token'])
            if success:
                click.echo(click.style(f'🟢 {message}', fg='green'))
            else:
                click.echo(click.style(f'🔴 {message}', fg='red'))


def configure_agent():
    """Interactive agent configuration"""
    agent_config = get_agent_config()

    if agent_config:
        click.echo(f'Current agent: {agent_config.get("name", "Unknown")} ({agent_config.get("id")})')
        click.echo()

    questions = [
        inquirer.List(
            'action',
            message='What would you like to do?',
            choices=[
                ('Select agent', 'select'),
                ('Set agent ID manually', 'manual'),
                ('← Back to main menu', 'back'),
            ],
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers or answers['action'] == 'back':
        return

    if answers['action'] == 'select':
        click.echo('Fetching available agents...')
        agents, error = fetch_agents_from_backend()

        if error:
            click.echo(click.style(f'\nError: {error}', fg='red'))
            return

        if not agents:
            click.echo(click.style('\n⚠  No agents found in current workspace.', fg='yellow'))
            return

        # Create choices for agent selection
        agent_choices = []
        for agent in agents:
            status_indicator = '🟢' if agent.get('status', '').lower() == 'connected' else '🔴'
            display_name = f'{status_indicator} {agent["name"]} ({agent["id"]})'
            if agent.get('url'):
                display_name += f' - {agent["url"]}'
            agent_choices.append((display_name, agent))

        agent_choices.append(('← Cancel', None))

        agent_questions = [inquirer.List('selected_agent', message='Select an agent:', choices=agent_choices)]

        agent_answers = inquirer.prompt(agent_questions)
        if agent_answers and agent_answers['selected_agent']:
            selected = agent_answers['selected_agent']
            set_agent_config(selected['id'], selected.get('name'), selected.get('url'), selected.get('token'))
            click.echo(click.style('\n✓ Agent configured!', fg='green'))
            click.echo(f'Selected: {selected["name"]} ({selected["id"]})')
            if selected.get('url'):
                click.echo(f'URL: {selected["url"]}')

            # Test the agent connection if URL and token are provided
            if selected.get('url') and selected.get('token'):
                click.echo('\nTesting agent connection...')
                success, message = check_agent_connection(selected['url'], selected['token'])
                if success:
                    click.echo(click.style(f'🟢 {message}', fg='green'))
                else:
                    click.echo(click.style(f'🔴 {message}', fg='red'))

    if answers['action'] == 'manual':
        manual_questions = [
            inquirer.Text('agent_id', message='Agent ID', default=agent_config.get('id', '') if agent_config else ''),
            inquirer.Text(
                'agent_url', message='Agent URL', default=agent_config.get('url', '') if agent_config else ''
            ),
            inquirer.Text(
                'agent_token', message='Agent Token', default=agent_config.get('token', '') if agent_config else ''
            ),
        ]

        manual_answers = inquirer.prompt(manual_questions)
        if manual_answers and manual_answers['agent_id']:
            set_agent_config(
                manual_answers['agent_id'], None, manual_answers.get('agent_url'), manual_answers.get('agent_token')
            )
            click.echo(click.style('\n✓ Agent configured!', fg='green'))
            click.echo(f'Agent ID: {manual_answers["agent_id"]}')
            if manual_answers.get('agent_url'):
                click.echo(f'Agent URL: {manual_answers["agent_url"]}')

            # Test the agent connection if URL and token are provided
            if manual_answers.get('agent_url') and manual_answers.get('agent_token'):
                click.echo('\nTesting agent connection...')
                success, message = check_agent_connection(manual_answers['agent_url'], manual_answers['agent_token'])
                if success:
                    click.echo(click.style(f'🟢 {message}', fg='green'))
                else:
                    click.echo(click.style(f'🔴 {message}', fg='red'))
        return


def show_current_config():
    """Show all current configuration"""
    backend_config = get_backend_config()
    agent_config = get_agent_config()

    click.echo(click.style('\n📋 Current Configuration', fg='cyan', bold=True))
    click.echo('=' * 30)

    # Backend section
    click.echo(click.style('\n🔗 Backend:', fg='blue', bold=True))
    if backend_config:
        click.echo(f'  Host: {backend_config["host"]}')
        click.echo(f'  Token: {backend_config["token"]}')
        click.echo(click.style('  Status: ✓ Configured', fg='green'))
    else:
        click.echo(click.style('  Status: ✗ Not configured', fg='red'))

    # Agent section
    click.echo(click.style('\n🤖 Agent:', fg='blue', bold=True))
    if agent_config:
        click.echo(f'  ID: {agent_config.get("id", "Not set")}')
        if 'name' in agent_config:
            click.echo(f'  Name: {agent_config["name"]}')
        click.echo(click.style('  Status: ✓ Configured', fg='green'))
    else:
        click.echo(click.style('  Status: ✗ Not configured', fg='red'))


def interactive_config():
    while True:
        clear_screen()
        click.echo(click.style('🔧 Configuration', fg='cyan', bold=True))
        click.echo('Configure your Synapse settings\n')

        questions = [
            inquirer.List(
                'choice',
                message='What would you like to configure?',
                choices=[
                    ('Synapse Backend Host', 'backend'),
                    ('Synapse Agent', 'agent'),
                    ('Show Current Config', 'show'),
                    ('← Back to Main Menu', 'exit'),
                ],
            )
        ]

        try:
            answers = inquirer.prompt(questions)
            if not answers or answers['choice'] == 'exit':
                clear_screen()  # Clear screen when exiting config
                break

            clear_screen()

            if answers['choice'] == 'backend':
                configure_backend()
                click.echo('\nPress Enter to continue...')
                input()
            elif answers['choice'] == 'agent':
                configure_agent()
                click.echo('\nPress Enter to continue...')
                input()
            elif answers['choice'] == 'show':
                show_current_config()
                click.echo('\nPress Enter to continue...')
                input()

        except (KeyboardInterrupt, EOFError):
            clear_screen()  # Clear screen on interrupt
            break
        except Exception as e:
            click.echo(click.style(f'\nError: {str(e)}', fg='red'))
            click.echo('\nPress Enter to continue...')
            input()


@click.command()
def config():
    """Configure Synapse settings interactively"""
    interactive_config()
