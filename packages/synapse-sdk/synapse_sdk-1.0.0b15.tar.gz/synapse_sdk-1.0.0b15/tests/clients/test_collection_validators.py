import pytest

from synapse_sdk.clients.validators.collections import FileSpecificationValidator


@pytest.fixture
def single_image_file_spec_template():
    return [
        {
            'name': 'image_1',
            'description': '',
            'file_type': 'image',
            'file_type_display': '이미지',
            'configuration': {},
            'is_sequential': False,
            'is_required': True,
            'is_primary': True,
            'function_type': 'main',
            'index': 1,
        }
    ]


@pytest.fixture
def single_image_organized_files():
    original_files = []
    for i in range(1, 21):
        image_file_name = f'{i:04d}.jpg'
        original_files.append({
            'files': {
                'image_1': f'/path/to/{image_file_name}',
            },
            'meta': {
                'original_file_name': image_file_name,
            },
        })
    return original_files


@pytest.fixture
def image_and_meta_file_spec_template():
    return [
        {
            'name': 'image_1',
            'description': '',
            'file_type': 'image',
            'file_type_display': '이미지',
            'configuration': {},
            'is_sequential': False,
            'is_required': True,
            'is_primary': True,
            'function_type': 'main',
            'index': 1,
        },
        {
            'name': 'image_2',
            'description': '',
            'file_type': 'image',
            'file_type_display': '이미지',
            'configuration': {},
            'is_sequential': False,
            'is_required': True,
            'is_primary': True,
            'function_type': 'main',
            'index': 2,
        },
        {
            'name': 'meta_1',
            'description': '',
            'file_type': 'text',
            'file_type_display': '텍스트',
            'configuration': {},
            'is_sequential': False,
            'is_required': True,
            'is_primary': False,
            'function_type': 'meta',
            'index': 1,
        },
    ]


@pytest.fixture
def image_and_meta_organized_files():
    original_files = []
    for i in range(1, 21):  # Create 20 copies
        image_1_file_name = f'{i:04d}_1.jpg'
        image_2_file_name = f'{i:04d}_2.jpg'
        meta_file_name = f'{i:04d}.txt'
        original_files.append({
            'files': {
                'image_1': f'/path/to/{image_1_file_name}',
                'image_2': f'/path/to/{image_2_file_name}',
                'meta_1': f'/path/to/{meta_file_name}',
            },
            'meta': {
                'original_file_name': {
                    'image_1': image_1_file_name,
                    'image_2': image_2_file_name,
                    'meta_1': meta_file_name,
                },
            },
        })
    return original_files


@pytest.fixture
def invalid_image_and_meta_organized_files():
    original_files = []
    for i in range(1, 21):  # Create 20 copies
        image_1_file_name = f'{i:04d}_1.jpg'
        image_2_file_name = f'{i:04d}_2.jpg'
        meta_file_name = f'{i:04d}.txt'
        original_files.append({
            'files': {
                'image_invalid_1': f'/path/to/{image_1_file_name}',
                'image_invalid_2': f'/path/to/{image_2_file_name}',
                'meta_1': f'/path/to/{meta_file_name}',
            },
            'meta': {
                'original_file_name': {
                    'image_1': image_1_file_name,
                    'image_2': image_2_file_name,
                    'meta_1': meta_file_name,
                },
            },
        })
    return original_files


def test_validate_single_image_file_spec_template(single_image_file_spec_template, single_image_organized_files):
    validator = FileSpecificationValidator(single_image_file_spec_template, single_image_organized_files)

    assert validator.validate() is True


def test_validate_image_and_meta_file_spec_template_success(
    image_and_meta_file_spec_template, image_and_meta_organized_files
):
    validator = FileSpecificationValidator(image_and_meta_file_spec_template, image_and_meta_organized_files)

    assert validator.validate() is True


def test_validate_image_and_meta_file_spec_template_failed_with_invalid_organized_files(
    image_and_meta_file_spec_template, invalid_image_and_meta_organized_files
):
    validator = FileSpecificationValidator(image_and_meta_file_spec_template, invalid_image_and_meta_organized_files)

    assert validator.validate() is False
