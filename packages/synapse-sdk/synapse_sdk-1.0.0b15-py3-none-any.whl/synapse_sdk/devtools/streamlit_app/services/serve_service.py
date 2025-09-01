"""Serve service for managing serve deployments."""

from typing import Dict, List, Optional

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.clients.exceptions import ClientError


class ServeService:
    """Service for serve deployment operations."""

    def __init__(self, backend_client: Optional[BackendClient] = None):
        self.backend_client = backend_client

    def list_serve_applications(self, agent_id: Optional[int] = None, agent_info: Optional[Dict] = None) -> List[Dict]:
        """List serve applications from the backend."""
        if not self.backend_client:
            return []

        try:
            params = {}
            if agent_id:
                params['agent'] = agent_id

            apps_response = self.backend_client.list_serve_applications(params=params)

            # Handle paginated response - extract results
            if apps_response is None:
                return []
            elif isinstance(apps_response, dict) and 'results' in apps_response:
                applications = apps_response['results']
            else:
                applications = apps_response if isinstance(apps_response, list) else []

            # Remove None applications
            valid_apps = [app for app in applications if app is not None]

            # Try to enrich applications with plugin and agent names
            enriched_apps = []
            for app in valid_apps:
                enriched_app = app.copy()

                # Try to get plugin info
                if 'plugin_release' in app:
                    try:
                        # Try to fetch plugin release details
                        plugin_release_response = self.backend_client.get(f'/plugin_releases/{app["plugin_release"]}/')
                        if plugin_release_response and isinstance(plugin_release_response, dict):
                            # Get version from plugin release
                            enriched_app['plugin_version'] = plugin_release_response.get('version')

                            # Try to get plugin details from the plugin ID
                            plugin_id = plugin_release_response.get('plugin')
                            if plugin_id:
                                try:
                                    plugin_response = self.backend_client.get(f'/plugins/{plugin_id}/')
                                    if plugin_response and isinstance(plugin_response, dict):
                                        enriched_app['plugin_name'] = plugin_response.get('name')
                                        enriched_app['plugin_code'] = plugin_response.get('code')
                                except Exception:
                                    # Fallback to config if plugin fetch fails
                                    config = plugin_release_response.get('config', {})
                                    enriched_app['plugin_name'] = config.get('name') or config.get('code')
                                    enriched_app['plugin_code'] = config.get('code')
                            else:
                                # Fallback to config if no plugin ID
                                config = plugin_release_response.get('config', {})
                                enriched_app['plugin_name'] = config.get('name') or config.get('code')
                                enriched_app['plugin_code'] = config.get('code')
                    except Exception:
                        pass

                # Try to get agent info
                if 'agent' in app:
                    # First check if we have local agent info
                    if agent_info and app.get('agent') == agent_id:
                        enriched_app['agent_name'] = agent_info.get('name')
                        enriched_app['agent_url'] = agent_info.get('url')
                    else:
                        # Try to fetch agent details from API
                        try:
                            agent_response = self.backend_client.get(f'/agents/{app["agent"]}/')
                            if agent_response and isinstance(agent_response, dict):
                                enriched_app['agent_name'] = agent_response.get('name')
                                enriched_app['agent_url'] = agent_response.get('url')
                        except Exception:
                            pass

                enriched_apps.append(enriched_app)

            return enriched_apps
        except ClientError:
            raise
        except Exception as e:
            raise Exception(f'Failed to list serve applications: {e}')
