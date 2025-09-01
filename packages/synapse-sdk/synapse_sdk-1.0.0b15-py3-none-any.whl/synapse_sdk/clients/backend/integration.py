from synapse_sdk.clients.backend.models import Storage, UpdateJob
from synapse_sdk.clients.base import BaseClient
from synapse_sdk.utils.file import convert_file_to_base64


class IntegrationClientMixin(BaseClient):
    def health_check_agent(self, token):
        path = f'agents/{token}/connect/'
        return self._post(path)

    def get_plugin(self, pk):
        path = f'plugins/{pk}/'
        return self._get(path)

    def create_plugin(self, data):
        path = 'plugins/'
        return self._post(path, data=data)

    def update_plugin(self, pk, data):
        path = f'plugins/{pk}/'
        return self._put(path, data=data)

    def run_plugin(self, pk, data):
        path = f'plugins/{pk}/run/'
        return self._post(path, data=data)

    def get_plugin_release(self, pk, params=None):
        path = f'plugin_releases/{pk}/'
        return self._get(path, params=params)

    def create_plugin_release(self, data):
        path = 'plugin_releases/'
        files = {'file': data.pop('file')}
        return self._post(path, data=data, files=files)

    def get_job(self, pk, params=None):
        path = f'jobs/{pk}/'
        return self._get(path, params=params)

    def list_jobs(self, params=None):
        path = 'jobs/'
        return self._list(path, params=params)

    def update_job(self, pk, data):
        path = f'jobs/{pk}/'
        return self._patch(path, request_model=UpdateJob, data=data)

    def list_job_console_logs(self, pk):
        path = f'jobs/{pk}/console_logs/'
        return self._get(path)

    def tail_job_console_logs(self, pk):
        path = f'jobs/{pk}/tail_console_logs/'

        url = self._get_url(path)
        headers = self._get_headers()

        response = self.requests_session.get(url, headers=headers, stream=True)
        for line in response.iter_lines(decode_unicode=True):
            if line:
                yield f'{line}\n'

    def create_logs(self, data):
        path = 'logs/'
        if not isinstance(data, list):
            data = [data]

        for item in data:
            if 'file' in item:
                item['file'] = convert_file_to_base64(item['file'])

        return self._post(path, data=data)

    def create_serve_application(self, data):
        path = 'serve_applications/'
        return self._post(path, data=data)

    def list_serve_applications(self, params=None, list_all=False):
        path = 'serve_applications/'
        return self._list(path, params=params, list_all=list_all)

    def get_storage(self, pk):
        """Get specific storage data from synapse backend."""
        path = f'storages/{pk}/'
        params = {'with_configuration': True}
        return self._get(path, params=params, response_model=Storage)
