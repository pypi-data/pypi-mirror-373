import copy
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator, BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.models import Run
from synapse_sdk.utils.file import archive, get_temp_path, unarchive
from synapse_sdk.utils.pydantic.validators import non_blank


class TrainRun(Run):
    def log_metric(self, category, key, value, **metrics):
        # TODO validate input via plugin config
        self.log('metric', {'category': category, 'key': key, 'value': value, 'metrics': metrics})

    def log_visualization(self, category, group, index, image, **meta):
        # TODO validate input via plugin config
        self.log('visualization', {'category': category, 'group': group, 'index': index, **meta}, file=image)


class Hyperparameter(BaseModel):
    batch_size: int
    epochs: int
    learning_rate: Decimal


class TrainParams(BaseModel):
    name: Annotated[str, AfterValidator(non_blank)]
    description: str
    checkpoint: int | None
    dataset: int
    hyperparameter: Hyperparameter

    @field_validator('name')
    @staticmethod
    def unique_name(value, info):
        action = info.context['action']
        client = action.client
        try:
            model_exists = client.exists('list_models', params={'name': value})
            job_exists = client.exists(
                'list_jobs',
                params={
                    'ids_ex': action.job_id,
                    'category': 'neural_net',
                    'job__action': 'train',
                    'is_active': True,
                    'params': f'name:{value.replace(":", "%3A")}',
                },
            )
            assert not model_exists and not job_exists, '존재하는 학습 이름입니다.'
        except ClientError:
            raise PydanticCustomError('client_error', '')
        return value


@register_action
class TrainAction(Action):
    name = 'train'
    category = PluginCategory.NEURAL_NET
    method = RunMethod.JOB
    run_class = TrainRun
    params_model = TrainParams
    progress_categories = {
        'dataset': {
            'proportion': 20,
        },
        'train': {
            'proportion': 75,
        },
        'model_upload': {
            'proportion': 5,
        },
    }

    def start(self):
        hyperparameter = self.params['hyperparameter']

        # download dataset
        self.run.log_message('Preparing dataset for training.')
        input_dataset = self.get_dataset()

        # retrieve checkpoint
        checkpoint = None
        if self.params['checkpoint']:
            self.run.log_message('Retrieving checkpoint.')
            checkpoint = self.get_model(self.params['checkpoint'])

        # train dataset
        self.run.log_message('Starting model training.')
        result = self.entrypoint(self.run, input_dataset, hyperparameter, checkpoint=checkpoint)

        # upload model_data
        self.run.log_message('Registering model data.')
        self.run.set_progress(0, 1, category='model_upload')
        model = self.create_model(result)
        self.run.set_progress(1, 1, category='model_upload')

        self.run.end_log()
        return {'model_id': model['id'] if model else None}

    def get_dataset(self):
        client = self.run.client
        assert bool(client)

        input_dataset = {}

        ground_truths, count_dataset = client.list_ground_truth_events(
            params={
                'fields': ['category', 'files', 'data'],
                'expand': ['data'],
                'ground_truth_dataset_versions': self.params['dataset'],
            },
            list_all=True,
        )
        self.run.set_progress(0, count_dataset, category='dataset')
        for i, ground_truth in enumerate(ground_truths, start=1):
            self.run.set_progress(i, count_dataset, category='dataset')
            try:
                input_dataset[ground_truth['category']].append(ground_truth)
            except KeyError:
                input_dataset[ground_truth['category']] = [ground_truth]

        return input_dataset

    def get_model(self, model_id):
        model = self.client.get_model(model_id)
        model_file = Path(model['file'])
        output_path = get_temp_path(f'models/{model_file.stem}')
        if not output_path.exists():
            unarchive(model_file, output_path)
        model['path'] = output_path
        return model

    def create_model(self, path):
        params = copy.deepcopy(self.params)
        configuration_fields = ['hyperparameter']
        configuration = {field: params.pop(field) for field in configuration_fields}

        with tempfile.TemporaryDirectory() as temp_path:
            input_path = Path(path)
            archive_path = Path(temp_path, 'archive.zip')
            archive(input_path, archive_path)

            return self.client.create_model({
                'plugin': self.plugin_release.plugin,
                'version': self.plugin_release.version,
                'file': str(archive_path),
                'configuration': configuration,
                **params,
            })
