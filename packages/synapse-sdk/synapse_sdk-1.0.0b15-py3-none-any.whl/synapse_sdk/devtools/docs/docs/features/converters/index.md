---
id: converters
title: Converters
sidebar_position: 1
---

# Converters

The Synapse SDK provides comprehensive data format conversion utilities for computer vision datasets. These converters enable seamless transformation between different annotation formats commonly used in machine learning workflows.

## Overview

The converter system supports bidirectional conversion between:

- **DM Format** - Synapse Data Manager's native annotation format (supports v1 ⟷ v2 migration)
- **COCO Format** - Microsoft Common Objects in Context format  
- **Pascal VOC Format** - Visual Object Classes XML format
- **YOLO Format** - You Only Look Once text-based format

All converters support both categorized datasets (with train/valid/test splits) and non-categorized datasets. Additionally, all converters now support single file conversion mode for processing individual files.

## Supported Annotation Types

| Annotation Type | DM | COCO | Pascal VOC | YOLO |
|----------------|----|----|-----------|------|
| Bounding Boxes | ✅ | ✅ | ✅ | ✅ |
| Polygons | ✅ | ✅ | ❌ | ✅ |
| Segmentation | ✅ | ✅ | ✅ | ❌ |
| Keypoints | ✅ | ✅ | ❌ | ✅ |
| Classifications | ✅ | ✅ | ❌ | ❌ |

## Pascal VOC Converters

### FromDMToPascalConverter

Converts DM format annotations to Pascal VOC XML format.

**Features:**
- Converts bounding box annotations and segmentation masks
- Creates standard Pascal VOC directory structure
- Generates `classes.txt` file automatically
- Supports both categorized and non-categorized datasets

**Usage:**
```python
from synapse_sdk.utils.converters.pascal.from_dm import FromDMToPascalConverter

# Convert categorized dataset
converter = FromDMToPascalConverter(
    root_dir='/path/to/dm/dataset',
    is_categorized_dataset=True
)
converted_data = converter.convert()
converter.save_to_folder('/output/pascal/dataset')

# Convert non-categorized dataset
converter = FromDMToPascalConverter(
    root_dir='/path/to/dm/dataset',
    is_categorized_dataset=False
)
converted_data = converter.convert()
converter.save_to_folder('/output/pascal/dataset')

# Single file conversion
converter = FromDMToPascalConverter(is_single_conversion=True)
with open('data.json') as f:
    dm_data = json.load(f)
with open('image.jpg', 'rb') as img_file:
    pascal_xml = converter.convert_single_file(dm_data, img_file)
```

**Input Structure (Categorized):**
```
dm_dataset/
├── train/
│   ├── json/
│   │   ├── image1.json
│   │   └── image2.json
│   └── original_files/
│       ├── image1.jpg
│       └── image2.jpg
├── valid/
│   ├── json/
│   └── original_files/
└── test/ (optional)
    ├── json/
    └── original_files/
```

**Output Structure:**
```
pascal_dataset/
├── train/
│   ├── Annotations/
│   │   ├── image1.xml
│   │   └── image2.xml
│   └── Images/
│       ├── image1.jpg
│       └── image2.jpg
├── valid/
├── test/ (if present)
└── classes.txt
```

### PascalToDMConverter

Converts Pascal VOC XML annotations to DM format.

**Features:**
- Parses Pascal VOC XML files
- Flexible directory naming (supports Annotations/annotations, Images/images/JPEGImages)
- Extracts bounding box annotations and segmentation information
- Maintains class information

**Usage:**
```python
from synapse_sdk.utils.converters.pascal.to_dm import PascalToDMConverter

# Convert Pascal VOC dataset
converter = PascalToDMConverter(
    root_dir='/path/to/pascal/dataset',
    is_categorized_dataset=True
)
converted_data = converter.convert()
converter.save_to_folder('/output/dm/dataset')
```

## YOLO Converters

### FromDMToYOLOConverter

Converts DM format annotations to YOLO format with comprehensive annotation support.

**Features:**
- Supports bounding boxes, polygons, and keypoints
- Creates `dataset.yaml` configuration file
- Normalizes coordinates automatically
- Handles keypoint visibility flags

**Usage:**
```python
from synapse_sdk.utils.converters.yolo.from_dm import FromDMToYOLOConverter

# Convert with all annotation types
converter = FromDMToYOLOConverter(
    root_dir='/path/to/dm/dataset',
    is_categorized_dataset=True
)
converted_data = converter.convert()
converter.save_to_folder('/output/yolo/dataset')

# Single file conversion
converter = FromDMToYOLOConverter(is_single_conversion=True)
with open('data.json') as f:
    dm_data = json.load(f)
with open('image.jpg', 'rb') as img_file:
    yolo_labels = converter.convert_single_file(dm_data, img_file)
```

**Output Structure:**
```
yolo_dataset/
├── train/
│   ├── images/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   └── labels/
│       ├── image1.txt
│       └── image2.txt
├── valid/
├── test/ (if present)
├── dataset.yaml
└── classes.txt
```

**YOLO Label Format Examples:**
```
# Bounding box: class_id center_x center_y width height
0 0.5 0.5 0.3 0.4

# Polygon: class_id x1 y1 x2 y2 x3 y3 x4 y4 ...
0 0.1 0.1 0.9 0.1 0.9 0.9 0.1 0.9

# Keypoints: class_id center_x center_y width height kp1_x kp1_y kp1_v kp2_x kp2_y kp2_v ...
0 0.5 0.5 0.3 0.4 0.45 0.3 2 0.55 0.3 2 0.5 0.7 1
```

### YOLOToDMConverter

Converts YOLO format annotations back to DM format.

**Features:**
- Intelligent parsing of different YOLO annotation types
- Requires `dataset.yaml` for class name mapping
- Handles bounding boxes, polygons, and keypoints
- Automatically detects image dimensions

**Usage:**
```python
from synapse_sdk.utils.converters.yolo.to_dm import YOLOToDMConverter

converter = YOLOToDMConverter(
    root_dir='/path/to/yolo/dataset',
    is_categorized_dataset=True
)
converted_data = converter.convert()
converter.save_to_folder('/output/dm/dataset')
```

## COCO Converters

### FromDMToCOCOConverter

Converts DM format to COCO format with full metadata support.

**Features:**
- Comprehensive COCO metadata (info, licenses, categories)
- Supports bounding boxes, polygons, segmentation, and keypoints
- Dynamic category management
- Extensible for different data types

**Usage:**
```python
from synapse_sdk.utils.converters.coco.from_dm import FromDMToCOCOConverter

# Basic conversion
converter = FromDMToCOCOConverter(
    root_dir='/path/to/dm/dataset',
    is_categorized_dataset=True
)
converted_data = converter.convert()
converter.save_to_folder('/output/coco/dataset')

# With custom metadata
info_dict = {
    "description": "My Custom Dataset",
    "version": "1.0",
    "contributor": "My Organization"
}

licenses_list = [{
    "id": 1,
    "name": "Custom License",
    "url": "https://example.com/license"
}]

converter = FromDMToCOCOConverter(
    root_dir='/path/to/dm/dataset',
    info_dict=info_dict,
    licenses_list=licenses_list,
    is_categorized_dataset=True
)

# Single file conversion
converter = FromDMToCOCOConverter(
    data_type='img',
    is_single_conversion=True
)
with open('data.json') as f:
    dm_data = json.load(f)
with open('image.jpg', 'rb') as img_file:
    coco_annotation = converter.convert_single_file(dm_data, img_file)
```

**Output Structure:**
```
coco_dataset/
├── train/
│   ├── annotations.json
│   ├── image1.jpg
│   └── image2.jpg
├── valid/
│   ├── annotations.json
│   └── images...
└── test/ (if present)
```

### COCOToDMConverter

Converts COCO format annotations to DM format.

**Features:**
- Parses COCO JSON annotations
- Handles image datasets
- Maintains keypoint groupings through DM groups
- Supports bounding boxes and keypoints

**Usage:**
```python
from synapse_sdk.utils.converters.coco.to_dm import COCOToDMConverter

converter = COCOToDMConverter(
    root_dir='/path/to/coco/dataset',
    is_categorized_dataset=True
)
converted_data = converter.convert()
converter.save_to_folder('/output/dm/dataset')
```

## DM Version Converter

### DMV1ToV2Converter

Migrates legacy DM v1 datasets to the current v2 format.

**Features:**
- Comprehensive migration for all annotation types
- Handles data structure changes between versions
- Supports images and videos
- Maintains annotation tool integrity

**Supported Tools:**
- Bounding boxes
- Named entities
- Classifications with attributes
- Polylines and polygons
- Keypoints
- 3D bounding boxes
- Segmentation
- Relations and groups

**Usage:**
```python
from synapse_sdk.utils.converters.dm.from_v1 import DMV1ToV2Converter

converter = DMV1ToV2Converter(
    root_dir='/path/to/dm/v1/dataset',
    is_categorized_dataset=True
)
converted_data = converter.convert()
converter.save_to_folder('/output/dm/v2/dataset')
```

### DMV2ToV1Converter

Converts DM v2 datasets back to the legacy v1 format for compatibility with older systems.

**Features:**
- Reverse migration from DM v2 to v1 format
- Preserves all annotation types and metadata
- Maintains coordinate integrity across formats
- Generates appropriate v1 structure with annotations and annotationsData

**Supported Tools:**
- Bounding boxes
- Named entities  
- Classifications with attributes
- Polylines and polygons
- Keypoints
- 3D bounding boxes
- Segmentation
- Relations and groups

**Usage:**
```python
from synapse_sdk.utils.converters.dm.to_v1 import DMV2ToV1Converter

# Load v2 data and convert to v1
with open('dm_v2_data.json', 'r') as f:
    v2_data = json.load(f)

converter = DMV2ToV1Converter(v2_data)
v1_data = converter.convert()

# Save or use the converted v1 data
with open('dm_v1_data.json', 'w') as f:
    json.dump(v1_data, f, indent=2)
```

## Common Parameters

All converters share these common parameters:

### `root_dir` (str)
Path to the root directory containing the dataset. Not required when using single file conversion mode.

### `is_categorized_dataset` (bool)
- `True`: Dataset has train/valid/test splits in separate subdirectories
- `False`: Dataset is in a single directory without splits

### `is_single_conversion` (bool)
- `True`: Enable single file conversion mode for processing individual files
- `False`: Process entire dataset directories (default behavior)

### Common Methods

#### `convert()`
Performs in-memory conversion and returns the converted data structure.

#### `convert_single_file(data, original_file, **kwargs)`
Available when `is_single_conversion=True`. Converts a single data object and corresponding original file.

#### `save_to_folder(output_dir)`
Saves the converted data to the specified output directory, creating the appropriate file structure for the target format.

## Error Handling

All converters include robust error handling:

- **File Validation**: Checks for required files and directories
- **Format Validation**: Validates annotation format correctness
- **Graceful Degradation**: Warns about unsupported annotations instead of failing
- **Progress Tracking**: Shows progress for large dataset conversions

## Best Practices

1. **Backup Original Data**: Always keep backups before conversion
2. **Validate Results**: Check converted annotations for accuracy
3. **Test on Small Datasets**: Test conversion on small samples first
4. **Check Requirements**: Ensure all required files (dataset.yaml, annotations.json, etc.) are present
5. **Monitor Warnings**: Pay attention to conversion warnings for data quality issues

## Examples

### Converting a Complete Workflow

```python
# 1. Convert Pascal VOC to DM
pascal_converter = PascalToDMConverter('/data/pascal', True)
dm_data = pascal_converter.convert()
pascal_converter.save_to_folder('/data/dm_intermediate')

# 2. Convert DM to YOLO
yolo_converter = FromDMToYOLOConverter('/data/dm_intermediate', True)
yolo_data = yolo_converter.convert()
yolo_converter.save_to_folder('/data/yolo_final')

# 3. Convert DM to COCO for evaluation
coco_converter = FromDMToCOCOConverter('/data/dm_intermediate', True)
coco_data = coco_converter.convert()
coco_converter.save_to_folder('/data/coco_eval')
```

### Single File Conversion Example

```python
import json
from synapse_sdk.utils.converters.yolo.from_dm import FromDMToYOLOConverter

# Initialize converter for single file processing
converter = FromDMToYOLOConverter(is_single_conversion=True)

# Load DM format data
with open('annotation.json', 'r') as f:
    dm_data = json.load(f)

# Convert single file
with open('image.jpg', 'rb') as img_file:
    yolo_labels = converter.convert_single_file(dm_data, img_file)

# yolo_labels contains the converted YOLO format labels
print(yolo_labels)
```

This converter system provides a complete solution for dataset format transformation, enabling seamless integration between different machine learning workflows and annotation tools.