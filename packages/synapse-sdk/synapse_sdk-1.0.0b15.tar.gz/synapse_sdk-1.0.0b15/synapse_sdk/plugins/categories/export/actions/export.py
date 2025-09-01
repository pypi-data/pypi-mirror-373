import json
from abc import ABC, abstractmethod
from datetime import datetime
from itertools import tee
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.i18n import gettext as _
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.categories.export.enums import ExportStatus
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.models import Run
from synapse_sdk.shared.enums import Context
from synapse_sdk.utils.pydantic.validators import non_blank
from synapse_sdk.utils.storage import get_pathlib


class ExportRun(Run):
    class ExportEventLog(BaseModel):
        """Export event log model."""

        target_id: int
        info: str | None = None
        status: Context
        created: str

    class DataFileLog(BaseModel):
        """Data file log model."""

        target_id: int
        data_file_info: str | None
        status: ExportStatus
        error: str | None = None
        created: str

    class MetricsRecord(BaseModel):
        """Metrics record model."""

        stand_by: int
        failed: int
        success: int

    LOG_MESSAGES = {
        'NULL_DATA_DETECTED': {
            'message': 'Data is null for export item',
            'level': Context.WARNING,
        },
    }

    def log_file(
        self, log_type: str, target_id: int, data_file_info: dict, status: ExportStatus, error: str | None = None
    ):
        """Log export file information.

        Args:
            log_type (str): The type of log ('export_data_file' or 'export_original_file').
            target_id (int): The ID of the data file.
            data_file_info (dict): The JSON info of the data file.
            status (ExportStatus): The status of the data file.
            error (str | None): The error message, if any.
        """
        now = datetime.now().isoformat()
        self.log(
            log_type,
            self.DataFileLog(
                target_id=target_id,
                data_file_info=json.dumps(data_file_info),
                status=status.value,
                error=error,
                created=now,
            ).model_dump(),
        )

    def log_export_event(self, code: str, target_id: int, *args, level: Context | None = None):
        """Log export event using predefined code.

        Args:
            code (str): The log message code.
            target_id (int): The ID of the export target.
            *args: Arguments to format the message.
            level (Context | None): Optional context level override.
        """
        if code not in self.LOG_MESSAGES:
            now = datetime.now().isoformat()
            self.log(
                'export_event',
                self.ExportEventLog(
                    target_id=target_id, info=f'Unknown log code: {code}', status=Context.DANGER, created=now
                ).model_dump(),
            )
            return

        log_config = self.LOG_MESSAGES[code]
        message = log_config['message'].format(*args) if args else log_config['message']
        log_level = level or log_config['level'] or Context.INFO

        now = datetime.now().isoformat()
        self.log(
            'export_event',
            self.ExportEventLog(info=message, status=log_level, target_id=target_id, created=now).model_dump(),
        )

    def log_metrics(self, record: MetricsRecord, category: str):
        """Log export metrics.

        Args:
            record (MetricsRecord): The metrics record to log.
            category (str): The category of the metrics.
        """
        record = self.MetricsRecord.model_validate(record)
        self.set_metrics(value=record.model_dump(), category=category)

    def export_log_json_file(
        self,
        target_id: int,
        data_file_info: dict,
        status: ExportStatus = ExportStatus.STAND_BY,
        error: str | None = None,
    ):
        """Log export json data file."""
        self.log_file('export_data_file', target_id, data_file_info, status, error)

    def export_log_original_file(
        self,
        target_id: int,
        data_file_info: dict,
        status: ExportStatus = ExportStatus.STAND_BY,
        error: str | None = None,
    ):
        """Log export origin data file."""
        self.log_file('export_original_file', target_id, data_file_info, status, error)


class ExportTargetHandler(ABC):
    """
    Abstract base class for handling export targets.

    This class defines the blueprint for export target handlers, requiring the implementation
    of methods to validate filters, retrieve results, and process collections of results.
    """

    @abstractmethod
    def validate_filter(self, value: dict, client: Any):
        """
        Validate filter query params to request original data from api.

        Args:
            value (dict): The filter criteria to validate.
            client (Any): The client used to validate the filter.

        Raises:
            PydanticCustomError: If the filter criteria are invalid.

        Returns:
            dict: The validated filter criteria.
        """
        pass

    @abstractmethod
    def get_results(self, client: Any, filters: dict):
        """
        Retrieve original data from target sources.

        Args:
            client (Any): The client used to retrieve the results.
            filters (dict): The filter criteria to apply.

        Returns:
            tuple: A tuple containing the results and the total count of results.
        """
        pass

    @abstractmethod
    def get_export_item(self, results):
        """
        Providing elements to build export data.

        Args:
            results (list): The results to process.

        Yields:
            generator: A generator that yields processed data items.
        """
        pass


class AssignmentExportTargetHandler(ExportTargetHandler):
    def validate_filter(self, value: dict, client: Any):
        if 'project' not in value:
            raise PydanticCustomError('missing_field', _('Project is required for Assignment.'))
        try:
            client.list_assignments(params=value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Assignment.'))
        return value

    def get_results(self, client: Any, filters: dict):
        return client.list_assignments(params=filters, list_all=True)

    def get_export_item(self, results):
        for result in results:
            yield {
                'data': result['data'],
                'files': result['file'],
                'id': result['id'],
            }


class GroundTruthExportTargetHandler(ExportTargetHandler):
    def validate_filter(self, value: dict, client: Any):
        if 'ground_truth_dataset_version' not in value:
            raise PydanticCustomError('missing_field', _('Ground Truth dataset version is required.'))
        try:
            client.get_ground_truth_version(value['ground_truth_dataset_version'])
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Ground Truth dataset version.'))
        return value

    def get_results(self, client: Any, filters: dict):
        filters['ground_truth_dataset_versions'] = filters.pop('ground_truth_dataset_version')
        return client.list_ground_truth_events(params=filters, list_all=True)

    def get_export_item(self, results):
        for result in results:
            files_key = next(iter(result['data_unit']['files']))
            yield {
                'data': result['data'],
                'files': result['data_unit']['files'][files_key],
                'id': result['id'],
            }


class TaskExportTargetHandler(ExportTargetHandler):
    def validate_filter(self, value: dict, client: Any):
        if 'project' not in value:
            raise PydanticCustomError('missing_field', _('Project is required for Task.'))
        try:
            client.list_tasks(params=value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Task.'))
        return value

    def get_results(self, client: Any, filters: dict):
        filters['expand'] = ['data_unit', 'assignment', 'workshop']
        return client.list_tasks(params=filters, list_all=True)

    def get_export_item(self, results):
        for result in results:
            files_key = next(iter(result['data_unit']['files']))
            yield {
                'data': result['data'],
                'files': result['data_unit']['files'][files_key],
                'id': result['id'],
            }


class TargetHandlerFactory:
    @staticmethod
    def get_handler(target: str) -> ExportTargetHandler:
        if target == 'assignment':
            return AssignmentExportTargetHandler()
        elif target == 'ground_truth':
            return GroundTruthExportTargetHandler()
        elif target == 'task':
            return TaskExportTargetHandler()
        else:
            raise ValueError(f'Unknown target: {target}')


class ExportParams(BaseModel):
    """
    Parameters for the export action.

    Attributes:
        name (str): The name of the action.
        description (str | None): The description of the action.
        storage (int): The storage ID to save the exported data.
        save_original_file (bool): Whether to save the original file.
        path (str): The path to save the exported data.
        target (str): The target source to export data from. (ex. ground_truth, assignment, task)
        filter (dict): The filter criteria to apply.
        extra_params (dict | None): Additional parameters for export customization.
            Example: {"include_metadata": True, "compression": "gzip"}
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str | None = None
    storage: int
    save_original_file: bool = True
    path: str
    target: Literal['assignment', 'ground_truth', 'task']
    filter: dict
    extra_params: dict | None = None

    @field_validator('storage')
    @staticmethod
    def check_storage_exists(value, info):
        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get storage from Synapse backend.'))
        return value

    @field_validator('filter')
    @staticmethod
    def check_filter_by_target(value, info):
        action = info.context['action']
        client = action.client
        target = action.params['target']
        handler = TargetHandlerFactory.get_handler(target)
        return handler.validate_filter(value, client)


@register_action
class ExportAction(Action):
    name = 'export'
    category = PluginCategory.EXPORT
    method = RunMethod.JOB
    params_model = ExportParams
    run_class = ExportRun
    progress_categories = {
        'dataset_conversion': {
            'proportion': 100,
        }
    }
    metrics_categories = {
        'data_file': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        },
        'original_file': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        },
    }

    def get_filtered_results(self, filters, handler):
        """Get filtered target results."""
        try:
            result_list = handler.get_results(self.client, filters)
            results = result_list[0]
            count = result_list[1]
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Ground Truth dataset.'))
        return results, count

    def start(self):
        filters = {'expand': 'data', **self.params['filter']}
        target = self.params['target']
        handler = TargetHandlerFactory.get_handler(target)

        self.params['results'], self.params['count'] = self.get_filtered_results(filters, handler)

        # For the 'ground_truth' target, retrieve project information from the first result and add configuration
        if target == 'ground_truth':
            try:
                # Split generator into two using tee()
                peek_iter, main_iter = tee(self.params['results'])
                first_result = next(peek_iter)  # Peek first value only
                project_pk = first_result['project']
                project_info = self.client.get_project(project_pk)
                self.params['project_id'] = project_pk
                self.params['configuration'] = project_info.get('configuration', {})
                self.params['results'] = main_iter  # Keep original generator intact
            except (StopIteration, KeyError):
                self.params['configuration'] = {}
        # For the 'assignment' and 'task' targets, retrieve the project from the filter as before
        elif target in ['assignment', 'task'] and 'project' in self.params['filter']:
            project_pk = self.params['filter']['project']
            project_info = self.client.get_project(project_pk)
            self.params['configuration'] = project_info.get('configuration', {})

        export_items = handler.get_export_item(self.params['results'])
        storage = self.client.get_storage(self.params['storage'])
        pathlib_cwd = get_pathlib(storage, self.params['path'])
        return self.entrypoint(self.run, export_items, pathlib_cwd, **self.params)
