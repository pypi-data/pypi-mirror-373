"""Jobs tab UI component."""

import time
import traceback
from typing import Dict, Optional

import streamlit as st

from synapse_sdk.clients.exceptions import ClientError

from ..services.job_service import JobService
from ..utils.json_viewer import render_json_as_table, render_json_compact, render_metrics_grid
from ..utils.log_formatter import format_log_line
from ..utils.styles import get_status_badge_html
from ..utils.ui_components import (
    render_action_button,
    render_empty_state,
    render_section_header,
)


class JobsTab:
    """UI component for the Jobs tab."""

    def __init__(self, job_service: JobService, agent_id: Optional[int] = None, agent_info: Optional[Dict] = None):
        self.job_service = job_service
        self.agent_id = agent_id
        self.agent_info = agent_info or {}

    def render(self):
        """Render the Jobs tab."""
        if not self.job_service.backend_client:
            st.error('Backend client not configured. Please check your backend configuration.')
            return

        # Check if we should show job details
        if 'selected_job' in st.session_state:
            self.render_job_details(st.session_state['selected_job'])
            return

        # Controls row
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if render_action_button('Refresh', key='refresh_jobs', icon='🔄', type='secondary'):
                st.rerun()

        with col2:
            auto_refresh = st.checkbox('Auto-refresh', value=False, key='jobs_auto_refresh')

        with col3:
            if auto_refresh:
                refresh_interval = st.selectbox(
                    'Refresh interval',
                    options=[2, 5, 10, 30],
                    index=1,  # Default to 5 seconds
                    format_func=lambda x: f'{x}s',
                    key='jobs_refresh_interval',
                )

        # Get page size from session state or use default
        page_size = st.session_state.get('page_size_value', 20)

        # Initialize pagination state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0

        try:
            valid_jobs = self.job_service.list_jobs(self.agent_id, self.agent_info)

            # Pagination logic
            total_jobs = len(valid_jobs)
            total_pages = (total_jobs + page_size - 1) // page_size if total_jobs > 0 else 1

            # Ensure current page is valid
            if st.session_state.current_page >= total_pages:
                st.session_state.current_page = max(0, total_pages - 1)

            start_idx = st.session_state.current_page * page_size
            end_idx = min(start_idx + page_size, total_jobs)
            page_jobs = valid_jobs[start_idx:end_idx]

            # Display job count info
            if total_jobs > 0:
                st.success(f'Showing {start_idx + 1}-{end_idx} of {total_jobs} jobs')
            else:
                render_empty_state(
                    'No jobs found', icon='📋', action_label='Refresh', action_callback=lambda: st.rerun()
                )
                return

            # Display jobs in table format
            if page_jobs:
                self._render_jobs_table(page_jobs)

            # Pagination controls at the bottom
            if total_pages > 1 or total_jobs > 10:
                self._render_pagination_controls(total_pages, page_size)

        except ClientError as e:
            st.error(f'Failed to fetch jobs: {e.reason}')
        except Exception as e:
            st.error(f'Unexpected error: {e}')
            st.code(traceback.format_exc())

        # Auto-refresh implementation
        if auto_refresh:
            refresh_interval = st.session_state.get('jobs_refresh_interval', 5)
            placeholder = st.empty()
            with placeholder.container():
                st.info(f'Refreshing in {refresh_interval} seconds...')
            time.sleep(refresh_interval)
            placeholder.empty()
            st.rerun()

    def _render_jobs_table(self, jobs):
        """Render the jobs table."""
        # Table header with balanced spacing
        header_cols = st.columns([2, 1.2, 1.5, 1, 0.8, 1, 0.6, 1.2])
        headers = ['Job', 'Plugin', 'User', 'Status', 'Progress', 'Duration', '', 'Created']

        for i, header in enumerate(headers):
            with header_cols[i]:
                st.markdown(
                    f"<div style='color:#666; font-size:13px; font-weight:600; padding: 4px 0;'>{header}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #e0e0e0'>", unsafe_allow_html=True)

        # Table rows with balanced spacing
        for job in jobs:
            cols = st.columns([2, 1.2, 1.5, 1, 0.8, 1, 0.6, 1.2])

            # Job Name/ID
            with cols[0]:
                job_id = job.get('id', 'N/A')
                # Try to get job name from various fields
                job_name = (
                    job.get('name')
                    or job.get('display_name')
                    or job.get('action')
                    or (job.get('params', {}).get('name') if isinstance(job.get('params'), dict) else None)
                    or f'Job {str(job_id)[:8]}...'
                )

                # Display name with ID as subtitle
                st.markdown(
                    f"<div style='font-size:13px; padding: 6px 0;'>"
                    f"<div style='font-weight: 500;'>{job_name}</div>"
                    f"<div style='font-size: 11px; color: #666; font-family: monospace;'>{str(job_id)[:8]}...</div>"
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Plugin Category
            with cols[1]:
                plugin_category = job.get('plugin_category', 'N/A')
                st.markdown(
                    f"<div style='font-size:13px; padding: 6px 0;'>{plugin_category}</div>",
                    unsafe_allow_html=True,
                )

            # User
            with cols[2]:
                user = job.get('user', {})
                user_name = user.get('name', user.get('email', 'N/A'))
                display_name = user_name[:12] + '...' if len(str(user_name)) > 12 else str(user_name)
                st.markdown(
                    f"<div style='font-size:13px; padding: 6px 0;'>{display_name}</div>", unsafe_allow_html=True
                )

            # Status with badge
            with cols[3]:
                status = job.get('status', 'Unknown')
                st.markdown(get_status_badge_html(status), unsafe_allow_html=True)

            # Progress
            with cols[4]:
                progress = job.get('progress', {})
                overall = progress.get('overall', 0)
                if overall is not None:
                    st.markdown(
                        f"<div style='font-size:13px; padding: 6px 0;'>{overall}%</div>", unsafe_allow_html=True
                    )
                else:
                    st.markdown("<div style='font-size:13px; padding: 6px 0;'>-</div>", unsafe_allow_html=True)

            # Duration
            with cols[5]:
                duration_text = self.job_service.format_duration(job.get('created'), job.get('completed'))
                st.markdown(
                    f"<div style='font-size:13px; padding: 6px 0;'>{duration_text}</div>",
                    unsafe_allow_html=True,
                )

            # Actions
            with cols[6]:
                logs_key = f'logs_{job.get("id")}_{hash(str(job))}'

                def select_job(job):
                    st.session_state['selected_job'] = job

                # Compact view button
                if render_action_button(
                    '', key=logs_key, icon='→', type='minimal', on_click=select_job, args=(job,), help='View details'
                ):
                    pass

            # Start Time
            with cols[7]:
                time_str = self.job_service.format_timestamp(job.get('created'))
                st.markdown(
                    f"<div style='font-size:13px; padding: 6px 0;'>{time_str}</div>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<hr style='margin: 6px 0; border: none; border-top: 1px solid #f0f0f0'>",
                unsafe_allow_html=True,
            )

    def _render_pagination_controls(self, total_pages, page_size):
        """Render pagination controls."""
        st.markdown('---')
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1.5, 1, 1, 1.5])

        with col1:
            if render_action_button(
                'First', key='bottom_first', type='minimal', disabled=st.session_state.current_page == 0
            ):
                st.session_state.current_page = 0
                st.rerun()

        with col2:
            if render_action_button(
                'Prev', key='bottom_prev', type='minimal', disabled=st.session_state.current_page == 0
            ):
                st.session_state.current_page -= 1
                st.rerun()

        with col3:
            st.markdown(
                f'<div style="text-align: center; padding: 8px; color: #495057; font-size: 14px;">'
                f'Page {st.session_state.current_page + 1} of {total_pages}</div>',
                unsafe_allow_html=True,
            )

        with col4:
            if render_action_button(
                'Next', key='bottom_next', type='minimal', disabled=st.session_state.current_page >= total_pages - 1
            ):
                st.session_state.current_page += 1
                st.rerun()

        with col5:
            if render_action_button(
                'Last', key='bottom_last', type='minimal', disabled=st.session_state.current_page >= total_pages - 1
            ):
                st.session_state.current_page = total_pages - 1
                st.rerun()

        with col6:
            new_page_size = st.selectbox(
                'Items per page',
                options=[10, 20, 50, 100],
                index=[10, 20, 50, 100].index(page_size) if page_size in [10, 20, 50, 100] else 1,
                key='page_size_selector',
            )
            if new_page_size != page_size:
                st.session_state.page_size_value = new_page_size
                st.session_state.current_page = 0  # Reset to first page
                st.rerun()

    def render_job_details(self, job):
        """Render the job details page."""
        job_id = job.get('id', 'Unknown')

        # Check if we're viewing a different job and clear cached logs
        if 'last_viewed_job_id' not in st.session_state or st.session_state['last_viewed_job_id'] != job_id:
            # Clear cached logs and streaming state when switching to a different job
            st.session_state.pop('job_logs_content', None)
            st.session_state.pop('stream_counter', None)
            st.session_state['last_viewed_job_id'] = job_id

        # Try to get job name
        job_name = (
            job.get('name')
            or job.get('display_name')
            or job.get('action')
            or (job.get('params', {}).get('name') if isinstance(job.get('params'), dict) else None)
            or f'Job {str(job_id)[:8]}...'
        )

        # Header with back button
        col1, col2 = st.columns([1, 4])
        with col1:
            if render_action_button('Back', key='back_to_jobs', icon='←', type='secondary'):
                del st.session_state['selected_job']
                st.rerun()
        with col2:
            render_section_header(job_name, f'ID: {job_id}')

        # Status badge with spacing
        status = job.get('status', 'Unknown')
        st.markdown(f"<div style='margin: 12px 0;'>{get_status_badge_html(status)}</div>", unsafe_allow_html=True)

        # Job Logs section (moved to top)
        render_section_header('Job Logs')

        # Add controls for logs
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.checkbox(
                'Auto-scroll', value=True, key='logs_auto_scroll', disabled=True, help='Always scrolls to bottom'
            )
        with col2:
            stream_logs = st.checkbox(
                'Auto-refresh', value=False, key='logs_stream', help='Refresh logs every 3 seconds'
            )
        with col3:
            if st.button('Clear cache', key='clear_logs'):
                st.session_state.pop('job_logs_content', None)

        # Create log display area with CSS
        log_css = """
        <style>
        .log-container {
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            padding: 12px;
            border-radius: 4px;
            height: 500px;
            overflow-y: auto;
            overflow-x: auto;
            white-space: pre;
        }
        .log-line {
            display: flex;
            line-height: 1.4;
            padding: 2px 0;
        }
        .log-line:hover {
            background-color: #2d2d2d;
        }
        .log-line-number {
            color: #858585;
            margin-right: 12px;
            min-width: 40px;
            text-align: right;
            user-select: none;
        }
        .log-line-content {
            flex: 1;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .log-error {
            color: #f48771;
        }
        .log-warning {
            color: #dcdcaa;
        }
        .log-info {
            color: #9cdcfe;
        }
        .log-debug {
            color: #858585;
        }
        .log-timestamp {
            color: #569cd6;
        }
        </style>
        """
        st.markdown(log_css, unsafe_allow_html=True)

        # Display logs container
        log_placeholder = st.empty()

        # Control buttons
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button('🔄 Refresh', key='refresh_logs'):
                st.session_state.pop('job_logs_content', None)
                st.rerun()

        # Auto-refresh using JavaScript
        if stream_logs:
            with col2:
                st.info('🔄 Auto-refresh enabled (every 3 seconds)')
            # Add JavaScript to refresh the page every 3 seconds
            st.markdown(
                """
                <script>
                setTimeout(function() {
                    window.location.reload();
                }, 3000);
                </script>
                """,
                unsafe_allow_html=True,
            )
            # Clear cache for fresh logs on each refresh
            st.session_state.pop('job_logs_content', None)

        # Display logs
        with log_placeholder.container():
            try:
                # Fetch logs if not cached
                if 'job_logs_content' not in st.session_state:
                    with st.spinner('Fetching logs...'):
                        logs = []
                        for log_line in self.job_service.get_job_logs(job_id):
                            logs.append(log_line)
                        st.session_state['job_logs_content'] = logs

                # Get logs from cache
                logs = st.session_state.get('job_logs_content', [])

                # Display logs
                if logs:
                    formatted_logs = []
                    for i, line in enumerate(logs, 1):
                        formatted_logs.append(format_log_line(line, i))

                    logs_html = f'<div class="log-container" id="logContainer">{"".join(formatted_logs)}</div>'
                    st.markdown(logs_html, unsafe_allow_html=True)

                    # Always scroll to bottom when logs are displayed
                    st.markdown(
                        """
                        <script>
                        setTimeout(function() {
                            var logContainer = document.getElementById('logContainer');
                            if (logContainer) {
                                logContainer.scrollTop = logContainer.scrollHeight;
                            }
                        }, 100);
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.info('No logs available for this job.')

            except Exception as e:
                st.error(f'Failed to fetch logs: {e}')

        # Job Information section with better spacing
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        render_section_header('Job Information')
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Job ID:</strong> <code>{job.get('id', 'N/A')}</code></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Status:</strong> {job.get('status', 'N/A')}</div>",
                unsafe_allow_html=True,
            )
            plugin_cat = job.get('plugin_category', 'N/A')
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Plugin Category:</strong> {plugin_cat}</div>",
                unsafe_allow_html=True,
            )
            # Display agent info with enriched data
            agent_id = job.get('agent', 'N/A')
            agent_name = job.get('agent_name')
            agent_url = job.get('agent_url')

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
            # Display plugin info with enriched data
            plugin_rel = job.get('plugin_release', 'N/A')
            plugin_name = job.get('plugin_name') or job.get('plugin_code')
            plugin_version = job.get('plugin_version')

            if not plugin_name:
                plugin_name = job.get('plugin_category')

            if plugin_name and plugin_version:
                plugin_display = f'{plugin_name} (v{plugin_version})'
            elif plugin_name:
                plugin_display = plugin_name
            else:
                plugin_display = f'Plugin #{plugin_rel}'

            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Plugin:</strong> {plugin_display}</div>",
                unsafe_allow_html=True,
            )

        with col2:
            user = job.get('user', {})
            user_name = user.get('name', user.get('email', 'N/A'))
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>User:</strong> {user_name}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Created:</strong> {job.get('created', 'N/A')}</div>",
                unsafe_allow_html=True,
            )
            completed = job.get('completed', 'N/A') if job.get('completed') else 'In Progress'
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Completed:</strong> {completed}</div>",
                unsafe_allow_html=True,
            )
            progress = job.get('progress', {})
            st.markdown(
                f"<div style='margin-bottom: 12px;'><strong>Progress:</strong> {progress.get('overall', 0)}%</div>",
                unsafe_allow_html=True,
            )

            # Calculate duration
            duration_text = self.job_service.format_duration(job.get('created'), job.get('completed'))
            if duration_text not in ['-', '...']:
                st.markdown(
                    f"<div style='margin-bottom: 12px;'><strong>Duration:</strong> {duration_text}</div>",
                    unsafe_allow_html=True,
                )

        # Parameters section with spacing
        if job.get('params'):
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            params = job.get('params')
            # Use table view for simple params, compact view for complex
            if isinstance(params, dict) and all(not isinstance(v, (dict, list)) for v in params.values()):
                render_json_as_table(params, 'Parameters')
            else:
                render_json_compact(params, 'Parameters')

        # Result section with spacing
        if job.get('result'):
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            render_json_compact(job.get('result'), 'Result')

        # Metrics section with spacing
        metrics = job.get('metrics_by_categories')
        if metrics and metrics != {}:
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            # Use grid for simple metrics, compact view for nested
            if isinstance(metrics, dict):
                has_nested = any(isinstance(v, (dict, list)) for v in metrics.values())
                if has_nested:
                    render_json_compact(metrics, 'Metrics by Categories')
                else:
                    render_metrics_grid(metrics, 'Metrics')
            else:
                render_json_compact(metrics, 'Metrics')

        # Detail section with spacing
        detail = job.get('detail')
        if detail and detail != {}:
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            # Use table for simple details, compact for complex
            if isinstance(detail, dict) and all(not isinstance(v, (dict, list)) for v in detail.values()):
                render_json_as_table(detail, 'Additional Details')
            else:
                render_json_compact(detail, 'Additional Details')
