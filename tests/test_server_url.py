# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import sys
from typing import Optional

from wokwi_client.constants import DEFAULT_WS_URL


def _client_url(env_server: Optional[str], server: Optional[str] = None) -> str:
    """Return the URL picked by a WokwiClient created in a fresh interpreter.

    WOKWI_CLI_SERVER is read at import time, so each case needs its own process.
    """
    env = {k: v for k, v in os.environ.items() if k != "WOKWI_CLI_SERVER"}
    if env_server is not None:
        env["WOKWI_CLI_SERVER"] = env_server
    code = (
        "from wokwi_client import WokwiClient; "
        f"print(WokwiClient('token', {server!r})._transport._url)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def test_default_server_url() -> None:
    assert _client_url(None) == DEFAULT_WS_URL


def test_server_url_from_env() -> None:
    assert _client_url("ws://localhost:9177") == "ws://localhost:9177"


def test_explicit_server_url_overrides_env() -> None:
    assert _client_url("ws://localhost:9177", "ws://example.com:3000") == "ws://example.com:3000"
