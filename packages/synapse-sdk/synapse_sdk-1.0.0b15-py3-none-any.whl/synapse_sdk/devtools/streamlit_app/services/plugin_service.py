"""Plugin service for managing plugin operations."""

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional

import yaml

from synapse_sdk.cli.plugin.publish import _publish
from synapse_sdk.clients.backend import BackendClient


class PluginService:
    """Service for plugin-related operations."""

    def __init__(self, plugin_directory: Path, backend_client: Optional[BackendClient] = None):
        self.plugin_directory = plugin_directory
        self.config_path = plugin_directory / 'config.yaml'
        self.test_http_path = plugin_directory / 'test.http'
        self.backend_client = backend_client

    def load_config(self) -> Dict:
        """Load plugin configuration from config.yaml."""
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def save_config(self, config: Dict) -> bool:
        """Save plugin configuration to config.yaml."""
        try:
            # Backup existing config
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.yaml.bak')
                self.config_path.rename(backup_path)

            # Write new config
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)

            return True
        except Exception:
            # Restore backup if write failed
            backup_path = self.config_path.with_suffix('.yaml.bak')
            if backup_path.exists():
                backup_path.rename(self.config_path)
            return False

    def parse_test_http(self) -> Dict[str, Dict]:
        """Parse test.http file and extract action parameters."""
        if not self.test_http_path.exists():
            return {}

        requests = {}
        current_request_name = None
        current_body_lines = []
        in_body = False

        try:
            with open(self.test_http_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('###'):
                        # Process previous request
                        if current_request_name and current_body_lines:
                            try:
                                full_request = json.loads(''.join(current_body_lines))
                                if 'params' in full_request:
                                    requests[current_request_name] = full_request['params']
                            except json.JSONDecodeError:
                                pass

                        # Start new request
                        current_request_name = line.replace('###', '').strip()
                        current_body_lines = []
                        in_body = False
                    elif current_request_name and line.startswith('{'):
                        in_body = True
                        current_body_lines.append(line)
                    elif in_body and current_request_name:
                        current_body_lines.append(line)

                # Process last request
                if current_request_name and current_body_lines:
                    try:
                        full_request = json.loads(''.join(current_body_lines))
                        if 'params' in full_request:
                            requests[current_request_name] = full_request['params']
                    except json.JSONDecodeError:
                        pass

            return requests
        except Exception:
            return {}

    def update_test_http_params(self, action: str, new_params: Dict) -> bool:
        """Update parameters for a specific action in test.http."""
        if not self.test_http_path.exists():
            return False

        try:
            with open(self.test_http_path, 'r') as f:
                lines = f.readlines()

            current_action = None
            in_json = False
            json_start_line = -1
            json_lines = []
            updated = False

            for i, line in enumerate(lines):
                if line.strip().startswith('###'):
                    current_action = line.replace('###', '').strip()
                    in_json = False
                    json_lines = []
                elif current_action and line.strip().startswith('{'):
                    in_json = True
                    json_start_line = i
                    json_lines = [line]
                elif in_json:
                    json_lines.append(line)
                    if line.strip() == '}':
                        if current_action == action:
                            try:
                                full_json = json.loads(''.join(json_lines))
                                full_json['params'] = new_params
                                new_json = json.dumps(full_json, indent=2)
                                lines[json_start_line : i + 1] = [new_json + '\n']
                                updated = True
                                break
                            except json.JSONDecodeError:
                                pass
                        in_json = False
                        json_lines = []

            if updated:
                with open(self.test_http_path, 'w') as f:
                    f.writelines(lines)
                return True

            return False
        except Exception:
            return False

    def execute_plugin_action(
        self, action: str, params: Dict, plugin_code: str, agent_id: Optional[int] = None, debug: bool = True
    ) -> Dict:
        """Execute a plugin action via HTTP request."""
        if not self.backend_client:
            return {'success': False, 'error': 'Backend client not configured'}

        if not plugin_code:
            return {'success': False, 'error': 'Plugin code not found in configuration'}

        plugin_url = f'{self.backend_client.base_url}/plugins/{plugin_code}/run/'

        headers = {
            'Accept': 'application/json; indent=4',
            'Content-Type': 'application/json',
        }

        # Get auth headers from backend client
        auth_headers = self.backend_client._get_headers()
        headers.update(auth_headers)

        payload = {
            'agent': agent_id or 2,
            'action': action,
            'params': params,
            'debug': debug,
        }

        start_time = time.time()

        try:
            import requests

            response = requests.post(plugin_url, json=payload, headers=headers, timeout=30)
            execution_time = int((time.time() - start_time) * 1000)

            try:
                response_data = response.json()
            except Exception:
                response_data = response.text

            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response_data': response_data,
                'execution_time': execution_time,
                'url': plugin_url,
                'method': 'POST',
                'headers': headers,
                'payload': payload,
            }
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'status_code': 500,
                'error': str(e),
                'execution_time': execution_time,
                'url': plugin_url,
            }

    def publish_plugin(self, host: str, access_token: str, debug: bool = True) -> Dict:
        """Publish plugin to Synapse platform."""
        original_cwd = os.getcwd()
        try:
            os.chdir(str(self.plugin_directory))

            debug_modules = os.getenv('SYNAPSE_DEBUG_MODULES', '')
            plugin_release = _publish(host, access_token, debug, debug_modules)

            return {
                'success': True,
                'message': (
                    f'Successfully published "{plugin_release.name}" ({plugin_release.code}) to synapse backend!'
                ),
                'plugin_code': plugin_release.code,
                'version': plugin_release.version,
                'name': plugin_release.name,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
        finally:
            os.chdir(original_cwd)
