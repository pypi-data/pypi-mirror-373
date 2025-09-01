import json
import os
from unittest.mock import MagicMock, patch

import pytest


class TestDMToCOCOConverter:
    """Test cases for DMToCOCOConverter class."""

    def test_converter_initialization(self, coco_from_dm_converter_class, not_categorized_dataset_path):
        """Test basic initialization of the converter."""
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))

        assert converter.root_dir == str(not_categorized_dataset_path)
        assert converter.data_type == 'img'
        assert converter.is_categorized_dataset is False
        assert converter.info_dict is not None
        assert converter.licenses_list is not None

    def test_converter_initialization_categorized(self, coco_from_dm_converter_class, categorized_dataset_path):
        """Test initialization with categorized dataset."""
        converter = coco_from_dm_converter_class(str(categorized_dataset_path), is_categorized_dataset=True)

        assert converter.root_dir == str(categorized_dataset_path)
        assert converter.is_categorized_dataset is True

    def test_default_info(self, coco_from_dm_converter_class):
        """Test default info dictionary creation."""
        converter = coco_from_dm_converter_class('/dummy/path')
        info = converter.info_dict

        assert 'description' in info
        assert 'version' in info
        assert 'year' in info
        assert 'date_created' in info
        assert info['description'] == 'Converted from DM format'

    def test_default_licenses(self, coco_from_dm_converter_class):
        """Test default licenses list creation."""
        converter = coco_from_dm_converter_class('/dummy/path')
        licenses = converter.licenses_list

        assert len(licenses) == 1
        assert licenses[0]['id'] == 1
        assert licenses[0]['name'] == 'Unknown'

    def test_reset_state(self, coco_from_dm_converter_class, not_categorized_dataset_path):
        """Test state reset functionality."""
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.reset_state()

        assert converter.coco_dict is None
        assert converter.category_name_to_id == {}
        assert converter.annotation_id == 1
        assert converter.img_id == 1

    def test_poly_to_bbox(self, coco_from_dm_converter_class):
        """Test polygon to bounding box conversion."""
        converter = coco_from_dm_converter_class('/dummy/path')
        poly = [[0, 0], [10, 0], [10, 10], [0, 10]]
        bbox = converter._poly_to_bbox(poly)

        assert bbox == [0, 0, 10, 10]

    def test_poly_to_segmentation(self, coco_from_dm_converter_class):
        """Test polygon to segmentation conversion."""
        converter = coco_from_dm_converter_class('/dummy/path')
        poly = [[0, 0], [10, 0], [10, 10], [0, 10]]
        seg = converter._poly_to_segmentation(poly)

        assert seg == [[0, 0, 10, 0, 10, 10, 0, 10]]

    def test_get_or_create_category(self, coco_from_dm_converter_class, not_categorized_dataset_path):
        """Test category creation and retrieval."""
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.reset_state()
        converter.coco_dict = {'categories': []}

        # Create new category
        cat_id = converter._get_or_create_category('car')
        assert cat_id == 1
        assert len(converter.coco_dict['categories']) == 1
        assert converter.coco_dict['categories'][0]['name'] == 'car'

        # Retrieve existing category
        cat_id_2 = converter._get_or_create_category('car')
        assert cat_id_2 == 1
        assert len(converter.coco_dict['categories']) == 1  # No new category added

    def test_process_polylines(self, coco_from_dm_converter_class, not_categorized_dataset_path):
        """Test polyline processing."""
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.reset_state()
        converter.coco_dict = {'annotations': [], 'categories': []}
        converter.img_id = 1

        anns = {'polyline': [{'classification': 'car', 'data': [[0, 0], [10, 0], [10, 10], [0, 10]]}]}

        converter._process_polylines(anns)

        assert len(converter.coco_dict['annotations']) == 1
        assert len(converter.coco_dict['categories']) == 1
        assert converter.coco_dict['annotations'][0]['category_id'] == 1
        assert converter.coco_dict['categories'][0]['name'] == 'car'

    def test_process_bboxes(self, coco_from_dm_converter_class, not_categorized_dataset_path):
        """Test bounding box processing."""
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.reset_state()
        converter.coco_dict = {'annotations': [], 'categories': []}
        converter.img_id = 1

        anns = {'bounding_box': [{'classification': 'person', 'data': [100, 100, 200, 300]}]}

        converter._process_bboxes(anns)

        assert len(converter.coco_dict['annotations']) == 1
        assert len(converter.coco_dict['categories']) == 1
        assert converter.coco_dict['annotations'][0]['category_id'] == 1
        assert converter.coco_dict['categories'][0]['name'] == 'person'

    def test_process_keypoints(self, coco_from_dm_converter_class, not_categorized_dataset_path):
        """Test keypoint processing."""
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.reset_state()
        converter.coco_dict = {'annotations': [], 'categories': []}
        converter.img_id = 1

        anns = {
            'keypoint': [{'classification': 'nose', 'data': [150, 200]}, {'classification': 'eye', 'data': [160, 180]}]
        }

        converter._process_keypoints(anns)

        assert len(converter.coco_dict['annotations']) == 1
        assert len(converter.coco_dict['categories']) == 1
        assert converter.coco_dict['annotations'][0]['num_keypoints'] == 2
        assert 'nose' in converter.coco_dict['categories'][0]['keypoints']
        assert 'eye' in converter.coco_dict['categories'][0]['keypoints']

    @patch('PIL.Image.open')
    def test_image_info(self, mock_image_open, coco_from_dm_converter_class, not_categorized_dataset_path):
        """Test image info extraction."""
        # Mock PIL Image
        mock_img = MagicMock()
        mock_img.size = (1920, 1080)
        mock_image_open.return_value.__enter__.return_value = mock_img

        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))
        converter.img_id = 1

        img_info = converter._image_info('/dummy/path.jpg')

        assert img_info['id'] == 1
        assert img_info['width'] == 1920
        assert img_info['height'] == 1080
        assert img_info['license'] == 1

    def test_convert_single_split_no_files(self, coco_from_dm_converter_class, temp_output_dir):
        """Test conversion with no matching files."""
        converter = coco_from_dm_converter_class(temp_output_dir)

        with pytest.raises(FileNotFoundError):
            converter._convert_single_split()

    def test_convert_non_categorized_dataset(self, coco_from_dm_converter_class, not_categorized_dataset_path):
        """Test conversion of non-categorized dataset."""
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))

        # Mock the _find_json_file_pairs method to return test data
        with patch.object(converter, '_find_json_file_pairs') as mock_find_pairs:
            mock_find_pairs.return_value = [
                ('/dummy/json1.json', '/dummy/img1.jpg'),
                ('/dummy/json2.json', '/dummy/img2.jpg'),
            ]

            with patch.object(converter, '_image_info') as mock_img_info:
                mock_img_info.return_value = {'id': 1, 'width': 100, 'height': 100, 'license': 1}

                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                        'images': [{'polyline': []}]
                    })

                    result = converter.convert()

                    assert 'images' in result
                    assert 'annotations' in result
                    assert 'categories' in result
                    assert 'info' in result
                    assert 'licenses' in result

    def test_convert_categorized_dataset(self, coco_from_dm_converter_class, categorized_dataset_path):
        """Test conversion of categorized dataset."""
        converter = coco_from_dm_converter_class(str(categorized_dataset_path), is_categorized_dataset=True)

        # Mock the _validate_splits method
        with patch.object(converter, '_validate_splits') as mock_validate:
            mock_validate.return_value = {'train': 'train_path', 'valid': 'valid_path'}

            with patch.object(converter, '_convert_single_split') as mock_convert:
                mock_convert.return_value = {'images': [], 'annotations': [], 'categories': []}

                result = converter.convert()

                assert 'train' in result
                assert 'valid' in result
                assert mock_convert.call_count == 2

    def test_save_to_folder(self, coco_from_dm_converter_class, not_categorized_dataset_path, temp_output_dir):
        """Test saving converted data to folder."""
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))

        # Mock the convert method
        with patch.object(converter, 'convert') as mock_convert:
            mock_convert.return_value = {
                'images': [{'id': 1, 'file_name': 'test.jpg'}],
                'annotations': [],
                'categories': [],
            }

            # Mock the _save_annotations_and_images method
            with patch.object(converter, '_save_annotations_and_images') as mock_save:
                converter.save_to_folder(temp_output_dir)

                mock_save.assert_called_once()

    def test_supported_types(self, coco_from_dm_converter_class):
        """Test supported file types."""
        converter = coco_from_dm_converter_class('/dummy/path')

        assert 'img' in converter.SUPPORTED_TYPES
        assert '.jpg' in converter.SUPPORTED_TYPES['img']
        assert '.jpeg' in converter.SUPPORTED_TYPES['img']
        assert '.png' in converter.SUPPORTED_TYPES['img']

    def test_find_json_file_pairs(self, coco_from_dm_converter_class, temp_output_dir):
        """Test JSON file pairing functionality."""
        converter = coco_from_dm_converter_class(temp_output_dir)

        # Create test files
        os.makedirs(os.path.join(temp_output_dir, 'json'), exist_ok=True)
        os.makedirs(os.path.join(temp_output_dir, 'original_files'), exist_ok=True)

        # Create matching files
        with open(os.path.join(temp_output_dir, 'json', 'test1.json'), 'w') as f:
            f.write('{}')
        with open(os.path.join(temp_output_dir, 'original_files', 'test1.jpg'), 'w') as f:
            f.write('test')

        # Create non-matching files
        with open(os.path.join(temp_output_dir, 'json', 'test2.json'), 'w') as f:
            f.write('{}')
        with open(os.path.join(temp_output_dir, 'original_files', 'test3.jpg'), 'w') as f:
            f.write('test')

        pairs = converter._find_json_file_pairs()

        # Should only return matching pairs
        assert len(pairs) == 1
        assert pairs[0][0].endswith('test1.json')
        assert pairs[0][1].endswith('test1.jpg')


class TestDMToCOCOConverterIntegration:
    """Integration tests for DMToCOCOConverter."""

    def test_full_conversion_workflow(
        self, coco_from_dm_converter_class, not_categorized_dataset_path, temp_output_dir
    ):
        """Test complete conversion workflow with real files."""
        # This test would require actual test data files
        # For now, we'll test the structure and basic functionality
        converter = coco_from_dm_converter_class(str(not_categorized_dataset_path))

        assert converter is not None
        assert hasattr(converter, 'convert')
        assert hasattr(converter, 'save_to_folder')

    def test_error_handling_invalid_json(self, coco_from_dm_converter_class, temp_output_dir):
        """Test error handling with invalid JSON files."""
        converter = coco_from_dm_converter_class(temp_output_dir)

        # Create invalid JSON file
        os.makedirs(os.path.join(temp_output_dir, 'json'), exist_ok=True)
        os.makedirs(os.path.join(temp_output_dir, 'original_files'), exist_ok=True)

        with open(os.path.join(temp_output_dir, 'json', 'invalid.json'), 'w') as f:
            f.write('invalid json content')
        with open(os.path.join(temp_output_dir, 'original_files', 'invalid.jpg'), 'w') as f:
            f.write('test')

        with patch.object(converter, '_find_json_file_pairs') as mock_find_pairs:
            mock_find_pairs.return_value = [
                (
                    os.path.join(temp_output_dir, 'json', 'invalid.json'),
                    os.path.join(temp_output_dir, 'original_files', 'invalid.jpg'),
                )
            ]

            # Should handle the error gracefully and continue
            result = converter._convert_single_split()
            assert result is not None
