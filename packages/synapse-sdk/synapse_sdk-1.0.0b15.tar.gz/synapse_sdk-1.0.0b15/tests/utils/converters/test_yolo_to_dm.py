import os
from unittest.mock import patch


def test_convert_categorized_dataset(yolo_to_dm_converter, categorized_yolo_dataset_path):
    """Test conversion of a categorized YOLO dataset."""
    converter = yolo_to_dm_converter(str(categorized_yolo_dataset_path), is_categorized_dataset=True)
    result = converter.convert()

    assert 'train' in result, 'Train split should be present in the result.'
    assert len(result['train']) > 0, 'Train split should not be empty.'
    jpg_files = [item[1] for item in result['train'].values()]
    filenames = [os.path.basename(file) for file in jpg_files]
    assert '13782.jpg' in filenames, 'Corresponding image file should be present in the result.'


def test_convert_non_categorized_dataset(yolo_to_dm_converter, not_categorized_yolo_dataset_path):
    """Test conversion of a non-categorized YOLO dataset."""
    converter = yolo_to_dm_converter(str(not_categorized_yolo_dataset_path), is_categorized_dataset=False)
    result = converter.convert()

    assert len(result) > 0, 'Result should not be empty for non-categorized dataset.'

    jpg_files = [item[1] for item in result.values()]
    filenames = [os.path.basename(file) for file in jpg_files]
    assert '25332.jpg' in filenames, 'Corresponding image file should be present in the result.'


def test_dataset_save_to_folder(yolo_to_dm_converter, not_categorized_yolo_dataset_path):
    """Test saving converted dataset to folder."""
    temp_output_dir = '/tmp/test_output'
    converter = yolo_to_dm_converter(str(not_categorized_yolo_dataset_path), is_categorized_dataset=False)
    converter.save_to_folder(temp_output_dir)

    with patch('shutil.copy') as mock_copy, patch('builtins.open', create=True) as mock_open:
        converter.save_to_folder(temp_output_dir)

        mock_copy.assert_called()
        mock_open.assert_called()
