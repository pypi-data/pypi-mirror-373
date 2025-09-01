from pathlib import Path

import pytest


@pytest.fixture
def pascal_to_dm_converter():
    """Return an instance of PascalToDMConverter."""
    from synapse_sdk.utils.converters.pascal.to_dm import PascalToDMConverter

    return PascalToDMConverter


@pytest.fixture
def fixtures_root():
    """Return the root directory of test fixtures."""
    return Path(__file__).parent


@pytest.fixture
def pascal_dataset_path(fixtures_root):
    """Return the path to Pascal dataset fixtures."""
    return fixtures_root / 'data_types' / 'image' / 'pascal'


@pytest.fixture
def categorized_pascal_dataset_path(pascal_dataset_path):
    """Return the path to categorized Pascal dataset fixtures."""
    return pascal_dataset_path / 'categorized'


@pytest.fixture
def not_categorized_pascal_dataset_path(pascal_dataset_path):
    """Return the path to non-categorized Pascal dataset fixtures."""
    return pascal_dataset_path / 'not_categorized'
