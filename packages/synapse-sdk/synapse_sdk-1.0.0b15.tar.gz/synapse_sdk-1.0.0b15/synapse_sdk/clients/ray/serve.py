from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.exceptions import ClientError


class ServeClientMixin(BaseClient):
    def list_serve_applications(self, params=None):
        path = 'api/serve/applications/'
        response = self._get(path, params=params)
        for key, item in response['applications'].items():
            response['applications'][key]['deployments'] = list(item['deployments'].values())
            response['applications'][key]['route_prefix'] = item['route_prefix']
        return list(response['applications'].values())

    def get_serve_application(self, pk, params=None):
        path = 'api/serve/applications/'
        response = self._get(path, params=params)
        try:
            response['applications'][pk]['deployments'] = list(response['applications'][pk]['deployments'].values())
            response['applications'][pk]['route_prefix'] = response['applications'][pk]['route_prefix']
            return response['applications'][pk]
        except KeyError:
            raise ClientError(404, 'Serve Application Not Found')
