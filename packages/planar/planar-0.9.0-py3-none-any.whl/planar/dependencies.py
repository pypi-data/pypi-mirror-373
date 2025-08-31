from __future__ import annotations

import sys
from importlib import import_module
from typing import Mapping, Tuple


# mapping: public_name -> (relative_submodule, attribute_in_submodule)
# This is a PEP 562 compliant way to lazily import modules
# which is a way to avoid circular dependencies in __init__.py.
def lazy_exports(module_name: str, mapping: Mapping[str, Tuple[str, str]]) -> None:
    mod = sys.modules[module_name]
    mod.__all__ = list(mapping.keys())  # type: ignore

    def __getattr__(name: str):
        try:
            submod, attr = mapping[name]
        except KeyError:
            raise AttributeError(
                f"module {module_name!r} has no attribute {name!r}"
            ) from None
        obj = getattr(import_module(submod, module_name), attr)
        setattr(mod, name, obj)  # cache
        return obj

    def __dir__():
        return sorted(set(mod.__dict__.keys()) | set(mod.__all__))

    mod.__getattr__ = __getattr__  # PEP 562
    mod.__dir__ = __dir__
