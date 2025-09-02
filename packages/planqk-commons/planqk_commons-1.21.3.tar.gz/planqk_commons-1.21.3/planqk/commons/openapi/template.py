import os
from typing import Dict, Any

from planqk.commons.openapi import resolve_package_path
from planqk.commons.openapi.file import read_to_dict


def get_template_managed_service() -> Dict[str, Any]:
    """
    Returns the OpenAPI template for a managed service.

    :return: The template as a dictionary.
    """
    package_path = resolve_package_path()

    file_path = os.path.join(package_path, "template-managed-service.yaml")

    return read_to_dict(file_path)
