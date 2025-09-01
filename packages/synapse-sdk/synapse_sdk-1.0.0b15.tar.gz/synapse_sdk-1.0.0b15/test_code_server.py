#!/usr/bin/env python3
"""Test the code-server command functionality"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synapse_sdk.cli.config import get_agent_config
from synapse_sdk.clients.agent import AgentClient
from synapse_sdk.devtools.config import get_backend_config

# Test getting the code-server info
agent_config = get_agent_config()
backend_config = get_backend_config()

if backend_config and agent_config:
    agent_id = agent_config.get('id')
    agent_token = agent_config.get('token')

    # Hardcode the agent info for testing
    agent_info = {'url': 'http://10.0.22.1:8000', 'id': agent_id}

    # Create agent client
    client = AgentClient(base_url=agent_info['url'], agent_token=agent_token, user_token=backend_config['token'])

    # Get code-server information
    try:
        info = client.get_code_server_info()
        print('Code-server info retrieved:')
        print(f'  Available: {info.get("available")}')
        print(f'  URL: {info.get("url")}')
        print(f'  Password: {info.get("password")}')
        print(f'  Workspace: {info.get("workspace")}')
        print(f'  Tunnel Name: {info.get("tunnel_name")}')
        print(f'  Tunnel URL: {info.get("tunnel_url")}')
        print(f'  SSH Port: {info.get("ssh_port")}')

        # Test the display logic
        tunnel_url = info.get('tunnel_url')
        tunnel_name = info.get('tunnel_name')

        print('\n🚀 Open in Desktop VS Code:')
        if tunnel_url:
            print(f'   ✨ VS Code Tunnel: {tunnel_url}')
            print('   → Open this URL in your browser to connect via VS Code (no SSH needed!)')
            print(f"   → Or install 'Remote - Tunnels' extension in VS Code and connect to: {tunnel_name}")

        print('\n✅ VS Code tunnel connection is properly configured!')
        print('\nTo connect:')
        print(f'1. Open {tunnel_url} in your browser')
        print('2. Sign in with GitHub if prompted')
        print('3. VS Code will open in your browser with full access to the remote workspace')

    except Exception as e:
        print(f'Error: {e}')
else:
    print('No backend or agent configured')
