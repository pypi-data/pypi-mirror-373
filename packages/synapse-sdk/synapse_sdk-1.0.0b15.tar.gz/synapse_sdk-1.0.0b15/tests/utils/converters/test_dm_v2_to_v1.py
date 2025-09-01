import json

from synapse_sdk.utils.converters.dm.to_v1 import DMV2ToV1Converter


class TestDMV2ToV1Converter:
    """Test cases for DMV2ToV1Converter class."""

    def test_converter_initialization(self):
        """Test basic initialization of the converter."""
        converter = DMV2ToV1Converter()
        assert converter.new_dm_data == {}
        assert converter.annotations == {}
        assert converter.annotations_data == {}
        assert converter.extra == {}
        assert converter.relations == {}
        assert converter.annotation_groups == {}

    def test_converter_initialization_with_data(self):
        """Test initialization with data."""
        test_data = {'classification': {'bounding_box': ['test_class']}, 'images': []}
        converter = DMV2ToV1Converter(test_data)
        assert converter.new_dm_data == test_data

    def test_empty_data_conversion(self):
        """Test conversion with empty data."""
        converter = DMV2ToV1Converter({})
        result = converter.convert()

        expected_structure = {
            'extra': {},
            'relations': {},
            'annotations': {},
            'annotationsData': {},
            'annotationGroups': {},
        }
        assert result == expected_structure

    def test_image_data_conversion(self, dm_v2_image_fixture_path, dm_v1_image_fixture_path):
        """Test conversion of image data with multiple annotation types."""
        # Load test data from fixture files
        with open(dm_v2_image_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference (not used in assertions due to coordinate ID differences)
        # with open(dm_v1_image_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        # Verify structure
        assert 'extra' in result
        assert 'relations' in result
        assert 'annotations' in result
        assert 'annotationsData' in result
        assert 'annotationGroups' in result

        # Verify image_1 data
        assert 'image_1' in result['annotations']
        assert 'image_1' in result['annotationsData']
        assert len(result['annotations']['image_1']) == 5  # polygon, polyline, bbox, keypoint, segmentation

        # Test annotations structure
        annotations = result['annotations']['image_1']
        annotation_ids = [ann['id'] for ann in annotations]
        expected_ids = ['I5i-w35Bsg', '2w1dsVleoo', 'WDHHkCvwOv', 'cdv5pXK9Ui', 'pPDtBInDeV']

        for expected_id in expected_ids:
            assert expected_id in annotation_ids

        # Test specific annotation types
        polygon_ann = next(ann for ann in annotations if ann['id'] == 'I5i-w35Bsg')
        assert polygon_ann['tool'] == 'polygon'
        assert polygon_ann['classification']['class'] == 'polygon__attributes'
        assert not polygon_ann['isLocked']
        assert polygon_ann['isVisible']

        bbox_ann = next(ann for ann in annotations if ann['id'] == 'WDHHkCvwOv')
        assert bbox_ann['tool'] == 'bounding_box'
        assert bbox_ann['classification']['class'] == 'boundingbox'

        keypoint_ann = next(ann for ann in annotations if ann['id'] == 'cdv5pXK9Ui')
        assert keypoint_ann['tool'] == 'keypoint'
        assert keypoint_ann['shape'] == 'circle'  # Special attribute for keypoints

        # Test annotationsData structure
        annotations_data = result['annotationsData']['image_1']
        data_ids = [ann['id'] for ann in annotations_data]

        for expected_id in expected_ids:
            assert expected_id in data_ids

        # Test polygon coordinates conversion
        polygon_data = next(ann for ann in annotations_data if ann['id'] == 'I5i-w35Bsg')
        assert 'coordinate' in polygon_data
        assert isinstance(polygon_data['coordinate'], list)
        assert len(polygon_data['coordinate']) == 4  # 4 coordinate points

        # Check coordinate structure
        first_coord = polygon_data['coordinate'][0]
        assert 'x' in first_coord
        assert 'y' in first_coord
        assert 'id' in first_coord
        assert first_coord['x'] == 228
        assert first_coord['y'] == 962

        # Test bounding box coordinates conversion
        bbox_data = next(ann for ann in annotations_data if ann['id'] == 'WDHHkCvwOv')
        assert 'coordinate' in bbox_data
        bbox_coord = bbox_data['coordinate']
        assert bbox_coord['x'] == 296
        assert bbox_coord['y'] == 161
        assert bbox_coord['width'] == 349
        assert bbox_coord['height'] == 315

        # Test keypoint coordinates
        keypoint_data = next(ann for ann in annotations_data if ann['id'] == 'cdv5pXK9Ui')
        assert 'coordinate' in keypoint_data
        kp_coord = keypoint_data['coordinate']
        assert kp_coord['x'] == 896
        assert kp_coord['y'] == 1230

        # Test segmentation data
        segmentation_data = next(ann for ann in annotations_data if ann['id'] == 'pPDtBInDeV')
        assert 'pixel_indices' in segmentation_data
        assert isinstance(segmentation_data['pixel_indices'], list)
        assert len(segmentation_data['pixel_indices']) == 13

    def test_text_data_conversion(self, dm_v2_text_fixture_path, dm_v1_text_fixture_path):
        """Test conversion of text data with named entity and classification."""
        # Load test data from fixture files
        with open(dm_v2_text_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference
        # with open(dm_v1_text_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        # Verify structure
        assert 'text_1' in result['annotations']
        assert 'text_1' in result['annotationsData']

        # Test annotations
        annotations = result['annotations']['text_1']
        assert len(annotations) == 2  # named_entity and classification

        # Test named entity annotation
        named_entity_ann = next(ann for ann in annotations if ann['tool'] == 'named_entity')
        assert named_entity_ann['id'] == 'HMPbWKsbZs'
        assert named_entity_ann['classification']['class'] == 'namedentity'

        # Test classification annotation
        classification_ann = next(ann for ann in annotations if ann['tool'] == 'classification')
        assert classification_ann['id'] == 'lIrwyXW9sL'
        assert classification_ann['classification']['class'] == 'classification_attributes'

        # Test annotationsData
        annotations_data = result['annotationsData']['text_1']

        # Test named entity data
        named_entity_data = next(ann for ann in annotations_data if ann['id'] == 'HMPbWKsbZs')
        assert 'ranges' in named_entity_data
        assert 'content' in named_entity_data
        assert named_entity_data['content'] == 'A, 징역 6월·집행'

        # Test classification data
        classification_data = next(ann for ann in annotations_data if ann['id'] == 'lIrwyXW9sL')
        assert classification_data['id'] == 'lIrwyXW9sL'

    def test_video_data_conversion(self, dm_v2_video_fixture_path, dm_v1_video_fixture_path):
        """Test conversion of video data with segmentation."""
        # Load test data from fixture files
        with open(dm_v2_video_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference
        # with open(dm_v1_video_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        # Verify structure
        assert 'video_1' in result['annotations']
        assert 'video_1' in result['annotationsData']

        # Test video segmentation
        annotations = result['annotations']['video_1']
        segmentation_ann = annotations[0]
        assert segmentation_ann['tool'] == 'segmentation'
        assert segmentation_ann['id'] == 'N_VG-a4_rX'
        assert segmentation_ann['classification']['class'] == 'segmentation2'

        # Test video segmentation data
        annotations_data = result['annotationsData']['video_1']
        segmentation_data = annotations_data[0]
        assert segmentation_data['id'] == 'N_VG-a4_rX'
        assert 'section' in segmentation_data
        assert segmentation_data['section']['startFrame'] == 9
        assert segmentation_data['section']['endFrame'] == 17516

    def test_pcd_data_conversion(self, dm_v2_pcd_fixture_path, dm_v1_pcd_fixture_path):
        """Test conversion of PCD data with 3D bounding box."""
        # Load test data from fixture files
        with open(dm_v2_pcd_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference
        # with open(dm_v1_pcd_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        # Verify structure
        assert 'pcd_1' in result['annotations']
        assert 'pcd_1' in result['annotationsData']

        # Test 3D bounding box annotation
        annotations = result['annotations']['pcd_1']
        bbox_3d_ann = annotations[0]
        assert bbox_3d_ann['tool'] == '3d_bounding_box'
        assert bbox_3d_ann['id'] == 'fuTDKAmbYu'
        assert bbox_3d_ann['classification']['class'] == 'cuboid'

        # Test 3D bounding box data
        annotations_data = result['annotationsData']['pcd_1']
        bbox_3d_data = annotations_data[0]
        assert bbox_3d_data['id'] == 'fuTDKAmbYu'
        assert 'psr' in bbox_3d_data

        # Verify PSR structure
        psr = bbox_3d_data['psr']
        assert 'position' in psr
        assert 'scale' in psr
        assert 'rotation' in psr
        assert psr['position']['x'] == 0.9659228324890137
        assert psr['scale']['x'] == 25.914079308509823
        assert psr['rotation']['z'] == 1.5707963267948966

    def test_bounding_box_coordinate_conversion(self):
        """Test bounding box coordinate conversion from [x1, y1, width, height] to v1 format."""
        input_data = {
            'classification': {'bounding_box': ['test_class']},
            'images': [
                {
                    'bounding_box': [
                        {
                            'id': 'test_bbox',
                            'classification': 'test_class',
                            'attrs': [],
                            'data': [100, 200, 50, 75],  # [x1, y1, width, height]
                        }
                    ]
                }
            ],
        }

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        # Check annotation
        bbox_annotation = result['annotations']['image_1'][0]
        assert bbox_annotation['id'] == 'test_bbox'
        assert bbox_annotation['tool'] == 'bounding_box'
        assert bbox_annotation['classification']['class'] == 'test_class'

        # Check coordinate conversion
        bbox_data = result['annotationsData']['image_1'][0]
        assert bbox_data['coordinate']['x'] == 100
        assert bbox_data['coordinate']['y'] == 200
        assert bbox_data['coordinate']['width'] == 50
        assert bbox_data['coordinate']['height'] == 75

    def test_media_type_singularization(self):
        """Test media type singularization for media IDs."""
        converter = DMV2ToV1Converter()

        # Test singularization
        assert converter._singularize_media_type('images') == 'image'
        assert converter._singularize_media_type('videos') == 'video'
        assert converter._singularize_media_type('pcds') == 'pcd'
        assert converter._singularize_media_type('texts') == 'text'

    def test_classification_with_additional_attributes(self):
        """Test classification conversion with additional attributes."""
        input_data = {
            'classification': {'classification': ['main_class']},
            'texts': [
                {
                    'classification': [
                        {
                            'id': 'test_classification',
                            'classification': 'main_class',
                            'attrs': [
                                {'name': 'text', 'value': 'additional_text'},
                                {'name': 'single_radio', 'value': 'option1'},
                                {'name': 'multiple', 'value': ['opt1', 'opt2']},
                            ],
                            'data': {},
                        }
                    ]
                }
            ],
        }

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        classification_ann = result['annotations']['text_1'][0]
        assert classification_ann['classification']['class'] == 'main_class'
        assert classification_ann['classification']['text'] == 'additional_text'
        assert classification_ann['classification']['single_radio'] == 'option1'
        assert classification_ann['classification']['multiple'] == ['opt1', 'opt2']

    def test_unknown_tool_handling(self):
        """Test handling of unknown tool types."""
        input_data = {
            'classification': {'unknown_tool': ['test_class']},
            'images': [
                {
                    'unknown_tool': [
                        {
                            'id': 'unknown_tool_test',
                            'classification': 'test_class',
                            'attrs': [],
                            'data': {'some_data': 'test'},
                        }
                    ]
                }
            ],
        }

        converter = DMV2ToV1Converter(input_data)

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

        # Should still process structure correctly
        assert 'image_1' in result['annotations']
        assert 'image_1' in result['annotationsData']

    def test_multiple_media_items(self):
        """Test conversion with multiple media items."""
        input_data = {
            'classification': {'bounding_box': ['class1', 'class2']},
            'images': [
                {
                    'bounding_box': [
                        {
                            'id': 'img1_bbox',
                            'classification': 'class1',
                            'attrs': [],
                            'data': [0, 0, 10, 10],  # [x1, y1, width, height]
                        }
                    ]
                },
                {
                    'bounding_box': [
                        {
                            'id': 'img2_bbox',
                            'classification': 'class2',
                            'attrs': [],
                            'data': [20, 20, 50, 50],  # [x1, y1, width, height]
                        }
                    ]
                },
            ],
        }

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        # Should have 2 image items
        assert 'image_1' in result['annotations']
        assert 'image_2' in result['annotations']

        # Check both bounding boxes were processed
        bbox1_ann = result['annotations']['image_1'][0]
        bbox2_ann = result['annotations']['image_2'][0]

        assert bbox1_ann['id'] == 'img1_bbox'
        assert bbox2_ann['id'] == 'img2_bbox'

        bbox1_data = result['annotationsData']['image_1'][0]
        bbox2_data = result['annotationsData']['image_2'][0]

        assert bbox1_data['coordinate'] == {'x': 0, 'y': 0, 'width': 10, 'height': 10}
        assert bbox2_data['coordinate'] == {'x': 20, 'y': 20, 'width': 50, 'height': 50}

    def test_polyline_coordinate_conversion(self):
        """Test polyline coordinate conversion to v1 format."""
        input_data = {
            'classification': {'polyline': ['test_polyline']},
            'images': [
                {
                    'polyline': [
                        {
                            'id': 'test_polyline',
                            'classification': 'test_polyline',
                            'attrs': [],
                            'data': [[10, 20], [30, 40], [50, 60]],  # [x1, y1, x2, y2, x3, y3]
                        }
                    ]
                }
            ],
        }

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        polyline_data = result['annotationsData']['image_1'][0]
        coordinates = polyline_data['coordinate']

        assert len(coordinates) == 3  # 3 coordinate points
        assert coordinates[0]['x'] == 10
        assert coordinates[0]['y'] == 20
        assert coordinates[1]['x'] == 30
        assert coordinates[1]['y'] == 40
        assert coordinates[2]['x'] == 50
        assert coordinates[2]['y'] == 60

        # Each coordinate should have an ID
        for coord in coordinates:
            assert 'id' in coord

    def test_polygon_coordinate_conversion(self):
        """Test polygon coordinate conversion to v1 format."""
        input_data = {
            'classification': {'polygon': ['test_polygon']},
            'images': [
                {
                    'polygon': [
                        {
                            'id': 'test_polygon',
                            'classification': 'test_polygon',
                            'attrs': [],
                            'data': [100, 200, 300, 400, 500, 600, 700, 800],  # [x1, y1, x2, y2, x3, y3, x4, y4]
                        }
                    ]
                }
            ],
        }

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        polygon_data = result['annotationsData']['image_1'][0]
        coordinates = polygon_data['coordinate']

        assert len(coordinates) == 4  # 4 coordinate points
        assert coordinates[0]['x'] == 100
        assert coordinates[0]['y'] == 200
        assert coordinates[3]['x'] == 700
        assert coordinates[3]['y'] == 800

    def test_named_entity_conversion(self):
        """Test named entity data conversion."""
        input_data = {
            'classification': {'named_entity': ['test_entity']},
            'texts': [
                {
                    'named_entity': [
                        {
                            'id': 'test_entity',
                            'classification': 'test_entity',
                            'attrs': [],
                            'data': {'ranges': [{'start': 0, 'end': 5}], 'content': 'test text'},
                        }
                    ]
                }
            ],
        }

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        entity_data = result['annotationsData']['text_1'][0]
        assert entity_data['ranges'] == [{'start': 0, 'end': 5}]
        assert entity_data['content'] == 'test text'

    def test_prompt_data_conversion(self, dm_v2_prompt_fixture_path, dm_v1_prompt_fixture_path):
        """Test conversion of prompt data with classification and attributes."""
        # Load test data from fixture files
        with open(dm_v2_prompt_fixture_path, 'r') as f:
            input_data = json.load(f)

        # Load expected data for reference
        # with open(dm_v1_prompt_fixture_path, 'r') as f:
        #     expected_data = json.load(f)

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        # Verify structure
        assert 'text_1' in result['annotations']
        assert 'text_1' in result['annotationsData']

        # Test classification with attributes
        classification_ann = result['annotations']['text_1'][0]
        assert classification_ann['id'] == 'YJBNFvqv6j'
        assert classification_ann['tool'] == 'classification'
        assert classification_ann['classification']['class'] == 'classification_attributes'

        # Verify attributes were properly converted back
        classification_data = classification_ann['classification']
        assert 'text' in classification_data
        assert classification_data['text'] == 'ㅇㅁㄴㅇㅁㄴㅇㅁㄴㅇㅁㄴㅇㅁㄴㅇㅁㄴㅇ'
        assert 'multiple' in classification_data
        assert classification_data['multiple'] == ['multiple1']
        assert 'single_dropdown' in classification_data
        assert classification_data['single_dropdown'] == 'sinsingle_dropdown1'

    def test_empty_classification_section(self):
        """Test conversion when input has no classification section."""
        input_data = {
            'images': [
                {
                    'bounding_box': [
                        {'id': 'test_bbox', 'classification': 'test_class', 'attrs': [], 'data': [0, 0, 10, 10]}
                    ]
                }
            ]
        }

        converter = DMV2ToV1Converter(input_data)
        result = converter.convert()

        # Should still create proper structure
        assert 'image_1' in result['annotations']
        assert 'image_1' in result['annotationsData']
        assert len(result['annotations']['image_1']) == 1
