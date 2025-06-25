# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import sys


def test_hello_esp32_example() -> None:
    """`python -m examples.hello_esp32.main` runs the hello_esp32 example and exits with 0."""

    assert os.environ.get("WOKWI_CLI_TOKEN") is not None, (
        "WOKWI_CLI_TOKEN environment variable is not set. You can get it from https://wokwi.com/dashboard/ci."
    )

    result = subprocess.run(
        [sys.executable, "-m", "examples.hello_esp32.main"],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "WOKWI_SLEEP_TIME": "1"},
    )

    assert result.returncode == 0
    assert "main_task: Calling app_main()" in result.stdout
