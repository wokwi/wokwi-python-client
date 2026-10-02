# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

"""File upload and download against a fake transport (no token or network needed)."""

import asyncio
import base64
from pathlib import Path

from wokwi_client import WokwiClient
from wokwi_client.file_ops import upload_file

from .utils import FakeTransport


def test_upload_file_sends_json_as_text_and_the_rest_as_binary(tmp_path: Path) -> None:
    (tmp_path / "inverter.chip.json").write_bytes("﻿{}".encode())
    (tmp_path / "firmware.bin").write_bytes(b"\x00\x01")
    transport = FakeTransport()

    asyncio.run(upload_file(transport, "inverter.chip.json", tmp_path / "inverter.chip.json"))
    asyncio.run(upload_file(transport, "firmware.bin", tmp_path / "firmware.bin"))

    assert transport.requests == [
        ("file:upload", {"name": "inverter.chip.json", "text": "{}"}),
        ("file:upload", {"name": "firmware.bin", "binary": base64.b64encode(b"\x00\x01").decode()}),
    ]


def test_download_returns_text_files_as_bytes() -> None:
    client = WokwiClient("token")
    client._transport = FakeTransport(text="{}")

    assert asyncio.run(client.download("diagram.json")) == b"{}"
