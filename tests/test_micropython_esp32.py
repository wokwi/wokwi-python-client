# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from .utils import run_example_module


def test_micropython_esp32_example() -> None:
    """MicroPython ESP32 example should run and print MicroPython banner."""
    # MicroPython boot can take a bit longer; give it a few seconds
    result = run_example_module("examples.micropython_esp32.main", sleep_time="3")
    assert result.returncode == 0
    # Expect a line from the injected MicroPython script
    assert "Hello, MicroPython! I'm running on a Wokwi ESP32 simulator." in result.stdout
