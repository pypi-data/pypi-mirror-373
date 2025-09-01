import json

from synapse_sdk.utils.converters.dm.from_v1 import DMV1ToV2Converter


class TestDMV1ToV2Converter:
    """Test cases for DMV1ToV2Converter class."""

    def test_converter_initialization(self):
        """Test basic initialization of the converter."""
        converter = DMV1ToV2Converter()
        assert converter.old_dm_data == {}
        assert converter.classification_info == {}
        assert converter.media_data == {}

    def test_converter_initialization_with_data(self):
        """Test initialization with data."""
        test_data = {'annotations': {'image_1': []}}
        converter = DMV1ToV2Converter(test_data)
        assert converter.old_dm_data == test_data

    def test_empty_data_conversion(self):
        """Test conversion with empty data."""
        converter = DMV1ToV2Converter({})
        result = converter.convert()

        assert result == {'classification': {}}

    def test_image_data_conversion(self, dm_v1_image_fixture_path, dm_v2_image_fixture_path):
        """Test conversion of image data with multiple annotation types."""
        # Load test data from fixture files
        with open(dm_v1_image_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference (not currently used in assertions)
        # with open(dm_v2_image_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        # Verify classification section
        assert 'classification' in result
        assert 'polygon' in result['classification']
        assert 'polyline' in result['classification']
        assert 'bounding_box' in result['classification']
        assert 'keypoint' in result['classification']
        assert 'segmentation' in result['classification']

        # Verify images section
        assert 'images' in result
        assert len(result['images']) == 1

        image_data = result['images'][0]

        # Test polygon conversion
        assert 'polygon' in image_data
        polygon = image_data['polygon'][0]
        assert polygon['id'] == 'I5i-w35Bsg'
        assert polygon['classification'] == 'polygon__attributes'
        assert polygon['data'] == [[228, 962], [275, 553], [743, 621], [505, 1111]]

        # Test polyline conversion
        assert 'polyline' in image_data
        polyline = image_data['polyline'][0]
        assert polyline['id'] == '2w1dsVleoo'
        assert polyline['classification'] == 'polyline_attributes'
        expected_polyline_data = [
            [990, 834],
            [1032, 1132],
            [1220, 736],
            [1147, 532],
            [1032, 481],
            [994, 783],
            [943, 881],
        ]
        assert polyline['data'] == expected_polyline_data

        # Test bounding box conversion
        assert 'bounding_box' in image_data
        bbox = image_data['bounding_box'][0]
        assert bbox['id'] == 'WDHHkCvwOv'
        assert bbox['classification'] == 'boundingbox'
        assert bbox['data'] == [296, 161, 349, 315]  # [x, y, width, height]

        # Test keypoint conversion
        assert 'keypoint' in image_data
        keypoint = image_data['keypoint'][0]
        assert keypoint['id'] == 'cdv5pXK9Ui'
        assert keypoint['classification'] == 'keypoint'
        assert keypoint['data'] == [896, 1230]

        # Test segmentation conversion
        assert 'segmentation' in image_data
        segmentation = image_data['segmentation'][0]
        assert segmentation['id'] == 'pPDtBInDeV'
        assert segmentation['classification'] == 'segmentation'
        expected_segmentation_data = [
            1667753,
            1667754,
            1667755,
            1667756,
            1667757,
            1667758,
            1667759,
            1667760,
            1667761,
            1667762,
            1667763,
            1667764,
            1667765,
        ]
        assert segmentation['data'] == expected_segmentation_data

    def test_text_data_conversion(self, dm_v1_text_fixture_path, dm_v2_text_fixture_path):
        """Test conversion of text data with named entity and classification."""
        # Load test data from fixture files
        with open(dm_v1_text_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference (not currently used in assertions)
        # with open(dm_v2_text_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        # Verify classification section
        assert 'classification' in result
        assert 'named_entity' in result['classification']
        assert 'classification' in result['classification']

        # Verify texts section
        assert 'texts' in result
        assert len(result['texts']) == 1

        text_data = result['texts'][0]

        # Test named entity conversion
        assert 'named_entity' in text_data
        named_entity = text_data['named_entity'][0]
        assert named_entity['id'] == 'HMPbWKsbZs'
        assert named_entity['classification'] == 'namedentity'
        assert 'ranges' in named_entity['data']
        assert 'content' in named_entity['data']
        assert named_entity['data']['content'] == 'A, 징역 6월·집행'

        # Test classification conversion
        assert 'classification' in text_data
        classification = text_data['classification'][0]
        assert classification['id'] == 'lIrwyXW9sL'
        assert classification['classification'] == 'classification_attributes'
        assert classification['data'] == {}

    def test_video_data_conversion(self, dm_v1_video_fixture_path, dm_v2_video_fixture_path):
        """Test conversion of video data with segmentation."""
        # Load test data from fixture files
        with open(dm_v1_video_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference (not currently used in assertions)
        # with open(dm_v2_video_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        # Verify classification section
        assert 'classification' in result
        assert 'segmentation' in result['classification']
        assert result['classification']['segmentation'] == ['segmentation2']

        # Verify videos section
        assert 'videos' in result
        assert len(result['videos']) == 1

        video_data = result['videos'][0]

        # Test video segmentation conversion
        assert 'segmentation' in video_data
        segmentation = video_data['segmentation'][0]
        assert segmentation['id'] == 'N_VG-a4_rX'
        assert segmentation['classification'] == 'segmentation2'
        assert segmentation['data']['startFrame'] == 9
        assert segmentation['data']['endFrame'] == 17516

    def test_pcd_data_conversion(self, dm_v1_pcd_fixture_path, dm_v2_pcd_fixture_path):
        """Test conversion of PCD data with 3D bounding box."""
        # Load test data from fixture files
        with open(dm_v1_pcd_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference (not currently used in assertions)
        # with open(dm_v2_pcd_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        # Verify classification section
        assert 'classification' in result
        assert '3d_bounding_box' in result['classification']
        assert result['classification']['3d_bounding_box'] == ['cuboid']

        # Verify pcds section
        assert 'pcds' in result
        assert len(result['pcds']) == 1

        pcd_data = result['pcds'][0]

        # Test 3D bounding box conversion
        assert '3d_bounding_box' in pcd_data
        bbox_3d = pcd_data['3d_bounding_box'][0]
        assert bbox_3d['id'] == 'fuTDKAmbYu'
        assert bbox_3d['classification'] == 'cuboid'
        assert 'scale' in bbox_3d['data']
        assert 'position' in bbox_3d['data']
        assert 'rotation' in bbox_3d['data']

        # Verify PSR data structure
        assert bbox_3d['data']['position']['x'] == 0.9659228324890137
        assert bbox_3d['data']['scale']['x'] == 25.914079308509823
        assert bbox_3d['data']['rotation']['z'] == 1.5707963267948966

    def test_bounding_box_coordinate_conversion(self):
        """Test bounding box coordinate conversion preserves [x, y, width, height] format."""
        input_data = {
            'annotations': {
                'image_1': [{'id': 'test_bbox', 'tool': 'bounding_box', 'classification': {'class': 'test_class'}}]
            },
            'annotationsData': {
                'image_1': [{'id': 'test_bbox', 'coordinate': {'x': 100, 'y': 200, 'width': 50, 'height': 75}}]
            },
        }

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        bbox = result['images'][0]['bounding_box'][0]
        assert bbox['data'] == [100, 200, 50, 75]  # [x, y, width, height]

    def test_media_type_extraction(self):
        """Test media type extraction from media IDs."""
        converter = DMV1ToV2Converter()

        # Test image type
        media_type, media_type_plural = converter._extract_media_type_info('image_1')
        assert media_type == 'image'
        assert media_type_plural == 'images'

        # Test video type
        media_type, media_type_plural = converter._extract_media_type_info('video_123')
        assert media_type == 'video'
        assert media_type_plural == 'videos'

        # Test pcd type
        media_type, media_type_plural = converter._extract_media_type_info('pcd_456')
        assert media_type == 'pcd'
        assert media_type_plural == 'pcds'

        # Test text type
        media_type, media_type_plural = converter._extract_media_type_info('text_789')
        assert media_type == 'text'
        assert media_type_plural == 'texts'

    def test_classification_with_additional_attributes(self):
        """Test classification conversion with additional attributes."""
        input_data = {
            'annotations': {
                'text_1': [
                    {
                        'id': 'test_classification',
                        'tool': 'classification',
                        'classification': {
                            'class': 'main_class',
                            'text': 'additional_text',
                            'single_radio': 'option1',
                            'multiple': ['opt1', 'opt2'],
                        },
                    }
                ]
            },
            'annotationsData': {'text_1': [{'id': 'test_classification'}]},
        }

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        classification = result['texts'][0]['classification'][0]
        assert classification['classification'] == 'main_class'

        # Check attributes
        attrs = classification['attrs']
        assert len(attrs) == 3

        attr_names = [attr['name'] for attr in attrs]
        assert 'text' in attr_names
        assert 'single_radio' in attr_names
        assert 'multiple' in attr_names

    def test_unknown_tool_handling(self):
        """Test handling of unknown tool types."""
        input_data = {
            'annotations': {
                'image_1': [
                    {'id': 'unknown_tool_test', 'tool': 'unknown_tool', 'classification': {'class': 'test_class'}}
                ]
            },
            'annotationsData': {'image_1': [{'id': 'unknown_tool_test', 'some_data': 'test'}]},
        }

        converter = DMV1ToV2Converter(input_data)

        # Capture print output to verify warning message
        import io
        import sys

        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = converter.convert()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Should print warning for unknown tool
        assert "Warning: Unknown tool type 'unknown_tool'" in output
        assert 'unknown_tool_test' in output

        # Should still process other data correctly
        assert 'classification' in result
        assert 'images' in result

    def test_multiple_media_items(self):
        """Test conversion with multiple media items."""
        input_data = {
            'annotations': {
                'image_1': [{'id': 'img1_bbox', 'tool': 'bounding_box', 'classification': {'class': 'class1'}}],
                'image_2': [{'id': 'img2_bbox', 'tool': 'bounding_box', 'classification': {'class': 'class2'}}],
            },
            'annotationsData': {
                'image_1': [{'id': 'img1_bbox', 'coordinate': {'x': 0, 'y': 0, 'width': 10, 'height': 10}}],
                'image_2': [{'id': 'img2_bbox', 'coordinate': {'x': 20, 'y': 20, 'width': 30, 'height': 30}}],
            },
        }

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        # Should have 2 image items
        assert len(result['images']) == 2

        # Check both bounding boxes were processed
        bbox1 = result['images'][0]['bounding_box'][0]
        bbox2 = result['images'][1]['bounding_box'][0]

        assert bbox1['id'] == 'img1_bbox'
        assert bbox2['id'] == 'img2_bbox'
        assert bbox1['data'] == [0, 0, 10, 10]
        assert bbox2['data'] == [20, 20, 30, 30]

    def test_duplicate_classification_filtering(self):
        """Test that duplicate classifications are filtered out."""
        input_data = {
            'annotations': {
                'image_1': [
                    {'id': 'bbox1', 'tool': 'bounding_box', 'classification': {'class': 'same_class'}},
                    {'id': 'bbox2', 'tool': 'bounding_box', 'classification': {'class': 'same_class'}},
                ]
            },
            'annotationsData': {
                'image_1': [
                    {'id': 'bbox1', 'coordinate': {'x': 0, 'y': 0, 'width': 10, 'height': 10}},
                    {'id': 'bbox2', 'coordinate': {'x': 20, 'y': 20, 'width': 30, 'height': 30}},
                ]
            },
        }

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        # Should only have one instance of "same_class" in classification
        assert len(result['classification']['bounding_box']) == 1
        assert result['classification']['bounding_box'][0] == 'same_class'

        # But should have both bounding boxes in the data
        assert len(result['images'][0]['bounding_box']) == 2

    def test_prompt_data_conversion(self, dm_v1_prompt_fixture_path, dm_v2_prompt_fixture_path):
        """Test conversion of prompt data with classification and attributes."""
        # Load test data from fixture files
        with open(dm_v1_prompt_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference (not currently used in assertions)
        # with open(dm_v2_prompt_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV1ToV2Converter(input_data)
        result = converter.convert()

        # Verify classification section
        assert 'classification' in result
        assert 'classification' in result['classification']
        assert result['classification']['classification'] == ['classification_attributes']

        # Verify texts section
        assert 'texts' in result
        assert len(result['texts']) == 1

        text_data = result['texts'][0]

        # Test classification conversion with attributes
        assert 'classification' in text_data
        classification = text_data['classification'][0]
        assert classification['id'] == 'YJBNFvqv6j'
        assert classification['classification'] == 'classification_attributes'
        assert classification['data'] == {}

        # Verify attributes were properly converted
        attrs = classification['attrs']
        assert len(attrs) == 3

        # Check each attribute
        attr_dict = {attr['name']: attr['value'] for attr in attrs}

        assert 'text' in attr_dict
        assert attr_dict['text'] == 'ㅇㅁㄴㅇㅁㄴㅇㅁㄴㅇㅁㄴㅇㅁㄴㅇㅁㄴㅇ'

        assert 'multiple' in attr_dict
        assert attr_dict['multiple'] == ['multiple1']

        assert 'single_dropdown' in attr_dict
        assert attr_dict['single_dropdown'] == 'sinsingle_dropdown1'

        # Note: single_radio is empty string in v1, so it should be filtered out in attrs
        # since empty strings are not included according to the converter logic
