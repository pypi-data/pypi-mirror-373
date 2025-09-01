from synapse_sdk.clients.base import BaseClient


class CoreClientMixin(BaseClient):
    def health_check(self):
        path = 'health/'
        return self._get(path)

    def get_metrics(self, panel):
        path = f'metrics/{panel}/'
        return self._get(path)

    def get_code_server_info(self, workspace_path=None):
        """Get code-server connection information from the agent.

        Args:
            workspace_path: Optional path to set as the workspace directory

        Returns:
            dict: Code-server connection information
        """
        path = 'code-server/info/'
        params = {}
        if workspace_path:
            params['workspace'] = workspace_path
        return self._get(path, params=params)
