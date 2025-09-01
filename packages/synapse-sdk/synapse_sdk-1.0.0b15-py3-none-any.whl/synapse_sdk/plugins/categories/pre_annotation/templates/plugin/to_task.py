class AnnotationToTask:
    def __init__(self, run, *args, **kwargs):
        """Initialize the plugin task pre annotation action class.

        Args:
            run: Plugin run object.
        """
        self.run = run

    def convert_data_from_file(
        self,
        primary_file_url: str,
        primary_file_original_name: str,
        data_file_url: str,
        data_file_original_name: str,
    ) -> dict:
        """Convert the data from a file to a task object.

        Args:
            primary_file_url (str): primary file url.
            primary_file_original_name (str): primary file original name.
            data_file_url (str): data file url.
            data_file_original_name (str): data file original name.

        Returns:
            dict: The converted data.
        """
        converted_data = {}
        return converted_data

    def convert_data_from_inference(self, data: dict) -> dict:
        """Convert the data from inference result to a task object.

        Args:
            data: Converted data.

        Returns:
            dict: The converted data.
        """
        return data
