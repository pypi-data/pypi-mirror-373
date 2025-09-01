from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.utils import get_default_url_conversion


class AnnotationClientMixin(BaseClient):
    def get_project(self, pk):
        path = f'projects/{pk}/'
        return self._get(path)

    def get_task(self, pk, params):
        path = f'tasks/{pk}/'
        return self._get(path, params=params)

    def annotate_task_data(self, pk, data):
        path = f'tasks/{pk}/annotate_task_data/'
        return self._put(path, data=data)

    def get_task_tag(self, pk):
        path = f'task_tags/{pk}/'
        return self._get(path)

    def list_task_tags(self, params):
        path = 'task_tags/'
        return self._list(path, params=params)

    def list_tasks(self, params=None, url_conversion=None, list_all=False):
        path = 'sdk/tasks/'
        url_conversion = get_default_url_conversion(url_conversion, files_fields=['files'])
        return self._list(path, params=params, url_conversion=url_conversion, list_all=list_all)

    def create_tasks(self, data):
        path = 'tasks/'
        return self._post(path, data=data)

    def set_tags_tasks(self, data, params=None):
        path = 'tasks/set_tags/'
        return self._post(path, data=data, params=params)
