import os
from typing import Dict, Any

import yaml

from planqk.commons.constants import ENTRYPOINT_ENV, DEFAULT_ENTRYPOINT
from planqk.commons.openapi.schema import generate_parameter_schema, generate_return_schema
from planqk.commons.openapi.template import get_template_managed_service
from planqk.commons.reflection import resolve_signature


def generate_openapi(entrypoint: str = os.environ.get(ENTRYPOINT_ENV, DEFAULT_ENTRYPOINT),
                     title: str = "PLANQK Service API",
                     version: str = "1") -> None:
    """
    Generate an OpenAPI specification for a PLANQK Service.

    :param entrypoint: The entrypoint of the service
    :param title: The title of the service, defaults to "PLANQK Service API"
    :param version: The version of the service, defaults to "1"
    :return:
    """
    entrypoint_signature = resolve_signature(entrypoint)

    parameter_schemas, parameter_schema_definitions = generate_parameter_schema(entrypoint_signature)
    return_schema, return_schema_definitions = generate_return_schema(entrypoint_signature)

    schema_definitions = {}
    schema_definitions.update(parameter_schema_definitions)
    schema_definitions.update(return_schema_definitions)

    openapi_template = get_template_managed_service()

    openapi = populate_openapi_template(openapi_template, parameter_schemas, return_schema, schema_definitions, title, version)

    print(yaml.dump(openapi, sort_keys=False))


def populate_openapi_template(openapi_template: Dict[str, Any],
                              input_schema: Dict[str, Any],
                              output_schema: Dict[str, Any],
                              schema_definitions: Dict[str, Any],
                              title: str,
                              version: str = "1") -> Dict[str, Any]:
    # deep copy of openapi_template
    openapi = dict(openapi_template)

    openapi["components"]["schemas"].update(schema_definitions)

    # start execution route
    if input_schema:
        openapi["paths"]["/"]["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"] = input_schema
    else:
        del openapi["paths"]["/"]["post"]["requestBody"]

    # result route
    if "properties" in output_schema:
        (openapi["paths"]["/{id}/result"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["properties"]
         .update(output_schema["properties"]))

    openapi["info"]["title"] = title
    openapi["info"]["version"] = version

    return openapi
