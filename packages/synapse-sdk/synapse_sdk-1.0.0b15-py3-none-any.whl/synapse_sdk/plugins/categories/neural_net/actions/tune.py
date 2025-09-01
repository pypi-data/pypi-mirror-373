import copy
import tempfile
from pathlib import Path
from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.categories.neural_net.actions.train import TrainAction, TrainRun
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.utils.file import archive
from synapse_sdk.utils.module_loading import import_string
from synapse_sdk.utils.pydantic.validators import non_blank


class TuneRun(TrainRun):
    is_tune = True
    completed_samples = 0
    num_samples = 0
    checkpoint_output = None


class SearchAlgo(BaseModel):
    name: str
    points_to_evaluate: Optional[dict] = None


class Scheduler(BaseModel):
    name: str
    options: Optional[str] = None


class TuneConfig(BaseModel):
    mode: Optional[str] = None
    metric: Optional[str] = None
    num_samples: int = 1
    max_concurrent_trials: Optional[int] = None
    search_alg: Optional[SearchAlgo] = None
    scheduler: Optional[Scheduler] = None


class TuneParams(BaseModel):
    name: Annotated[str, AfterValidator(non_blank)]
    description: str
    checkpoint: int | None
    dataset: int
    tune_config: TuneConfig

    @field_validator('name')
    @staticmethod
    def unique_name(value, info):
        action = info.context['action']
        client = action.client
        try:
            job_exists = client.exists(
                'list_jobs',
                params={
                    'ids_ex': action.job_id,
                    'category': 'neural_net',
                    'job__action': 'tune',
                    'is_active': True,
                    'params': f'name:{value}',
                },
            )
            assert not job_exists, '존재하는 튜닝 작업 이름입니다.'
        except ClientError:
            raise PydanticCustomError('client_error', '')
        return value


@register_action
class TuneAction(TrainAction):
    """
    **Must read** Important notes before using Tune:

    1. Path to the model output (which is the return value of your train function)
       should be set to the checkpoint_output attribute of the run object **before**
       starting the training.
    2. Before exiting the training function, report the results to Tune.
    3. When using own tune.py, take note of the difference in the order of parameters.
       tune() function starts with hyperparameter, run, dataset, checkpoint, **kwargs
       whereas the train() function starts with run, dataset, hyperparameter, checkpoint, **kwargs.
    ----
    1)
    Set the output path for the checkpoint to export best model

    output_path = Path('path/to/your/weights')
    run.checkpoint_output = str(output_path)

    2)
    Before exiting the training function, report the results to Tune.
    The results_dict should contain the metrics you want to report.

    Example: (In train function)
    results_dict = {
        "accuracy": accuracy,
        "loss": loss,
        # Add other metrics as needed
    }
    if hasattr(self.dm_run, 'is_tune') and self.dm_run.is_tune:
        tune.report(results_dict, checkpoint=tune.Checkpoint.from_directory(self.dm_run.checkpoint_output))


    3)
    tune() function takes hyperparameter, run, dataset, checkpoint, **kwargs in that order
    whereas train() function takes run, dataset, hyperparameter, checkpoint, **kwargs in that order.

    --------------------------------------------------------------------------------------------------------

    **중요** Tune 사용 전 반드시 읽어야 할 사항들

    1. 본 플러그인의 train 함수에서, 학습을 진행하기 코드 전에
       결과 모델 파일의 경로(train함수의 리턴 값)을 checkpoint_output 속성에 설정해야 합니다.
    2. 학습이 종료되기 전에, 결과를 Tune에 보고해야 합니다.
    3. 플러그인에서 tune.py를 직접 생성해서 사용할 시, 매개변수의 순서가 다릅니다.

    ----
    1)
    체크포인트를 설정할 경로를 지정합니다.
    output_path = Path('path/to/your/weights')
    run.checkpoint_output = str(output_path)

    2)
    학습이 종료되기 전에, 결과를 Tune에 보고합니다.
    results_dict = {
        "accuracy": accuracy,
        "loss": loss,
        # 필요한 다른 메트릭 추가
    }
    if hasattr(self.dm_run, 'is_tune') and self.dm_run.is_tune:
        tune.report(results_dict, checkpoint=tune.Checkpoint.from_directory(self.dm_run.checkpoint_output))

    3)
    tune() 함수는 hyperparameter, run, dataset, checkpoint, **kwargs 순서이고
    train() 함수는 run, dataset, hyperparameter, checkpoint, **kwargs 순서입니다.
    """

    name = 'tune'
    category = PluginCategory.NEURAL_NET
    method = RunMethod.JOB
    run_class = TuneRun
    params_model = TuneParams
    progress_categories = {
        'dataset': {
            'proportion': 5,
        },
        'trials': {
            'proportion': 90,
        },
        'model_upload': {
            'proportion': 5,
        },
    }

    def start(self):
        from ray import tune

        # download dataset
        self.run.log_message('Preparing dataset for hyperparameter tuning.')
        input_dataset = self.get_dataset()

        # retrieve checkpoint
        checkpoint = None
        if self.params['checkpoint']:
            self.run.log_message('Retrieving checkpoint.')
            checkpoint = self.get_model(self.params['checkpoint'])

        # train dataset
        self.run.log_message('Starting training for hyperparameter tuning.')

        # Save num_samples to TuneRun for logging
        self.run.num_samples = self.params['tune_config']['num_samples']

        entrypoint = self.entrypoint
        if not self._tune_override_exists():
            # entrypoint must be train entrypoint
            def _tune(param_space, run, dataset, checkpoint=None, **kwargs):
                return entrypoint(run, dataset, param_space, checkpoint, **kwargs)

            entrypoint = _tune

        trainable = tune.with_parameters(entrypoint, run=self.run, dataset=input_dataset, checkpoint=checkpoint)

        tune_config = self.params['tune_config']

        tune_config['search_alg'] = self.convert_tune_search_alg(tune_config)
        tune_config['scheduler'] = self.convert_tune_scheduler(tune_config)

        hyperparameter = self.params['hyperparameter']
        param_space = self.convert_tune_params(hyperparameter)
        temp_path = tempfile.TemporaryDirectory()

        tuner = tune.Tuner(
            tune.with_resources(trainable, resources=self.tune_resources),
            tune_config=tune.TuneConfig(**tune_config),
            run_config=tune.RunConfig(
                name=f'synapse_tune_hpo_{self.job_id}',
                log_to_file=('stdout.log', 'stderr.log'),
                storage_path=temp_path.name,
            ),
            param_space=param_space,
        )
        result = tuner.fit()

        best_result = result.get_best_result()

        # upload model_data
        self.run.log_message('Registering best model data.')
        self.run.set_progress(0, 1, category='model_upload')
        self.create_model_from_result(best_result)
        self.run.set_progress(1, 1, category='model_upload')

        self.run.end_log()

        return {'best_result': best_result.config}

    @property
    def tune_resources(self):
        resources = {}
        for option in ['num_cpus', 'num_gpus']:
            option_value = self.params.get(option)
            if option_value:
                # Remove the 'num_' prefix and trailing s from the option name
                resources[(lambda s: s[4:-1])(option)] = option_value
        return resources

    def create_model_from_result(self, result):
        params = copy.deepcopy(self.params)
        configuration_fields = ['hyperparameter']
        configuration = {field: params.pop(field) for field in configuration_fields}

        with tempfile.TemporaryDirectory() as temp_path:
            archive_path = Path(temp_path, 'archive.zip')

            # Archive tune results
            # https://docs.ray.io/en/latest/tune/tutorials/tune_get_data_in_and_out.html#getting-data-out-of-tune-using-checkpoints-other-artifacts
            archive(result.path, archive_path)

            return self.client.create_model({
                'plugin': self.plugin_release.plugin,
                'version': self.plugin_release.version,
                'file': str(archive_path),
                'configuration': configuration,
                **params,
            })

    @staticmethod
    def convert_tune_scheduler(tune_config):
        """
        Convert YAML hyperparameter configuration to a Ray Tune scheduler.

        Args:
            tune_config (dict): Hyperparameter configuration.

        Returns:
            object: Ray Tune scheduler instance.
        """

        from ray.tune.schedulers import (
            ASHAScheduler,
            FIFOScheduler,
            HyperBandScheduler,
            MedianStoppingRule,
            PopulationBasedTraining,
        )

        if tune_config.get('scheduler') is None:
            return None

        scheduler_map = {
            'fifo': FIFOScheduler,
            'asha': ASHAScheduler,
            'hyperband': HyperBandScheduler,
            'pbt': PopulationBasedTraining,
            'median': MedianStoppingRule,
        }

        scheduler_type = tune_config['scheduler'].get('name', 'fifo').lower()
        scheduler_class = scheduler_map.get(scheduler_type, ASHAScheduler)

        # 옵션이 있는 경우 전달하고, 없으면 기본 생성자 호출
        options = tune_config['scheduler'].get('options')

        # options가 None이거나 빈 딕셔너리가 아닌 경우에만 전달
        scheduler = scheduler_class(**options) if options else scheduler_class()

        return scheduler

    @staticmethod
    def convert_tune_search_alg(tune_config):
        """
        Convert YAML hyperparameter configuration to Ray Tune search algorithm and scheduler.

        Args:
            tune_config (dict): Hyperparameter configuration.

        Returns:
            dict: Ray Tune search algorithm and scheduler
        """

        if tune_config.get('search_alg') is None:
            return None

        search_alg_name = tune_config['search_alg']['name'].lower()
        metric = tune_config['metric']
        mode = tune_config['mode']
        points_to_evaluate = tune_config['search_alg'].get('points_to_evaluate', None)

        if search_alg_name == 'axsearch':
            from ray.tune.search.ax import AxSearch

            search_alg = AxSearch(metric=metric, mode=mode)
        elif search_alg_name == 'bayesoptsearch':
            from ray.tune.search.bayesopt import BayesOptSearch

            search_alg = BayesOptSearch(metric=metric, mode=mode)
        elif search_alg_name == 'hyperoptsearch':
            from ray.tune.search.hyperopt import HyperOptSearch

            search_alg = HyperOptSearch(metric=metric, mode=mode)
        elif search_alg_name == 'optunasearch':
            from ray.tune.search.optuna import OptunaSearch

            search_alg = OptunaSearch(metric=metric, mode=mode)
        elif search_alg_name == 'basicvariantgenerator':
            from ray.tune.search.basic_variant import BasicVariantGenerator

            search_alg = BasicVariantGenerator(points_to_evaluate=points_to_evaluate)

        return search_alg

    @staticmethod
    def convert_tune_params(param_list):
        """
        Convert YAML hyperparameter configuration to Ray Tune parameter dictionary.

        Args:
            param_list (list): List of hyperparameter configurations.

        Returns:
            dict: Ray Tune parameter dictionary
        """
        from ray import tune

        param_handlers = {
            'uniform': lambda p: tune.uniform(p['min'], p['max']),
            'quniform': lambda p: tune.quniform(p['min'], p['max']),
            'loguniform': lambda p: tune.loguniform(p['min'], p['max'], p['base']),
            'qloguniform': lambda p: tune.qloguniform(p['min'], p['max'], p['base']),
            'randn': lambda p: tune.randn(p['mean'], p['sd']),
            'qrandn': lambda p: tune.qrandn(p['mean'], p['sd']),
            'randint': lambda p: tune.randint(p['min'], p['max']),
            'qrandint': lambda p: tune.qrandint(p['min'], p['max']),
            'lograndint': lambda p: tune.lograndint(p['min'], p['max'], p['base']),
            'qlograndint': lambda p: tune.qlograndint(p['min'], p['max'], p['base']),
            'choice': lambda p: tune.choice(p['options']),
            'grid_search': lambda p: tune.grid_search(p['options']),
        }

        param_space = {}

        for param in param_list:
            name = param['name']
            param_type = param['type']

            if param_type in param_handlers:
                param_space[name] = param_handlers[param_type](param)
            else:
                raise ValueError(f'Unknown parameter type: {param_type}')

        return param_space

    @staticmethod
    def _tune_override_exists(module_path='plugin.tune') -> bool:
        try:
            import_string(module_path)
            return True
        except ImportError:
            return False
