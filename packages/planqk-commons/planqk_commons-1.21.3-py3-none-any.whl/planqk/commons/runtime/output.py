import os
from typing import ByteString, Union, Any

from planqk.commons.constants import OUTPUT_DIRECTORY_ENV, DEFAULT_OUTPUT_DIRECTORY
from planqk.commons.file import write_str_to_file, write_blob_to_file
from planqk.commons.json import any_to_json


def write_string_output(file_name: str, content: str):
    """
    Write a string to a file in the output directory.

    :param file_name: The name of the file.
    :param content: The content to write to the file.
    """
    directory_path = os.environ.get(OUTPUT_DIRECTORY_ENV, DEFAULT_OUTPUT_DIRECTORY)
    write_str_to_file(directory_path, file_name, content)


def write_binary_output(file_name: str, content: Union[bytes, bytearray, ByteString]):
    """
    Write a binary blob to a file in the output directory.

    :param file_name: The name of the file.
    :param content: The content to write to the file.
    """
    directory_path = os.environ.get(OUTPUT_DIRECTORY_ENV, DEFAULT_OUTPUT_DIRECTORY)
    write_blob_to_file(directory_path, file_name, content)


def print_output(content: Any):
    """
    Print the content as JSON. Wraps the output in a PlanQK:Job:MultilineResult block.

    :param content: The content to print. Must be JSON serializable.
    """
    output = any_to_json(content)

    if output:
        print(f"PlanQK:Job:MultilineResult\n{output}\nPlanQK:Job:MultilineResult")
