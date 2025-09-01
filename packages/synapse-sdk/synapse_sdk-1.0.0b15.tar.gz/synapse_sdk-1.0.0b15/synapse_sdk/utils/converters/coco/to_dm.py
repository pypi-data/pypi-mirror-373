import json
import os
from typing import IO, Any, Dict

from synapse_sdk.utils.converters import ToDMConverter


class COCOToDMConverter(ToDMConverter):
    """Convert COCO format annotations to DM (Data Manager) format."""

    def __init__(self, root_dir: str = None, is_categorized_dataset: bool = False, is_single_conversion: bool = False):
        super().__init__(root_dir, is_categorized_dataset, is_single_conversion)

    def convert(self):
        if self.is_categorized_dataset:
            splits = self._validate_splits(['train', 'valid'], ['test'])
            all_split_data = {}
            for split, split_dir in splits.items():
                annotation_path = os.path.join(split_dir, 'annotations.json')
                if not os.path.exists(annotation_path):
                    raise FileNotFoundError(f'annotations.json not found in {split_dir}')
                with open(annotation_path, 'r', encoding='utf-8') as f:
                    coco_data = json.load(f)
                split_data = self._convert_coco_ann_to_dm(coco_data, split_dir)
                all_split_data[split] = split_data
            self.converted_data = all_split_data
            return all_split_data
        else:
            annotation_path = os.path.join(self.root_dir, 'annotations.json')
            if not os.path.exists(annotation_path):
                raise FileNotFoundError(f'annotations.json not found in {self.root_dir}')
            with open(annotation_path, 'r', encoding='utf-8') as f:
                coco_data = json.load(f)
            converted_data = self._convert_coco_ann_to_dm(coco_data, self.root_dir)
            self.converted_data = converted_data
            return converted_data

    def _convert_coco_ann_to_dm(self, coco_data, base_dir):
        """Convert COCO annotations to DM format."""
        dataset_type = coco_data.get('type', 'image')  # Default to 'image' if type is not specified
        if dataset_type == 'image':
            return self._process_image_data(coco_data, base_dir)
        else:
            raise ValueError(f'Unsupported dataset type: {dataset_type}')

    def _process_image_data(self, coco_data, img_base_dir):
        """Process COCO image data and convert to DM format."""
        images = coco_data.get('images', [])
        annotations = coco_data.get('annotations', [])
        categories = coco_data.get('categories', [])
        cat_map = {cat['id']: cat for cat in categories}

        # Build image_id -> annotation list
        ann_by_img_id = {}
        for ann in annotations:
            img_id = ann['image_id']
            ann_by_img_id.setdefault(img_id, []).append(ann)

        result = {}
        for img in images:
            img_id = img['id']
            img_filename = img['file_name']
            img_path = os.path.join(img_base_dir, img_filename)
            anns = ann_by_img_id.get(img_id, [])

            # DM image structure
            dm_img = {
                'bounding_box': [],
                'keypoint': [],
                'relation': [],
                'group': [],
            }

            # Handle bounding_box
            bbox_ids = []
            for ann in anns:
                cat = cat_map.get(ann['category_id'], {})
                if 'bbox' in ann and ann['bbox']:
                    bbox_id = self._generate_unique_id()
                    bbox_ids.append(bbox_id)
                    dm_img['bounding_box'].append({
                        'id': bbox_id,
                        'classification': cat.get('name', str(ann['category_id'])),
                        'attrs': ann.get('attrs', []),
                        'data': list(ann['bbox']),
                    })

            # Handle keypoints
            for ann in anns:
                cat = cat_map.get(ann['category_id'], {})
                attrs = ann.get('attrs', [])
                if 'keypoints' in ann and ann['keypoints']:
                    kp_names = cat.get('keypoints', [])
                    kps = ann['keypoints']
                    keypoint_ids = []
                    for idx in range(min(len(kps) // 3, len(kp_names))):
                        x, y, v = kps[idx * 3 : idx * 3 + 3]
                        kp_id = self._generate_unique_id()
                        keypoint_ids.append(kp_id)
                        dm_img['keypoint'].append({
                            'id': kp_id,
                            'classification': kp_names[idx] if idx < len(kp_names) else f'keypoint_{idx}',
                            'attrs': attrs,
                            'data': [x, y],
                        })
                    group_ids = bbox_ids + keypoint_ids
                    if group_ids:
                        dm_img['group'].append({
                            'id': self._generate_unique_id(),
                            'classification': cat.get('name', str(ann['category_id'])),
                            'attrs': attrs,
                            'data': group_ids,
                        })

            dm_json = {'images': [dm_img]}
            result[img_filename] = (dm_json, img_path)
        return result

    def convert_single_file(self, data: Dict[str, Any], original_file: IO, original_image_name: str) -> Dict[str, Any]:
        """Convert a single COCO annotation data and corresponding image to DM format.

        Args:
            data: COCO format data dictionary (JSON content)
            original_file: File object for the corresponding original image
            original_image_name: Original image name

        Returns:
            Dictionary containing DM format data for the single file
        """
        if not self.is_single_conversion:
            raise RuntimeError('convert_single_file is only available when is_single_conversion=True')

        images = data.get('images', [])
        annotations = data.get('annotations', [])
        categories = data.get('categories', [])

        if not images:
            raise ValueError('No images found in COCO data')

        # Get file name from original_file
        img_path = getattr(original_file, 'name', None)
        if not img_path:
            raise ValueError('original_file must have a "name" attribute representing its path or filename.')
        img_basename = os.path.basename(img_path)

        # Find the matching image info in COCO 'images' section by comparing file name
        # COCO image dicts might use 'file_name', 'filename', or similar
        matched_img = None
        for img in images:
            for key in ['file_name', 'filename', 'name']:
                if key in img and os.path.basename(img[key]) == original_image_name:
                    matched_img = img
                    break
            if matched_img:
                break

        if not matched_img:
            raise ValueError(f'No matching image found in COCO data for file: {img_basename}')

        img_id = matched_img['id']
        cat_map = {cat['id']: cat for cat in categories}
        anns = [ann for ann in annotations if ann['image_id'] == img_id]

        dm_img = {
            'bounding_box': [],
            'keypoint': [],
            'relation': [],
            'group': [],
        }

        bbox_ids = []
        for ann in anns:
            cat = cat_map.get(ann['category_id'], {})
            if 'bbox' in ann and ann['bbox']:
                bbox_id = self._generate_unique_id()
                bbox_ids.append(bbox_id)
                dm_img['bounding_box'].append({
                    'id': bbox_id,
                    'classification': cat.get('name', str(ann['category_id'])),
                    'attrs': ann.get('attrs', []),
                    'data': list(ann['bbox']),
                })

        for ann in anns:
            cat = cat_map.get(ann['category_id'], {})
            attrs = ann.get('attrs', [])
            if 'keypoints' in ann and ann['keypoints']:
                kp_names = cat.get('keypoints', [])
                kps = ann['keypoints']
                keypoint_ids = []
                for idx in range(min(len(kps) // 3, len(kp_names))):
                    x, y, _ = kps[idx * 3 : idx * 3 + 3]
                    kp_id = self._generate_unique_id()
                    keypoint_ids.append(kp_id)
                    dm_img['keypoint'].append({
                        'id': kp_id,
                        'classification': kp_names[idx] if idx < len(kp_names) else f'keypoint_{idx}',
                        'attrs': attrs,
                        'data': [x, y],
                    })
                group_ids = bbox_ids + keypoint_ids
                if group_ids:
                    dm_img['group'].append({
                        'id': self._generate_unique_id(),
                        'classification': cat.get('name', str(ann['category_id'])),
                        'attrs': attrs,
                        'data': group_ids,
                    })

        dm_json = {'images': [dm_img]}
        return {
            'dm_json': dm_json,
            'image_path': img_path,
            'image_name': img_basename,
        }
