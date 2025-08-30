import os

import pytest

from mm_test_adapters import device_adapter_path


@pytest.mark.parametrize(
    "lib", ["DemoCamera", "Utilities", "NotificationTester", "SequenceTester"]
)
def test_path(lib: str) -> None:
    path = device_adapter_path()
    libs = set(os.listdir(path))
    assert any(lib in s for s in libs), f"Missing library: {lib}"
