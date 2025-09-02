"""Operation name to engine error code mapping."""
import importlib
import inspect
import os
from pathlib import Path
from types import ModuleType

from move_errors.codes import engine
from move_errors.codes.base import BaseErrorCode

# The engine error codes mapping.
# This allows the engine to provide an operation name and for us to then map that
# to the correct error code class.
codes = {}


def _build_code_for_module(module: ModuleType) -> None:
    """Build the error code mapping for the module.

    Args:
        module: The module to build the codes for.
    """
    ops_classes = inspect.getmembers(module, inspect.isclass)
    for ops_class_name, ops_class in ops_classes:
        # Ensure that we only load classes that are named with `Ops`
        is_ops_error_code_class = issubclass(ops_class, (BaseErrorCode,))
        if ops_class_name.startswith("Ops") and is_ops_error_code_class:
            codes[str(ops_class.operation_name())] = ops_class


def _init() -> None:
    """Initialise the engine error codes dynamically.

    We don't want to have to remember to add ops error codes and classes. Therefore,
    build the list dynamically. This functionality is inspired by requests.status_codes
    """
    for module_name in os.listdir(os.path.dirname(inspect.getfile(engine))):
        if module_name.startswith("ops_"):
            # Ensure that we only import modules that begin with `ops_`
            imported_sub_module = importlib.import_module(
                "{0}.{1}".format(engine.__name__, Path(module_name).stem),
            )
            _build_code_for_module(imported_sub_module)


_init()
