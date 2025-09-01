from pydantic import BaseModel

# for load file with synapse
# from synapse_sdk.types import FileField
from synapse_sdk.plugins.categories.neural_net.base.inference import BaseInference, app


class InputData(BaseModel):  # Pydantic
    input_string: str


class ResNetInference(BaseInference):
    async def _get_model(self, model):  # Load model
        model_directory_path = model['path']

        # implement model_load code
        model = model_directory_path

        return model  # return loaded_model

    @app.post('/load_model')
    async def load_model(self):
        await self.get_model()

    @app.post('/')
    async def infer(self, data: InputData):
        model = await self.get_model()
        results = model(data.input_string)  # This is Sample code. implement your model's prediction code

        return results
