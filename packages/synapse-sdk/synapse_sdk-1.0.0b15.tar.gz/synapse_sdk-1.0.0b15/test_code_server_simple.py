#!/usr/bin/env python3
"""Simple test of VS Code tunnel URL handling"""

# Simulate the agent response
info = {
    'available': True,
    'host': '10.0.22.1',
    'port': 8443,
    'url': 'http://10.0.22.1:8443',
    'password': '4rzFr58gWtQTZAXs',
    'workspace': '/home/coder/workspace',
    'tunnel_name': 'synapse-agent-72b06ad96087',
    'tunnel_url': 'https://vscode.dev/tunnel/synapse-agent-72b06ad96087',
    'ssh_port': 22,
}

tunnel_url = info.get('tunnel_url')
tunnel_name = info.get('tunnel_name')
workspace = info.get('workspace', '/home/coder/workspace')

print('=' * 60)
print('Code-Server Connection Information')
print('=' * 60)

print('\n🚀 Open in Desktop VS Code:')

if tunnel_url:
    # VS Code tunnel is available - this works without SSH!
    print(f'   ✨ VS Code Tunnel: {tunnel_url}')
    print('   → Open this URL in your browser to connect via VS Code (no SSH needed!)')
    print(f"   → Or install 'Remote - Tunnels' extension in VS Code and connect to: {tunnel_name}")

print('\n🌐 Or use Web Browser:')
print(f'   URL: {info["url"]}')
password = info.get('password')
if password:
    print(f'   Password: {password}')
else:
    print('   Password: Not required (passwordless mode)')
print('   → Works from anywhere with browser access')

print(f'\n📁 Workspace: {workspace}')

print('\n' + '=' * 60)
print('✅ VS Code Tunnel Setup Explanation:')
print('=' * 60)
print("""
The VS Code tunnel (https://vscode.dev/tunnel/...) works as follows:

1. The code-server container runs a VS Code tunnel service
2. This creates a secure tunnel to Microsoft's servers
3. You access it via https://vscode.dev/tunnel/<tunnel-name>
4. No SSH or port forwarding needed - works through firewalls!

To connect:
1. Open the tunnel URL in your browser
2. Sign in with GitHub (for authentication)
3. VS Code opens in your browser with full remote access

Alternative: Install 'Remote - Tunnels' extension in desktop VS Code
and connect directly to the tunnel name.
""")

print('=' * 60)
