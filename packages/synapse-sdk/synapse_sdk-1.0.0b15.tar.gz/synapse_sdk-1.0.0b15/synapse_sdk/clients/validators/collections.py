class FileSpecificationValidator:
    """File specification validator class for synapse backend collection.

    Args:
        file_spec_template (list):
            * List of dictionaries containing file specification template
            * This is from synapse-backend file specification data.
        organized_files (list): List of dictionaries containing organized files.
    """

    def __init__(self, file_spec_template, organized_files):
        self.file_spec_template = file_spec_template
        self.organized_files = organized_files

    def validate(self):
        """Validate the file specification template with organized files.

        Returns:
            bool: True if the file specification template is valid, False otherwise.
        """
        for spec in self.file_spec_template:
            spec_name = spec['name']
            is_required = spec['is_required']

            for file_group in self.organized_files:
                files = file_group['files']
                if is_required and spec_name not in files:
                    return False
                if spec_name in files and not files[spec_name]:
                    return False
        return True
