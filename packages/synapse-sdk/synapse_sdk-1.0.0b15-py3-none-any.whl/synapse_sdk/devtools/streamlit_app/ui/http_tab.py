"""HTTP Request tab UI component."""

import json
from typing import Optional

import streamlit as st
from streamlit_ace import st_ace

from synapse_sdk.devtools.config import get_backend_config

from ..services.plugin_service import PluginService
from ..utils.json_viewer import render_json_compact
from ..utils.ui_components import render_action_button, render_info_card, render_section_header


class HttpTab:
    """UI component for the HTTP Request tab."""

    def __init__(self, plugin_service: PluginService, agent_id: Optional[int] = None):
        self.plugin_service = plugin_service
        self.agent_id = agent_id

    def render(self):
        """Render the HTTP Request tab."""
        config = st.session_state.get('config', self.plugin_service.load_config())
        if not config:
            st.error('Please configure your plugin first')
            return

        # Get available actions
        actions = list(config.get('actions', {}).keys())
        if not actions:
            st.warning('No actions configured in your plugin')
            return

        # Backend configuration check
        backend_config = get_backend_config()
        if not backend_config:
            st.error('❌ Backend not configured')
            return

        # Action selection
        selected_action = st.selectbox('Select Action', actions)

        # Load parameters from test.http
        test_http_params = self.plugin_service.parse_test_http()
        default_params = test_http_params.get(selected_action, {})

        # Parameters editor
        render_section_header('Parameters', 'Parameters are automatically saved to test.http when request succeeds')
        render_info_card(
            'Editor Note',
            'Ctrl+Enter keyboard shortcut is not available in the editor. Use the Execute button below.',
            type='info',
            icon='ℹ️',
        )

        params_str = st_ace(
            value=json.dumps(default_params, indent=2),
            language='json',
            theme='monokai',
            key=f'params_{selected_action}',
            height=300,
            auto_update=False,
            font_size=14,
        )

        # Execute button
        col1, col2 = st.columns([2, 1])
        with col1:
            execute_btn = render_action_button(
                'Execute Request', key='execute_request', icon='▶', type='primary', use_container_width=True
            )
        with col2:
            debug_mode = st.checkbox('Debug mode', value=True)

        # Show endpoint reference
        with st.expander('Endpoint Reference'):
            plugin_code = config.get('code', 'plugin_code')
            st.code(
                f"""POST {backend_config['host']}/plugins/{plugin_code}/run/
Content-Type: application/json
Accept: application/json; indent=4
SYNAPSE-Access-Token: Token ••••••••

{{
    "agent": {self.agent_id or 2},
    "action": "{selected_action}",
    "params": {params_str},
    "debug": {str(debug_mode).lower()}
}}""",
                language='http',
            )

        # Execute request
        if execute_btn:
            try:
                params = json.loads(params_str)

                with st.spinner('Executing request...'):
                    result = self.plugin_service.execute_plugin_action(
                        selected_action, params, config.get('code'), self.agent_id, debug_mode
                    )

                # Display result
                if result['success']:
                    st.success(f'Success - Status: {result["status_code"]} - Time: {result["execution_time"]}ms')

                    # Auto-save params on successful execution
                    if self.plugin_service.update_test_http_params(selected_action, params):
                        st.info('Parameters saved to test.http')
                else:
                    status_code = result.get('status_code', 'Unknown')
                    exec_time = result.get('execution_time', 0)
                    st.error(f'Failed - Status: {status_code} - Time: {exec_time}ms')

                # Show response
                if 'response_data' in result:
                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                    render_json_compact(result['response_data'], 'Response')
                elif 'error' in result:
                    st.error(result['error'])

            except json.JSONDecodeError as e:
                st.error(f'Invalid JSON: {e}')
