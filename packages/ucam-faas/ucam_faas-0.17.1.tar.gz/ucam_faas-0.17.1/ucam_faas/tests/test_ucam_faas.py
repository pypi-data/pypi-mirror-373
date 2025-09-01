from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest
import structlog
from cloudevents import conversion
from flask import Flask
from structlog.testing import capture_logs

from ucam_faas import FaaSGunicornApplication, cloud_event, raw_event, run_ucam_faas
from ucam_faas.exceptions import UCAMFAASCouldNotProcess
from ucam_faas.testing import CreateEventAppClientFn

if TYPE_CHECKING:
    from typing_extensions import Never


script_path = Path(__file__).resolve()
cwd = Path.cwd()
relative_path = script_path.relative_to(cwd)


# Raw events
@raw_event
def example_raw_event_no_exception(event: bytes) -> None:
    pass


@raw_event
def example_raw_event_handled_exception(event: bytes) -> Never:
    raise UCAMFAASCouldNotProcess


@raw_event
def example_raw_event_unhandled_exception(event: bytes) -> Never:
    raise Exception("Did not expect this")


# Cloud Events
@cloud_event
def example_cloud_event_no_exception(event: Any) -> None:
    pass


@cloud_event
def example_cloud_event_handled_exception(event: Any) -> None:
    raise UCAMFAASCouldNotProcess


@cloud_event
def example_cloud_event_unhandled_exception(event: Any) -> None:
    raise Exception("Did not expect this")


def test_faas_gunicorn_application_bind() -> None:
    app = Flask(__name__)
    application = FaaSGunicornApplication(app, "0.0.0.0", "8080")

    with patch("gunicorn.app.base.BaseApplication.run") as mock_run:
        application.run()
        mock_run.assert_called_once()  # Ensures that the server's run method was indeed called


@pytest.mark.parametrize(
    "target_tuple",
    [
        (
            "example_raw_event_no_exception",
            "example_raw_event_handled_exception",
            "example_raw_event_unhandled_exception",
        ),
        (
            "example_cloud_event_no_exception",
            "example_cloud_event_handled_exception",
            "example_cloud_event_unhandled_exception",
        ),
    ],
)
def test_exceptions_raw_events(
    event_app_test_client_factory: CreateEventAppClientFn,
    target_tuple: tuple[str, str, str],
    valid_cloud_event: Any,
) -> None:
    # No exception
    test_client = event_app_test_client_factory(target=target_tuple[0], source=relative_path)
    response = test_client.post("/", json=conversion.to_dict(valid_cloud_event))
    assert response.status_code == 200

    # Handle exception
    test_client = event_app_test_client_factory(target=target_tuple[1], source=relative_path)
    response = test_client.post("/", json=conversion.to_dict(valid_cloud_event))
    assert response.status_code == 500
    assert "The function raised UCAMFAASCouldNotProcess" in response.data.decode()

    # Unhandled exception
    test_client = event_app_test_client_factory(target=target_tuple[2], source=relative_path)
    with structlog.testing.capture_logs() as cap_logs:
        response = test_client.post("/", json=conversion.to_dict(valid_cloud_event))
    assert response.status_code == 500

    assert len(cap_logs) == 1
    log_call = cap_logs[0]
    assert (
        log_call.get("event") == "function_failed_uncaught_exception"
        # structlog will include exception details in rendered log message
        and log_call.get("exc_info") is True
    )


@pytest.mark.parametrize(
    "target,expected_return",
    [
        ("example_raw_event_no_exception", 0),
        ("example_raw_event_handled_exception", 1),
        ("example_raw_event_unhandled_exception", 2),
        ("example_cloud_event_no_exception", 0),
        ("example_cloud_event_handled_exception", 1),
        ("example_cloud_event_unhandled_exception", 2),
    ],
)
def test_long_running(target: str, expected_return: int) -> None:
    assert (
        run_ucam_faas(
            target,
            source=relative_path,
            host="no-host",
            port=0,
            debug=False,
            long_running=True,
        )
        == expected_return
    )


def normal_function() -> None:
    pass


def test_long_running_no_registered_event_handler() -> None:
    """
    Test that running a normal function as a long-running function raises an error.
    """
    with capture_logs() as cap_logs:
        assert (
            run_ucam_faas(
                normal_function.__name__,
                source=relative_path,
                host="no-host",
                port=0,
                debug=False,
                long_running=True,
            )
            == 2
        )

    assert len(cap_logs) == 1
    assert cap_logs[0]["event"] == "function_handler_not_registered"
