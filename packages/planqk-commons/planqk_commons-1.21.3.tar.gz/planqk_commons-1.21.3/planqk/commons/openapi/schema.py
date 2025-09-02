from enum import Enum
from inspect import Signature, Parameter
from typing import Any, Dict, Tuple, get_origin, get_args

from pydantic import BaseModel

from planqk.commons.parameters import is_container_type, is_datapool_type


def _is_enum_type(parameter_type: type) -> bool:
    """
    Check if a type is an Enum type.
    
    :param parameter_type: The type to check
    :return: True if the type is an Enum, False otherwise
    """
    try:
        return issubclass(parameter_type, Enum)
    except TypeError:
        return False


def _get_enum_schema(parameter_type: type) -> Dict[str, Any]:
    """
    Generate OpenAPI schema for an Enum type.
    
    :param parameter_type: The Enum type
    :return: OpenAPI schema dictionary for the enum
    """
    if not _is_enum_type(parameter_type):
        raise ValueError("Type is not an Enum")

    # Extract enum values
    enum_values = [member.value for member in parameter_type]

    # Determine the base type for OpenAPI schema
    if hasattr(parameter_type, '__bases__') and parameter_type.__bases__:
        # Check if enum inherits from a specific type (e.g., str, int)
        for base in parameter_type.__bases__:
            if base == str:
                return {
                    "type": "string",
                    "enum": enum_values,
                    "examples": [enum_values[0]] if enum_values else []
                }
            elif base == int:
                return {
                    "type": "integer",
                    "enum": enum_values,
                    "examples": [enum_values[0]] if enum_values else []
                }
            elif base == float:
                return {
                    "type": "number",
                    "enum": enum_values,
                    "examples": [enum_values[0]] if enum_values else []
                }

    # Default case - infer type from first value
    if enum_values:
        first_value = enum_values[0]
        if isinstance(first_value, str):
            schema_type = "string"
        elif isinstance(first_value, int) and not isinstance(first_value, bool):
            schema_type = "integer"
        elif isinstance(first_value, float):
            schema_type = "number"
        elif isinstance(first_value, bool):
            schema_type = "boolean"
        else:
            schema_type = "string"  # fallback

        return {
            "type": schema_type,
            "enum": enum_values,
            "examples": [first_value]
        }

    # Empty enum fallback
    return {
        "type": "string",
        "enum": [],
        "examples": []
    }


def _get_example_value_for_type(parameter_type: type) -> Any:
    """
    Get a sensible example value for basic Python types.
    
    :param parameter_type: The type for which to generate an example
    :return: A sensible example value for the type
    """
    if issubclass(parameter_type, str):
        return "string value"
    elif issubclass(parameter_type, bool):
        return True
    elif issubclass(parameter_type, int):
        return 42
    elif issubclass(parameter_type, float):
        return 3.14
    elif issubclass(parameter_type, list):
        return ["item1", "item2"]
    elif issubclass(parameter_type, tuple):
        return ["item1", "item2"]
    else:
        return None


def _add_default_or_example(parameter: Parameter, parameter_type: type, schema: Dict[str, Any]) -> None:
    """
    Add default value or examples to the schema based on parameter properties.
    Uses OpenAPI 3.1.0 'examples' attribute for better compliance.
    When the default value is None, also adds an example value.
    
    :param parameter: The function parameter to process
    :param parameter_type: The type of the parameter
    :param schema: The OpenAPI schema dictionary to modify
    """
    if parameter.default != Parameter.empty:
        # Parameter has a default value
        if _is_enum_type(parameter_type) and hasattr(parameter.default, 'value'):
            # For enum defaults, use the enum value
            schema["default"] = parameter.default.value
        else:
            schema["default"] = parameter.default

        # If the default value is None, also add an example
        if parameter.default is None:
            # Don't override examples for enums as they already have appropriate examples
            if not _is_enum_type(parameter_type):
                example_value = _get_example_value_for_type(parameter_type)
                if example_value is not None:
                    schema["examples"] = [example_value]
    else:
        # Parameter has no default, add a sensible example using OpenAPI 3.1.0 examples attribute
        # Don't override examples for enums as they already have appropriate examples
        if not _is_enum_type(parameter_type):
            example_value = _get_example_value_for_type(parameter_type)
            if example_value is not None:
                schema["examples"] = [example_value]


def generate_parameter_schema(signature: Signature) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    parameter_schemas = {}
    schema_definitions = {}

    # generate schema for each parameter
    parameters = signature.parameters
    for parameter in parameters.values():
        parameter_type = parameter.annotation
        args = get_args(parameter_type)
        origin = get_origin(parameter_type)

        # check if parameter is DataPool type FIRST
        if is_datapool_type(parameter_type):
            # generate DataPool schema
            parameter_schemas[parameter.name] = {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The ID of the datapool to mount."
                    },
                    "ref": {
                        "type": "string",
                        "enum": ["datapool"],
                        "description": "Reference type indicating this is a datapool."
                    }
                },
                "required": ["id", "ref"],
                "additionalProperties": False
            }
            continue  # skip other type checks

        if origin:
            parameter_type = origin

        # Check if parameter is Enum type BEFORE other checks
        if _is_enum_type(parameter_type):
            schema = _get_enum_schema(parameter_type)
            _add_default_or_example(parameter, parameter_type, schema)
            parameter_schemas[parameter.name] = schema
            continue  # skip other type checks

        if len(args) > 0 and is_container_type(origin):
            # nested native lists are not supported
            # it only considers the first type of the given tuple definition
            item_type = args[0]
            if issubclass(item_type, BaseModel):
                schema, schema_definition = generate_pydantic_schema(item_type)
                parameter_schemas[parameter.name] = {"type": "array", "items": schema}
                if schema_definition is not None:
                    schema_definitions.update(schema_definition)
            else:
                parameter_schemas[parameter.name] = {"type": "array"}
        elif issubclass(parameter_type, BaseModel):
            schema, schema_definition = generate_pydantic_schema(parameter_type)
            parameter_schemas[parameter.name] = schema
            if schema_definition is not None:
                schema_definitions.update(schema_definition)
        elif issubclass(parameter_type, list) or issubclass(parameter_type, tuple):
            schema = {"type": "array"}
            _add_default_or_example(parameter, parameter_type, schema)
            parameter_schemas[parameter.name] = schema
        elif issubclass(parameter_type, str):
            schema = {"type": "string"}
            _add_default_or_example(parameter, parameter_type, schema)
            parameter_schemas[parameter.name] = schema
        # bool needs to be checked before int as otherwise it would be classified as int
        elif issubclass(parameter_type, bool):
            schema = {"type": "boolean"}
            _add_default_or_example(parameter, parameter_type, schema)
            parameter_schemas[parameter.name] = schema
        elif issubclass(parameter_type, int):
            schema = {"type": "integer"}
            _add_default_or_example(parameter, parameter_type, schema)
            parameter_schemas[parameter.name] = schema
        elif issubclass(parameter_type, float):
            schema = {"type": "number"}
            _add_default_or_example(parameter, parameter_type, schema)
            parameter_schemas[parameter.name] = schema
        else:
            # for the rest we assume dict
            parameter_schemas[parameter.name] = {"type": "object", "additionalProperties": {"type": "string"}}

    return parameter_schemas, schema_definitions


def generate_return_schema(signature: Signature) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return_schema = {}
    schema_definitions = {}

    # generate schema for the return type
    return_type = signature.return_annotation

    if return_type is None:
        return return_schema, schema_definitions

    args = get_args(return_type)
    origin = get_origin(return_type)
    if origin:
        return_type = origin

    if len(args) > 0 and is_container_type(origin):
        # nested native lists are not supported
        # it only considers the first type of the given tuple definition
        return_type = args[0]

    if issubclass(return_type, BaseModel):
        schema, schema_definition = generate_pydantic_schema(return_type)
        return_schema = schema
        if schema_definition is not None:
            schema_definitions.update(schema_definition)

    return return_schema, schema_definitions


def generate_pydantic_schema(parameter_type) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not issubclass(parameter_type, BaseModel):
        raise ValueError("Only Pydantic models are supported")

    schema_definition = None
    schema = parameter_type.model_json_schema(
        ref_template="#/components/schemas/{model}",
        mode="serialization"
    )

    if "$defs" in schema:
        schema_definition = schema.pop("$defs")

    return schema, schema_definition
