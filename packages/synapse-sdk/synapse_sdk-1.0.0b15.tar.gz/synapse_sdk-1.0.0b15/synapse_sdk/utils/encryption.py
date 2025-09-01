"""Encryption utilities for plugin code security."""

import base64
import os
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_key(password: str, salt: bytes) -> bytes:
    """Generate encryption key from password.

    * Argument iterations should be at least 500,000.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=700000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_data(data: bytes, password: str) -> Dict:
    """Encrypt data with password."""
    salt = os.urandom(16)
    key = generate_key(password, salt)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)

    return {
        'encrypted_data': base64.b64encode(encrypted_data).decode(),
        'salt': base64.b64encode(salt).decode(),
    }


def decrypt_data(encrypted_package: Dict, password: str) -> bytes:
    """Decrypt data with password."""
    salt = base64.b64decode(encrypted_package['salt'])
    encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])

    key = generate_key(password, salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)


def is_plugin_directory(path: Path) -> bool:
    """Check if directory contains a Synapse plugin."""
    config_file = path / 'config.yaml'
    plugin_dir = path / 'plugin'

    return config_file.exists() and plugin_dir.exists() and plugin_dir.is_dir()


def get_plugin_files(plugin_path: Path) -> List[Tuple[Path, str]]:
    """Get all plugin files with their relative paths."""
    plugin_files = []

    # Essential plugin files
    essential_patterns = [
        'config.yaml',
        'requirements.txt',
        'README.md',
        'pyproject.toml',
    ]

    for pattern in essential_patterns:
        file_path = plugin_path / pattern
        if file_path.exists():
            plugin_files.append((file_path, pattern))

    # Plugin source code
    plugin_dir = plugin_path / 'plugin'
    if plugin_dir.exists():
        for file_path in plugin_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = f'plugin/{file_path.relative_to(plugin_dir)}'
                plugin_files.append((file_path, relative_path))

    # Additional common directories
    for additional_dir in ['tests', 'docs', 'data']:
        dir_path = plugin_path / additional_dir
        if dir_path.exists() and dir_path.is_dir():
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    relative_path = f'{additional_dir}/{file_path.relative_to(dir_path)}'
                    plugin_files.append((file_path, relative_path))

    return plugin_files


def create_plugin_archive(plugin_path: Path) -> bytes:
    """Create a zip archive of the plugin."""
    plugin_files = get_plugin_files(plugin_path)

    archive_buffer = BytesIO()
    with zipfile.ZipFile(archive_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, archive_path in plugin_files:
            zip_file.write(file_path, archive_path)

    return archive_buffer.getvalue()


def encrypt_plugin(plugin_path: Path, password: Optional[str] = None) -> Dict:
    """Encrypt a plugin directory."""
    if not is_plugin_directory(plugin_path):
        raise ValueError(f'Directory {plugin_path} is not a valid plugin directory')

    # Generate password if not provided
    if password is None:
        password = base64.urlsafe_b64encode(os.urandom(32)).decode()

    # Create plugin archive
    archive_data = create_plugin_archive(plugin_path)

    # Encrypt the archive
    encrypted_package = encrypt_data(archive_data, password)

    # Add metadata
    encrypted_package.update({
        'plugin_name': plugin_path.name,
        'plugin_path': str(plugin_path),
        'encryption_method': 'fernet',
        'archive_format': 'zip',
    })

    return encrypted_package, password


def get_plugin_info(plugin_path: Path) -> Optional[Dict]:
    """Get basic plugin information."""
    if not is_plugin_directory(plugin_path):
        return None

    info = {'name': plugin_path.name, 'path': str(plugin_path), 'is_plugin': True}

    # Try to read config.yaml for additional info
    config_file = plugin_path / 'config.yaml'
    if config_file.exists():
        try:
            import yaml

            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                info.update({
                    'version': config.get('version', 'unknown'),
                    'description': config.get('description', ''),
                    'category': config.get('category', 'unknown'),
                })
        except Exception:
            pass  # Continue without config details if parsing fails

    return info
