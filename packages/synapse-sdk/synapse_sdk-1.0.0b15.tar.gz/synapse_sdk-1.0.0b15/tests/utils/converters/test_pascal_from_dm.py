import xml.etree.ElementTree as ET
from pathlib import Path


class TestFromDMToPascalConverter:
    """Test cases for FromDMToPascalConverter class."""

    def test_converter_initialization(self, pascal_from_dm_converter_class, not_categorized_dataset_path):
        """Test basic initialization of the Pascal converter."""
        converter = pascal_from_dm_converter_class(str(not_categorized_dataset_path))

        assert converter.root_dir == str(not_categorized_dataset_path)
        assert converter.is_categorized_dataset is False
        assert converter.class_names == set()

    def test_find_image_for_base(self, pascal_from_dm_converter_class, tmp_path):
        """Test finding image for a given base name."""
        img_dir = tmp_path / 'images'
        img_dir.mkdir()
        (img_dir / 'test.jpg').touch()

        converter = pascal_from_dm_converter_class(str(tmp_path))
        img_path = converter.find_image_for_base(str(img_dir), 'test')

        assert img_path == str(img_dir / 'test.jpg')

    def test_build_pascal_xml(self, pascal_from_dm_converter_class):
        """Test building Pascal VOC XML."""
        converter = pascal_from_dm_converter_class('/dummy/path')
        img_filename = 'test.jpg'
        img_size = (100, 200, 3)
        objects = [{'name': 'car', 'xmin': 10, 'ymin': 20, 'xmax': 50, 'ymax': 60}]

        xml_tree = converter.build_pascal_xml(img_filename, img_size, objects)
        root = xml_tree.getroot()

        assert root.find('filename').text == img_filename
        assert root.find('size/width').text == '100'
        assert root.find('object/name').text == 'car'

    def test_parse_dm_annotations(self, pascal_from_dm_converter_class):
        """Test parsing DM annotations."""
        converter = pascal_from_dm_converter_class('/dummy/path')
        annotation = {
            'bounding_box': [
                {'classification': 'car', 'data': [10, 20, 30, 40]},
                {'classification': 'person', 'data': [50, 60, 70, 80]},
            ]
        }

        objects, has_segmentation = converter.parse_dm_annotations(annotation)

        assert len(objects) == 2
        assert objects[0]['name'] == 'car'
        assert objects[0]['xmin'] == 10
        assert objects[0]['has_segmentation'] is False
        assert objects[1]['name'] == 'person'
        assert objects[1]['has_segmentation'] is False
        assert has_segmentation is False
        assert 'car' in converter.class_names
        assert 'person' in converter.class_names

    def test_parse_dm_annotations_with_segmentation(self, pascal_from_dm_converter_class):
        """Test parsing DM annotations with segmentation data."""
        converter = pascal_from_dm_converter_class('/dummy/path')
        annotation = {
            'bounding_box': [
                {'classification': 'car', 'data': [10, 20, 30, 40]},
            ],
            'segmentation': [
                {'classification': 'car', 'data': [[10, 20, 30, 40, 50, 60]]},
            ],
        }

        objects, has_segmentation = converter.parse_dm_annotations(annotation)

        assert len(objects) == 1
        assert objects[0]['name'] == 'car'
        assert objects[0]['has_segmentation'] is True
        assert has_segmentation is True
        assert 'car' in converter.class_names

    def test_parse_dm_annotations_no_bounding_box(self, pascal_from_dm_converter_class):
        """Test parsing DM annotations with no bounding box."""
        converter = pascal_from_dm_converter_class('/dummy/path')
        annotation = {}

        objects, has_segmentation = converter.parse_dm_annotations(annotation)

        assert len(objects) == 0
        assert has_segmentation is False
        assert 'car' not in converter.class_names
        assert 'person' not in converter.class_names

    def test_save_to_folder(self, pascal_from_dm_converter_class, not_categorized_dataset_path, temp_output_dir):
        """Test saving converted Pascal VOC data to folder."""
        converter = pascal_from_dm_converter_class(str(not_categorized_dataset_path))
        xml_str = '<annotation><object><name>car</name></object></annotation>'
        xml_elem = ET.ElementTree(ET.fromstring(xml_str))
        converter.converted_data = [
            (xml_elem, 'path.xml', f'{not_categorized_dataset_path}/original_files/dm_1.jpg', 'dm_1.jpg')
        ]

        output_dir = Path(temp_output_dir) / 'pascal_voc'
        converter.save_to_folder(output_dir)

        assert (output_dir / 'Annotations' / 'path.xml').exists()
        assert (output_dir / 'Images' / 'dm_1.jpg').exists()

    def test_convert_categorized_dataset(self, pascal_from_dm_converter_class, categorized_dataset_path):
        converter = pascal_from_dm_converter_class(str(categorized_dataset_path), is_categorized_dataset=True)
        result = converter.convert()

        if 'train' in result and result['train']:
            for i, item in enumerate(result['train']):
                print(f'Item {i}: {item}')

        assert 'train' in result
        assert len(result['train']) == 4

        xml_files = [item[1] for item in result['train']]
        assert 'dm_4.xml' in xml_files

        jpg_files = [item[3] for item in result['train']]
        assert 'dm_4.jpg' in jpg_files

    def test_convert_non_categorized_dataset(self, pascal_from_dm_converter_class, not_categorized_dataset_path):
        """Test conversion of a non-categorized dataset."""
        converter = pascal_from_dm_converter_class(str(not_categorized_dataset_path), is_categorized_dataset=False)
        result = converter.convert()

        assert len(result) == 3

        xml_files = [item[1] for item in result]
        jpg_files = [item[3] for item in result]

        assert 'dm_3.xml' in xml_files
        assert 'dm_3.jpg' in jpg_files
