import pytest

from synapse_sdk.loggers import BaseLogger


def test_base_logger_with_metrics_categories_setup_categories_success():
    base_logger = BaseLogger(
        metrics_categories={
            'category_1': {
                'stand_by': 0,
                'success': 0,
                'failed': 0,
            },
            'category_2': {
                'stand_by': 0,
                'success': 0,
                'failed': 0,
            },
        }
    )

    assert 'category_1' in base_logger.metrics_record['categories']
    assert 'category_2' in base_logger.metrics_record['categories']


def test_base_logger_set_metrics_success():
    base_logger = BaseLogger()
    base_logger.set_metrics({'test_metric': 'value'}, 'category_name')

    assert base_logger.metrics_record['categories']['category_name'] == {'test_metric': 'value'}


def test_base_logger_set_metrics_with_empty_category_failed():
    base_logger = BaseLogger()

    with pytest.raises(AssertionError, match='A category argument must be a non-empty string.'):
        base_logger.set_metrics({'test_metric': 'value'}, '')


def test_base_logger_set_metrics_with_not_dict_value_failed():
    base_logger = BaseLogger()
    with pytest.raises(AssertionError, match='A value argument must be a dictionary, but got str.'):
        base_logger.set_metrics('not_dict', 'category_name')
