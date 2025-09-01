import re
from unittest.mock import patch

import pytest


class TestDMToYOLOConverter:
    """Test cases for DMToYOLOConverter class."""

    def test_converter_initialization(self, yolo_from_dm_converter_class, not_categorized_dataset_path):
        """Test basic initialization of the YOLO converter."""
        converter = yolo_from_dm_converter_class(str(not_categorized_dataset_path))

        assert converter.root_dir == str(not_categorized_dataset_path)
        assert converter.is_categorized_dataset is False
        assert converter.class_names == []
        assert converter.class_map == {}

    def test_get_all_classes(self, yolo_from_dm_converter_class, categorized_dataset_path):
        """Test collecting all unique class names."""
        converter = yolo_from_dm_converter_class(str(categorized_dataset_path), is_categorized_dataset=True)
        splits = converter._validate_splits(required_splits=['train', 'valid'], optional_splits=['test'])
        classes = converter.get_all_classes(list(splits.values()))

        assert 'a' in classes
        assert len(classes) == 1

    def test_polygon_to_bbox(self, yolo_from_dm_converter_class):
        """Test polygon to bounding box conversion."""
        converter = yolo_from_dm_converter_class('/dummy/path')
        polygon = [[0, 0], [10, 0], [10, 10], [0, 10]]
        bbox = converter.polygon_to_bbox(polygon)

        assert bbox == [5.0, 5.0, 10, 10]

    def test_keypoints_to_yolo_string(self, yolo_from_dm_converter_class):
        """Test keypoints to YOLO format string conversion."""
        converter = yolo_from_dm_converter_class('/dummy/path')
        keypoints = [[100, 200, 2], [300, 400, 1]]
        result = converter.keypoints_to_yolo_string(keypoints, 1000, 1000)

        assert result == '0.100000 0.200000 2 0.300000 0.400000 1'

    def test_polygon_to_yolo_string(self, yolo_from_dm_converter_class):
        """Test polygon to YOLO format string conversion."""
        converter = yolo_from_dm_converter_class('/dummy/path')
        polygon = [[0, 0], [10, 0], [10, 10], [0, 10]]
        yolo_str = converter.polygon_to_yolo_string(polygon, 100, 100)

        assert yolo_str == '0.000000 0.000000 0.100000 0.000000 0.100000 0.100000 0.000000 0.100000'

    def test_convert_split_dir_without_class_map(self, yolo_from_dm_converter_class, categorized_dataset_path):
        """Test conversion of a split directory without class_map initialized."""
        converter = yolo_from_dm_converter_class(str(categorized_dataset_path), is_categorized_dataset=True)
        splits = converter._validate_splits(required_splits=['train', 'valid'], optional_splits=['test'])

        with pytest.raises(
            ValueError,
            match=re.escape('class_map is not initialized. Ensure get_all_classes() is called before this method.'),
        ):
            converter._convert_split_dir(splits['train'], 'train')

    def test_convert_root_dir(self, yolo_from_dm_converter_class, not_categorized_dataset_path):
        """Test conversion of a non-categorized dataset."""
        converter = yolo_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.class_map = {'car': 0}

        with (
            patch('builtins.open', create=True) as mock_open,
            patch.object(converter, 'get_image_size') as mock_img_size,
        ):
            mock_open.return_value.__enter__.return_value.read.return_value = (
                '{"images": [{"bounding_box": [{"classification": "car", "data": [0, 0, 100, 100]}]}]}'
            )
            mock_img_size.return_value = (1000, 1000)

            entries = converter._convert_root_dir()

        assert len(entries) > 0
        assert entries[0]['label_lines'][0].startswith('0')

    def test_save_to_folder(self, yolo_from_dm_converter_class, not_categorized_dataset_path, temp_output_dir):
        """Test saving converted YOLO data to folder."""
        converter = yolo_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.converted_data = [
            {
                'img_path': '/dummy/path.jpg',
                'img_name': 'path.jpg',
                'label_name': 'path.txt',
                'label_lines': ['0 0.5 0.5 1.0 1.0'],
            }
        ]

        with patch('shutil.copy') as mock_copy, patch('builtins.open', create=True) as mock_open:
            converter.save_to_folder(temp_output_dir)

            mock_copy.assert_called()
            mock_open.assert_called()

    def test_dataset_yaml_content(self, yolo_from_dm_converter_class, not_categorized_dataset_path):
        """Test dataset.yaml content generation."""
        converter = yolo_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.convert()
        assert 'nc: 1' in converter.dataset_yaml_content
        assert "names: ['a']" in converter.dataset_yaml_content
