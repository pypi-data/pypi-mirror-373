from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import FunctionType, ModuleType

from ucam_faas.exceptions import UCAMFAASCouldNotLoadTarget


def load_function(target: str, source: str | Path | None) -> FunctionType:
    # If this raises an exception it is propogated up
    module = _load_source_module(source or "./main.py")

    if not hasattr(module, target):
        raise UCAMFAASCouldNotLoadTarget(
            f"Source file {source} did not have expected target function {target}"
        )
    func = getattr(module, target)
    if not isinstance(func, FunctionType):
        raise UCAMFAASCouldNotLoadTarget(
            f"Target {target} in source file {source} does not appear to be a valid function"
        )
    return func


def _load_source_module(source: str | Path) -> ModuleType:
    realpath = os.path.realpath(source)
    dir, filename = os.path.split(realpath)
    name, _ = os.path.splitext(filename)
    spec = importlib.util.spec_from_file_location(name, realpath, submodule_search_locations=[dir])
    if spec and spec.loader:
        source_module = importlib.util.module_from_spec(spec)
        sys.path.append(dir)
        sys.modules[name] = source_module
        spec.loader.exec_module(source_module)
        return source_module
    raise UCAMFAASCouldNotLoadTarget(
        f"Source file {source} could not be loaded as a python module"
    )
