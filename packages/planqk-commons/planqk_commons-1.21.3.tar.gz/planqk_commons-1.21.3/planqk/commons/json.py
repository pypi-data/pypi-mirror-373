import json
from typing import Optional

from pydantic import BaseModel


def any_to_json(data: any) -> Optional[str]:
    """
    Convert any data to a JSON string, if JSON serializable. If the data is a Pydantic
    model, the model_dump_json method is used.

    :param data: The data to convert.
    :return: The JSON string representation of the data.
    """
    if data is None:
        return None

    if issubclass(data.__class__, BaseModel):
        return data.model_dump_json(indent=2)

    return json.dumps(data, default=lambda o: getattr(o, "__dict__", str(o)), indent=2)
