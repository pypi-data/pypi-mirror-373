import inspect
import json
import os
from functools import cached_property
from pprint import pprint

import requests
from pydantic import ValidationError

from synapse_sdk.clients.ray import RayClient
from synapse_sdk.plugins.enums import RunMethod
from synapse_sdk.plugins.exceptions import ActionError
from synapse_sdk.plugins.models import PluginRelease, Run
from synapse_sdk.plugins.upload import archive_and_upload, build_and_upload, download_and_upload
from synapse_sdk.utils.module_loading import import_string
from synapse_sdk.utils.pydantic.errors import pydantic_to_drf_error


class Action:
    """Base class for all plugin actions.

    Attrs:
        name (str): The name of the action.
        category (PluginCategory): The category of the action.
        method (RunMethod): The method to run of the action.
        run_class (Run): The class to run the action.
        params_model (BaseModel): The model to validate the params.
        progress_categories (Dict[str] | None): The categories to update the progress.
        metrics_categories (Dict[str] | None): The categories to update the metrics.
        params (Dict): The params to run the action.
        plugin_config (Dict): The plugin config.
        plugin_release (PluginRelease): The plugin release.
        config (Dict): The action config.
        requirements (List[str]): The requirements to install.
        job_id (str): The job id.
        direct (bool): The flag to run the action directly.
        debug (bool): The flag to run the action in debug mode.
        envs (Dict): The runtime envs.
        run (Run): The run instance.

    Raises:
        ActionError: If the action fails.
    """

    # class 변수
    name = None
    category = None
    method = None
    run_class = Run
    params_model = None
    progress_categories = None
    metrics_categories = None

    # init 변수
    params = None
    plugin_config = None
    plugin_release = None
    config = None
    requirements = None
    job_id = None
    direct = None
    debug = None
    envs = None
    run = None

    # TODO: Refactor to use Synapse Access Token instead of SYNAPSE_PLUGIN_RUN_USER_TOKEN and SYNAPSE_PLUGIN_RUN_TENANT
    REQUIRED_ENVS = [
        'RAY_ADDRESS',
        'RAY_DASHBOARD_URL',
        'RAY_SERVE_ADDRESS',
        'SYNAPSE_PLUGIN_STORAGE',
        'SYNAPSE_DEBUG_PLUGIN_PATH',
        'SYNAPSE_DEBUG_MODULES',
        'SYNAPSE_PLUGIN_RUN_HOST',
        'SYNAPSE_PLUGIN_RUN_USER_TOKEN',
        'SYNAPSE_PLUGIN_RUN_TENANT',
    ]

    def __init__(self, params, plugin_config, requirements=None, envs=None, job_id=None, direct=False, debug=False):
        self.params = params
        self.plugin_config = plugin_config
        self.plugin_release = PluginRelease(config=plugin_config)
        self.config = self.plugin_release.get_action_config(self.name)
        self.requirements = requirements
        self.job_id = job_id
        self.direct = direct
        self.debug = debug
        self.envs = {**self.get_default_envs(), **envs} if envs else self.get_default_envs()
        self.run = self.get_run()

    @cached_property
    def entrypoint(self):
        return import_string(self.config['entrypoint'])

    @property
    def plugin_storage_url(self):
        return self.envs['SYNAPSE_PLUGIN_STORAGE']

    @property
    def client(self):
        return self.run.client

    @property
    def ray_client(self):
        return RayClient(self.envs['RAY_DASHBOARD_URL'])

    @property
    def plugin_url(self):
        if self.debug:
            plugin_path = self.envs.get('SYNAPSE_DEBUG_PLUGIN_PATH') or '.'
            if plugin_path.startswith('https://'):  # TODO ray에서 지원하는 remote uri 형식 (https, s3, gs) 모두 지원
                plugin_url = plugin_path
            elif plugin_path.startswith('http://'):
                plugin_url = download_and_upload(plugin_path, self.plugin_storage_url)
            else:
                plugin_url = archive_and_upload(plugin_path, self.plugin_storage_url)
            self.envs['SYNAPSE_DEBUG_PLUGIN_PATH'] = plugin_url
            return plugin_url
        return self.plugin_release.get_url(self.plugin_storage_url)

    @property
    def debug_modules(self):
        debug_modules = []
        if self.envs.get('SYNAPSE_DEBUG_MODULES'):
            for module_path in self.envs['SYNAPSE_DEBUG_MODULES'].split(','):
                # TODO ray에서 지원하는 remote uri 형식 (https, s3, gs) 모두 지원
                if module_path.startswith('https://'):
                    module_url = module_path
                else:
                    module_url = build_and_upload(module_path, self.plugin_storage_url)
                debug_modules.append(module_url)
            self.envs['SYNAPSE_DEBUG_MODULES'] = ','.join(debug_modules)
        return debug_modules

    @property
    def plugin_package_manager(self):
        return self.plugin_config.get('package_manager', 'pip')

    @property
    def package_manager_options(self):
        options = {'pip': {}, 'uv': {'uv_pip_install_options': []}}
        return options[self.plugin_package_manager]

    def get_run(self):
        context = {
            'plugin_release': self.plugin_release,
            'progress_categories': self.progress_categories,
            'metrics_categories': self.metrics_categories,
            'params': self.params,
            'envs': self.envs,
            'debug': self.debug,
        }
        return self.run_class(self.job_id, context)

    def get_default_envs(self):
        return {env: os.environ[env] for env in self.REQUIRED_ENVS if env in os.environ}

    def get_runtime_env(self):
        runtime_env = {self.plugin_package_manager: {'packages': []}, 'working_dir': self.plugin_url}

        if self.requirements:
            runtime_env[self.plugin_package_manager]['packages'] += self.requirements

        if self.debug:
            runtime_env[self.plugin_package_manager]['packages'] += self.debug_modules

        for key, value in self.package_manager_options.items():
            runtime_env[self.plugin_package_manager][key] = value

        # 맨 마지막에 진행되어야 함
        runtime_env['env_vars'] = self.envs

        if self.debug:
            pprint(runtime_env)
        return runtime_env

    def validate_params(self):
        if self.params_model:
            try:
                self.params_model.model_validate(self.params, context={'action': self})
            except ValidationError as e:
                raise ActionError({'params': pydantic_to_drf_error(e)})

    def run_action(self):
        self.validate_params()

        if self.direct:
            if self.method == RunMethod.RESTAPI:
                return self.start_by_restapi()
            else:
                result = self.start()
                if self.job_id:
                    self.post_action_by_job(result)
                return result
        return getattr(self, f'start_by_{self.method.value}')()

    def start(self):
        """Start the action.

        TODO: Specify the return type of start method for overrided methods.
        """
        if self.method == RunMethod.JOB:
            return self.entrypoint(self.run, **self.params)
        return self.entrypoint(**self.params)

    def start_by_task(self):
        """Ray Task based execution.

        * A task method that simply executes the entrypoint without job management functionality.
        """
        import ray
        from ray.exceptions import RayTaskError

        @ray.remote(runtime_env=self.get_runtime_env())
        def run_task(category, action, *args, **kwargs):
            from synapse_sdk.plugins.utils import get_action_class

            action = get_action_class(category, action)(*args, **kwargs)
            return action.run_action()

        init_signature = inspect.signature(self.__class__.__init__)

        args = []
        kwargs = {}

        for param in init_signature.parameters.values():
            if param.name == 'self':
                continue
            if param.default == param.empty:
                args.append(getattr(self, param.name))
            else:
                kwargs[param.name] = getattr(self, param.name)

        kwargs['direct'] = True
        try:
            self.ray_init()
            return ray.get(run_task.remote(self.category.value, self.name, *args, **kwargs))
        except RayTaskError as e:
            raise ActionError(e.cause)

    def start_by_job(self):
        """Ray Job based execution.

        * Executes the entrypoint with Ray job. Ray job manages the entrypoint execution and stores the results.
        """
        main_options = []
        options = ['run', '--direct']
        arguments = [self.name, f'{json.dumps(json.dumps(self.params))}']

        if self.debug:
            main_options.append('--debug')

        if self.job_id:
            options.append(f'--job-id={self.job_id}')

        cmd = ' '.join(main_options + options + arguments)

        client = self.get_job_client()
        return client.submit_job(
            submission_id=self.job_id,
            entrypoint=f'synapse plugin {cmd}',
            runtime_env=self.get_runtime_env(),
        )

    def start_by_restapi(self):
        """Ray Serve based execution.

        * This method executes a Fastapi endpoint defined within the Plugin.
        """
        path = self.params.pop('path', '')
        method = self.params.pop('method')

        url = self.plugin_release.get_serve_url(self.envs['RAY_SERVE_ADDRESS'], path)
        try:
            response = getattr(requests, method)(url, **self.params)
            try:
                response_body = response.json()
            except ValueError:
                response_body = response.text
            if response.ok:
                return response_body
            else:
                raise ActionError({'status': response.status_code, 'reason': response.reason, 'message': response_body})
        except requests.ConnectionError:
            raise ActionError('Unable to connect to serve application')

    def post_action_by_job(self, result):
        job_client = self.get_job_client()
        logs = job_client.get_job_logs(self.job_id).split('\n')
        self.client.update_job(self.job_id, data={'result': result or {}, 'console_logs': logs})

    def get_job_client(self):
        from ray.dashboard.modules.job.sdk import JobSubmissionClient

        return JobSubmissionClient(address=self.envs.get('RAY_DASHBOARD_URL'))

    def ray_init(self):
        import ray

        if not ray.is_initialized():
            ray.init(address=self.envs['RAY_ADDRESS'], ignore_reinit_error=True)
