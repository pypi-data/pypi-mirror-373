import datetime
import time
from typing import Any, Dict

from synapse_sdk.clients.exceptions import ClientError


class BaseLogger:
    """Base class for logging progress and events.

    Args:
        progress_record(dict): Progress record to track the progress of a task.
        progress_categories: dict | None: List of categories for progress tracking.
        metrics_categories: dict | None: List of categories for metrics tracking.
        current_progress_category: str | None: Current progress category.
        time_begin_per_category(dict): Dictionary to track the start time for each category.
        metrics_record(dict): Dictionary to record metrics.
    """

    progress_record = {}
    metrics_record = {}
    progress_categories = None
    metrics_categories = None
    current_progress_category = None
    time_begin_per_category = {}

    def __init__(self, progress_categories=None, metrics_categories=None):
        # Setup progress categories
        self.progress_categories = progress_categories
        if progress_categories:
            self.progress_record['categories'] = progress_categories

        # Setup metrics categories
        self.metrics_categories = metrics_categories
        if metrics_categories:
            self.metrics_record['categories'] = metrics_categories

    def set_progress(self, current: int, total: int, category: str | None = None):
        """Set progress for plugin run.

        Args:
            current(int): current progress value
            total(int): total progress value
            category(str | None): progress category
        """
        assert 0 <= current <= total and total > 0
        assert category is not None or 'categories' not in self.progress_record

        percent = (current / total) * 100
        percent = round(percent, 2)
        # TODO current 0 으로 시작하지 않아도 작동되도록 수정
        if current == 0:
            self.time_begin_per_category[category] = time.time()
            time_remaining = None
        else:
            seconds_per_item = (time.time() - self.time_begin_per_category[category]) / current
            time_remaining = round(seconds_per_item * (total - current), 2)

        current_progress = {'percent': percent, 'time_remaining': time_remaining}

        if category:
            self.current_progress_category = category
            self.progress_record['categories'][category].update(current_progress)
        else:
            self.progress_record.update(current_progress)

    def get_current_progress(self):
        categories = self.progress_record.get('categories')

        if categories:
            category_progress = None

            overall = 0
            for category, category_record in categories.items():
                if category == self.current_progress_category:
                    break
                overall += category_record['proportion']

            category_record = categories[self.current_progress_category]
            category_percent = category_record.get('percent', 0)
            if not category_progress and 'percent' in category_record:
                category_progress = {
                    'category': self.current_progress_category,
                    'percent': category_percent,
                    'time_remaining': category_record.get('time_remaining'),
                }
            if category_percent > 0:
                overall += round(category_record['proportion'] / 100 * category_percent, 2)
            progress = {'overall': overall, **category_progress}
        else:
            progress = {
                'overall': self.progress_record.get('percent'),
                'time_remaining': self.progress_record.get('time_remaining'),
            }

        return progress

    def set_metrics(self, value: Dict[Any, Any], category: str):
        """Set metrics for plugin run.

        * Metrics which are representing the progress of the plugin run should be set in the metrics_record.

        Args:
            value(Dict[Any, Any]): metrics value
            category(str): metrics category
        """
        assert category is not None and category != '', 'A category argument must be a non-empty string.'
        assert isinstance(value, dict), f'A value argument must be a dictionary, but got {type(value).__name__}.'

        if 'categories' not in self.metrics_record:
            self.metrics_record['categories'] = {}

        self.metrics_record['categories'].setdefault(category, {}).update(value)

    def log(self, action, data, file=None):
        raise NotImplementedError


class ConsoleLogger(BaseLogger):
    def set_progress(self, current, total, category=None):
        super().set_progress(current, total, category=category)
        print(self.get_current_progress())

    def set_metrics(self, value: Dict[Any, Any], category: str):
        super().set_metrics(value, category)
        print(self.metrics_record)

    def log(self, action, data, file=None):
        print(action, data)


class BackendLogger(BaseLogger):
    logs_queue = []
    client = None
    job_id = None

    def __init__(self, client, job_id, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.job_id = job_id

    def set_progress(self, current, total, category=None):
        super().set_progress(current, total, category=category)
        try:
            progress_record = {
                'record': self.progress_record,
                'current_progress': self.get_current_progress(),
            }
            self.client.update_job(self.job_id, data={'progress_record': progress_record})
        except ClientError:
            pass

    def set_metrics(self, value: Dict[Any, Any], category: str):
        super().set_metrics(value, category)
        try:
            metrics_record = {
                'record': self.metrics_record,
            }
            self.client.update_job(self.job_id, data={'metrics_record': metrics_record})
        except ClientError:
            pass

    def log(self, event, data, file=None):
        print(event, data)

        log = {
            'event': event,
            'data': data,
            'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'job': self.job_id,
        }
        if file:
            log['file'] = file

        self.logs_queue.append(log)

        try:
            self.client.create_logs(self.logs_queue)
            self.logs_queue.clear()
        except ClientError as e:
            print(e)
