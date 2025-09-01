"""
Pytest configuration file for converters tests.
This file makes fixtures available to all tests in the converters module.
"""

# Import fixtures from dm_schema.py
from tests.utils.converters.fixtures.coco import (
    categorized_coco_dataset_path,
    coco_dataset_path,
    coco_to_dm_converter,
    not_categorized_coco_dataset_path,
)
from tests.utils.converters.fixtures.dm_schema import (
    categorized_dataset_path,
    coco_from_dm_converter_class,
    dm_v1_image_fixture_path,
    dm_v1_pcd_fixture_path,
    dm_v1_prompt_fixture_path,
    dm_v1_text_fixture_path,
    dm_v1_video_fixture_path,
    dm_v2_image_fixture_path,
    dm_v2_pcd_fixture_path,
    dm_v2_prompt_fixture_path,
    dm_v2_text_fixture_path,
    dm_v2_video_fixture_path,
    fixtures_root,
    jpg_file_path_1,
    jpg_file_path_2,
    jpg_file_path_3,
    jpg_file_paths,
    jpg_file_paths_dict,
    jpg_files_dir,
    not_categorized_dataset_path,
    pascal_from_dm_converter_class,
    sample_coco_expected,
    sample_dm_json,
    temp_output_dir,
    test_dataset_path,
    train_dataset_path,
    valid_dataset_path,
    yolo_from_dm_converter_class,
)

# Import fixtures from pascal.py
from tests.utils.converters.fixtures.pascal import (
    categorized_pascal_dataset_path,
    not_categorized_pascal_dataset_path,
    pascal_dataset_path,
    pascal_to_dm_converter,
)

# Import fixtures from yolo.py
from tests.utils.converters.fixtures.yolo import (
    categorized_yolo_dataset_path,
    not_categorized_yolo_dataset_path,
    yolo_dataset_path,
    yolo_to_dm_converter,
)

# Re-export all fixtures so they're available to tests
__all__ = [
    'fixtures_root',
    'categorized_dataset_path',
    'not_categorized_dataset_path',
    'train_dataset_path',
    'test_dataset_path',
    'valid_dataset_path',
    'sample_dm_json',
    'sample_coco_expected',
    'temp_output_dir',
    'coco_from_dm_converter_class',
    'yolo_from_dm_converter_class',
    'pascal_from_dm_converter_class',
    'jpg_files_dir',
    'jpg_file_paths',
    'jpg_file_path_1',
    'jpg_file_path_2',
    'jpg_file_path_3',
    'jpg_file_paths_dict',
    'yolo_dataset_path',
    'categorized_yolo_dataset_path',
    'not_categorized_yolo_dataset_path',
    'yolo_to_dm_converter',
    'pascal_dataset_path',
    'categorized_pascal_dataset_path',
    'not_categorized_pascal_dataset_path',
    'pascal_to_dm_converter',
    'coco_dataset_path',
    'categorized_coco_dataset_path',
    'not_categorized_coco_dataset_path',
    'coco_to_dm_converter',
    'dm_v1_image_fixture_path',
    'dm_v2_image_fixture_path',
    'dm_v1_text_fixture_path',
    'dm_v2_text_fixture_path',
    'dm_v1_video_fixture_path',
    'dm_v2_video_fixture_path',
    'dm_v1_pcd_fixture_path',
    'dm_v2_pcd_fixture_path',
    'dm_v1_prompt_fixture_path',
    'dm_v2_prompt_fixture_path',
]
