import json
import os
import shutil
import uuid
from typing import IO


class BaseConverter:
    """Base class for shared logic between converters."""

    def __init__(
        self, root_dir: str = None, is_categorized_dataset: bool = False, is_single_conversion: bool = False
    ) -> None:
        self.root_dir: str = root_dir
        self.is_categorized_dataset: bool = is_categorized_dataset
        self.is_single_conversion: bool = is_single_conversion
        self.converted_data = None

        # Set directories if single_conversion is False.
        if not is_single_conversion:
            if not root_dir:
                raise ValueError('root_dir must be specified for conversion')

    @staticmethod
    def ensure_dir(path: str) -> None:
        """Ensure that the directory exists, creating it if necessary."""
        if not os.path.exists(path):
            os.makedirs(path)

    def _validate_required_dirs(self, dirs):
        """Validate that all required directories exist."""
        for name, path in dirs.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f'[ERROR] Required directory "{name}" does not exist at {path}')

    def _validate_optional_dirs(self, dirs):
        """Validate optional directories and return those that exist."""
        existing_dirs = {}
        for name, path in dirs.items():
            if os.path.exists(path):
                existing_dirs[name] = path
            else:
                print(f'[WARNING] Optional directory "{name}" does not exist. Skipping.')
        return existing_dirs

    def _validate_splits(self, required_splits, optional_splits=[]):
        """Validate required and optional splits in the dataset."""
        splits = {}

        if self.is_categorized_dataset:
            required_dirs = {split: os.path.join(self.root_dir, split) for split in required_splits}
            self._validate_required_dirs(required_dirs)
            splits.update(required_dirs)

            optional_dirs = {split: os.path.join(self.root_dir, split) for split in optional_splits}
            splits.update(self._validate_optional_dirs(optional_dirs))
        else:
            required_dirs = {
                'json': os.path.join(self.root_dir, 'json'),
                'original_files': os.path.join(self.root_dir, 'original_files'),
            }
            self._validate_required_dirs(required_dirs)
            splits['root'] = self.root_dir

        return splits

    def convert_single_file(self, data, original_file: IO, **kwargs):
        """Convert a single data object and corresponding original file.

        This method should be implemented by subclasses for single file conversion.
        Only available when is_single_conversion=True.

        Args:
            data: The data object to convert (dict for JSON data, etc.)
            original_file_path: File object for the corresponding original file
            **kwargs: Additional parameters specific to each converter

        Returns:
            Converted data in the target format
        """
        if not self.is_single_conversion:
            raise RuntimeError('convert_single_file is only available when is_single_conversion=True')
        raise NotImplementedError('Subclasses must implement convert_single_file method')

    def _set_directories(self, split=None):
        """Set `self.json_dir` and `self.original_file_dir` based on the dataset split."""
        if split:
            split_dir = os.path.join(self.root_dir, split)
            self.json_dir = os.path.join(split_dir, 'json')
            self.original_file_dir = os.path.join(split_dir, 'original_files')
        else:
            self.json_dir = os.path.join(self.root_dir, 'json')
            self.original_file_dir = os.path.join(self.root_dir, 'original_files')


class FromDMConverter(BaseConverter):
    """Base class for converting data from DM format to a specific format.

    Attrs:
        root_dir (str): Root directory containing data.
        is_categorized_dataset (bool): Whether to handle train, test, valid splits.
        version (str): Version of the converter.
        converted_data: Holds the converted data after calling `convert()`.

    Usage:
        1. Subclass this base class and implement the `convert()` and `save_to_folder()` methods.
        2. Instantiate the converter with the required arguments.
        3. Call `convert()` to perform the in-memory conversion and obtain the result as a dict or list of dicts.
        4. Call `save_to_folder(output_dir)` to save the converted data and optionally copy original files.

    Args:
        root_dir (str): Path to the root directory containing data.
            - If `is_categorized_dataset=True`, the directory should contain subdirectories for
            `train`, `valid`, and optionally `test`.
            - Each subdirectory should contain `json` and `original_file` folders.
            - `train` and `valid` are required, while `test` is optional.
        is_categorized_dataset (bool): Whether to handle train, test, valid splits.

    Returns:
        - convert(): Returns the converted data as a Python dict or a dictionary with keys for each split.
        - save_to_folder(): Saves the converted data and optionally copies original files
        to the specified output directory.

    Example usage:
        # Dataset with splits
        converter = MyCustomConverter(root_dir='/path/to/data', is_categorized_dataset=True)
        converted = converter.convert()  # Returns a dict with keys for `train`, `valid`, and optionally `test`
        converter.save_to_folder('/my/target/output')  # Writes files/folders to output location

        # Dataset without splits
        converter = MyCustomConverter(root_dir='/path/to/data', is_categorized_dataset=False)
        converted = converter.convert()  # Returns a dict or a list, depending on the implementation
        converter.save_to_folder('/my/target/output')  # Writes files/folders to output location
    """

    def __init__(
        self, root_dir: str = None, is_categorized_dataset: bool = False, is_single_conversion: bool = False
    ) -> None:
        super().__init__(root_dir, is_categorized_dataset, is_single_conversion)
        self.version: str = '1.0'

    def convert(self):
        """Convert DM format to a specific format.

        This method should be implemented by subclasses to perform the actual conversion.
        """
        raise NotImplementedError

    def save_to_folder(self, output_dir: str) -> None:
        """Save converted data to the specified folder."""
        self.ensure_dir(output_dir)
        if self.converted_data is None:
            # Automatically call convert() if converted_data is not set
            self.converted_data = self.convert()


class ToDMConverter(BaseConverter):
    """Base class for converting data to DM format.

    Attrs:
        root_dir (str): Root directory containing data.
        is_categorized_dataset (bool): Whether to handle train, test, valid splits.
        converted_data: Holds the converted data after calling `convert()`.

    Usage:
        1. Subclass this base class and implement the `convert()` method.
        2. Instantiate the converter with the required arguments.
        3. Call `convert()` to perform the in-memory conversion and obtain the result as a dict or list of dicts.
        4. Call `save_to_folder(output_dir)` to save the converted data and optionally copy original files.

    Args:
        root_dir (str): Path to the root directory containing data.
            - If `is_categorized_dataset=True`, the directory should contain subdirectories for
            `train`, `valid`, and optionally `test`.
            - Each subdirectory should contain `annotations.json` and the corresponding image files.
            - `train` and `valid` are required, while `test` is optional.
        is_categorized_dataset (bool): Whether to handle train, test, valid splits.

    Returns:
        - convert(): Returns the converted data as a Python dict or a dictionary with keys for each split.
        - save_to_folder(): Saves the converted data and optionally copies original files
        to the specified output directory.

    Example usage:
        # Dataset with splits
        converter = MyCustomToDMConverter(root_dir='/path/to/data', is_categorized_dataset=True)
        converted = converter.convert()  # Returns a dict with keys for `train`, `valid`, and optionally `test`
        converter.save_to_folder('/my/target/output')  # Writes files/folders to output location

        # Dataset without splits
        converter = MyCustomToDMConverter(root_dir='/path/to/data', is_categorized_dataset=False)
        converted = converter.convert()  # Returns a dict or a list, depending on the implementation
        converter.save_to_folder('/my/target/output')  # Writes files/folders to output location
    """

    def convert(self):
        """Convert data to DM format.

        This method should be implemented by subclasses to perform the actual conversion.
        """
        raise NotImplementedError

    def _generate_unique_id(self):
        """Generate a unique 10-character UUID."""
        return uuid.uuid4().hex[:10]

    def save_to_folder(self, output_dir: str) -> None:
        """Save converted DM schema data to the specified folder."""
        self.ensure_dir(output_dir)
        if self.converted_data is None:
            self.converted_data = self.convert()

        if self.is_categorized_dataset:
            for split, img_dict in self.converted_data.items():
                split_dir = os.path.join(output_dir, split)
                json_dir = os.path.join(split_dir, 'json')
                original_file_dir = os.path.join(split_dir, 'original_files')
                self.ensure_dir(json_dir)
                self.ensure_dir(original_file_dir)
                for img_filename, (dm_json, img_src_path) in img_dict.items():
                    json_filename = os.path.splitext(img_filename)[0] + '.json'
                    with open(os.path.join(json_dir, json_filename), 'w', encoding='utf-8') as jf:
                        json.dump(dm_json, jf, indent=2, ensure_ascii=False)
                    if img_src_path:
                        if not os.path.exists(img_src_path):
                            raise FileNotFoundError(f'Source file does not exist: {img_src_path}')
                        shutil.copy(img_src_path, os.path.join(original_file_dir, img_filename))
        else:
            json_dir = os.path.join(output_dir, 'json')
            original_file_dir = os.path.join(output_dir, 'original_files')
            self.ensure_dir(json_dir)
            self.ensure_dir(original_file_dir)
            for img_filename, (dm_json, img_src_path) in self.converted_data.items():
                json_filename = os.path.splitext(img_filename)[0] + '.json'
                with open(os.path.join(json_dir, json_filename), 'w', encoding='utf-8') as jf:
                    json.dump(dm_json, jf, indent=2, ensure_ascii=False)
                if img_src_path and os.path.exists(img_src_path):
                    shutil.copy(img_src_path, os.path.join(original_file_dir, img_filename))

        print(f'[DM] Data exported to {output_dir}')
