# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

"""Server URL resolution: explicit argument > WOKWI_CLI_SERVER > public server.

These are unit tests: no token or network access is required.
"""

import pytest

from wokwi_client import WokwiClient, WokwiClientSync
from wokwi_client.constants import DEFAULT_WS_URL
from wokwi_client.transport import Transport

ENV_URL = "ws://localhost:9177"
EXPLICIT_URL = "ws://example.com:3000"


def test_transport_default_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WOKWI_CLI_SERVER", raising=False)
    assert Transport("token")._url == DEFAULT_WS_URL


def test_transport_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOKWI_CLI_SERVER", ENV_URL)
    assert Transport("token")._url == ENV_URL


def test_transport_env_read_at_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    """The env var must be honored even if it was set after the module was imported."""
    monkeypatch.delenv("WOKWI_CLI_SERVER", raising=False)
    before = Transport("token")._url
    monkeypatch.setenv("WOKWI_CLI_SERVER", ENV_URL)
    after = Transport("token")._url
    assert (before, after) == (DEFAULT_WS_URL, ENV_URL)


def test_transport_empty_env_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOKWI_CLI_SERVER", "")
    assert Transport("token")._url == DEFAULT_WS_URL


def test_client_default_server_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WOKWI_CLI_SERVER", raising=False)
    assert WokwiClient("token")._transport._url == DEFAULT_WS_URL


def test_client_server_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOKWI_CLI_SERVER", ENV_URL)
    assert WokwiClient("token")._transport._url == ENV_URL


def test_client_explicit_server_url_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOKWI_CLI_SERVER", ENV_URL)
    assert WokwiClient("token", EXPLICIT_URL)._transport._url == EXPLICIT_URL


def test_sync_client_server_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOKWI_CLI_SERVER", ENV_URL)
    client = WokwiClientSync("token")
    try:
        assert client._async_client._transport._url == ENV_URL
    finally:
        client.disconnect()


def test_sync_client_explicit_server_url_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOKWI_CLI_SERVER", ENV_URL)
    client = WokwiClientSync("token", EXPLICIT_URL)
    try:
        assert client._async_client._transport._url == EXPLICIT_URL
    finally:
        client.disconnect()
