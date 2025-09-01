"""Code-server integration for remote plugin development."""

import os
import shutil
import socket
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import click
import inquirer
import yaml

from synapse_sdk.cli.config import fetch_agents_from_backend, get_agent_config
from synapse_sdk.devtools.config import get_backend_config
from synapse_sdk.utils.encryption import encrypt_plugin, get_plugin_info, is_plugin_directory


def get_agent_client(agent: Optional[str] = None):
    """Helper function to get an agent client.

    Args:
        agent: Optional agent ID. If not provided, uses current agent or prompts user.

    Returns:
        tuple: (AgentClient instance, agent_id) or (None, None) if failed
    """
    # Get current agent configuration
    agent_config = get_agent_config()
    backend_config = get_backend_config()

    if not backend_config:
        click.echo("❌ No backend configured. Run 'synapse config' first.")
        return None, None

    # If no agent specified, use current agent or let user choose
    if not agent:
        if agent_config and agent_config.get('id'):
            agent = agent_config['id']
            click.echo(f'Using current agent: {agent_config.get("name", agent)}')
        else:
            # List available agents
            agents, error = fetch_agents_from_backend()
            if not agents:
                click.echo('❌ No agents available. Check your backend configuration.')
                return None, None

            if len(agents) == 1:
                # If only one agent, use it
                agent = agents[0]['id']
                click.echo(f'Using agent: {agents[0].get("name", agent)}')
            else:
                # Let user choose
                click.echo('Available agents:')
                for i, agent_info in enumerate(agents, 1):
                    status = agent_info.get('status_display', 'Unknown')
                    name = agent_info.get('name', agent_info['id'])
                    click.echo(f'  {i}. {name} ({status})')

                try:
                    choice = click.prompt('Select agent', type=int)
                    if 1 <= choice <= len(agents):
                        agent = agents[choice - 1]['id']
                    else:
                        click.echo('❌ Invalid selection')
                        return None, None
                except (ValueError, EOFError, KeyboardInterrupt):
                    click.echo('\n❌ Cancelled')
                    return None, None

    # Get agent details from backend
    try:
        from synapse_sdk.clients.backend import BackendClient

        backend_client = BackendClient(backend_config['host'], access_token=backend_config['token'])

        # Get agent information
        try:
            agent_info = backend_client._get(f'agents/{agent}/')
        except Exception as e:
            click.echo(f'❌ Failed to get agent information for: {agent}')
            click.echo(f'Error: {e}')
            return None, None

        if not agent_info or not agent_info.get('url'):
            click.echo(f'❌ Agent {agent} does not have a valid URL')
            return None, None

        # Get the agent token from local configuration
        agent_token = agent_config.get('token')
        if not agent_token:
            click.echo('❌ No agent token found in configuration')
            click.echo("Run 'synapse config' to configure the agent")
            return None, None

        # Create agent client
        from synapse_sdk.clients.agent import AgentClient

        client = AgentClient(base_url=agent_info['url'], agent_token=agent_token, user_token=backend_config['token'])
        return client, agent

    except Exception as e:
        click.echo(f'❌ Failed to connect to agent: {e}')
        return None, None


def detect_and_encrypt_plugin(workspace_path: str) -> Optional[dict]:
    """Detect and encrypt plugin code in the workspace.

    Args:
        workspace_path: Path to check for plugin

    Returns:
        dict: Encrypted plugin data or None if no plugin found
    """
    plugin_path = Path(workspace_path)

    if not is_plugin_directory(plugin_path):
        return None

    try:
        plugin_info = get_plugin_info(plugin_path)
        click.echo(f'🔍 Detected plugin: {plugin_info["name"]}')

        if 'version' in plugin_info:
            click.echo(f'   Version: {plugin_info["version"]}')
        if 'description' in plugin_info:
            click.echo(f'   Description: {plugin_info["description"]}')

        click.echo('🔐 Encrypting plugin code...')
        encrypted_package, password = encrypt_plugin(plugin_path)

        # Add password to the package (in real implementation, this would be handled securely)
        encrypted_package['password'] = password

        click.echo('✅ Plugin code encrypted successfully')
        return encrypted_package

    except Exception as e:
        click.echo(f'❌ Failed to encrypt plugin: {e}')
        return None


def is_ssh_session() -> bool:
    """Check if we're in an SSH session.

    Returns:
        bool: True if in SSH session, False otherwise
    """
    return bool(os.environ.get('SSH_CONNECTION') or os.environ.get('SSH_CLIENT'))


def is_vscode_terminal() -> bool:
    """Check if we're running in a VSCode terminal.

    Returns:
        bool: True if in VSCode terminal, False otherwise
    """
    return os.environ.get('TERM_PROGRAM') == 'vscode'


def is_vscode_ssh_session() -> bool:
    """Check if we're in a VSCode terminal over SSH.

    Returns:
        bool: True if in VSCode terminal via SSH, False otherwise
    """
    return is_vscode_terminal() and is_ssh_session()


def get_ssh_tunnel_instructions(port: int) -> str:
    """Get SSH tunnel setup instructions for VSCode users.

    Args:
        port: The port number code-server is running on

    Returns:
        str: Instructions for setting up SSH tunnel
    """
    ssh_client = os.environ.get('SSH_CLIENT', '').split()[0] if os.environ.get('SSH_CLIENT') else 'your_server'

    instructions = f"""
📡 VSCode SSH Tunnel Setup:

Since you're using VSCode's integrated terminal over SSH, you can access code-server locally by:

1. Using VSCode's built-in port forwarding:
   • Open Command Palette (Cmd/Ctrl+Shift+P)
   • Type "Forward a Port"
   • Enter port: {port}
   • VSCode will automatically forward the port

2. Or manually forward the port in a new local terminal:
   ssh -L {port}:localhost:{port} {ssh_client}

3. Then open in your local browser:
   http://localhost:{port}
"""
    return instructions


def open_browser_smart(url: str) -> bool:
    """Open browser with smart fallback handling.

    Attempts to open a browser using multiple methods, with appropriate
    handling for SSH sessions and headless environments.

    Args:
        url: URL to open

    Returns:
        bool: True if browser was opened successfully, False otherwise
    """
    # Don't even try to open browser in SSH sessions (except VSCode can handle it)
    if is_ssh_session() and not is_vscode_terminal():
        return False

    # Try Python's webbrowser module first (cross-platform)
    try:
        if webbrowser.open(url):
            return True
    except Exception:
        pass

    # Try platform-specific commands
    commands = []

    # Check for macOS
    if shutil.which('open'):
        commands.append(['open', url])

    # Check for Linux with display
    if os.environ.get('DISPLAY'):
        if shutil.which('xdg-open'):
            commands.append(['xdg-open', url])
        if shutil.which('gnome-open'):
            commands.append(['gnome-open', url])
        if shutil.which('kde-open'):
            commands.append(['kde-open', url])

    # Try each command
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return True
        except Exception:
            continue

    return False


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use.

    Args:
        port: Port number to check

    Returns:
        bool: True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except socket.error:
            return True


def get_process_on_port(port: int) -> Optional[str]:
    """Get the name of the process using a specific port.

    Args:
        port: Port number to check

    Returns:
        str: Process name if found, None otherwise
    """
    try:
        # Use lsof to find the process
        result = subprocess.run(['lsof', '-i', f':{port}', '-t'], capture_output=True, text=True, timeout=2)

        if result.returncode == 0 and result.stdout.strip():
            # Get the PID
            pid = result.stdout.strip().split('\n')[0]

            # Get process details
            proc_result = subprocess.run(['ps', '-p', pid, '-o', 'comm='], capture_output=True, text=True, timeout=2)

            if proc_result.returncode == 0:
                process_name = proc_result.stdout.strip()
                # Check if it's a code-server process
                if 'node' in process_name or 'code-server' in process_name:
                    # Try to get more details
                    cmd_result = subprocess.run(
                        ['ps', '-p', pid, '-o', 'args='], capture_output=True, text=True, timeout=2
                    )
                    if cmd_result.returncode == 0 and 'code-server' in cmd_result.stdout:
                        return 'code-server'
                return process_name
    except Exception:
        pass

    return None


def is_code_server_installed() -> bool:
    """Check if code-server is installed locally.

    Returns:
        bool: True if code-server is available in PATH
    """
    return shutil.which('code-server') is not None


def get_code_server_port() -> int:
    """Get code-server port from config file.

    Returns:
        int: Port number from config, defaults to 8070 if not found
    """
    config_path = Path.home() / '.config' / 'code-server' / 'config.yaml'

    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Parse bind-addr which can be in format "127.0.0.1:8070" or just ":8070"
            bind_addr = config.get('bind-addr', '')
            if ':' in bind_addr:
                port_str = bind_addr.split(':')[-1]
                try:
                    return int(port_str)
                except ValueError:
                    pass
    except Exception:
        # If any error occurs reading config, fall back to default
        pass

    # Default port if config not found or invalid
    return 8070


def launch_local_code_server(workspace_path: str, open_browser: bool = True, custom_port: Optional[int] = None) -> None:
    """Launch local code-server instance.

    Args:
        workspace_path: Directory to open in code-server
        open_browser: Whether to open browser automatically
        custom_port: Optional custom port to use instead of config/default
    """
    try:
        # Use custom port if provided, otherwise get from config
        port = custom_port if custom_port else get_code_server_port()

        # Check if port is already in use
        if is_port_in_use(port):
            process_name = get_process_on_port(port)

            if process_name == 'code-server':
                # Code-server is already running
                click.echo(f'⚠️  Code-server is already running on port {port}')

                # Create URL with folder query parameter
                encoded_path = quote(workspace_path)
                url_with_folder = f'http://localhost:{port}/?folder={encoded_path}'

                # Ask user what to do
                questions = [
                    inquirer.List(
                        'action',
                        message='What would you like to do?',
                        choices=[
                            ('Use existing code-server instance', 'use_existing'),
                            ('Stop existing and start new instance', 'restart'),
                            ('Cancel', 'cancel'),
                        ],
                    )
                ]

                try:
                    answers = inquirer.prompt(questions)

                    if not answers or answers['action'] == 'cancel':
                        click.echo('Cancelled')
                        return

                    if answers['action'] == 'use_existing':
                        click.echo('\n✅ Using existing code-server instance')
                        click.echo(f'   URL: {url_with_folder}')

                        # Optionally open browser
                        if open_browser:
                            if is_vscode_ssh_session():
                                # Special handling for VSCode SSH sessions
                                click.echo(get_ssh_tunnel_instructions(port))
                                click.echo(f'🔗 Remote URL: {url_with_folder}')
                                click.echo(f'\n✨ After port forwarding, access at: http://localhost:{port}')
                            elif is_ssh_session():
                                click.echo('📝 SSH session detected - please open the URL in your local browser')
                                click.echo(f'👉 URL: {url_with_folder}')
                            elif open_browser_smart(url_with_folder):
                                click.echo('✅ Browser opened successfully')
                            else:
                                click.echo('⚠️  Could not open browser automatically')
                                click.echo(f'👉 URL: {url_with_folder}')
                        return

                    if answers['action'] == 'restart':
                        # Stop existing code-server
                        click.echo('Stopping existing code-server...')
                        try:
                            # Get PID of code-server process
                            result = subprocess.run(
                                ['lsof', '-i', f':{port}', '-t'], capture_output=True, text=True, timeout=2
                            )

                            if result.returncode == 0 and result.stdout.strip():
                                pid = result.stdout.strip().split('\n')[0]
                                subprocess.run(['kill', pid], timeout=5)

                                # Wait a moment for process to stop
                                import time

                                time.sleep(2)

                                click.echo('✅ Existing code-server stopped')
                        except Exception as e:
                            click.echo(f'⚠️  Could not stop existing code-server: {e}')
                            click.echo('Please stop it manually and try again')
                            return

                except (KeyboardInterrupt, EOFError):
                    click.echo('\nCancelled')
                    return

            else:
                # Another process is using the port
                click.echo(f'❌ Port {port} is already in use by: {process_name or "unknown process"}')
                if not custom_port:
                    click.echo('\nYou can:')
                    click.echo('1. Stop the process using the port')
                    click.echo('2. Use a different port with --port option (e.g., --port 8071)')
                    click.echo('3. Change the default port in ~/.config/code-server/config.yaml')
                else:
                    click.echo(f'Please try a different port or stop the process using port {port}')
                return

        # Create URL with folder query parameter
        encoded_path = quote(workspace_path)
        url_with_folder = f'http://localhost:{port}/?folder={encoded_path}'

        # Basic code-server command - let code-server handle the workspace internally
        cmd = ['code-server']

        # Add custom port binding if specified
        if custom_port:
            cmd.extend(['--bind-addr', f'127.0.0.1:{port}'])

        cmd.append(workspace_path)

        if not open_browser:
            cmd.append('--disable-getting-started-override')

        click.echo(f'🚀 Starting local code-server for workspace: {workspace_path}')
        if custom_port:
            click.echo(f'   Using custom port: {port}')
        click.echo(f'   URL: {url_with_folder}')
        click.echo('   Press Ctrl+C to stop the server')

        # Start code-server in background if we need to open browser
        if open_browser:
            # Start code-server in background
            import threading
            import time

            def start_server():
                subprocess.run(cmd)

            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()

            # Give server a moment to start
            click.echo('   Waiting for server to start...')
            time.sleep(3)

            # Open browser with folder parameter
            if is_vscode_ssh_session():
                # Special handling for VSCode SSH sessions
                click.echo(get_ssh_tunnel_instructions(port))
                click.echo(f'🔗 Remote URL: {url_with_folder}')
                click.echo(f'\n✨ After port forwarding, access at: http://localhost:{port}')
            elif is_ssh_session():
                click.echo('📝 SSH session detected - please open the URL in your local browser')
                click.echo(f'👉 URL: {url_with_folder}')
            elif open_browser_smart(url_with_folder):
                click.echo('✅ Browser opened successfully')
            else:
                click.echo('⚠️  Could not open browser automatically')
                click.echo(f'👉 Please manually open: {url_with_folder}')

            # Wait for the server thread (blocking)
            try:
                server_thread.join()
            except KeyboardInterrupt:
                click.echo('\n\n✅ Code-server stopped')
        else:
            # Start code-server normally (blocking)
            subprocess.run(cmd)

    except KeyboardInterrupt:
        click.echo('\n\n✅ Code-server stopped')
    except Exception as e:
        click.echo(f'❌ Failed to start local code-server: {e}')


def show_code_server_installation_help() -> None:
    """Show installation instructions for code-server."""
    click.echo('\n❌ Code-server is not installed locally')
    click.echo('\n📦 To install code-server, choose one of these options:')
    click.echo('\n1. Install script (recommended):')
    click.echo('   curl -fsSL https://code-server.dev/install.sh | sh')
    click.echo('\n2. Using npm:')
    click.echo('   npm install -g code-server')
    click.echo('\n3. Using yarn:')
    click.echo('   yarn global add code-server')
    click.echo('\n4. Download from releases:')
    click.echo('   https://github.com/coder/code-server/releases')
    click.echo('\n📚 For more installation options, visit: https://coder.com/docs/code-server/latest/install')


def run_agent_code_server(agent: Optional[str], workspace: str, open_browser: bool) -> None:
    """Run code-server through agent (existing functionality).

    Args:
        agent: Agent name or ID
        workspace: Workspace directory path
        open_browser: Whether to open browser automatically
    """
    client, _ = get_agent_client(agent)
    if not client:
        return

    # Check for plugin and show info if found
    plugin_data = detect_and_encrypt_plugin(workspace)
    if plugin_data:
        click.echo('📦 Plugin detected and encrypted for secure transfer')

    # Get code-server information
    try:
        info = client.get_code_server_info(workspace_path=workspace)
    except Exception as e:
        # Handle other errors
        click.echo(f'❌ Failed to get code-server info: {e}')
        click.echo('\nNote: The agent might not have code-server endpoint implemented yet.')
        return

    # Ensure info is a dictionary
    if not isinstance(info, dict):
        click.echo('❌ Invalid response from agent')
        return

    if not info.get('available', False):
        message = info.get('message', 'Code-server is not available')
        click.echo(f'❌ {message}')
        click.echo('\nTo enable code-server, reinstall the agent with code-server support.')
        return

    # Display connection information
    click.echo('\n✅ Code-Server is available!')

    # Get the workspace path from response or use the requested one
    actual_workspace = info.get('workspace', workspace)

    # Show web browser access
    click.echo('\n🌐 Web-based VS Code:')
    url = info.get('url')
    if not url:
        click.echo('❌ No URL provided by agent')
        return

    click.echo(f'   URL: {url}')
    password = info.get('password')
    if password:
        click.echo(f'   Password: {password}')
    else:
        click.echo('   Password: Not required (passwordless mode)')

    # Show workspace information with better context
    click.echo(f'\n📁 Agent Workspace: {actual_workspace}')
    click.echo(f'📂 Local Project: {workspace}')

    # Only show warning if the paths are drastically different and it's not the expected container path
    if actual_workspace != workspace and not actual_workspace.startswith('/home/coder'):
        click.echo('   ⚠️  Note: Agent workspace differs from local project path')

    # Optionally open in browser
    if open_browser and url:
        click.echo('\nAttempting to open in browser...')

        if is_vscode_ssh_session():
            # Extract port from URL for instructions
            import re

            port_match = re.search(r':(\d+)', url)
            if port_match:
                agent_port = int(port_match.group(1))
                click.echo(get_ssh_tunnel_instructions(agent_port))
            click.echo(f'🔗 Remote URL: {url}')
        elif is_ssh_session():
            click.echo('📝 SSH session detected - please open the URL in your local browser')
            click.echo(f'👉 URL: {url}')
        elif open_browser_smart(url):
            click.echo('✅ Browser opened successfully')
        else:
            click.echo('⚠️  Could not open browser automatically')
            click.echo(f'👉 Please manually open: {url}')

    # Show additional instructions
    click.echo('\n📝 Quick Start:')
    click.echo('1. Open the URL in your browser')
    click.echo('2. Enter the password if prompted')
    click.echo('3. Start coding in the web-based VS Code!')

    # Add note about workspace synchronization
    if actual_workspace.startswith('/home/coder'):
        click.echo("\n💡 Note: Your local project files will be available in the agent's workspace.")
        click.echo('   Changes made in code-server will be reflected in your local project.')


@click.command()
@click.option('--agent', help='Agent name or ID')
@click.option('--open-browser/--no-open-browser', default=True, help='Open in browser')
@click.option('--workspace', help='Workspace directory path (defaults to current directory)')
@click.option('--port', type=int, help='Port to bind code-server (default: from config or 8070)')
def code_server(agent: Optional[str], open_browser: bool, workspace: Optional[str], port: Optional[int]):
    """Open code-server either through agent or locally."""

    # Get current working directory if workspace not specified
    if not workspace:
        workspace = os.getcwd()

    click.echo(f'Using workspace: {workspace}')

    # Check if local code-server is available
    local_available = is_code_server_installed()

    # Create menu options based on availability
    choices = []

    # Always offer agent option
    choices.append(('Open code-server through agent', 'agent'))

    # Add local option if available
    if local_available:
        choices.append(('Open local code-server', 'local'))
    else:
        choices.append(('Install local code-server (not installed)', 'install'))

    choices.append(('Cancel', 'cancel'))

    # Show selection menu
    questions = [inquirer.List('option', message='How would you like to open code-server?', choices=choices)]

    try:
        answers = inquirer.prompt(questions)
        if not answers or answers['option'] == 'cancel':
            click.echo('Cancelled')
            return

        if answers['option'] == 'agent':
            click.echo('\n🤖 Opening code-server through agent...')
            run_agent_code_server(agent, workspace, open_browser)

        elif answers['option'] == 'local':
            click.echo('\n💻 Starting local code-server...')
            launch_local_code_server(workspace, open_browser, port)

        elif answers['option'] == 'install':
            show_code_server_installation_help()

    except (KeyboardInterrupt, EOFError):
        click.echo('\n\nCancelled')
        return
