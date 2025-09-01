import json
import os
import shutil
import xml.etree.ElementTree as ET
from glob import glob
from typing import IO, Any, Dict, List, Optional

from PIL import Image

from synapse_sdk.utils.converters import FromDMConverter


class FromDMToPascalConverter(FromDMConverter):
    """Convert DM format to Pascal VOC format."""

    IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']

    def __init__(self, root_dir: str = None, is_categorized_dataset: bool = False, is_single_conversion: bool = False):
        super().__init__(root_dir, is_categorized_dataset, is_single_conversion)
        self.class_names = set()

    def find_image_for_base(self, img_dir: str, base: str) -> Optional[str]:
        """Find the image file for a given base name in the specified directory."""
        for ext in self.IMG_EXTENSIONS:
            img_path = os.path.join(img_dir, base + ext)
            if os.path.exists(img_path):
                return img_path
        return None

    def build_pascal_xml(
        self, img_filename: str, img_size: tuple, objects: List[dict], has_segmentation: bool = None
    ) -> ET.ElementTree:
        """Build a Pascal VOC XML tree from image filename, size, and objects."""
        folder = 'Images'
        width, height, depth = img_size
        annotation = ET.Element('annotation')
        ET.SubElement(annotation, 'folder').text = folder
        ET.SubElement(annotation, 'filename').text = img_filename
        ET.SubElement(annotation, 'path').text = img_filename
        source = ET.SubElement(annotation, 'source')
        ET.SubElement(source, 'database').text = 'Unknown'
        size = ET.SubElement(annotation, 'size')
        ET.SubElement(size, 'width').text = str(width)
        ET.SubElement(size, 'height').text = str(height)
        ET.SubElement(size, 'depth').text = str(depth)

        # Set segmented to 1 if there are any segmentation objects, 0 otherwise
        if has_segmentation is None:
            has_segmentation = any(obj.get('has_segmentation', False) for obj in objects)
        ET.SubElement(annotation, 'segmented').text = '1' if has_segmentation else '0'

        for obj in objects:
            obj_elem = ET.SubElement(annotation, 'object')
            ET.SubElement(obj_elem, 'name').text = obj['name']
            ET.SubElement(obj_elem, 'pose').text = 'Unspecified'
            ET.SubElement(obj_elem, 'truncated').text = '0'
            ET.SubElement(obj_elem, 'difficult').text = '0'
            bndbox = ET.SubElement(obj_elem, 'bndbox')
            ET.SubElement(bndbox, 'xmin').text = str(obj['xmin'])
            ET.SubElement(bndbox, 'ymin').text = str(obj['ymin'])
            ET.SubElement(bndbox, 'xmax').text = str(obj['xmax'])
            ET.SubElement(bndbox, 'ymax').text = str(obj['ymax'])
        return ET.ElementTree(annotation)

    def parse_dm_annotations(self, annotation: dict):
        """Parse DM annotations and convert to Pascal VOC format."""
        objects = []
        has_segmentation = 'segmentation' in annotation

        # Only include bounding_box (Pascal VOC does not support polyline/keypoint by default)
        if 'bounding_box' in annotation:
            for box in annotation['bounding_box']:
                class_name = box['classification']
                x, y, w, h = box['data']
                xmin = int(round(x))
                ymin = int(round(y))
                xmax = int(round(x + w))
                ymax = int(round(y + h))
                objects.append({
                    'name': class_name,
                    'xmin': xmin,
                    'ymin': ymin,
                    'xmax': xmax,
                    'ymax': ymax,
                    'has_segmentation': has_segmentation,
                })
                self.class_names.add(class_name)

        # polyline, keypoint 등은 무시
        return objects, has_segmentation

    def _convert_split_dir(self, split_dir: str, split_name: str):
        """Convert a split dir (train/valid/test) to list of (xml_tree, xml_filename, img_src, img_name)."""
        json_dir = os.path.join(split_dir, 'json')
        img_dir = os.path.join(split_dir, 'original_files')
        results = []
        for jfile in glob(os.path.join(json_dir, '*.json')):
            base = os.path.splitext(os.path.basename(jfile))[0]
            img_path = self.find_image_for_base(img_dir, base)
            if not img_path:
                print(f'[{split_name}] Image for {base} not found, skipping.')
                continue
            with open(jfile, encoding='utf-8') as jf:
                data = json.load(jf)
            img_ann = data['images'][0]
            with Image.open(img_path) as img:
                width, height = img.size
                depth = len(img.getbands())
            objects, has_segmentation = self.parse_dm_annotations(img_ann)
            xml_tree = self.build_pascal_xml(
                os.path.basename(img_path), (width, height, depth), objects, has_segmentation
            )
            xml_filename = base + '.xml'
            results.append((xml_tree, xml_filename, img_path, os.path.basename(img_path)))
        return results

    def _convert_root_dir(self):
        """Convert non-categorized dataset to list of (xml_tree, xml_filename, img_src, img_name)."""
        json_dir = os.path.join(self.root_dir, 'json')
        img_dir = os.path.join(self.root_dir, 'original_files')
        results = []
        for jfile in glob(os.path.join(json_dir, '*.json')):
            base = os.path.splitext(os.path.basename(jfile))[0]
            img_path = self.find_image_for_base(img_dir, base)
            if not img_path:
                print(f'[Pascal] Image for {base} not found, skipping.')
                continue
            with open(jfile, encoding='utf-8') as jf:
                data = json.load(jf)
            img_ann = data['images'][0]
            with Image.open(img_path) as img:
                width, height = img.size
                depth = len(img.getbands())
            objects, has_segmentation = self.parse_dm_annotations(img_ann)
            xml_tree = self.build_pascal_xml(
                os.path.basename(img_path), (width, height, depth), objects, has_segmentation
            )
            xml_filename = base + '.xml'
            results.append((xml_tree, xml_filename, img_path, os.path.basename(img_path)))
        return results

    def convert(self) -> Any:
        """Converts DM format to Pascal VOC format.

        Returns:
            - If categorized: dict {split: list of (xml_tree, xml_filename, img_src, img_name)}
            - If not: list of (xml_tree, xml_filename, img_src, img_name)
        """
        self.class_names = set()
        if self.is_categorized_dataset:
            splits = self._validate_splits(['train', 'valid'], ['test'])
            result = {}
            for split, split_dir in splits.items():
                result[split] = self._convert_split_dir(split_dir, split)
            self.converted_data = result
            return result
        else:
            self._validate_splits([], [])
            result = self._convert_root_dir()
            self.converted_data = result
            return result

    def save_to_folder(self, output_dir: Optional[str] = None):
        """Save all Pascal VOC XML/Images to output_dir (Annotations, Images).
        - If categorized: per split under output_dir/{split}/{Annotations, Images}
        - If not: directly under output_dir/{Annotations, Images}
        """
        outdir = output_dir or self.root_dir
        self.ensure_dir(outdir)
        if self.converted_data is None:
            self.converted_data = self.convert()

        if self.is_categorized_dataset:
            for split, entries in self.converted_data.items():
                ann_dir = os.path.join(outdir, split, 'Annotations')
                img_dir = os.path.join(outdir, split, 'Images')
                os.makedirs(ann_dir, exist_ok=True)
                os.makedirs(img_dir, exist_ok=True)
                for xml_tree, xml_filename, img_src, img_name in entries:
                    xml_tree.write(os.path.join(ann_dir, xml_filename), encoding='utf-8', xml_declaration=True)
                    dst_path = os.path.join(img_dir, img_name)
                    if os.path.abspath(img_src) != os.path.abspath(dst_path):
                        shutil.copy(img_src, dst_path)
        else:
            ann_dir = os.path.join(outdir, 'Annotations')
            img_dir = os.path.join(outdir, 'Images')
            os.makedirs(ann_dir, exist_ok=True)
            os.makedirs(img_dir, exist_ok=True)
            for xml_tree, xml_filename, img_src, img_name in self.converted_data:
                xml_tree.write(os.path.join(ann_dir, xml_filename), encoding='utf-8', xml_declaration=True)
                dst_path = os.path.join(img_dir, img_name)
                if os.path.abspath(img_src) != os.path.abspath(dst_path):
                    shutil.copy(img_src, dst_path)
        # Save classes.txt
        with open(os.path.join(outdir, 'classes.txt'), 'w', encoding='utf-8') as f:
            for c in sorted(self.class_names):
                f.write(f'{c}\n')
        print(f'Pascal VOC data exported to {outdir}')

    def convert_single_file(self, data: Dict[str, Any], original_file: IO) -> Dict[str, Any]:
        """Convert a single DM data dict and corresponding image file object to Pascal VOC format.

        Args:
            data: DM format data dictionary (JSON content)
            original_file: File object for the corresponding original image

        Returns:
            Dictionary containing Pascal VOC format data for the single file
        """
        if not self.is_single_conversion:
            raise RuntimeError('convert_single_file is only available when is_single_conversion=True')

        # Extract image info from file object
        with Image.open(original_file) as img:
            width, height = img.size
            depth = len(img.getbands())

        # Get filename from original_file
        img_filename = getattr(original_file, 'name', 'image.jpg')
        if img_filename:
            img_filename = os.path.basename(img_filename)

        # Process annotations from the first (and only) image in data
        if 'images' in data and len(data['images']) > 0:
            img_ann = data['images'][0]
            objects, has_segmentation = self.parse_dm_annotations(img_ann)
        else:
            objects = []
            has_segmentation = False

        # Build Pascal VOC XML
        xml_tree = self.build_pascal_xml(img_filename, (width, height, depth), objects, has_segmentation)
        xml_filename = os.path.splitext(img_filename)[0] + '.xml'

        # Convert XML tree to string for easy viewing
        xml_string = ET.tostring(xml_tree.getroot(), encoding='unicode', xml_declaration=True)

        return {
            'xml_tree': xml_tree,
            'xml_content': xml_string,
            'xml_filename': xml_filename,
            'image_filename': img_filename,
            'class_names': sorted(list(self.class_names)),
        }
