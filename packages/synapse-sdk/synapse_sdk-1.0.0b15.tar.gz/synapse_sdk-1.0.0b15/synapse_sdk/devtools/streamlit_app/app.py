"""Main Streamlit DevTools Application."""

from pathlib import Path
from typing import Dict, Optional

import streamlit as st

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.devtools.config import get_backend_config, load_devtools_config

from .services import JobService, PluginService, ServeService
from .ui import ConfigTab, DeploymentTab, HttpTab, JobsTab, ServeTab
from .ui.status_bar import StatusBar
from .utils import CUSTOM_CSS


class DevToolsApp:
    """Main DevTools application class."""

    def __init__(self):
        self.plugin_directory = Path.cwd()

        # Initialize backend client and agent info
        self.backend_client = self._init_backend_client()
        self.agent_id = self._get_agent_id()
        self.agent_info = self._get_agent_info()

        # Initialize services
        self.plugin_service = PluginService(self.plugin_directory, self.backend_client)
        self.job_service = JobService(self.backend_client)
        self.serve_service = ServeService(self.backend_client)

        # Initialize UI components
        self.status_bar = StatusBar(
            backend_client=self.backend_client, agent_id=self.agent_id, agent_info=self.agent_info
        )
        self.config_tab = ConfigTab(self.plugin_service)
        self.http_tab = HttpTab(self.plugin_service, self.agent_id)
        self.deployment_tab = DeploymentTab(self.plugin_service)
        self.jobs_tab = JobsTab(self.job_service, self.agent_id, self.agent_info)
        self.serve_tab = ServeTab(self.serve_service, self.agent_id, self.agent_info)

    def _init_backend_client(self) -> Optional[BackendClient]:
        """Initialize backend client from configuration."""
        config = get_backend_config()
        if config:
            return BackendClient(config['host'], access_token=config['token'])
        return None

    def _get_agent_id(self) -> Optional[int]:
        """Get agent ID from devtools configuration."""
        devtools_config = load_devtools_config()
        agent_config = devtools_config.get('agent', {})
        if agent_config and 'id' in agent_config:
            return agent_config['id']
        return None

    def _get_agent_info(self) -> Optional[Dict]:
        """Get complete agent information from configuration or backend."""
        devtools_config = load_devtools_config()
        agent_config = devtools_config.get('agent', {})

        # Return the full agent config which should include name, ip, etc.
        if agent_config:
            return agent_config

        # If we have an agent_id but no full config, try to fetch from backend
        if self.agent_id and self.backend_client:
            try:
                # Try to get agent details from backend
                # This would require an API endpoint - for now return basic info
                return {
                    'id': self.agent_id,
                    'name': agent_config.get('name', f'Agent-{self.agent_id}'),
                    'url': agent_config.get('url', agent_config.get('ip', 'localhost')),
                }
            except Exception:
                pass

        return None

    def run(self):
        """Main application entry point."""
        # Page configuration
        st.set_page_config(
            page_title='Synapse DevTools',
            page_icon=None,
            layout='wide',
            initial_sidebar_state='collapsed',
        )

        # Apply custom CSS
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

        # Display status bar
        self.status_bar.render()

        # Initialize session state
        if 'config' not in st.session_state:
            st.session_state['config'] = self.plugin_service.load_config()

        # Create tabs
        tabs = st.tabs(['Configuration', 'HTTP Request', 'Deployment', 'Jobs', 'Serve Apps'])

        with tabs[0]:
            self.config_tab.render()

        with tabs[1]:
            self.http_tab.render()

        with tabs[2]:
            self.deployment_tab.render()

        with tabs[3]:
            self.jobs_tab.render()

        with tabs[4]:
            self.serve_tab.render()


def main():
    """Main entry point for Streamlit app."""
    app = DevToolsApp()
    app.run()


if __name__ == '__main__':
    main()
