"""Micro SD card helpers.

Upload the card contents (`upload_sdcard_folder`, or `upload` + `SDCardConfig(prefix=...)`),
pass the config to `sim:start`, and read the card back with the `sdcard:export` command.

Exposed helpers:
* upload_sdcard_folder  -> upload a local folder, returns the SDCardConfig for sim:start
* export_sdcard_image   -> raw disk image bytes
* export_sdcard_files   -> files on the card
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from .file_ops import upload
from .models import SDCardConfig, SDCardFile
from .transport import Transport

__all__ = [
    "SKIPPED_NAMES",
    "export_sdcard_files",
    "export_sdcard_image",
    "upload_sdcard_folder",
]

# OS clutter never copied to the card (same list as the Wokwi CLI)
SKIPPED_NAMES = frozenset({".DS_Store", "Thumbs.db", "desktop.ini", ".git"})


async def upload_sdcard_folder(
    transport: Transport,
    local_dir: str | Path,
    *,
    part: str | None = None,
    size_bytes: int | None = None,
) -> SDCardConfig:
    root = Path(local_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"SD card folder not found: {root}")
    # One prefix per card, same convention as the Wokwi CLI
    prefix = f"sdcard/{part}/" if part else "sdcard/"
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and SKIPPED_NAMES.isdisjoint(relative.parts):
            await upload(transport, prefix + relative.as_posix(), path.read_bytes())
    return SDCardConfig(part=part, prefix=prefix, size_bytes=size_bytes)


async def _export(transport: Transport, fmt: str, part: str | None) -> dict[str, Any]:
    params: dict[str, Any] = {"format": fmt}
    if part is not None:
        params["part"] = part
    response = await transport.request("sdcard:export", params)
    return response["result"]


async def export_sdcard_image(transport: Transport, part: str | None = None) -> bytes:
    result = await _export(transport, "image", part)
    return base64.b64decode(result["image"])


async def export_sdcard_files(transport: Transport, part: str | None = None) -> list[SDCardFile]:
    result = await _export(transport, "files", part)
    return [
        SDCardFile(name=entry["name"], content=base64.b64decode(entry["binary"]))
        for entry in result["files"]
    ]
