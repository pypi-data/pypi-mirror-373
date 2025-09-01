import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_root():
    """Return the root directory of test fixtures."""
    return Path(__file__).parent


@pytest.fixture
def categorized_dataset_path(fixtures_root):
    """Return the path to categorized dataset fixtures."""
    return fixtures_root / 'data_types' / 'image' / 'dm' / 'categorized'


@pytest.fixture
def not_categorized_dataset_path(fixtures_root):
    """Return the path to non-categorized dataset fixtures."""
    return fixtures_root / 'data_types' / 'image' / 'dm' / 'not_categorized'


@pytest.fixture
def train_dataset_path(categorized_dataset_path):
    """Return the path to train dataset."""
    return categorized_dataset_path / 'train'


@pytest.fixture
def test_dataset_path(categorized_dataset_path):
    """Return the path to test dataset."""
    return categorized_dataset_path / 'test'


@pytest.fixture
def valid_dataset_path(categorized_dataset_path):
    """Return the path to validation dataset."""
    return categorized_dataset_path / 'valid'


@pytest.fixture
def sample_dm_json():
    """Return a sample DM format JSON data."""
    return {
        'images': [
            {
                'polyline': [
                    {
                        'id': 'e1ve10k7Cv',
                        'classification': 'car',
                        'attrs': {'color': 'red'},
                        'data': [[899, 392], [821, 505], [954, 598], [1142, 574], [1179, 663]],
                    }
                ],
                'bounding_box': [
                    {
                        'id': 'bbox1',
                        'classification': 'person',
                        'attrs': {'confidence': 0.95},
                        'data': [100, 100, 200, 300],
                    }
                ],
                'keypoint': [
                    {'id': 'kp1', 'classification': 'nose', 'attrs': {'visible': True}, 'data': [150, 200]},
                    {'id': 'kp2', 'classification': 'eye', 'attrs': {'visible': True}, 'data': [160, 180]},
                ],
                'relation': [],
                'group': [],
            }
        ]
    }


@pytest.fixture
def sample_coco_expected():
    """Return expected COCO format data for the sample DM data."""
    return {
        'info': {
            'description': 'Converted from DM format',
            'url': '',
            'version': '1.0',
            'year': 2024,
            'contributor': '',
            'date_created': '2024-01-01 00:00:00',
        },
        'licenses': [{'id': 1, 'name': 'Unknown', 'url': ''}],
        'images': [{'id': 1, 'width': 1920, 'height': 1080, 'license': 1}],
        'annotations': [
            {
                'id': 1,
                'image_id': 1,
                'category_id': 1,
                'segmentation': [[899, 392, 821, 505, 954, 598, 1142, 574, 1179, 663]],
                'bbox': [821, 392, 358, 271],
                'area': 97018,
                'iscrowd': 0,
            },
            {
                'id': 2,
                'image_id': 1,
                'category_id': 2,
                'segmentation': [],
                'bbox': [100, 100, 200, 300],
                'area': 60000,
                'iscrowd': 0,
            },
            {
                'id': 3,
                'image_id': 1,
                'category_id': 3,
                'keypoints': [150, 200, 2, 160, 180, 2],
                'num_keypoints': 2,
                'bbox': [150, 180, 10, 20],
                'area': 0,
                'iscrowd': 0,
            },
        ],
        'categories': [
            {'id': 1, 'name': 'car', 'supercategory': 'car'},
            {'id': 2, 'name': 'person', 'supercategory': 'person'},
            {'id': 3, 'name': 'keypoints', 'supercategory': 'keypoints', 'keypoints': ['nose', 'eye'], 'skeleton': []},
        ],
    }


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def coco_from_dm_converter_class():
    """Import and return the DMToCOCOConverter class."""
    from synapse_sdk.utils.converters.coco.from_dm import FromDMToCOCOConverter

    return FromDMToCOCOConverter


@pytest.fixture
def yolo_from_dm_converter_class():
    """Import and return the FromDMToYOLOConverter class."""
    from synapse_sdk.utils.converters.yolo.from_dm import FromDMToYOLOConverter

    return FromDMToYOLOConverter


@pytest.fixture
def pascal_from_dm_converter_class():
    from synapse_sdk.utils.converters.pascal.from_dm import FromDMToPascalConverter

    return FromDMToPascalConverter


@pytest.fixture
def jpg_files_dir():
    """Return the directory containing JPG test files."""
    current_dir = Path(__file__).parent
    return current_dir / 'data_types' / 'image' / 'jpg'


@pytest.fixture
def jpg_file_paths():
    """Return a list of all JPG file paths in the test fixtures."""
    jpg_dir = Path(__file__).parent / 'data_types' / 'image' / 'jpg'
    jpg_files = list(jpg_dir.glob('*.jpg'))
    return [str(jpg_file) for jpg_file in jpg_files]


@pytest.fixture
def jpg_file_path_1():
    """Return the path to dm_data_1.jpg."""
    jpg_dir = Path(__file__).parent / 'data_types' / 'image' / 'jpg'
    return str(jpg_dir / 'dm_data_1.jpg')


@pytest.fixture
def jpg_file_path_2():
    """Return the path to dm_data_2.jpg."""
    jpg_dir = Path(__file__).parent / 'data_types' / 'image' / 'jpg'
    return str(jpg_dir / 'dm_data_2.jpg')


@pytest.fixture
def jpg_file_path_3():
    """Return the path to dm_data_3.jpg."""
    jpg_dir = Path(__file__).parent / 'data_types' / 'image' / 'jpg'
    return str(jpg_dir / 'dm_data_3.jpg')


@pytest.fixture
def jpg_file_paths_dict():
    """Return a dictionary mapping file names to their full paths."""
    jpg_dir = Path(__file__).parent / 'data_types' / 'image' / 'jpg'
    return {
        'dm_data_1.jpg': str(jpg_dir / 'dm_data_1.jpg'),
        'dm_data_2.jpg': str(jpg_dir / 'dm_data_2.jpg'),
        'dm_data_3.jpg': str(jpg_dir / 'dm_data_3.jpg'),
    }


# DM V1 to V2 converter test fixture paths
@pytest.fixture
def dm_v1_image_fixture_path(fixtures_root):
    """Return the path to DM v1 image test fixture."""
    return fixtures_root / 'data_types' / 'image' / 'dm' / 'ver1' / 'json' / '25669.json'


@pytest.fixture
def dm_v2_image_fixture_path(fixtures_root):
    """Return the path to DM v2 image test fixture."""
    return fixtures_root / 'data_types' / 'image' / 'dm' / 'ver2' / 'json' / '25669.json'


@pytest.fixture
def dm_v1_text_fixture_path(fixtures_root):
    """Return the path to DM v1 text test fixture."""
    return fixtures_root / 'data_types' / 'text' / 'dm' / 'ver1' / 'json' / '23811.json'


@pytest.fixture
def dm_v2_text_fixture_path(fixtures_root):
    """Return the path to DM v2 text test fixture."""
    return fixtures_root / 'data_types' / 'text' / 'dm' / 'ver2' / 'json' / '23811.json'


@pytest.fixture
def dm_v1_video_fixture_path(fixtures_root):
    """Return the path to DM v1 video test fixture."""
    return fixtures_root / 'data_types' / 'video' / 'dm' / 'ver1' / 'json' / '23831.json'


@pytest.fixture
def dm_v2_video_fixture_path(fixtures_root):
    """Return the path to DM v2 video test fixture."""
    return fixtures_root / 'data_types' / 'video' / 'dm' / 'ver2' / 'json' / '23831.json'


@pytest.fixture
def dm_v1_pcd_fixture_path(fixtures_root):
    """Return the path to DM v1 PCD test fixture."""
    return fixtures_root / 'data_types' / 'pcd' / 'dm' / 'ver1' / 'json' / '23791.json'


@pytest.fixture
def dm_v2_pcd_fixture_path(fixtures_root):
    """Return the path to DM v2 PCD test fixture."""
    return fixtures_root / 'data_types' / 'pcd' / 'dm' / 'ver2' / 'json' / '23791.json'


@pytest.fixture
def dm_v1_prompt_fixture_path(fixtures_root):
    """Return the path to DM v1 prompt test fixture."""
    return fixtures_root / 'data_types' / 'prompt' / 'dm' / 'ver1' / 'json' / '18662.json'


@pytest.fixture
def dm_v2_prompt_fixture_path(fixtures_root):
    """Return the path to DM v2 prompt test fixture."""
    return fixtures_root / 'data_types' / 'prompt' / 'dm' / 'ver2' / 'json' / '18662.json'
