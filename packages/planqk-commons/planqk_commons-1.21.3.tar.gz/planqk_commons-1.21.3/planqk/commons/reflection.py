import importlib
import inspect
from typing import Callable


def resolve_function(entrypoint: str) -> Callable:
    """
    Resolve a function by its entrypoint string.

    :param entrypoint: The entrypoint string in the format 'module_path:function_name'.
    :return: The function object.
    """
    module_path, func_name = entrypoint.split(':')

    # import the module dynamically
    module = importlib.import_module(module_path)

    func = getattr(module, func_name)

    return func


def resolve_signature(entrypoint: str) -> inspect.Signature:
    """
    Resolve the signature of a function by its entrypoint string.

    :param entrypoint: The entrypoint string in the format 'module_path:function_name'.
    :return: The signature of the function.
    """
    func = resolve_function(entrypoint)

    signature = inspect.signature(func)

    return signature
