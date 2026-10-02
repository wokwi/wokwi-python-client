# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

"""Micro SD card helpers against a fake transport (no token or network needed)."""

import asyncio
import base64
from pathlib import Path
from typing import Any

from wokwi_client import SDCardConfig, SDCardFile
from wokwi_client.protocol_types import ResponseMessage
from wokwi_client.sdcard import export_sdcard_files, upload_sdcard_folder
from wokwi_client.simulation import start
from wokwi_client.transport import Transport

MB = 1024 * 1024


class FakeTransport(Transport):
    def __init__(self, **result: Any):
        super().__init__("token")
        self.result = result
        self.requests: list[tuple[str, dict[str, Any]]] = []

    async def request(self, command: str, params: dict[str, Any]) -> ResponseMessage:
        self.requests.append((command, params))
        return {
            "type": "response",
            "command": command,
            "id": "1",
            "result": self.result,
            "error": False,
        }


def test_start_sends_sdcards_in_wire_format() -> None:
    transport = FakeTransport()
    card = SDCardConfig(part="sd1", prefix="sdcard/sd1/", size_bytes=16 * MB)

    asyncio.run(start(transport, firmware="firmware.bin", sdcards=[card]))

    ((_, params),) = transport.requests
    assert params["sdcards"] == [{"part": "sd1", "prefix": "sdcard/sd1/", "sizeBytes": 16 * MB}]


def test_upload_sdcard_folder(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_bytes(b"{}")
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "boot.txt").write_bytes(b"ok")
    (tmp_path / ".DS_Store").write_bytes(b"")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_bytes(b"ref")
    transport = FakeTransport()

    card = asyncio.run(upload_sdcard_folder(transport, tmp_path, part="sd1"))

    uploaded = [params["name"] for _, params in transport.requests]
    assert uploaded == ["sdcard/sd1/config.json", "sdcard/sd1/logs/boot.txt"]
    assert card == SDCardConfig(part="sd1", prefix="sdcard/sd1/")


def test_export_sdcard_files() -> None:
    content = base64.b64encode(b"ok").decode()
    transport = FakeTransport(files=[{"name": "logs/boot.txt", "binary": content}])

    files = asyncio.run(export_sdcard_files(transport, "sd1"))

    assert transport.requests == [("sdcard:export", {"format": "files", "part": "sd1"})]
    assert files == [SDCardFile(name="logs/boot.txt", content=b"ok")]
