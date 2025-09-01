from __future__ import annotations

import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast, runtime_checkable

import click
import flask
import flask.typing
import functions_framework
import gunicorn.app.base  # type: ignore[import-untyped]
from cloudevents.http import conversion
from cloudevents.http.event import CloudEvent
from google.cloud import storage
from structlog.typing import FilteringBoundLogger
from typing_extensions import ParamSpec
from ucam_observe.gunicorn import logconfig_dict  # type: ignore[import-untyped]
from werkzeug.exceptions import InternalServerError

from ucam_faas._logging import get_structlog_logger
from ucam_faas.exceptions import UCAMFAASException
from ucam_faas.loading import load_function

if TYPE_CHECKING:
    from _typeshed.wsgi import WSGIApplication

P = ParamSpec("P")
T = TypeVar("T")

# As well as making a logger available this should setup logging before the flask app is created
logger: FilteringBoundLogger = get_structlog_logger(__name__)


class IsRawEvent:
    pass


class IsCloudEvent:
    pass


class HasName(Protocol):
    @property
    def __name__(self) -> str:
        ...


def _common_function_wrapper(function: Callable[P, T]) -> Callable[P, T]:
    def _common_function_wrapper_internal(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return function(*args, **kwargs)
        except UCAMFAASException as exception:
            exception_name = exception.__class__.__name__

            logger.warning("function_failed_gracefully", exception_name=exception_name)

            raise InternalServerError(
                description=f"The function raised {exception_name}."
            ) from exception

        except Exception as exception:
            exception_name = exception.__class__.__name__

            logger.exception("function_failed_uncaught_exception", exception_name=exception_name)

            raise

    return _common_function_wrapper_internal


class RawEventHandlerFn(HasName, Protocol):
    def __call__(self, event: bytes, /) -> flask.typing.ResponseReturnValue | None:
        ...


@runtime_checkable
class RegisteredRawEventHandlerFn(HasName, Protocol):
    __ucam_wrapped__: RawEventHandlerFn
    _event: IsRawEvent

    def __call__(self, request: flask.Request, /) -> flask.typing.ResponseReturnValue:
        ...


def raw_event(function: RawEventHandlerFn) -> RegisteredRawEventHandlerFn:
    @_common_function_wrapper
    def _raw_event_internal(request: flask.Request, /) -> flask.typing.ResponseReturnValue:
        return_value = function(request.data)

        if return_value is not None:
            return return_value

        return "", 200

    # Decorators must preserve the wrapped function identity because
    # functions_framework registers metadata against the __name__ of `function`.
    _raw_event_internal.__name__ = function.__name__
    _raw_event_internal = functions_framework.http(_raw_event_internal)

    _raw_event_internal = cast(RegisteredRawEventHandlerFn, _raw_event_internal)
    _raw_event_internal.__ucam_wrapped__ = function
    _raw_event_internal._event = IsRawEvent()

    return _raw_event_internal


class CloudEventHandlerFn(HasName, Protocol):
    def __call__(self, event_data: Any, /) -> None:
        ...


@runtime_checkable
class RegisteredCloudEventHandlerFn(HasName, Protocol):
    __ucam_wrapped__: CloudEventHandlerFn
    _event: IsCloudEvent

    def __call__(self, event: CloudEvent, /) -> None:
        ...


def cloud_event(function: CloudEventHandlerFn) -> RegisteredCloudEventHandlerFn:
    @_common_function_wrapper
    def _cloud_event_internal(event: CloudEvent, /) -> None:
        return function(event.data)

    # Decorators must preserve the wrapped function identity because
    # functions_framework registers metadata against the __name__ of `function`.
    _cloud_event_internal.__name__ = function.__name__
    _cloud_event_internal = functions_framework.cloud_event(_cloud_event_internal)

    _cloud_event_internal = cast(RegisteredCloudEventHandlerFn, _cloud_event_internal)
    _cloud_event_internal.__ucam_wrapped__ = function
    _cloud_event_internal._event = IsCloudEvent()

    return _cloud_event_internal


class FaaSGunicornApplication(gunicorn.app.base.Application):  # type: ignore[misc] # gunicorn is not typed # noqa: E501
    def __init__(self, app: WSGIApplication, host: str, port: int | str) -> None:
        self.host = host
        self.port = port
        self.app = app

        self.options = {
            "bind": "%s:%s" % (host, port),
            "workers": os.environ.get("WORKERS", 2),
            "threads": os.environ.get("THREADS", (os.cpu_count() or 1) * 4),
            "timeout": 0,
            "limit_request_line": 0,
            "logconfig_dict": logconfig_dict,
        }

        super().__init__()

    def load_config(self) -> None:
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self) -> WSGIApplication:
        return self.app


def _initialize_ucam_faas_app(target: str, source: str | Path | None) -> flask.Flask:
    app: flask.Flask = functions_framework.create_app(target, source)  # type: ignore[no-untyped-call] # noqa: E501

    app.logger.info("flask_app_created")

    @app.route("/healthy")
    @app.route("/status")
    def get_status() -> str:
        return "ok"

    return app


def _execute_as_long_running(
    target: str, source: str | Path | None, input_bucket: str | None, input_file: str | Path | None
) -> int:
    """
    Internal function to execute a function as a long-running function (e.g. directly, not served
    as a flask application).

    This method relies on the function registration process having taken place, so must only be
    called after a call to functions_framework.create_app().
    """
    handler = load_function(target, source)

    event = CloudEvent(data=None, attributes={"source": "ucam_faas", "type": "ucam_faas_event"})

    try:
        if input_bucket is not None and input_file is not None:
            client = storage.Client()
            bucket = client.bucket(input_bucket)
            blob = bucket.blob(input_file)
            event = conversion.from_json(blob.download_as_bytes())
    except Exception as exc:
        logger.exception("Unhandled exception when loading input file", exception=exc)
        return 3

    try:
        if not isinstance(handler, (RegisteredRawEventHandlerFn, RegisteredCloudEventHandlerFn)):
            logger.exception("function_handler_not_registered")
            return 2

        handler(event)
    except InternalServerError:
        # This is raised by the `_common_function_wrapper_internal` decorator when
        # `UCAMFAASException` is raised. Logging is already done in the decorator.
        return 1
    except Exception:
        # Logging already done in `_common_function_wrapper_internal`
        return 2
    return 0


def run_ucam_faas(
    target: str,
    source: str | Path | None,
    host: str,
    port: int,
    debug: bool,
    long_running: bool,
    input_bucket: str | None = None,
    input_file: str | Path | None = None,
) -> None | int:  # pragma: no cover
    if long_running:
        return _execute_as_long_running(target, source, input_bucket, input_file)

    # Not long-running, so execute normally
    app = _initialize_ucam_faas_app(target, source)
    if debug:
        app.run(host, port, debug)
    else:
        server = FaaSGunicornApplication(app, host, port)
        server.run()
    return None


@click.command()
@click.option("--target", envvar="FUNCTION_TARGET", type=click.STRING, required=True)
@click.option("--source", envvar="FUNCTION_SOURCE", type=click.Path(), default=None)
@click.option("--host", envvar="HOST", type=click.STRING, default="0.0.0.0")
@click.option("--port", envvar="PORT", type=click.INT, default=8080)
@click.option("--debug", envvar="DEBUG", is_flag=True)
@click.option("--long-running", envvar="LONG_RUNNING", is_flag=True)
@click.option("--input-bucket", envvar="INPUT_BUCKET", type=click.STRING, default=None)
@click.option("--input-file", envvar="INPUT_FILE", type=click.Path(), default=None)
def _cli(
    target: str,
    source: str,
    host: str,
    port: int,
    debug: bool,
    long_running: bool,
    input_bucket: str | None = None,
    input_file: str | Path | None = None,
) -> None:  # pragma: no cover
    return_code = run_ucam_faas(
        target, source, host, port, debug, long_running, input_bucket, input_file
    )

    if long_running:
        sys.exit(return_code)
