import logging
import os
import traceback

from loguru import logger

from planqk.commons import __version__
from planqk.commons.constants import OUTPUT_DIRECTORY_ENV, INPUT_DIRECTORY_ENV, ENTRYPOINT_ENV, DEFAULT_ENTRYPOINT, DEFAULT_INPUT_DIRECTORY, \
    DEFAULT_OUTPUT_DIRECTORY
from planqk.commons.entrypoint import run_entrypoint
from planqk.commons.file import list_directory_files, write_str_to_file
from planqk.commons.json import any_to_json
from planqk.commons.parameters import files_to_parameters, is_simple_type
from planqk.commons.reflection import resolve_signature


def main() -> int:
    """
    Main function to run the entrypoint of a PLANQK service.

    :return: 0 if successful, 1 otherwise.
    """
    logger.debug(f"planqk-commons Version: {__version__}")

    entrypoint = os.environ.get(ENTRYPOINT_ENV, DEFAULT_ENTRYPOINT)
    entrypoint_signature = resolve_signature(entrypoint)
    logger.debug(f"Entrypoint: {entrypoint}")

    input_directory = os.environ.get(INPUT_DIRECTORY_ENV, DEFAULT_INPUT_DIRECTORY)
    output_directory = os.environ.get(OUTPUT_DIRECTORY_ENV, DEFAULT_OUTPUT_DIRECTORY)

    input_files = list_directory_files(input_directory)
    logger.debug(f"Input files: {list(input_files.values())}")

    input_parameters = files_to_parameters(input_files, entrypoint_signature)

    try:
        return_value = run_entrypoint(entrypoint, input_parameters)
    except Exception as e:
        logger.error(f"{e}")
        if logging.getLogger("main").isEnabledFor(logging.ERROR):
            traceback.print_exc()
        return 1

    logger.debug(f"Return type: {type(return_value)}")

    string_value = any_to_json(return_value)
    if string_value is None:
        return 0

    if is_simple_type(return_value):
        file_path = write_str_to_file(output_directory, "output.txt", string_value)
    else:
        file_path = write_str_to_file(output_directory, "output.json", string_value)
    logger.debug(f"Output file: {file_path}")

    return 0
