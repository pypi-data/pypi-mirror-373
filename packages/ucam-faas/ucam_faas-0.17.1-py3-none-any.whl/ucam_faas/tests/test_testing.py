import os
import sys

import pytest
from cloudevents.pydantic.v2 import CloudEvent

from ucam_faas.testing import CloudEventFactory, cleanup_functions_framework


def test_cloudeventfactory_model_static_type_has_pydantic_methods() -> None:
    event = CloudEventFactory.build()
    assert CloudEvent.model_validate(event.model_dump()) == event

    # However type checkers don't see Pydantic methods on cloudevents.pydantic.CloudEvent
    from cloudevents.pydantic import CloudEvent as CloudEventAutoVersion

    # mypy complains: "type[CloudEvent]" has no attribute "model_validate"
    assert CloudEventAutoVersion.model_validate(event.model_dump()) == event


def test_cleanup_functions_framework(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend("/bar")
    monkeypatch.syspath_prepend("/foo")
    syspath_before = list(sys.path)
    # syspath_before = list({p: None for p in sys.path}.keys())

    monkeypatch.delenv("FUNCTION_TARGET", raising=False)
    monkeypatch.setenv("FUNCTION_SIGNATURE_TYPE", "foo")
    monkeypatch.setenv("FUNCTION_TRIGGER_TYPE", "")

    with cleanup_functions_framework():
        sys.path.extend(["/foo", "/bar"] * 2)
        monkeypatch.setenv("FUNCTION_TARGET", "A")
        monkeypatch.setenv("FUNCTION_SIGNATURE_TYPE", "B")
        monkeypatch.setenv("FUNCTION_TRIGGER_TYPE", "C")

    assert syspath_before == sys.path

    assert "FUNCTION_TARGET" not in os.environ
    assert os.environ.get("FUNCTION_SIGNATURE_TYPE") == "foo"
    assert os.environ.get("FUNCTION_TRIGGER_TYPE") == ""
