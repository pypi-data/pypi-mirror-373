"""Deployment tab UI component."""

import os

import streamlit as st

from synapse_sdk.devtools.config import get_backend_config

from ..services.plugin_service import PluginService
from ..utils.ui_components import (
    render_action_button,
    render_divider,
    render_info_card,
    render_key_value_pair,
)


class DeploymentTab:
    """UI component for the Deployment tab."""

    def __init__(self, plugin_service: PluginService):
        self.plugin_service = plugin_service

    def render(self):
        """Render the Deployment tab."""
        backend_config = get_backend_config()
        if not backend_config:
            st.error('Backend not configured')
            return

        # Display current configuration
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Backend URL', value=backend_config['host'], disabled=True)
        with col2:
            st.text_input('Access Token', value='••••••••', disabled=True, type='password')

        # Debug options
        debug_mode = st.checkbox('Enable Debug Mode', value=True)
        debug_modules = st.text_input('Debug Modules (comma-separated)', placeholder='module1,module2')

        # Publish button
        if render_action_button(
            'Publish Plugin', key='publish_plugin', icon='🚀', type='primary', use_container_width=True
        ):
            with st.spinner('Publishing plugin...'):
                # Set debug modules env var if provided
                if debug_modules:
                    os.environ['SYNAPSE_DEBUG_MODULES'] = debug_modules

                result = self.plugin_service.publish_plugin(backend_config['host'], backend_config['token'], debug_mode)

            if result['success']:
                render_info_card('Published Successfully!', result['message'], type='success', icon='✅')

                render_divider()

                col1, col2, col3 = st.columns(3)
                with col1:
                    render_key_value_pair('Plugin Code', result['plugin_code'], monospace_value=True, inline=False)
                with col2:
                    render_key_value_pair('Version', result['version'], inline=False)
                with col3:
                    render_key_value_pair('Name', result['name'], inline=False)
            else:
                render_info_card('Publication Failed', result['error'], type='error', icon='❌')
