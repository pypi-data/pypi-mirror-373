"""Status bar component for displaying connection and system information."""

from typing import Dict, Optional

import streamlit as st

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.devtools.config import get_backend_config


class StatusBar:
    """Status bar UI component."""

    def __init__(
        self,
        *,
        backend_client: Optional[BackendClient] = None,
        agent_id: Optional[int] = None,
        agent_info: Optional[Dict] = None,
    ):
        self.backend_client = backend_client
        self.agent_id = agent_id
        self.agent_info = agent_info or {}

    def render(self):
        """Render the status bar."""
        backend_config = get_backend_config()

        # Use a single horizontal layout
        if backend_config and self.backend_client:
            host = backend_config.get('host', 'Unknown')
            # Extract just the domain/host part
            if '://' in host:
                host_display = host.split('://')[1].split('/')[0]
            else:
                host_display = host.split('/')[0]

            # Build agent display HTML
            agent_html = ''
            if self.agent_info:
                agent_name = self.agent_info.get('name', f'Agent-{self.agent_id}')
                agent_url = self.agent_info.get('url', 'unknown')
                agent_html = (
                    '<div style="display: flex; align-items: center; gap: 8px;">'
                    '<span style="color: #495057; font-weight: 500;">Agent:</span>'
                    f'<span style="color: #212529; font-family: monospace;">{agent_name} @ {agent_url}</span>'
                    '</div>'
                )
            elif self.agent_id:
                agent_html = (
                    '<div style="display: flex; align-items: center; gap: 8px;">'
                    '<span style="color: #495057; font-weight: 500;">Agent:</span>'
                    f'<span style="color: #212529; font-family: monospace;">#{self.agent_id}</span>'
                    '</div>'
                )

            # Create compact horizontal status bar
            status_html = (
                '<div style="'
                'background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);'
                'border-bottom: 1px solid #dee2e6;'
                'padding: 8px 16px;'
                'margin: -1rem -3rem 1rem -3rem;'
                'display: flex;'
                'align-items: center;'
                'gap: 24px;'
                'font-size: 13px;'
                '">'
                '<div style="display: flex; align-items: center; gap: 8px;">'
                '<span style="'
                'width: 8px;'
                'height: 8px;'
                'background-color: #28a745;'
                'border-radius: 50%;'
                'display: inline-block;'
                '"></span>'
                '<span style="color: #495057; font-weight: 500;">Backend:</span>'
                f'<span style="color: #212529; font-family: monospace;">{host_display}</span>'
                '</div>'
                f'{agent_html}'
                '<div style="margin-left: auto; color: #6c757d; font-size: 11px;">'
                'Synapse DevTools'
                '</div>'
                '</div>'
            )

            st.markdown(status_html, unsafe_allow_html=True)

        else:
            # Not connected status - compact horizontal bar
            disconnected_html = (
                '<div style="'
                'background: linear-gradient(90deg, #fff5f5 0%, #ffe0e0 100%);'
                'border-bottom: 1px solid #f5c6cb;'
                'padding: 8px 16px;'
                'margin: -1rem -3rem 1rem -3rem;'
                'display: flex;'
                'align-items: center;'
                'gap: 24px;'
                'font-size: 13px;'
                '">'
                '<div style="display: flex; align-items: center; gap: 8px;">'
                '<span style="'
                'width: 8px;'
                'height: 8px;'
                'background-color: #dc3545;'
                'border-radius: 50%;'
                'display: inline-block;'
                '"></span>'
                '<span style="color: #721c24; font-weight: 500;">Backend:</span>'
                '<span style="color: #721c24;">Not configured</span>'
                '</div>'
                '<div style="margin-left: auto; color: #721c24; font-size: 11px;">'
                'Synapse DevTools'
                '</div>'
                '</div>'
            )
            st.markdown(disconnected_html, unsafe_allow_html=True)
