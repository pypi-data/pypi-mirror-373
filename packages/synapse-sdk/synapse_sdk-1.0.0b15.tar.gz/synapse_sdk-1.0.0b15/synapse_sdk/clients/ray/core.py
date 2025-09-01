from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.exceptions import ClientError


class CoreClientMixin(BaseClient):
    def list_nodes(self, params=None):
        path = 'nodes'
        response = self._get(path, params=params)
        if not response['result']:
            raise ClientError(200, response['msg'])
        return response['data']['summary']

    def get_node(self, pk, params=None):
        path = f'nodes/{pk}'
        response = self._get(path, params=params)['detail']

        if not response['result']:
            raise ClientError(200, response['msg'])

        if 'agent' not in response['data']:
            raise ClientError(404, 'Node Not Found')
        return response['data']
