from synapse_sdk.clients.base import BaseClient


class ServiceClientMixin(BaseClient):
    def run_plugin_release(self, code, data):
        path = f'plugin_releases/{code}/run/'
        return self._post(path, data=data)

    def run_debug_plugin_release(self, data):
        path = 'plugin_releases/run_debug/'
        return self._post(path, data=data)

    def create_plugin_release(self, data):
        path = 'plugin_releases/'
        return self._post(path, data=data)
