import logging


def remap_class_labels(dataset, data_type, class_pattern, new_class):
    """
    Remaps class labels in a dataset by replacing specific classification patterns.

    This function finds items of a specified data type (e.g., 'pcd', 'image', 'video')
    where the classification matches a given pattern (e.g., 'truck', 'car'), and
    remaps them to a new class label (e.g., 'vehicle'). Useful for consolidating
    or standardizing class labels in ground truth data.

    Args:
        dataset (dict): The dataset containing ground truth labels
        data_type (str): Type of data to process (e.g., 'pcd', 'image', 'video')
        class_pattern (dict): Pattern to identify target classifications (e.g., {'name': 'truck'})
        new_class (dict): New classification to apply (e.g., {'name': 'vehicle'})

    Returns:
        dict: Dataset with remapped class labels
    """
    updated_dataset = dataset.copy()

    if data_type not in updated_dataset:
        logging.log(logging.WARNING, f"Data type '{data_type}' not found in dataset.")
        return updated_dataset

    def matches_pattern(classification, pattern):
        """Check if a classification matches the specified pattern."""
        for key, pattern_value in pattern.items():
            if key not in classification:
                return False

            if isinstance(pattern_value, dict) and isinstance(classification[key], dict):
                if not matches_pattern(classification[key], pattern_value):
                    return False
            elif classification[key] != pattern_value:
                return False

        return True

    for item in updated_dataset[data_type]:
        if 'classification' in item and matches_pattern(item['classification'], class_pattern):
            item['classification'] = new_class.copy()

    return updated_dataset
