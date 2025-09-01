from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.utils import get_default_url_conversion


class HITLClientMixin(BaseClient):
    def get_assignment(self, pk):
        path = f'assignments/{pk}/'
        return self._get(path)

    def list_assignments(self, params=None, url_conversion=None, list_all=False):
        path = 'sdk/assignments/'
        url_conversion = get_default_url_conversion(url_conversion, files_fields=['files'])
        return self._list(path, params=params, url_conversion=url_conversion, list_all=list_all)

    def set_tags_assignments(self, data, params=None):
        path = 'assignments/set_tags/'
        return self._post(path, payload=data, params=params)
