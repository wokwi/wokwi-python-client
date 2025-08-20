"""
Test utilities for running example modules.

Provides a helper to execute `python -m <module>` with a short sleep to keep
CI fast and shared environment handling (WOKWI_CLI_TOKEN, etc.).
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Mapping
from subprocess import CompletedProcess


def run_example_module(
    module: str, *, sleep_time: str = "1", extra_env: Mapping[str, str] | None = None
) -> CompletedProcess[str]:
    """Run an example module with a short simulation time.

    Requires WOKWI_CLI_TOKEN to be set in the environment.
    Returns the CompletedProcess so tests can assert on return code and output.
    """

    assert os.environ.get("WOKWI_CLI_TOKEN") is not None, (
        "WOKWI_CLI_TOKEN environment variable is not set. You can get it from https://wokwi.com/dashboard/ci."
    )

    env = {**os.environ, "WOKWI_SLEEP_TIME": sleep_time}
    if extra_env:
        env.update(extra_env)

    return subprocess.run(
        [sys.executable, "-m", module],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
