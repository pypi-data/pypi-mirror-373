import json
import os
import shutil
from glob import glob
from typing import IO, Any, Dict, List, Optional, Union

from PIL import Image

from synapse_sdk.utils.converters import FromDMConverter


class FromDMToYOLOConverter(FromDMConverter):
    """Convert DM dataset format to YOLO format."""

    IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']

    def __init__(self, root_dir: str = None, is_categorized_dataset: bool = False, is_single_conversion: bool = False):
        super().__init__(root_dir, is_categorized_dataset, is_single_conversion)
        self.class_names: List[str] = []
        self.class_map: Dict[str, int] = {}
        self.dataset_yaml_content: str = ''

    @staticmethod
    def get_all_classes(list_of_dirs: List[str]) -> List[str]:
        """Collect all unique class names from all splits or the root."""
        classes = set()
        for d in list_of_dirs:
            if not d or not os.path.isdir(d):
                continue
            json_dir = os.path.join(d, 'json') if os.path.isdir(os.path.join(d, 'json')) else d
            for jfile in glob(os.path.join(json_dir, '*.json')):
                with open(jfile, encoding='utf-8') as jf:
                    data = json.load(jf)
                for img_ann in data['images']:
                    for k in ['bounding_box', 'polygon', 'keypoint']:
                        if k in img_ann:
                            for ann in img_ann[k]:
                                classes.add(ann['classification'])
        return sorted(list(classes))

    @staticmethod
    def get_image_size(image_path: str):
        with Image.open(image_path) as img:
            return img.size

    @staticmethod
    def polygon_to_bbox(polygon: list):
        """Convert polygon points to bounding box [cx, cy, w, h]."""
        if not polygon or len(polygon) == 0:
            return None
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        x_min, y_min = min(xs), min(ys)
        x_max, y_max = max(xs), max(ys)
        cx = (x_min + x_max) / 2
        cy = (y_min + y_max) / 2
        w = x_max - x_min
        h = y_max - y_min
        return [cx, cy, w, h]

    @staticmethod
    def polygon_to_yolo_string(polygon: list, width: int, height: int):
        """Convert polygon points to normalized YOLO polygon format string (x1 y1 x2 y2 ...)."""
        if not polygon or len(polygon) == 0:
            return ''

        coords = []
        for point in polygon:
            x, y = point
            # Normalize coordinates to 0-1 range
            x_norm = x / width
            y_norm = y / height
            coords.extend([f'{x_norm:.6f}', f'{y_norm:.6f}'])

        return ' '.join(coords)

    @staticmethod
    def keypoints_to_yolo_string(keypoints: list, width: int, height: int):
        """Convert keypoints to normalized YOLO keypoint format string (x1 y1 v1 x2 y2 v2 ...)."""
        kp_strs = []
        for kp in keypoints:
            # kp: [x, y, visible]
            x, y, v = kp
            x = x / width
            y = y / height
            kp_strs.extend([f'{x:.6f}', f'{y:.6f}', str(v)])
        return ' '.join(kp_strs)

    def _convert_split_dir(self, split_dir: str, split_name: str) -> List[Dict[str, Any]]:
        """Convert one split folder to YOLO format."""
        if not self.class_map:
            raise ValueError('class_map is not initialized. Ensure get_all_classes() is called before this method.')

        json_dir = os.path.join(split_dir, 'json')
        img_dir = os.path.join(split_dir, 'original_files')
        entries = []
        for jfile in glob(os.path.join(json_dir, '*.json')):
            base = os.path.splitext(os.path.basename(jfile))[0]
            found_img = None
            for ext in self.IMG_EXTENSIONS:
                img_path = os.path.join(img_dir, base + ext)
                if os.path.exists(img_path):
                    found_img = img_path
                    break
            if not found_img:
                print(f'[{split_name}] Image for {base} not found, skipping.')
                continue
            width, height = self.get_image_size(found_img)
            with open(jfile, encoding='utf-8') as jf:
                data = json.load(jf)
            img_ann = data['images'][0]
            label_lines = []

            # bbox
            if 'bounding_box' in img_ann:
                for box in img_ann['bounding_box']:
                    cidx = self.class_map[box['classification']]
                    x, y, w, h = box['data']
                    cx = x + w / 2
                    cy = y + h / 2
                    cx /= width
                    cy /= height
                    w /= width
                    h /= height
                    label_lines.append(f'{cidx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}')

            # polygon
            if 'polygon' in img_ann:
                for poly in img_ann['polygon']:
                    cidx = self.class_map[poly['classification']]
                    poly_str = self.polygon_to_yolo_string(poly['data'], width, height)
                    if poly_str:  # Only add if polygon is valid
                        label_lines.append(f'{cidx} {poly_str}')
                    else:
                        print(f'[{split_name}] Polygon for {base} is empty, skipping this polygon.')

            # keypoint
            if 'keypoint' in img_ann:
                for kp in img_ann['keypoint']:
                    cidx = self.class_map[kp['classification']]
                    # Assume bounding box exists for keypoint, or fallback to full image
                    if 'bounding_box' in kp:
                        x, y, w, h = kp['bounding_box']
                        cx = x + w / 2
                        cy = y + h / 2
                        cx /= width
                        cy /= height
                        w /= width
                        h /= height
                    else:
                        # fallback to the whole image
                        cx, cy, w, h = 0.5, 0.5, 1.0, 1.0
                    kp_str = self.keypoints_to_yolo_string(kp['data'], width, height)
                    label_lines.append(f'{cidx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f} {kp_str}')

            entries.append({
                'img_path': found_img,
                'img_name': os.path.basename(found_img),
                'label_name': base + '.txt',
                'label_lines': label_lines,
            })
        return entries

    def _convert_root_dir(self) -> List[Dict[str, Any]]:
        """Convert non-categorized dataset to YOLO format."""
        json_dir = os.path.join(self.root_dir, 'json')
        img_dir = os.path.join(self.root_dir, 'original_files')
        entries = []
        for jfile in glob(os.path.join(json_dir, '*.json')):
            base = os.path.splitext(os.path.basename(jfile))[0]
            found_img = None
            for ext in self.IMG_EXTENSIONS:
                img_path = os.path.join(img_dir, base + ext)
                if os.path.exists(img_path):
                    found_img = img_path
                    break
            if not found_img:
                print(f'[single] Image for {base} not found, skipping.')
                continue
            width, height = self.get_image_size(found_img)
            with open(jfile, encoding='utf-8') as jf:
                data = json.load(jf)
            img_ann = data['images'][0]
            label_lines = []

            # bbox
            if 'bounding_box' in img_ann:
                for box in img_ann['bounding_box']:
                    cidx = self.class_map[box['classification']]
                    x, y, w, h = box['data']
                    cx = x + w / 2
                    cy = y + h / 2
                    cx /= width
                    cy /= height
                    w /= width
                    h /= height
                    label_lines.append(f'{cidx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}')

            # polygon
            if 'polygon' in img_ann:
                for poly in img_ann['polygon']:
                    cidx = self.class_map[poly['classification']]
                    poly_str = self.polygon_to_yolo_string(poly['data'], width, height)
                    if poly_str:  # Only add if polygon is valid
                        label_lines.append(f'{cidx} {poly_str}')
                    else:
                        print(f'[single] Polygon for {base} is empty, skipping this polygon.')

            # keypoint
            if 'keypoint' in img_ann:
                for kp in img_ann['keypoint']:
                    cidx = self.class_map[kp['classification']]
                    if 'bounding_box' in kp:
                        x, y, w, h = kp['bounding_box']
                        cx = x + w / 2
                        cy = y + h / 2
                        cx /= width
                        cy /= height
                        w /= width
                        h /= height
                    else:
                        cx, cy, w, h = 0.5, 0.5, 1.0, 1.0
                    kp_str = self.keypoints_to_yolo_string(kp['data'], width, height)
                    label_lines.append(f'{cidx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f} {kp_str}')

            entries.append({
                'img_path': found_img,
                'img_name': os.path.basename(found_img),
                'label_name': base + '.txt',
                'label_lines': label_lines,
            })
        return entries

    def convert(self) -> Union[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """Convert DM format to YOLO format (categorized split or not).

        Returns:
            - If categorized: dict {split: list of entries}
            - If not: list of entries
        """
        # Prepare dataset.yaml content (for save_to_folder)
        yaml_lines = [
            'path: ' + self.root_dir,
        ]

        if self.is_categorized_dataset:
            splits = self._validate_splits(required_splits=['train', 'valid'], optional_splits=['test'])
            self.class_names = self.get_all_classes(list(splits.values()))
            self.class_map = {name: idx for idx, name in enumerate(self.class_names)}
            result = {}
            for split, split_dir in splits.items():
                result[split] = self._convert_split_dir(split_dir, split)
            self.converted_data = result

            yaml_lines.append('train: train/images')
            yaml_lines.append('val: valid/images')
            if 'test' in splits:
                yaml_lines.append('test: test/images')
        else:
            self._validate_splits(required_splits=[], optional_splits=[])
            self.class_names = self.get_all_classes([self.root_dir])
            self.class_map = {name: idx for idx, name in enumerate(self.class_names)}
            result = self._convert_root_dir()
            self.converted_data = result

        yaml_lines += ['', f'nc: {len(self.class_names)}', f'names: {self.class_names}', '']
        self.dataset_yaml_content = '\n'.join(yaml_lines)
        return result

    def save_to_folder(self, output_dir: Optional[str] = None) -> None:
        """Save converted YOLO data to the specified folder."""
        output_dir = output_dir or self.root_dir
        self.ensure_dir(output_dir)
        if self.converted_data is None:
            self.converted_data = self.convert()

        if self.is_categorized_dataset:
            for split, entries in self.converted_data.items():
                split_imgs = os.path.join(output_dir, split, 'images')
                split_labels = os.path.join(output_dir, split, 'labels')
                self.ensure_dir(split_imgs)
                self.ensure_dir(split_labels)
                for entry in entries:
                    shutil.copy(entry['img_path'], os.path.join(split_imgs, entry['img_name']))
                    with open(os.path.join(split_labels, entry['label_name']), 'w', encoding='utf-8') as f:
                        f.write('\n'.join(entry['label_lines']))
        else:
            imgs_dir = os.path.join(output_dir, 'images')
            labels_dir = os.path.join(output_dir, 'labels')
            self.ensure_dir(imgs_dir)
            self.ensure_dir(labels_dir)
            for entry in self.converted_data:
                shutil.copy(entry['img_path'], os.path.join(imgs_dir, entry['img_name']))
                with open(os.path.join(labels_dir, entry['label_name']), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(entry['label_lines']))

        with open(os.path.join(output_dir, 'dataset.yaml'), 'w', encoding='utf-8') as f:
            f.write(self.dataset_yaml_content)
        with open(os.path.join(output_dir, 'classes.txt'), 'w', encoding='utf-8') as f:
            for c in self.class_names:
                f.write(f'{c}\n')
        print(f'YOLO data exported to {output_dir}')

    def convert_single_file(
        self, data: Dict[str, Any], original_file: IO, class_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Convert a single DM data dict and corresponding image file object to YOLO format.

        Args:
            data: DM format data dictionary (JSON content)
            original_file: File object for the corresponding original image
            class_names: Optional list of class names. If not provided, classes will be extracted from data.

        Returns:
            Dictionary containing YOLO format data for the single file
        """
        if not self.is_single_conversion:
            raise RuntimeError('convert_single_file is only available when is_single_conversion=True')

        if class_names is None:
            classes = set()
            for img_ann in data['images']:
                for k in ['bounding_box', 'polygon', 'keypoint']:
                    if k in img_ann:
                        for ann in img_ann[k]:
                            classes.add(ann['classification'])
            class_names = sorted(list(classes))

        class_map = {name: idx for idx, name in enumerate(class_names)}
        # You need to update get_image_size to accept a file object
        width, height = self.get_image_size(original_file)

        img_ann = data['images'][0]
        label_lines = []

        # bbox
        if 'bounding_box' in img_ann:
            for box in img_ann['bounding_box']:
                if box['classification'] not in class_map:
                    continue
                cidx = class_map[box['classification']]
                x, y, w, h = box['data']
                cx = x + w / 2
                cy = y + h / 2
                cx /= width
                cy /= height
                w /= width
                h /= height
                label_lines.append(f'{cidx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}')

        # polygon
        if 'polygon' in img_ann:
            for poly in img_ann['polygon']:
                if poly['classification'] not in class_map:
                    continue
                cidx = class_map[poly['classification']]
                poly_str = self.polygon_to_yolo_string(poly['data'], width, height)
                if poly_str:
                    label_lines.append(f'{cidx} {poly_str}')

        # keypoint
        if 'keypoint' in img_ann:
            for kp in img_ann['keypoint']:
                if kp['classification'] not in class_map:
                    continue
                cidx = class_map[kp['classification']]
                if 'bounding_box' in kp:
                    x, y, w, h = kp['bounding_box']
                    cx = x + w / 2
                    cy = y + h / 2
                    cx /= width
                    cy /= height
                    w /= width
                    h /= height
                else:
                    cx, cy, w, h = 0.5, 0.5, 1.0, 1.0
                kp_str = self.keypoints_to_yolo_string(kp['data'], width, height)
                label_lines.append(f'{cidx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f} {kp_str}')

        return {
            'label_lines': label_lines,
            'class_names': class_names,
            'class_map': class_map,
        }
