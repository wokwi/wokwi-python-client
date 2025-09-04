# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from .utils import run_example_module


def test_hello_esp32_example() -> None:
    """Async hello_esp32 example should run and exit with 0."""
    result = run_example_module("examples.hello_esp32.main")
    assert result.returncode == 0
    assert "main_task: Calling app_main()" in result.stdout


def test_hello_esp32_sync_example() -> None:
    """Sync hello_esp32 example should run and exit with 0."""
    result = run_example_module("examples.hello_esp32_sync.main")
    assert result.returncode == 0
    assert "main_task: Calling app_main()" in result.stdout


def test_hello_esp32_idf_example() -> None:
    """Sync hello_esp32 example should run and exit with 0."""
    result = run_example_module("examples.hello_esp32_idf.main")
    assert result.returncode == 0
    assert "cpu_start: Starting scheduler on APP CPU" in result.stdout
