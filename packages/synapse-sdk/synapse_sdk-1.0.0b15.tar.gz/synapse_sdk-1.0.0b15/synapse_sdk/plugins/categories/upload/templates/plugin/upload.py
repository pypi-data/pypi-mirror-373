from pathlib import Path
from typing import List


class Uploader:
    """Plugin upload action interface for organizing files.

    This class provides a minimal interface for plugin developers to implement
    their own file organization logic.
    """

    def __init__(self, run, path: Path, file_specification: List = None, organized_files: List = None):
        """Initialize the plugin upload action class.

        Args:
            run: Plugin run object with logging capabilities.
            path: Path object pointing to the upload target directory.
            file_specification: List of specifications that define the structure of files to be uploaded.
                Each specification contains details like file name, type, and requirements.
        """
        self.run = run
        self.path = path
        self.file_specification = file_specification
        self.organized_files = organized_files

    def handle_upload_files(self) -> List:
        """Customize the organization of files for upload.

        This method provides a hook for plugin developers to modify the default file organization.
        You can override this method to filter files, transform data, or add custom metadata
        based on your specific requirements.

        Args:
            organized_files (List): The default organized files structure.
                Each item is a dictionary with 'files' and 'meta' keys.

        Returns:
            List: The modified list of organized files to be uploaded.
        """
        return self.organized_files
