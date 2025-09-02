"""
Parameter mapping utilities for PLANQK runtime system.

This module provides functions to map input files to function parameters,
including support for DataPool parameter injection.
"""
import json
import os
from inspect import Signature, Parameter
from typing import Any, Dict, get_origin, get_args, Union, Optional

from loguru import logger
from pydantic import BaseModel

from planqk.commons.datapool import DataPool


def files_to_parameters(input_files: Dict[str, str], signature: Signature) -> Dict[str, Any]:
    """
    Maps input files to parameters of a function signature. If a parameter is not found in the input files,
    the default value of the parameter is used. If the parameter is optional and has no default value,
    it is set to None.

    DataPool parameters are automatically injected based on parameter name and type annotation.

    :param input_files: The input files to be mapped to the parameters.
                        The keys are the parameter names. The values are the file paths.
    :param signature: The signature of the function to which the input files should be mapped.
    :return: A dictionary containing the parameters of the function with input files mapped to them.
    """
    parameters = {}

    logger.debug(f"Found input files: {list(input_files.keys())}")
    logger.debug(f"Parameters in signature: {list(signature.parameters.keys())}")

    for parameter in signature.parameters.values():
        parameter_name = parameter.name
        parameter_type = parameter.annotation

        # Check if parameter is DataPool type
        if is_datapool_type(parameter_type):
            try:
                datapool_instance = create_datapool_instance(parameter_name)
                parameters[parameter_name] = datapool_instance
            except (FileNotFoundError, NotADirectoryError) as e:
                logger.warning(
                    f"DataPool directory not found for parameter '{parameter_name}': {e}"
                )
                if is_optional_type(parameter_type):
                    parameters[parameter_name] = None
                else:
                    # For required DataPool parameters, we might want to fail fast
                    raise
            continue

        if parameter_name not in input_files:
            try:
                parameters[parameter_name] = map_default(parameter)
            except TypeError:
                pass
            continue

        parameters[parameter_name] = map_input_file(input_files[parameter_name], parameter)

    return parameters


def map_input_file(input_file: str, parameter: Parameter) -> Any:
    """
    Maps an input file to a parameter of a function signature.

    :param input_file: The path to the input file.
    :param parameter: The parameter to which the input file should be mapped.
    :return: The value of the input file as the type of the parameter.
    """
    parameter_type = parameter.annotation

    origin = get_origin(parameter_type)
    if origin:
        parameter_type = origin

    with open(input_file, "r", encoding="utf-8") as file:
        file_content = file.read()

    return str_to_parameter_type(file_content, parameter_type)


def map_default(parameter: Parameter) -> Any:
    """
    Maps the default value of a parameter to the parameter type.

    :param parameter: The parameter for which the default value should be mapped.
    :return: The default value of the parameter.
    """
    parameter_type = parameter.annotation

    # use default value if available
    if parameter.default != parameter.empty:
        return parameter.default

    # if optional w/o default, set to None
    if is_optional_type(parameter_type):
        return None

    # if it is a Pydantic model, try to create an empty instance (using defaults if available)
    if issubclass(parameter_type, BaseModel):
        return parameter_type.model_validate_json("{}")

    raise TypeError(f"Could not find a default value for parameter '{parameter.name}' of type '{parameter_type}'")


def str_to_parameter_type(data: str, parameter_type: Any) -> Any:
    """
    Converts a string to a parameter type.

    :param data: The string to be converted.
    :param parameter_type: The type to which the string should be converted.
    :return: The value of the string as the type of the parameter.
    """
    if issubclass(parameter_type, str):
        return data

    if issubclass(parameter_type, bool):
        return bool(data)

    if issubclass(parameter_type, int):
        return int(data)

    if issubclass(parameter_type, float):
        return float(data)

    if issubclass(parameter_type, (list, dict)):
        return json.loads(data)

    if issubclass(parameter_type, BaseModel):
        return parameter_type.model_validate_json(data)

    raise ValueError(f"Type {parameter_type} is not supported")


def is_simple_type(value: Any) -> bool:
    """
    Checks if the value is a simple type (str, int, float, bool).
    """
    return isinstance(value, (str, int, float, bool))


def is_container_type(value: Any) -> bool:
    """
    Checks if the value is a container type (list, tuple, Union, Optional).
    """
    return value is list or value is tuple or value is Union or value is Optional


def is_optional_type(value: Any) -> bool:
    """
    Checks if the value is an optional type (Union with None or Optional).
    """
    origin = get_origin(value)
    if origin is Union:
        args = get_args(value)
        return len(args) == 2 and type(None) in args
    return origin is Optional


def is_datapool_type(parameter_type: Any) -> bool:
    """
    Check if parameter type is DataPool or Optional[DataPool].

    :param parameter_type: The parameter type annotation to check
    :return: True if the parameter type is DataPool or Optional[DataPool], False otherwise
    """
    # Handle Optional[DataPool] case
    origin = get_origin(parameter_type)
    if origin is Union:
        args = get_args(parameter_type)
        return any(arg is DataPool for arg in args if arg is not type(None))

    return parameter_type is DataPool


def create_datapool_instance(parameter_name: str) -> DataPool:
    """
    Create DataPool instance for parameter based on parameter name.

    Creates a DataPool instance pointing to '/var/runtime/datapool/{parameter_name}'.

    :param parameter_name: The name of the parameter, used as the datapool directory name
    :return: DataPool instance for the specified parameter
    :raises FileNotFoundError: If the datapool directory doesn't exist
    :raises NotADirectoryError: If the datapool path exists but is not a directory
    """
    # Import here to get the current value, allowing tests to mock it
    from planqk.commons.constants import DEFAULT_DATAPOOL_DIRECTORY

    datapool_path = os.path.join(DEFAULT_DATAPOOL_DIRECTORY, parameter_name)
    return DataPool(datapool_path)
