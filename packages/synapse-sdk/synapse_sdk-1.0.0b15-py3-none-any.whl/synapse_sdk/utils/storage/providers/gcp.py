from upath import UPath

from synapse_sdk.utils.storage.providers import BaseStorage


class GCPStorage(BaseStorage):
    def __init__(self, url):
        super().__init__(url)

        self.upath = UPath(f'gs://{self.query_params["bucket_name"]}', token=self.query_params['credentials'])

    def get_pathlib(self, path):
        return self.upath.joinuri(path)
