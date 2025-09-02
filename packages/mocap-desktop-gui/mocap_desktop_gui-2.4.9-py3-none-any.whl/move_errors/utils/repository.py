"""Move errors repository."""
import importlib
import inspect
import os
from enum import Enum
from itertools import chain
from pathlib import Path
from types import ModuleType
from typing import Type

from move_errors.codes import engine, internal_services, public_apis
from move_errors.codes.base import BaseErrorCode
from move_errors.codes.engine.base import BaseEngineOpsErrorCode


def _import_all_error_codes_by_submodule(
    module: ModuleType,
) -> None:
    """Import all error codes by submodule.

    Args:
        module (ModuleType): The module to import the error codes from.
    """
    for submodule in os.listdir(os.path.dirname(inspect.getfile(module))):
        importlib.import_module(
            "{0}.{1}".format(module.__name__, Path(submodule).stem),
        )


def _get_child_error_codes(
    base_class: Type[BaseErrorCode],
    exclude_list: list[Type[BaseErrorCode]] | None = None,
) -> list[Type[BaseErrorCode]]:
    """Get all the child error codes of the given base class.

    Args:
        base_class (Type[BaseErrorCode]):
            The base class to get the child error codes for.
        exclude_list (list[Type[BaseErrorCode]], optional):
            The list of error codes to exclude. Defaults to ().

    Returns:
        list[Type[BaseErrorCode]]: The list of child error codes.
    """
    return [
        code_class
        for code_class in base_class.__subclasses__()
        if code_class not in (exclude_list or [])
    ]


def _build_unified_enum() -> Enum:
    """Build the unified error codes enum.

    Returns:
        Enum: The unified error codes enum.
    """
    chained_codes = chain.from_iterable(  # type: ignore[var-annotated]
        _get_child_error_codes(  # type: ignore[arg-type]
            BaseErrorCode,
            exclude_list=[BaseEngineOpsErrorCode],
        ),
    )
    engine_chained_codes = chain.from_iterable(  # type: ignore[var-annotated]
        _get_child_error_codes(BaseEngineOpsErrorCode),  # type: ignore[arg-type]
    )
    chained_codes = chain(chained_codes, engine_chained_codes)
    return Enum(
        "MoveErrorCodes",
        [(code.name, code.value) for code in chained_codes],
    )


def _init() -> None:
    """Initialise the error codes dynamically."""
    _import_all_error_codes_by_submodule(internal_services)
    _import_all_error_codes_by_submodule(public_apis)
    _import_all_error_codes_by_submodule(engine)


_init()
MoveErrorCodes = _build_unified_enum()
