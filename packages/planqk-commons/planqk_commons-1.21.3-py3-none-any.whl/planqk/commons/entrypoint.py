from typing import Any, Dict

from loguru import logger

from planqk.commons.reflection import resolve_function, resolve_signature


def run_entrypoint(entrypoint: str, entrypoint_arguments: Dict[str, Any]) -> Any:
    """
    Run the entrypoint with the given arguments.

    :param entrypoint: The entrypoint to run, e.g. 'user_code.src.program:run'.
    :param entrypoint_arguments: The arguments to pass to the entrypoint.
    :return: The return value of the entrypoint.
    """
    signature = resolve_signature(entrypoint)

    logger.debug(f"Parameters in signature: {list(signature.parameters.keys())}")
    logger.debug(f"Found input parameters: {list(entrypoint_arguments.keys())}")

    # remove keys from 'entrypoint_arguments' that are not parameters in the signature
    entrypoint_arguments = {k: v for k, v in entrypoint_arguments.items() if k in signature.parameters}

    func = resolve_function(entrypoint)
    return func(**entrypoint_arguments)
