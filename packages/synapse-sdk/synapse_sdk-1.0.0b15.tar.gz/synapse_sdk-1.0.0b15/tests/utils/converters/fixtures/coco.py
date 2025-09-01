from pathlib import Path

import pytest


@pytest.fixture
def coco_to_dm_converter():
    """Return an instance of COCOToDMConverter."""
    from synapse_sdk.utils.converters.coco.to_dm import COCOToDMConverter

    return COCOToDMConverter


@pytest.fixture
def fixtures_root():
    """Return the root directory of test fixtures."""
    return Path(__file__).parent


@pytest.fixture
def coco_dataset_path(fixtures_root):
    """Return the path to COCO dataset fixtures."""
    return fixtures_root / 'data_types' / 'image' / 'coco'


@pytest.fixture
def categorized_coco_dataset_path(coco_dataset_path):
    """Return the path to categorized COCO dataset fixtures."""
    return coco_dataset_path / 'categorized'


@pytest.fixture
def not_categorized_coco_dataset_path(coco_dataset_path):
    """Return the path to non-categorized COCO dataset fixtures."""
    return coco_dataset_path / 'not_categorized'
