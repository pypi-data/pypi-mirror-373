from typing import Any

import pytest
from cloudevents.http.event import CloudEvent

# Register the ucam_faas testing module as a pytest plugin - as it provides
# fixtures that we can make use of when testing the functions.
pytest_plugins = ["ucam_faas.testing"]


@pytest.fixture()
def valid_cloud_event() -> Any:
    return CloudEvent(
        data={"foo": "bar"}, attributes={"source": "ucam_faas", "type": "ucam_faas_event"}
    )
