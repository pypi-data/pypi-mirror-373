import json
import os
import tempfile
from unittest.mock import patch

import pytest
import requests
import requests_mock
from click.testing import CliRunner

from synapse_sdk.cli import cli
from synapse_sdk.cli.config import (
    clear_agent_config,
    configure_agent,
    configure_backend,
    fetch_agents_from_backend,
    get_agent_config,
    interactive_config,
    set_agent_config,
)


class TestCLIConfiguration:
    """Test configuration management functionality"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'devtools.json')
            with patch('synapse_sdk.devtools.config.DEVTOOLS_CONFIG_FILE', config_path):
                yield temp_dir

    @pytest.fixture
    def mock_backend_config(self):
        """Mock backend configuration"""
        return {'host': 'https://api.synapse.sh', 'token': 'test-token-123'}

    @pytest.fixture
    def mock_agent_response(self):
        """Mock agent API response"""
        return {
            'results': [
                {
                    'id': 'agent-1',
                    'name': 'Test Agent 1',
                    'url': 'http://agent1.example.com',
                    'status_display': 'online',
                },
                {
                    'id': 'agent-2',
                    'name': 'Test Agent 2',
                    'url': 'http://agent2.example.com',
                    'status_display': 'offline',
                },
            ]
        }

    def test_agent_config_operations(self, temp_config_dir):
        """Test agent configuration CRUD operations"""
        # Test empty config initially
        config = get_agent_config()
        assert config == {}

        # Test setting agent config
        set_agent_config('test-agent-id', 'Test Agent')
        config = get_agent_config()
        assert config['id'] == 'test-agent-id'
        assert config['name'] == 'Test Agent'

        # Test setting agent config without name
        set_agent_config('agent-id-only')
        config = get_agent_config()
        assert config['id'] == 'agent-id-only'
        assert 'name' not in config

        # Test clearing agent config
        clear_agent_config()
        config = get_agent_config()
        assert config == {}

    @patch('synapse_sdk.cli.config.get_backend_config')
    def test_fetch_agents_no_backend_config(self, mock_get_backend):
        """Test fetching agents when no backend is configured"""
        mock_get_backend.return_value = None

        agents, error = fetch_agents_from_backend()

        assert agents is None
        assert 'No backend configuration found' in error

    @patch('synapse_sdk.cli.config.get_backend_config')
    def test_fetch_agents_success(self, mock_get_backend, mock_backend_config, mock_agent_response):
        """Test successful agent fetching"""
        mock_get_backend.return_value = mock_backend_config

        with requests_mock.Mocker() as m:
            m.get(f'{mock_backend_config["host"]}/agents/', json=mock_agent_response, status_code=200)

            agents, error = fetch_agents_from_backend()

            assert error is None
            assert len(agents) == 2
            assert agents[0]['name'] == 'Test Agent 1'
            assert agents[1]['status_display'] == 'offline'

    @patch('synapse_sdk.cli.config.get_backend_config')
    def test_fetch_agents_auth_error(self, mock_get_backend, mock_backend_config):
        """Test agent fetching with authentication error"""
        mock_get_backend.return_value = mock_backend_config

        with requests_mock.Mocker() as m:
            m.get(f'{mock_backend_config["host"]}/agents/', text='', status_code=401)

            agents, error = fetch_agents_from_backend()

            assert agents is None
            assert 'Authentication failed' in error

    @patch('synapse_sdk.cli.config.get_backend_config')
    def test_fetch_agents_timeout(self, mock_get_backend, mock_backend_config):
        """Test agent fetching with timeout"""
        mock_get_backend.return_value = mock_backend_config

        with requests_mock.Mocker() as m:
            m.get(f'{mock_backend_config["host"]}/agents/', exc=requests.exceptions.Timeout)

            agents, error = fetch_agents_from_backend()

            assert agents is None
            assert 'timeout' in error.lower()


class TestCLIConnectionStatus:
    """Test connection status checking functionality"""

    @pytest.fixture
    def mock_backend_config(self):
        return {'host': 'https://api.synapse.sh', 'token': 'test-token-123'}

    @patch('synapse_sdk.devtools.config.get_backend_config')
    def test_check_backend_status_not_configured(self, mock_get_backend):
        """Test backend status when not configured"""
        from synapse_sdk.cli import check_backend_status

        mock_get_backend.return_value = None

        status, message = check_backend_status()

        assert status == 'not_configured'
        assert 'No backend configured' in message

    @patch('synapse_sdk.devtools.config.get_backend_config')
    def test_check_backend_status_healthy(self, mock_get_backend, mock_backend_config):
        """Test healthy backend status"""
        from synapse_sdk.cli import check_backend_status

        mock_get_backend.return_value = mock_backend_config

        with requests_mock.Mocker() as m:
            m.get(f'{mock_backend_config["host"]}/users/me/', json={'tenants': [{'code': 'test'}]}, status_code=200)

            status, message = check_backend_status()

            assert status == 'healthy'
            assert mock_backend_config['host'] in message

    @patch('synapse_sdk.devtools.config.get_backend_config')
    def test_check_backend_status_auth_error(self, mock_get_backend, mock_backend_config):
        """Test backend status with auth error"""
        from synapse_sdk.cli import check_backend_status

        mock_get_backend.return_value = mock_backend_config

        with requests_mock.Mocker() as m:
            m.get(f'{mock_backend_config["host"]}/users/me/', text='', status_code=401)

            status, message = check_backend_status()

            assert status == 'auth_error'
            assert '401' in message

    @patch('synapse_sdk.devtools.config.load_devtools_config')
    def test_check_agent_status_not_configured(self, mock_load_config):
        """Test agent status when not configured"""
        from synapse_sdk.cli import check_agent_status

        mock_load_config.return_value = {}

        status, message = check_agent_status()

        assert status == 'not_configured'
        assert 'No agent selected' in message

    @patch('synapse_sdk.devtools.config.load_devtools_config')
    def test_check_agent_status_configured(self, mock_load_config):
        """Test agent status when configured"""
        from synapse_sdk.cli import check_agent_status

        mock_load_config.return_value = {'agent': {'id': 'test-agent', 'name': 'Test Agent'}}

        status, message = check_agent_status()

        assert status == 'configured'
        assert 'Test Agent' in message


class TestCLIInteractiveMenus:
    """Test interactive menu functionality"""

    @patch('synapse_sdk.cli.config.inquirer.prompt')
    @patch('synapse_sdk.cli.config.clear_screen')
    def test_configure_backend_show_action(self, mock_clear, mock_prompt):
        """Test backend configuration show action"""
        # Mock user selecting 'show' action
        mock_prompt.return_value = {'action': 'show'}

        with patch('synapse_sdk.cli.config.get_backend_config') as mock_get_config:
            mock_get_config.return_value = {'host': 'https://test.com', 'token': 'test-token'}

            with patch('click.echo') as mock_echo:
                configure_backend()

                # Verify show action was called
                mock_echo.assert_any_call('  Host: https://test.com')

    @patch('synapse_sdk.cli.config.inquirer.prompt')
    @patch('synapse_sdk.cli.config.clear_screen')
    def test_configure_backend_clear_action(self, mock_clear, mock_prompt):
        """Test backend configuration clear action"""
        # Mock user selecting 'clear' and confirming
        mock_prompt.side_effect = [
            {'action': 'clear'},  # First prompt - select clear
            True,  # Confirmation prompt
        ]

        with patch('synapse_sdk.cli.config.clear_backend_config') as mock_clear_config:
            with patch('click.echo'):
                with patch('inquirer.confirm', return_value=True):
                    configure_backend()

                    mock_clear_config.assert_called_once()

    @patch('synapse_sdk.cli.config.inquirer.prompt')
    @patch('synapse_sdk.cli.config.clear_screen')
    def test_configure_agent_manual_action(self, mock_clear, mock_prompt):
        """Test agent configuration manual ID entry"""
        # Mock user selecting manual and entering agent ID
        mock_prompt.side_effect = [
            {'action': 'manual'},  # Select manual entry
            {'agent_id': 'manual-agent-123'},  # Enter agent ID
        ]

        with patch('synapse_sdk.cli.config.get_agent_config') as mock_get_config:
            mock_get_config.return_value = {}

            with patch('synapse_sdk.cli.config.set_agent_config') as mock_set_config:
                with patch('click.echo'):
                    configure_agent()

                    mock_set_config.assert_called_once_with('manual-agent-123', None, None, None)

    @patch('synapse_sdk.cli.config.inquirer.prompt')
    @patch('synapse_sdk.cli.config.clear_screen')
    def test_configure_agent_select_action(self, mock_clear, mock_prompt):
        """Test agent configuration with selection from list"""
        # Mock user selecting from agent list
        mock_agent = {'id': 'selected-agent', 'name': 'Selected Agent'}

        mock_prompt.side_effect = [
            {'action': 'select'},  # Select from list
            {'selected_agent': mock_agent},  # Choose specific agent
        ]

        with patch('synapse_sdk.cli.config.get_agent_config') as mock_get_config:
            mock_get_config.return_value = {}

            with patch('synapse_sdk.cli.config.fetch_agents_from_backend') as mock_fetch:
                mock_fetch.return_value = ([mock_agent], None)

                with patch('synapse_sdk.cli.config.set_agent_config') as mock_set_config:
                    with patch('click.echo'):
                        configure_agent()

                        mock_set_config.assert_called_once_with('selected-agent', 'Selected Agent', None, None)


class TestCLIMainInterface:
    """Test main CLI interface functionality"""

    def test_cli_help(self):
        """Test CLI help output"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert 'Synapse SDK' in result.output
        assert 'Interactive CLI' in result.output

    def test_config_command_help(self):
        """Test config command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', '--help'])

        assert result.exit_code == 0
        assert 'Configure Synapse settings' in result.output

    def test_devtools_command_help(self):
        """Test devtools command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['devtools', '--help'])

        assert result.exit_code == 0
        assert 'devtools' in result.output.lower()

    @patch('synapse_sdk.cli.inquirer.prompt')
    @patch('synapse_sdk.cli.clear_screen')
    def test_main_cli_exit(self, mock_clear, mock_prompt):
        """Test main CLI exit functionality"""
        # Mock user selecting exit
        mock_prompt.return_value = {'choice': 'exit'}

        runner = CliRunner()

        with patch('synapse_sdk.cli.display_connection_status'):
            result = runner.invoke(cli, input='\n')

            # Should exit cleanly
            assert result.exit_code == 0

    @patch('synapse_sdk.cli.inquirer.prompt')
    @patch('synapse_sdk.cli.clear_screen')
    @patch('synapse_sdk.cli.display_connection_status')
    def test_main_cli_config_selection(self, mock_status, mock_clear, mock_prompt):
        """Test selecting configuration from main menu"""
        # Mock user selecting config then exiting
        mock_prompt.side_effect = [
            {'choice': 'config'},  # Select config
            {'choice': 'exit'},  # Exit from config menu
        ]

        runner = CliRunner()

        with patch('synapse_sdk.cli.run_config') as mock_run_config:
            runner.invoke(cli, input='\n')

            mock_run_config.assert_called_once()


class TestCLIConfigPersistence:
    """Test configuration persistence and file operations"""

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_config_file_creation(self, temp_config_file):
        """Test configuration file creation and loading"""
        with patch('synapse_sdk.devtools.config.DEVTOOLS_CONFIG_FILE', temp_config_file):
            # Set some configuration
            set_agent_config('test-agent', 'Test Agent')

            # Verify it was saved
            config = get_agent_config()
            assert config['id'] == 'test-agent'
            assert config['name'] == 'Test Agent'

            # Verify file contents
            with open(temp_config_file, 'r') as f:
                file_config = json.load(f)
                assert file_config['agent']['id'] == 'test-agent'

    def test_config_file_error_handling(self):
        """Test configuration file error handling"""
        # Test with non-existent directory
        fake_path = '/nonexistent/path/config.json'

        with patch('synapse_sdk.devtools.config.DEVTOOLS_CONFIG_FILE', fake_path):
            # Should handle gracefully and return empty config
            config = get_agent_config()
            assert config == {}


class TestCLIErrorHandling:
    """Test error handling in CLI operations"""

    @patch('synapse_sdk.cli.config.get_backend_config')
    def test_network_error_handling(self, mock_get_backend):
        """Test handling of network errors"""
        mock_get_backend.return_value = {'host': 'https://unreachable.example.com', 'token': 'test-token'}

        with requests_mock.Mocker() as m:
            m.get('https://unreachable.example.com/agents/', exc=requests.exceptions.ConnectionError)

            agents, error = fetch_agents_from_backend()

            assert agents is None
            assert 'Connection failed' in error

    @patch('synapse_sdk.cli.config.inquirer.prompt')
    def test_keyboard_interrupt_handling(self, mock_prompt):
        """Test handling of keyboard interrupts"""
        # Simulate KeyboardInterrupt
        mock_prompt.side_effect = KeyboardInterrupt()

        with patch('synapse_sdk.cli.config.clear_screen'):
            with patch('click.echo'):
                # Should handle gracefully without crashing
                try:
                    interactive_config()
                except KeyboardInterrupt:
                    pytest.fail('KeyboardInterrupt not handled properly')


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
