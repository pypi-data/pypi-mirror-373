from pathlib import Path

import pytest


@pytest.fixture
def yolo_to_dm_converter():
    """Return an instance of YOLOToDMConverter."""
    from synapse_sdk.utils.converters.yolo.to_dm import YOLOToDMConverter

    return YOLOToDMConverter


@pytest.fixture
def yolo_dataset_path():
    """Return the path to YOLO dataset fixtures."""
    return Path(__file__).parent / 'data_types' / 'image' / 'yolo'


@pytest.fixture
def categorized_yolo_dataset_path(yolo_dataset_path):
    """Return the path to categorized YOLO dataset fixtures."""
    return yolo_dataset_path / 'categorized'


@pytest.fixture
def not_categorized_yolo_dataset_path(yolo_dataset_path):
    """Return the path to non-categorized YOLO dataset fixtures."""
    return yolo_dataset_path / 'not_categorized'


@pytest.fixture
def sample_yolo_annotation():
    """Return a sample YOLO annotation."""
    return {
        'image_id': 'image1',
        'annotations': [
            {'class_id': 0, 'bbox': [0.5, 0.5, 0.2, 0.3]},
            {'class_id': 1, 'bbox': [0.7, 0.8, 0.1, 0.1]},
        ],
        'classes': ['car', 'person'],
    }
