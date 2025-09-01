import tempfile

import jwt
from fastapi import FastAPI
from ray import serve

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.utils.file import unarchive

app = FastAPI()


class BaseInference:
    backend_url = None
    client = None

    def __init__(self, backend_url):
        self.backend_url = backend_url

    @serve.multiplexed()
    async def _load_model(self, model_id: str):
        model_info = jwt.decode(model_id, self.backend_url, algorithms='HS256')
        client = BackendClient(self.backend_url, token=model_info['token'], tenant=model_info['tenant'])
        model = client.get_model(model_info['model'])
        with tempfile.TemporaryDirectory() as temp_path:
            unarchive(model['file'], temp_path)
            model['path'] = temp_path
            return await self._get_model(model)

    async def get_model(self):
        return await self._load_model(serve.get_multiplexed_model_id())

    async def _get_model(self, model):
        raise NotImplementedError

    async def infer(self, *args, **kwargs):
        raise NotImplementedError
