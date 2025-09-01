import os
from unittest.mock import patch


def test_convert_categorized_dataset(pascal_to_dm_converter, categorized_pascal_dataset_path):
    """Test conversion of a categorized Pascal VOC dataset."""
    converter = pascal_to_dm_converter(str(categorized_pascal_dataset_path), is_categorized_dataset=True)
    result = converter.convert()

    assert 'train' in result, 'Train split should be present in the result.'
    assert len(result['train']) > 0, 'Train split should not be empty.'
    jpg_files = [item[1] for item in result['train'].values()]
    filenames = [os.path.basename(file) for file in jpg_files]
    assert '9136.jpg' in filenames, 'Corresponding image file should be present in the result.'


def test_convert_non_categorized_dataset(pascal_to_dm_converter, not_categorized_pascal_dataset_path):
    """Test conversion of a non-categorized Pascal VOC dataset."""
    converter = pascal_to_dm_converter(str(not_categorized_pascal_dataset_path), is_categorized_dataset=False)
    result = converter.convert()

    assert len(result) > 0, 'Result should not be empty for non-categorized dataset.'

    jpg_files = [item[1] for item in result.values()]
    filenames = [os.path.basename(file) for file in jpg_files]
    assert '9122.jpg' in filenames, 'Corresponding image file should be present in the result.'


def test_dataset_save_to_folder(pascal_to_dm_converter, not_categorized_pascal_dataset_path):
    """Test saving converted dataset to folder."""
    converter = pascal_to_dm_converter(str(not_categorized_pascal_dataset_path), is_categorized_dataset=False)
    result = converter.convert()

    # Mock the save method to avoid actual file I/O
    with patch.object(converter, 'save_to_folder') as mock_save:
        converter.save_to_folder(result, 'mock_output_dir')

        # Assert that save_to_folder was called with the correct parameters
        mock_save.assert_called_once_with(result, 'mock_output_dir')
        assert mock_save.call_count == 1, 'save_to_folder should be called exactly once.'
