import json
from pathlib import Path
from typing import Dict, Optional

CONFIG_DIR = Path.home() / '.config' / 'synapse'
DEVTOOLS_CONFIG_FILE = CONFIG_DIR / 'devtools.json'


def ensure_config_dir():
    """Ensure the config directory exists"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_devtools_config() -> Dict:
    """Load devtools configuration from file"""
    ensure_config_dir()

    # Handle both Path and string types for testing
    config_file = Path(DEVTOOLS_CONFIG_FILE) if isinstance(DEVTOOLS_CONFIG_FILE, str) else DEVTOOLS_CONFIG_FILE

    if not config_file.exists():
        return {}

    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_devtools_config(config: Dict):
    """Save devtools configuration to file"""
    ensure_config_dir()

    # Handle both Path and string types for testing
    config_file = Path(DEVTOOLS_CONFIG_FILE) if isinstance(DEVTOOLS_CONFIG_FILE, str) else DEVTOOLS_CONFIG_FILE

    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError:
        pass


def get_backend_config() -> Optional[Dict]:
    """Get backend configuration (host and token)"""
    config = load_devtools_config()
    backend = config.get('backend', {})

    host = backend.get('host')
    token = backend.get('token')

    if host and token:
        return {'host': host, 'token': token}

    return None


def set_backend_config(host: str, token: str):
    """Set backend configuration"""
    config = load_devtools_config()
    config['backend'] = {'host': host, 'token': token}
    save_devtools_config(config)


def clear_backend_config():
    """Clear backend configuration"""
    config = load_devtools_config()
    if 'backend' in config:
        del config['backend']
    save_devtools_config(config)


def get_server_config() -> Dict:
    """Get server configuration (host and port)"""
    config = load_devtools_config()
    server = config.get('server', {})

    return {'host': server.get('host', '0.0.0.0'), 'port': server.get('port', 8080)}


def set_server_config(host: str = None, port: int = None):
    """Set server configuration"""
    config = load_devtools_config()

    if 'server' not in config:
        config['server'] = {}

    if host is not None:
        config['server']['host'] = host
    if port is not None:
        config['server']['port'] = port

    save_devtools_config(config)
