import os
from typing import Dict, Any

import yaml


def read_to_dict(file_path: str) -> Dict[str, Any]:
    """
    Read a YAML file and return it as a dictionary.

    :param file_path: The path to the file
    :return: The content of the file as a dictionary
    """
    with open(file_path, "r") as file:
        openapi = yaml.safe_load(file)

    return openapi


def write_dict(directory_path: str, openapi: Dict[str, Any], filename: str = "openapi.yaml"):
    """
    Write a dictionary to a YAML file.

    :param directory_path: The directory where the file should be saved
    :param openapi: The dictionary to be written to the file
    :param filename: The name of the file, defaults to "openapi.yaml"
    """
    file_path = os.path.join(directory_path, filename)
    with open(file_path, "w") as file:
        yaml.dump(openapi, file, sort_keys=False)
