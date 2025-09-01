"""Job service for managing job operations."""

from datetime import datetime
from typing import Dict, List, Optional

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.clients.exceptions import ClientError


class JobService:
    """Service for job-related operations."""

    def __init__(self, backend_client: Optional[BackendClient] = None):
        self.backend_client = backend_client

    def list_jobs(self, agent_id: Optional[int] = None, agent_info: Optional[Dict] = None) -> List[Dict]:
        """List jobs from the backend."""
        if not self.backend_client:
            return []

        try:
            params = {}
            if agent_id:
                params['agent'] = agent_id

            jobs_response = self.backend_client.list_jobs(params=params)

            # Handle paginated response - extract results
            if jobs_response is None:
                return []
            elif isinstance(jobs_response, dict) and 'results' in jobs_response:
                jobs = jobs_response['results']
            else:
                jobs = jobs_response if isinstance(jobs_response, list) else []

            # Remove None jobs and sort by created time (most recent first)
            valid_jobs = [job for job in jobs if job is not None]
            valid_jobs.sort(key=lambda job: job.get('created', ''), reverse=True)

            # Try to enrich jobs with plugin names
            enriched_jobs = []
            for job in valid_jobs:
                enriched_job = job.copy()

                # Try to get plugin info
                if 'plugin_release' in job:
                    try:
                        # Try to fetch plugin release details
                        plugin_release_response = self.backend_client.get(f'/plugin_releases/{job["plugin_release"]}/')
                        if plugin_release_response and isinstance(plugin_release_response, dict):
                            # Get version from plugin release
                            enriched_job['plugin_version'] = plugin_release_response.get('version')

                            # Try to get plugin details from the plugin ID
                            plugin_id = plugin_release_response.get('plugin')
                            if plugin_id:
                                try:
                                    plugin_response = self.backend_client.get(f'/plugins/{plugin_id}/')
                                    if plugin_response and isinstance(plugin_response, dict):
                                        enriched_job['plugin_name'] = plugin_response.get('name')
                                        enriched_job['plugin_code'] = plugin_response.get('code')
                                except Exception:
                                    # Fallback to config if plugin fetch fails
                                    config = plugin_release_response.get('config', {})
                                    enriched_job['plugin_name'] = config.get('name') or config.get('code')
                                    enriched_job['plugin_code'] = config.get('code')
                            else:
                                # Fallback to config if no plugin ID
                                config = plugin_release_response.get('config', {})
                                enriched_job['plugin_name'] = config.get('name') or config.get('code')
                                enriched_job['plugin_code'] = config.get('code')
                    except Exception:
                        pass

                # Try to get agent info
                if 'agent' in job:
                    # First check if we have local agent info
                    if agent_info and job.get('agent') == agent_id:
                        enriched_job['agent_name'] = agent_info.get('name')
                        enriched_job['agent_url'] = agent_info.get('url')
                    else:
                        # Try to fetch agent details from API
                        try:
                            agent_response = self.backend_client.get(f'/agents/{job["agent"]}/')
                            if agent_response and isinstance(agent_response, dict):
                                enriched_job['agent_name'] = agent_response.get('name')
                                enriched_job['agent_url'] = agent_response.get('url')
                        except Exception:
                            pass

                enriched_jobs.append(enriched_job)

            return enriched_jobs
        except ClientError:
            raise
        except Exception as e:
            raise Exception(f'Failed to list jobs: {e}')

    def get_job_logs(self, job_id: str):
        """Get all logs for a job at once."""
        if not self.backend_client:
            raise Exception('Backend client not configured')

        try:
            # Get logs from console_logs endpoint (returns list of strings)
            logs_response = self.backend_client.list_job_console_logs(job_id)

            # API returns a list of log strings
            if isinstance(logs_response, list):
                if not logs_response:
                    # Empty list means no logs yet
                    yield 'No logs available for this job yet.\n'
                else:
                    for log_entry in logs_response:
                        # Each entry is already a formatted string with timestamp
                        yield str(log_entry) + '\n' if not str(log_entry).endswith('\n') else str(log_entry)
            elif logs_response:
                # Fallback for unexpected format
                yield str(logs_response) + '\n'
            else:
                yield 'No logs available for this job yet.\n'

        except Exception as e:
            from synapse_sdk.clients.exceptions import ClientError

            # Check if it's a ClientError with specific status
            if isinstance(e, ClientError):
                if e.status == 404:
                    yield 'Job not found or logs not available.\n'
                elif e.status == 401:
                    yield 'Unauthorized to access job logs.\n'
                else:
                    # Check for Korean error message in the reason
                    error_str = str(e.reason) if hasattr(e, 'reason') else str(e)
                    if '찾을 수 없습니다' in error_str:
                        yield 'Job logs not found. The job may not have generated any logs yet.\n'
                    else:
                        yield f'Failed to fetch logs: {error_str}\n'
            else:
                error_str = str(e)
                if '찾을 수 없습니다' in error_str or '404' in error_str or 'Not found' in error_str:
                    yield 'Job logs not found. The job may not have generated any logs yet.\n'
                elif '401' in error_str or 'Unauthorized' in error_str:
                    yield 'Unauthorized to access job logs.\n'
                else:
                    yield f'Failed to fetch logs: {error_str}\n'

    def stream_job_logs(self, job_id: str):
        """Stream logs for a job (simulated streaming since tail endpoint doesn't exist)."""
        if not self.backend_client:
            raise Exception('Backend client not configured')

        # Since tail_console_logs endpoint returns 404, we'll simulate streaming
        # by fetching all logs and yielding them one by one
        try:
            from synapse_sdk.clients.exceptions import ClientError

            # Get logs from console_logs endpoint (returns list of strings)
            logs_response = self.backend_client.list_job_console_logs(job_id)

            # API returns a list of log strings
            if isinstance(logs_response, list):
                if not logs_response:
                    # Empty list means no logs yet
                    yield 'No logs available for this job yet.\n'
                else:
                    # Yield logs one by one to simulate streaming
                    for log_entry in logs_response:
                        # Each entry is already a formatted string with timestamp
                        yield str(log_entry) + '\n' if not str(log_entry).endswith('\n') else str(log_entry)
            elif logs_response:
                # Fallback for unexpected format
                yield str(logs_response) + '\n'
            else:
                yield 'No logs available for this job yet.\n'

        except Exception as e:
            # Check if it's a ClientError with specific status
            if isinstance(e, ClientError):
                if e.status == 404:
                    yield 'Job not found or logs not available.\n'
                elif e.status == 401:
                    yield 'Unauthorized to access job logs.\n'
                else:
                    # Check for Korean error message in the reason
                    error_str = str(e.reason) if hasattr(e, 'reason') else str(e)
                    if '찾을 수 없습니다' in error_str:
                        yield 'Job logs not found. The job may not have generated any logs yet.\n'
                    else:
                        yield f'Failed to stream logs: {error_str}\n'
            else:
                error_str = str(e)
                if '찾을 수 없습니다' in error_str or '404' in error_str or 'Not found' in error_str:
                    yield 'Job logs not found. The job may not have generated any logs yet.\n'
                elif '401' in error_str or 'Unauthorized' in error_str:
                    yield 'Unauthorized to access job logs.\n'
                else:
                    yield f'Failed to stream logs: {error_str}\n'

    @staticmethod
    def format_duration(created: str, completed: Optional[str] = None) -> str:
        """Format duration between created and completed timestamps."""
        if not created:
            return '-'

        try:
            created_dt = datetime.fromisoformat(created.replace('+09:00', '+09:00'))
            if completed:
                completed_dt = datetime.fromisoformat(completed.replace('+09:00', '+09:00'))
                duration = completed_dt - created_dt
                total_seconds = int(duration.total_seconds())
                if total_seconds < 60:
                    return f'{total_seconds}s'
                else:
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    return f'{minutes}m {seconds}s'
            else:
                return '...'
        except Exception:
            return '-'

    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """Format timestamp for display."""
        if not timestamp:
            return '-'

        try:
            dt = datetime.fromisoformat(timestamp.replace('+09:00', '+09:00'))
            return dt.strftime('%m/%d %H:%M')
        except Exception:
            return timestamp[:16] if len(timestamp) > 16 else timestamp
