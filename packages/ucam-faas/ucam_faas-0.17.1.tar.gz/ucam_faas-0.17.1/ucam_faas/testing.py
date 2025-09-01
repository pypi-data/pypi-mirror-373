from __future__ import annotations

import contextlib
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Protocol

from flask.testing import FlaskClient

from . import _initialize_ucam_faas_app

if TYPE_CHECKING:
    from typing_extensions import Never


class CreateEventAppClientFn(Protocol):
    def __call__(self, target: str, source: str | Path | None = None) -> FlaskClient:
        ...


try:
    if TYPE_CHECKING:
        from cloudevents.pydantic.v2 import CloudEvent
    else:
        from cloudevents.pydantic import CloudEvent
    from polyfactory.factories.pydantic_factory import ModelFactory
    from pytest import fixture

    @fixture
    def event_app_test_client_factory(cleanup_functions_framework: None) -> CreateEventAppClientFn:
        # Although we use the cleanup_functions_framework fixture, tests that
        # call event_app_test_client_factory() multiple times will still be able
        # to see global state changes made by functions_framework in previous
        # calls to event_app_test_client_factory() within the same test. We
        # could make _event_app_client() a context manager to clean each call
        # rather than at the per-test level.

        def _event_app_client(target: str, source: str | Path | None = None) -> FlaskClient:
            test_app = _initialize_ucam_faas_app(target, source)
            return test_app.test_client()

        return _event_app_client

    class CloudEventFactory(ModelFactory[CloudEvent]):
        __model__ = CloudEvent

        specversion = "1.0"

except ImportError as e:
    _import_error = e

    @fixture
    def event_app_test_client_factory() -> Never:  # type: ignore[misc]
        raise RuntimeError(
            f"Fixture {event_app_test_client_factory.__name__} is not available "
            f"because ucam_faas is not installed with the 'testing' extra]"
        ) from _import_error


@fixture(scope="function", name="cleanup_functions_framework")
def cleanup_functions_framework_fixture() -> Generator[None]:
    with cleanup_functions_framework():
        yield


@contextlib.contextmanager
def cleanup_functions_framework() -> Generator[None]:
    """
    A context manager that resets changes made to global Python interpreter
    state by `functions_framework` within the managed context.

    `functions_framework` changes environment variables and changes `sys.path`.
    These changes persist between subsequent `functions_framework.create_app()`
    calls, resulting in subsequent calls being affected by state changed by
    previous calls. (Specifically, envars that remain set cause subsequent
    functions to be registered with the wrong function type.)

    Wrapping calls to `functions_framework` within this context manager will
    prevent global changes affecting subsequent calls to `functions_framework`.
    """
    mutated_envars = ["FUNCTION_TARGET", "FUNCTION_SIGNATURE_TYPE", "FUNCTION_TRIGGER_TYPE"]
    initial_envars = {e: os.environ.get(e) for e in mutated_envars}

    # functions_framework appends to sys.path without checking if an entry
    # already exists. This results in the path increasing in size with each
    # call. To limit growth, we remove duplicate entries from sys.path.
    initial_syspath = list(sys.path)

    yield

    for name, initial_value in initial_envars.items():
        if initial_value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = initial_value

    sys.path[:] = initial_syspath
