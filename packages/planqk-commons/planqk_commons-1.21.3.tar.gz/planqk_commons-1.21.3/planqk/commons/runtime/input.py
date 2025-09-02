import os
from typing import List

from planqk.commons.constants import INPUT_DIRECTORY_ENV, DEFAULT_INPUT_DIRECTORY
from planqk.commons.file import list_directory_files


def read_input_as_string(file_or_attribute: str, input_directories: List[str] = None) -> str:
    """
    Read the content of a file from the input directory as a string.

    :param file_or_attribute: The name of the file or attribute (API) to read.
    :param input_directories: The directories to search for the file. If None, the environment variable INPUT_DIRECTORY is used.
    :return: The content of the file as a string.
    """
    if input_directories is None:
        input_directory = os.environ.get(INPUT_DIRECTORY_ENV, DEFAULT_INPUT_DIRECTORY)
        input_directories = [input_directory]

    # find first input directory that exists
    for input_directory in input_directories:
        if os.path.exists(input_directory):
            input_directory = os.path.abspath(input_directory)
            break
    else:
        raise FileNotFoundError(f"None of the input directories exist: {input_directories}")

    # remove possible file extension
    name = file_or_attribute.split(".")[0]

    input_files = list_directory_files(input_directory)

    if name not in input_files:
        raise FileNotFoundError(f"File '{name}' not found in input directory '{input_directory}'")

    with open(input_files[name], "r") as file:
        file_content = file.read()

    return file_content
