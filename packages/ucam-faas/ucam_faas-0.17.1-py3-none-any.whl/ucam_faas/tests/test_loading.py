import pytest

from ucam_faas.exceptions import UCAMFAASCouldNotLoadTarget
from ucam_faas.loading import load_function

MY_DICTIONARY: dict[str, str] = {}


def my_function() -> str:
    return "function_called"


def test_loading() -> None:
    func = load_function("my_function", "ucam_faas/tests/test_loading.py")

    assert func() == "function_called"


def test_loading_file_not_valid_module() -> None:
    with pytest.raises(UCAMFAASCouldNotLoadTarget):
        _ = load_function("my_function", "ucam_faas/tests/not_a_module.txt")


def test_loading_module_doesnt_contain_target() -> None:
    with pytest.raises(UCAMFAASCouldNotLoadTarget):
        _ = load_function("not_my_function", "ucam_faas/tests/test_loading.py")


def test_loading_target_isnt_a_function() -> None:
    with pytest.raises(UCAMFAASCouldNotLoadTarget):
        _ = load_function("MY_DICTIONARY", "ucam_faas/tests/test_loading.py")
