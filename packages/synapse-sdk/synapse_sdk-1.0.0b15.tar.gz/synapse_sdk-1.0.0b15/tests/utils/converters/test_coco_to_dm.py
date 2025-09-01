import json
import os

import pytest


def test_categorized_conversion(coco_to_dm_converter, categorized_coco_dataset_path):
    """Test conversion of categorized COCO dataset."""
    converter = coco_to_dm_converter(str(categorized_coco_dataset_path), is_categorized_dataset=True)
    result = converter.convert()

    assert isinstance(result, dict)
    assert 'train' in result
    assert 'valid' in result
    assert all(isinstance(data, dict) for data in result.values())
    jpg_files = [item[1] for item in result['train'].values()]
    filenames = [os.path.basename(file) for file in jpg_files]
    assert 'new_dm_data4.jpg' in filenames, 'Corresponding image file should be present in the result.'


def test_not_categorized_conversion(coco_to_dm_converter, not_categorized_coco_dataset_path):
    """Test conversion of non-categorized COCO dataset."""
    converter = coco_to_dm_converter(str(not_categorized_coco_dataset_path), is_categorized_dataset=False)
    result = converter.convert()

    assert isinstance(result, dict)
    assert len(result) > 0
    jpg_files = [item[1] for item in result.values()]
    filenames = [os.path.basename(file) for file in jpg_files]
    assert 'new_dm_data1.jpg' in filenames, 'Corresponding image file should be present in the result.'


def test_missing_annotations(coco_to_dm_converter, tmp_path):
    """Test handling of missing annotations.json."""
    converter = coco_to_dm_converter(str(tmp_path), is_categorized_dataset=False)

    with pytest.raises(FileNotFoundError, match='annotations.json not found'):
        converter.convert()


def test_invalid_dataset_type(coco_to_dm_converter, tmp_path):
    """Test handling of unsupported dataset type."""
    annotations_path = tmp_path / 'annotations.json'
    annotations_data = {'type': 'unsupported'}
    annotations_path.write_text(json.dumps(annotations_data), encoding='utf-8')

    converter = coco_to_dm_converter(str(tmp_path), is_categorized_dataset=False)

    with pytest.raises(ValueError, match='Unsupported dataset type'):
        converter.convert()
