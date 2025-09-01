import json
from itertools import tee
from pathlib import Path

import requests

from synapse_sdk.plugins.categories.export.enums import ExportStatus


def export(run, export_items, path_root, **params):
    """Executes the export task.

    Args:
        run : Execution object
        export_items (generator):
            - data (dict): dm_schema_data information.
            - files (dict): File information. Includes file URL, original file path, metadata, etc.
            - id (int): ground_truth ID
        path_root : pathlib object, the path to export
        **params: Additional parameters

    Returns:
        dict: Result
    """

    export_path = path_root / params['name']
    unique_export_path = export_path
    counter = 1
    while unique_export_path.exists():
        unique_export_path = export_path.with_name(f'{export_path.name}({counter})')
        counter += 1
    unique_export_path.mkdir(parents=True)

    run.log_message('Starting export process.')

    # results contains all information fetched through the list API.
    # example:
    #   params.get('results', [])

    save_original_file_flag = params.get('save_original_file')
    errors_json_file_list = []
    errors_original_file_list = []

    # Path to save JSON files
    json_output_path = unique_export_path / 'json'
    json_output_path.mkdir(parents=True, exist_ok=True)

    # Path to save original files
    if save_original_file_flag:
        origin_files_output_path = unique_export_path / 'origin_files'
        origin_files_output_path.mkdir(parents=True, exist_ok=True)

    export_items_count, export_items_process = tee(export_items)
    total = sum(1 for _ in export_items_count)

    original_file_metrics_record = run.MetricsRecord(stand_by=total, success=0, failed=0)
    data_file_metrics_record = run.MetricsRecord(stand_by=total, success=0, failed=0)
    # progress init
    run.set_progress(0, total, category='dataset_conversion')
    for no, export_item in enumerate(export_items_process, start=1):
        run.set_progress(no, total, category='dataset_conversion')
        if no == 1:
            run.log_message('Converting dataset.')
        preprocessed_data = before_convert(export_item)
        converted_data = convert_data(preprocessed_data)
        final_data = after_convert(converted_data)

        # Call if original file extraction is needed
        if save_original_file_flag:
            if no == 1:
                run.log_message('Saving original file.')
            original_status = save_original_file(run, final_data, origin_files_output_path, errors_original_file_list)

            original_file_metrics_record.stand_by -= 1
            if original_status == ExportStatus.FAILED:
                original_file_metrics_record.failed += 1
                continue
            else:
                original_file_metrics_record.success += 1

        run.log_metrics(record=original_file_metrics_record, category='original_file')

        # Extract data as JSON files
        if no == 1:
            run.log_message('Saving json file.')
        data_status = save_as_json(run, final_data, json_output_path, errors_json_file_list)

        data_file_metrics_record.stand_by -= 1
        if data_status == ExportStatus.FAILED:
            data_file_metrics_record.failed += 1
            continue
        else:
            data_file_metrics_record.success += 1

        run.log_metrics(record=data_file_metrics_record, category='data_file')

    run.end_log()

    # Save error list files
    if len(errors_json_file_list) > 0 or len(errors_original_file_list) > 0:
        export_error_file = {'json_file_name': errors_json_file_list, 'origin_file_name': errors_original_file_list}
        with (unique_export_path / 'error_file_list.json').open('w', encoding='utf-8') as f:
            json.dump(export_error_file, f, indent=4, ensure_ascii=False)

    return {'export_path': str(path_root)}


def convert_data(data):
    """Converts the data."""
    return data


def before_convert(data):
    """Preprocesses the data before conversion."""
    return data


def after_convert(data):
    """Post-processes the data after conversion."""
    return data


def get_original_file_name(files):
    """Retrieve the original file path from the given file information.

    Args:
        files (dict): A dictionary containing file information, including file URL,
                      original file path, metadata, etc.

    Returns:
        file_name (str): The original file name extracted from the file information.
    """
    return files['file_name_original']


def save_original_file(run, result, base_path, error_file_list):
    """Saves the original file.

    Args:
        run : Execution object
        result (dict): API response data containing file information.
        base_path (Path): The directory where the file will be saved.
        error_file_list (list): A list to store error files.
    """
    file_url = result['files']['url']
    file_name = get_original_file_name(result['files'])
    response = requests.get(file_url)
    file_info = {'file_name': file_name}
    error_msg = ''
    try:
        with (base_path / file_name).open('wb') as file:
            file.write(response.content)
        status = ExportStatus.SUCCESS
    except Exception as e:
        error_msg = str(e)
        error_file_list.append([file_name, error_msg])
        status = ExportStatus.FAILED

    run.export_log_original_file(result['id'], file_info, status, error_msg)
    return status


def save_as_json(run, result, base_path, error_file_list):
    """Saves the data as a JSON file.

    Args:
        run : Execution object
        result (dict): API response data containing file information.
        base_path (Path): The directory where the file will be saved.
        error_file_list (list): A list to store error files.
    """
    # Default save file name: original file name
    file_name = Path(get_original_file_name(result['files'])).stem
    json_data = result['data']
    file_info = {'file_name': f'{file_name}.json'}

    if json_data is None:
        error_msg = 'data is Null'
        error_file_list.append([f'{file_name}.json', error_msg])
        status = ExportStatus.FAILED
        run.log_export_event('NULL_DATA_DETECTED', result['id'])
        run.export_log_json_file(result['id'], file_info, status, error_msg)

        return status

    error_msg = ''
    try:
        with (base_path / f'{file_name}.json').open('w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        status = ExportStatus.SUCCESS
    except Exception as e:
        error_msg = str(e)
        error_file_list.append([f'{file_name}.json', str(e)])
        status = ExportStatus.FAILED

    run.export_log_json_file(result['id'], file_info, status, error_msg)
    return status
