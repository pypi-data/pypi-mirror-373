"""
Integration tests for Synapse CLI

These tests simulate real user workflows and interactions with the CLI.
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest
import requests
import requests_mock
from click.testing import CliRunner

from synapse_sdk.cli import cli


class TestCLIWorkflows:
    """Test complete CLI workflows end-to-end"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'devtools.json')
            with patch('synapse_sdk.devtools.config.DEVTOOLS_CONFIG_FILE', config_path):
                yield temp_dir, config_path

    @pytest.fixture
    def mock_api_responses(self):
        """Setup mock API responses"""
        return {
            'users_me': {'tenants': [{'code': 'test-tenant'}]},
            'agents': {
                'results': [
                    {
                        'id': 'agent-123',
                        'name': 'Production Agent',
                        'url': 'http://prod-agent.example.com',
                        'status_display': 'online',
                    },
                    {
                        'id': 'agent-456',
                        'name': 'Development Agent',
                        'url': 'http://dev-agent.example.com',
                        'status_display': 'offline',
                    },
                ]
            },
        }

    def test_complete_setup_workflow(self, temp_config_dir, mock_api_responses):
        """Test complete setup workflow: backend config -> agent selection"""
        temp_dir, config_path = temp_config_dir

        backend_host = 'https://api.example.com'
        backend_token = 'test-token-abc123'

        # Mock the entire configuration workflow
        with requests_mock.Mocker() as m:
            # Mock backend health check
            m.get(f'{backend_host}/users/me/', json=mock_api_responses['users_me'])
            # Mock agents endpoint
            m.get(f'{backend_host}/agents/', json=mock_api_responses['agents'])

            # Simulate user interactions
            user_inputs = [
                # Backend configuration
                {'action': 'configure'},
                {'host': backend_host, 'token': backend_token},
                # Agent selection
                {'action': 'select'},
                {'selected_agent': mock_api_responses['agents']['results'][0]},
                # Exit
                {'action': 'back'},
            ]

            with patch('synapse_sdk.cli.config.inquirer.prompt') as mock_prompt:
                mock_prompt.side_effect = user_inputs

                with patch('synapse_sdk.cli.config.clear_screen'):
                    with patch('click.echo'):
                        with patch('builtins.input'):  # Mock input() for "Press Enter to continue"
                            # Configure backend first
                            from synapse_sdk.cli.config import configure_backend

                            configure_backend()

                            # Then configure agent
                            from synapse_sdk.cli.config import configure_agent

                            configure_agent()

        # Verify configuration was saved correctly
        with open(config_path, 'r') as f:
            saved_config = json.load(f)

        # Check backend config
        assert 'backend' in saved_config
        assert saved_config['backend']['host'] == backend_host
        assert saved_config['backend']['token'] == backend_token

        # Check agent config
        assert 'agent' in saved_config
        assert saved_config['agent']['id'] == 'agent-123'
        assert saved_config['agent']['name'] == 'Production Agent'

    def test_connection_status_display_workflow(self, temp_config_dir, mock_api_responses):
        """Test connection status display with various states"""
        temp_dir, config_path = temp_config_dir

        # Create initial config
        initial_config = {
            'backend': {'host': 'https://api.example.com', 'token': 'valid-token'},
            'agent': {'id': 'agent-123', 'name': 'Test Agent'},
        }

        with open(config_path, 'w') as f:
            json.dump(initial_config, f)

        # Test healthy connection status
        with requests_mock.Mocker() as m:
            m.get('https://api.example.com/users/me/', json=mock_api_responses['users_me'])

            from synapse_sdk.cli import check_agent_status, check_backend_status

            # Test backend status
            backend_status, backend_msg = check_backend_status()
            assert backend_status == 'healthy'
            assert 'api.example.com' in backend_msg

            # Test agent status
            agent_status, agent_msg = check_agent_status()
            assert agent_status == 'configured'
            assert 'Test Agent' in agent_msg

    def test_error_recovery_workflow(self, temp_config_dir):
        """Test error recovery in various scenarios"""
        temp_dir, config_path = temp_config_dir

        # Setup config with invalid token
        config_with_bad_token = {'backend': {'host': 'https://api.example.com', 'token': 'invalid-token'}}

        with open(config_path, 'w') as f:
            json.dump(config_with_bad_token, f)

        # Test auth error handling
        with requests_mock.Mocker() as m:
            m.get('https://api.example.com/users/me/', status_code=401)

            from synapse_sdk.cli import check_backend_status

            status, message = check_backend_status()

            assert status == 'auth_error'
            assert '401' in message

    def test_agent_selection_workflow(self, temp_config_dir, mock_api_responses):
        """Test agent selection with different scenarios"""
        temp_dir, config_path = temp_config_dir

        # Setup backend config
        backend_config = {'backend': {'host': 'https://api.example.com', 'token': 'valid-token'}}

        with open(config_path, 'w') as f:
            json.dump(backend_config, f)

        with requests_mock.Mocker() as m:
            m.get('https://api.example.com/agents/', json=mock_api_responses['agents'])

            # Test agent fetching
            from synapse_sdk.cli.config import fetch_agents_from_backend

            agents, error = fetch_agents_from_backend()

            assert error is None
            assert len(agents) == 2
            assert agents[0]['name'] == 'Production Agent'
            assert agents[1]['status_display'] == 'offline'

    def test_config_persistence_workflow(self, temp_config_dir):
        """Test configuration persistence across operations"""
        temp_dir, config_path = temp_config_dir

        # Test multiple configuration operations
        from synapse_sdk.cli.config import clear_agent_config, get_agent_config, set_agent_config

        # Set initial agent config
        set_agent_config('agent-1', 'First Agent')
        config1 = get_agent_config()
        assert config1['id'] == 'agent-1'
        assert config1['name'] == 'First Agent'

        # Update agent config
        set_agent_config('agent-2', 'Second Agent')
        config2 = get_agent_config()
        assert config2['id'] == 'agent-2'
        assert config2['name'] == 'Second Agent'

        # Clear agent config
        clear_agent_config()
        config3 = get_agent_config()
        assert config3 == {}

        # Verify file state after each operation
        with open(config_path, 'r') as f:
            final_config = json.load(f)
            assert 'agent' not in final_config

    def test_main_menu_navigation_workflow(self):
        """Test navigation through main CLI menu"""
        runner = CliRunner()

        # Test showing help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Synapse SDK' in result.output

        # Test config command
        result = runner.invoke(cli, ['config', '--help'])
        assert result.exit_code == 0
        assert 'Configure Synapse settings' in result.output

    @patch('synapse_sdk.cli.inquirer.prompt')
    @patch('synapse_sdk.cli.clear_screen')
    def test_interactive_main_menu_workflow(self, mock_clear, mock_prompt):
        """Test interactive main menu workflow"""
        # Simulate user selecting config then exit
        mock_prompt.side_effect = [
            {'choice': 'config'},  # Select configuration
            {'choice': 'exit'},  # Exit from config
        ]

        runner = CliRunner()

        with patch('synapse_sdk.cli.run_config') as mock_run_config:
            runner.invoke(cli)

            # Verify config was called
            mock_run_config.assert_called_once()
            # Verify clear screen was called
            mock_clear.assert_called()


class TestCLIEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'devtools.json')
            with patch('synapse_sdk.devtools.config.DEVTOOLS_CONFIG_FILE', config_path):
                yield temp_dir, config_path

    def test_corrupted_config_file_handling(self):
        """Test handling of corrupted configuration files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            temp_path = f.name

        try:
            with patch('synapse_sdk.devtools.config.DEVTOOLS_CONFIG_FILE', temp_path):
                from synapse_sdk.cli.config import get_agent_config

                # Should handle gracefully and return empty config
                config = get_agent_config()
                assert config == {}
        finally:
            import os

            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_empty_agent_list_handling(self, temp_config_dir):
        """Test handling when no agents are available"""
        temp_dir, config_path = temp_config_dir

        # Setup backend config
        backend_config = {'backend': {'host': 'https://api.example.com', 'token': 'valid-token'}}

        with open(config_path, 'w') as f:
            json.dump(backend_config, f)

        with requests_mock.Mocker() as m:
            # Return empty agent list
            m.get('https://api.example.com/agents/', json={'results': []})

            from synapse_sdk.cli.config import fetch_agents_from_backend

            agents, error = fetch_agents_from_backend()

            assert error is None
            assert agents == []

    def test_network_timeout_handling(self, temp_config_dir):
        """Test handling of network timeouts"""
        temp_dir, config_path = temp_config_dir

        # Setup backend config
        backend_config = {'backend': {'host': 'https://slow.example.com', 'token': 'valid-token'}}

        with open(config_path, 'w') as f:
            json.dump(backend_config, f)

        with requests_mock.Mocker() as m:
            m.get('https://slow.example.com/agents/', exc=requests.exceptions.Timeout)

            from synapse_sdk.cli.config import fetch_agents_from_backend

            agents, error = fetch_agents_from_backend()

            assert agents is None
            assert 'timeout' in error.lower()

    def test_malformed_api_response_handling(self, temp_config_dir):
        """Test handling of malformed API responses"""
        temp_dir, config_path = temp_config_dir

        # Setup backend config
        backend_config = {'backend': {'host': 'https://api.example.com', 'token': 'valid-token'}}

        with open(config_path, 'w') as f:
            json.dump(backend_config, f)

        with requests_mock.Mocker() as m:
            # Return malformed response (missing 'results' key)
            m.get('https://api.example.com/agents/', json={'invalid': 'response'}, status_code=200)

            from synapse_sdk.cli.config import fetch_agents_from_backend

            # Should handle gracefully
            try:
                agents, error = fetch_agents_from_backend()
                # Should either return empty list or handle error
                assert agents is not None or error is not None
            except Exception as e:
                pytest.fail(f'Should handle malformed response gracefully: {e}')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
