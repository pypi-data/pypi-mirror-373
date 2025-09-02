import os
import json
import yaml
from typing import List
from joblib import load, dump
import inspect
import logging

from .timekeeper import get_timestamp_now_as_string

logger = logging.getLogger(__name__)

def check_and_create_folder(path: str) -> None:
    """
    Checks if the directory for the given file path exists, and creates it if it does not.

    This function ensures that the directory structure for a specified file path is available.
    If the directory does not exist, it will create all the necessary subdirectories.
    Logs information when a directory is successfully created.

    Args:
        path (str): The file path whose directory needs to be checked and potentially created.

    Returns:
        None
    """
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"{directory} created")


def get_folder_name(filepath: str) -> str:
    """
    Extracts the folder name from the provided file path.

    The function takes a file path as input and returns the directory portion 
    of the path, which represents the folder containing the file.

    Args:
        filepath (str): The absolute or relative file path as a string.

    Returns:
        str: The folder or directory name extracted from the given file path.

    Example:
        >>> get_folder_name(filepath='/path/to/file.txt')
        '/path/to'
        >>> get_folder_name(filepath='folder/subfolder/data.csv')
        'folder/subfolder'
    """
    return os.path.dirname(filepath)


def check_file_exists(filepath) -> bool:
    """
    Checks if the specified file exists in the given filepath.

    This function checks the existence of a file at the given filepath
    and returns a boolean indicating whether the file exists.

    :param filepath: The path of the file to check for existence
    :type filepath: str
    :return: True if the file exists, otherwise False
    :rtype: bool
    """
    if not os.path.isfile(filepath):
        return False
    else:
        return True


def get_file_extension(path: str) -> str:
    """
    Retrieve the file extension from the given file path.

    This function extracts and returns the file extension from
    a given file path string. It uses the `os.path.splitext`
    method to split the path and obtain the extension.

    Args:
        path (str): The file path from which to extract the extension.

    Returns:
        str: The file extension, including the leading period.
    """
    return os.path.splitext(path)[1]


def del_file_extension(file_path: str) -> str:
    """
    Removes the extension from a file path.

    The function accepts a file path as input and removes its extension, returning
    the file path without the extension.

    Args:
        file_path (str): The path of the file whose extension is to be removed.

    Returns:
        str: The file path without its extension.
    """
    path, _ = os.path.splitext(file_path)
    return path


def load_file(file_path: str) -> any:
    """
    Loads a file based on the provided path.

    This function provides support for loading files based on the provided path. Supports `.joblib`, `.json`,
    and `.yaml/.yml` file types. Ensures relative file paths are resolved against the current
    working directory if no directory is specified in the given path. Raises ValueError if the file type is not supported.

    Args:
        file_path (str) : Path to the input file.

    Returns:
        The content of the loaded file. The type of the returned content depends on
        the file type and its structure.

    Raises:
        ValueError: Raised if the file type is not supported.
    """
    # Ensure the file path is treated as relative to the current directory if no directory is specified
    if not os.path.isabs(file_path) and not os.path.dirname(file_path):
        file_path = os.path.join(os.getcwd(), file_path)

    file_type = get_file_extension(file_path)

    if file_type == ".joblib":
        return load(filename=file_path)
    elif file_type == ".json":
        with open(file_path, 'r') as file:
            return json.load(file)
    elif file_type == ".yaml" or file_type == ".yml":
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    else:
        logger.warning(f"type {file_type} of file {file_path} not supported yet. File has been ignored.")


def save_file(data: any, path: str, autocreate_folder: bool = True) -> None:
    """
    Saves data to a file at the specified path.

    This function supports saving in JSON, YAML/YML, and
    Joblib formats. If enabled, automatically creates the necessary folder structure
    for the file if it does not already exist. Logs an informational message upon
    successful save.

    Args:
        data (Any): The data to be saved to the file.
        path (str): The file path including the file name and extension where the data should be saved.
        autocreate_folder (bool, optional): If True, automatically creates the folder structure required by the specified path if it does not exist. Defaults to True.

    Raises:
        ValueError : If the file extension is not supported.

    Returns:
        None
    """
    if autocreate_folder:
        check_and_create_folder(path)

    filetype = get_file_extension(path)

    if filetype == ".joblib":
        dump(data, path)
    elif filetype == ".json":
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent=4)
    elif filetype == ".yaml" or filetype == ".yml":
        with open(path, 'w') as outfile:
            yaml.dump(data, outfile)
    else:
        raise ValueError("datatype not supported yet")

    logging.info("File saved to %s", path)


def get_folder_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Retrieves a list of file paths from a specified directory.

    This function returns the file paths in the provided directory as a list. The function can operate
    recursively to include files from subdirectories or non-recursively to include files
    from the top-level directory only.

    Args:
        directory (str): The directory path from which to retrieve the file paths.

        recursive (bool, optional): If True, retrieves files from the directory and all subdirectories. Defaults to True.

    Returns:
        List[str]: A list containing file paths as strings.
    """
    files_list = []
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                files_list.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path):
                files_list.append(full_path)
    return files_list


def get_folder_names(directory: str) -> List[str]:
    # List all entries in the given directory
    all_entries = os.listdir(directory)

    # Filter out only directories
    folder_names = [entry for entry in all_entries if os.path.isdir(os.path.join(directory, entry))]

    return folder_names


from .utils import deep_update


def update_json_file(filepath: str, dictionary: dict) -> None:
    try:
        file_data = load_file(filepath)
        # Update the file data with the new dictionary
        deep_update(file_data, dictionary)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        # If the file doesn't exist or is not a valid JSON, start with an empty dictionary
        file_data = dictionary

    # Save the updated data back to the file
    save_file(file_data, filepath)


def log_to_file(filepath: str, log_entry: str, log_meta: bool = True) -> None:
    """
        Log an entry to a JSON file. If the file exists, append to it; otherwise, create a new file.

        :param file_path: Path to the JSON log file.
        :param log_entry: Dictionary containing the log entry to be added.
    """
    if check_file_exists(filepath):
        logdata = load_file(filepath)
    else:
        logdata = list()

    if log_meta:
        # Get the name of the calling method
        caller_frame = inspect.stack()[1]
        caller_method = caller_frame.function
        caller_filename = caller_frame.filename

        logdata.append(
            {
                'timestamp': get_timestamp_now_as_string(),
                'caller_filename': caller_filename,
                'caller_method': caller_method,
                'log_entry': log_entry
            }
        )
    else:
        logdata.append({
            'log_entry': log_entry
        })

    save_file(logdata, filepath)
