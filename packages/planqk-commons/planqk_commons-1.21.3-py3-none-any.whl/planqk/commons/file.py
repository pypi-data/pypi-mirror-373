import os
from typing import Dict, Union, ByteString


def list_directory_files(directory_path: str, strip_extension_from_key: bool = True) -> Dict[str, str]:
    """
    List all files in a directory and return a dictionary with the file name as key and the absolute path as value.

    :param directory_path: The path to the directory.
    :param strip_extension_from_key: Whether to remove the file extension from the key or not.
    :return: Dictionary with file name as key and absolute path as value.
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Path \"{directory_path}\" must be a directory")

    try:
        files = {}
        for f in os.listdir(directory_path):
            file_path = os.path.join(directory_path, f)
            if os.path.isfile(file_path):
                absolute_path = os.path.abspath(file_path)

                # remove file extension from file name
                if strip_extension_from_key:
                    f = f.split(".")[0]

                files[f] = absolute_path
        return files
    except FileNotFoundError:
        return {}


def write_str_to_file(directory_path: str, file_name: str, content: str) -> str:
    """
    Write a string to a file in a directory.

    :param directory_path: The path to the directory.
    :param file_name: The name of the file.
    :param content: The content to write to the file.
    :return: The absolute path to the created file.
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Path \"{directory_path}\" must be a directory")

    file_path = os.path.join(directory_path, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    return file_path


def write_blob_to_file(directory_path: str, file_name: str, content: Union[bytes, bytearray, ByteString]) -> str:
    """
    Write a binary blob to a file in a directory.

    :param directory_path: The path to the directory.
    :param file_name: The name of the file.
    :param content: The content to write to the file.
    :return: The absolute path to the created file.
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Path \"{directory_path}\" must be a directory")

    file_path = os.path.join(directory_path, file_name)
    with open(file_path, "wb") as file:
        file.write(content)

    return file_path
