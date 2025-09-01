from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.utils import get_default_url_conversion


class MLClientMixin(BaseClient):
    def list_models(self, params=None):
        path = 'models/'
        return self._list(path, params=params)

    def get_model(self, pk, params=None, url_conversion=None):
        path = f'models/{pk}/'
        url_conversion = get_default_url_conversion(url_conversion, files_fields=['file'], is_list=False)
        return self._get(path, params=params, url_conversion=url_conversion)

    def create_model(self, data):
        path = 'models/'
        file = data.pop('file')
        data['chunked_upload'] = self.create_chunked_upload(file)['id']
        return self._post(path, data=data)

    def list_ground_truth_events(self, params=None, url_conversion=None, list_all=False):
        path = 'sdk/ground_truth_events/'
        url_conversion = get_default_url_conversion(url_conversion, files_fields=['files'])
        return self._list(path, params=params, url_conversion=url_conversion, list_all=list_all)

    def get_ground_truth_version(self, pk):
        path = f'ground_truth_dataset_versions/{pk}/'
        return self._get(path)
