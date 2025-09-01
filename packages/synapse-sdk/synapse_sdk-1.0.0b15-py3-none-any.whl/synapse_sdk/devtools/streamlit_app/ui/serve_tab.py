"""Serve Applications tab UI component."""

import time
import traceback
from datetime import datetime
from typing import Dict, Optional

import streamlit as st

from synapse_sdk.clients.exceptions import ClientError

from ..services.serve_service import ServeService
from ..utils.json_viewer import render_json_as_table, render_json_compact
from ..utils.styles import get_status_badge_html
from ..utils.ui_components import render_action_button, render_empty_state, render_section_header


class ServeTab:
    """UI component for the Serve Applications tab."""

    def __init__(self, serve_service: ServeService, agent_id: Optional[int] = None, agent_info: Optional[Dict] = None):
        self.serve_service = serve_service
        self.agent_id = agent_id
        self.agent_info = agent_info or {}

    def render(self):
        """Render the Serve Applications tab."""
        if not self.serve_service.backend_client:
            st.error('Backend client not configured. Please check your backend configuration.')
            return

        # Check if we should show app details
        if 'selected_app' in st.session_state:
            self.render_app_details(st.session_state['selected_app'])
            return

        # Auto-refresh controls
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if render_action_button('Refresh', key='refresh_apps', icon='🔄', type='secondary'):
                st.rerun()

        with col2:
            auto_refresh = st.checkbox('Auto-refresh', value=False, key='serve_auto_refresh')

        with col3:
            if auto_refresh:
                refresh_interval = st.selectbox(
                    'Refresh interval',
                    options=[2, 5, 10, 30],
                    index=1,  # Default to 5 seconds
                    format_func=lambda x: f'{x}s',
                    key='serve_refresh_interval',
                )
                st.caption(f'Auto-refreshing every {refresh_interval} seconds')

        # Create a container for applications display to ensure proper rendering
        apps_container = st.container()

        with apps_container:
            try:
                applications = self.serve_service.list_serve_applications(self.agent_id, self.agent_info)

                if not applications:
                    render_empty_state(
                        'No serve applications found',
                        icon='🚀',
                        action_label='Refresh',
                        action_callback=lambda: st.rerun(),
                    )
                    if auto_refresh:
                        refresh_interval = st.session_state.get('serve_refresh_interval', 5)
                        placeholder = st.empty()
                        with placeholder.container():
                            st.info(f'Refreshing in {refresh_interval} seconds...')
                        time.sleep(refresh_interval)
                        placeholder.empty()
                        st.rerun()
                    return

                # Display applications in table format
                st.success(f'Showing {len(applications)} applications')
                self._render_applications_table(applications)

            except ClientError as e:
                st.error(f'Failed to fetch serve applications: {e.reason}')
            except Exception as e:
                st.error(f'Unexpected error: {e}')
                st.code(traceback.format_exc())

        # Auto-refresh implementation
        if auto_refresh:
            refresh_interval = st.session_state.get('serve_refresh_interval', 5)
            placeholder = st.empty()
            with placeholder.container():
                st.info(f'Refreshing in {refresh_interval} seconds...')
            time.sleep(refresh_interval)
            placeholder.empty()
            st.rerun()

    def _render_applications_table(self, applications):
        """Render the applications table."""
        # Table header
        header_cols = st.columns([2, 1.5, 1, 1, 1.2, 1.2, 0.6])
        headers = ['Application', 'Plugin', 'Status', 'Active', 'Job', 'Created', '']

        for i, header in enumerate(headers):
            with header_cols[i]:
                st.markdown(
                    f"<div style='color:#666; font-size:13px; font-weight:600; padding: 4px 0;'>{header}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #e0e0e0'>", unsafe_allow_html=True)

        # Table rows
        for app in applications:
            cols = st.columns([2, 1.5, 1, 1, 1.2, 1.2, 0.6])

            # Application Name (with ID as fallback)
            with cols[0]:
                app_id = app.get('id', 'N/A')
                # Try to get application name from various possible fields
                app_name = (
                    app.get('name')
                    or app.get('display_name')
                    or app.get('deployment_name')
                    or (app.get('data', {}).get('name') if isinstance(app.get('data'), dict) else None)
                    or f'Deployment {str(app_id)[:8]}...'
                )

                # Display name with ID as tooltip/subtitle
                st.markdown(
                    f"<div style='font-size:13px; padding: 6px 0;'>"
                    f"<div style='font-weight: 500;'>{app_name}</div>"
                    f"<div style='font-size: 11px; color: #666; font-family: monospace;'>{str(app_id)[:8]}...</div>"
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Plugin
            with cols[1]:
                plugin_release = app.get('plugin_release', 'N/A')
                # Try to extract plugin name or code from release info
                plugin_name = app.get('plugin_name') or app.get('plugin_code')
                if not plugin_name and isinstance(app.get('data'), dict):
                    plugin_name = app.get('data', {}).get('plugin_name') or app.get('data', {}).get('plugin_code')

                if plugin_name:
                    st.markdown(
                        f"<div style='font-size:13px; padding: 6px 0;'>"
                        f'<div>{plugin_name}</div>'
                        f"<div style='font-size: 11px; color: #666;'>v{plugin_release}</div>"
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    display_pr = (
                        str(plugin_release)[:12] + '...' if len(str(plugin_release)) > 12 else str(plugin_release)
                    )
                    st.markdown(
                        f"<div style='font-size:13px; padding: 6px 0;'>{display_pr}</div>", unsafe_allow_html=True
                    )

            # Status
            with cols[2]:
                status = app.get('status', 'Unknown')
                st.markdown(get_status_badge_html(status), unsafe_allow_html=True)

            # Is Active
            with cols[3]:
                is_active = app.get('is_active', False)
                active_text = 'Yes' if is_active else 'No'
                active_color = '#28a745' if is_active else '#6c757d'
                st.markdown(
                    f"<div style='font-size:13px; padding: 6px 0; color: {active_color};'>{active_text}</div>",
                    unsafe_allow_html=True,
                )

            # Job
            with cols[4]:
                job_id = app.get('job', 'N/A')
                display_job = str(job_id)[:10] + '...' if len(str(job_id)) > 10 else str(job_id)
                st.markdown(f"<div style='font-size:13px; padding: 6px 0;'>{display_job}</div>", unsafe_allow_html=True)

            # Created
            with cols[5]:
                created = app.get('created')
                if created:
                    try:
                        created_dt = datetime.fromisoformat(created.replace('+09:00', '+09:00'))
                        time_str = created_dt.strftime('%m/%d %H:%M')
                        st.markdown(
                            f"<div style='font-size:13px; padding: 6px 0;'>{time_str}</div>",
                            unsafe_allow_html=True,
                        )
                    except Exception:
                        st.markdown(
                            f"<div style='font-size:13px; padding: 6px 0;'>{str(created)[:16]}</div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown("<div style='font-size:13px; padding: 6px 0;'>-</div>", unsafe_allow_html=True)

            # Actions
            with cols[6]:
                details_key = f'app_details_{app_id}_{hash(str(app))}'

                def select_app(app_data):
                    st.session_state['selected_app'] = app_data

                if render_action_button(
                    '', key=details_key, icon='→', type='minimal', on_click=select_app, args=(app,), help='View details'
                ):
                    pass

            st.markdown(
                "<hr style='margin: 6px 0; border: none; border-top: 1px solid #f0f0f0'>",
                unsafe_allow_html=True,
            )

    def render_app_details(self, app):
        """Render the serve deployment details page."""
        app_id = app.get('id', 'Unknown')

        # Try to get application name
        app_name = (
            app.get('name')
            or app.get('display_name')
            or app.get('deployment_name')
            or (app.get('data', {}).get('name') if isinstance(app.get('data'), dict) else None)
            or f'Deployment {str(app_id)[:8]}...'
        )

        # Header with back button
        col1, col2 = st.columns([1, 4])
        with col1:
            if render_action_button('Back', key='back_to_apps', icon='←', type='secondary'):
                del st.session_state['selected_app']
                st.rerun()
        with col2:
            render_section_header(app_name, f'ID: {app_id}')

        # Status badge with spacing
        status = app.get('status', 'Unknown')
        st.markdown(f"<div style='margin: 12px 0;'>{get_status_badge_html(status)}</div>", unsafe_allow_html=True)

        # Deployment Information section
        render_section_header('Deployment Information')
        col1, col2 = st.columns(2)

        with col1:
            # Show name if different from the generated one
            if app.get('name') or app.get('display_name') or app.get('deployment_name'):
                display_name = app.get('name') or app.get('display_name') or app.get('deployment_name')
                st.markdown(
                    f"<div style='margin-bottom: 12px;'><strong>Name:</strong> {display_name}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>ID:</strong> <code>{app.get('id', 'N/A')}</code></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Status:</strong> {status}</div>", unsafe_allow_html=True
            )
            status_display = app.get('status_display', 'N/A')
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Status Display:</strong> {status_display}</div>",
                unsafe_allow_html=True,
            )
            is_active = 'Yes' if app.get('is_active') else 'No'
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Active:</strong> {is_active}</div>",
                unsafe_allow_html=True,
            )

        with col2:
            # Display plugin info with enriched data
            plugin_release = app.get('plugin_release', 'N/A')
            plugin_name = app.get('plugin_name') or app.get('plugin_code')
            plugin_version = app.get('plugin_version')

            if plugin_name and plugin_version:
                plugin_display = f'{plugin_name} (v{plugin_version})'
            elif plugin_name:
                plugin_display = plugin_name
            else:
                plugin_display = f'Plugin #{plugin_release}'

            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Plugin:</strong> {plugin_display}</div>",
                unsafe_allow_html=True,
            )

            # Display agent info with enriched data
            agent_id = app.get('agent', 'N/A')
            agent_name = app.get('agent_name')
            agent_url = app.get('agent_url')

            if agent_name and agent_url:
                agent_display = f'{agent_name} @ {agent_url}'
            elif agent_name:
                agent_display = agent_name
            elif agent_url:
                agent_display = agent_url
            else:
                agent_display = f'Agent #{agent_id}'

            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Agent:</strong> {agent_display}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Job:</strong> {app.get('job', 'N/A')}</div>",
                unsafe_allow_html=True,
            )

            created = app.get('created')
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace('+09:00', '+09:00'))
                    formatted_time = created_dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.markdown(
                        f"<div style='margin-bottom: 12px;'><strong>Created:</strong> {formatted_time}</div>",
                        unsafe_allow_html=True,
                    )
                except Exception:
                    st.markdown(
                        f"<div style='margin-bottom: 12px;'><strong>Created:</strong> {created}</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    "<div style='margin-bottom: 12px;'><strong>Created:</strong> N/A</div>", unsafe_allow_html=True
                )

        # Data section
        data = app.get('data', {})
        if data:
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            # Use table for simple data, compact for complex
            if isinstance(data, dict) and all(not isinstance(v, (dict, list)) for v in data.values()):
                render_json_as_table(data, 'Deployment Data')
            else:
                render_json_compact(data, 'Deployment Data')
