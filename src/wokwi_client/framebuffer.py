"""Framebuffer command helpers.

Provides utilities to interact with devices exposing a framebuffer (e.g. LCD
modules) via the `framebuffer:read` command.

Exposed helpers:
* framebuffer_read          -> raw response (contains base64 PNG at result.png)
* framebuffer_png_bytes     -> decoded PNG bytes
* save_framebuffer_png      -> save PNG to disk
* compare_framebuffer_png   -> compare current framebuffer against reference
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
from pathlib import Path

from .exceptions import WokwiError
from .protocol_types import ResponseMessage
from .transport import Transport

__all__ = [
    "framebuffer_read",
    "framebuffer_png_bytes",
    "save_framebuffer_png",
    "compare_framebuffer_png",
]


async def framebuffer_read(transport: Transport, *, id: str) -> ResponseMessage:
    """Issue `framebuffer:read` for the given device id and return raw response."""
    return await transport.request("framebuffer:read", {"id": id})


def _extract_png_b64(resp: ResponseMessage) -> str:
    result = resp.get("result", {})
    png_b64 = result.get("png")
    if not isinstance(png_b64, str):  # pragma: no cover - defensive
        raise WokwiError("Malformed framebuffer:read response: missing 'png' base64 string")
    return png_b64


async def framebuffer_png_bytes(transport: Transport, *, id: str) -> bytes:
    """Return decoded PNG bytes for the framebuffer of device `id`."""
    resp = await framebuffer_read(transport, id=id)
    return base64.b64decode(_extract_png_b64(resp))


async def save_framebuffer_png(
    transport: Transport, *, id: str, path: Path, overwrite: bool = True
) -> Path:
    """Save the framebuffer PNG to `path` and return the path.

    Args:
            transport: Active transport.
            id: Device id (e.g. "lcd1").
            path: Destination file path.
            overwrite: Overwrite existing file (default True). If False and file
                    exists, raises WokwiError.
    """
    if path.exists() and not overwrite:
        raise WokwiError(f"File already exists and overwrite=False: {path}")
    data = await framebuffer_png_bytes(transport, id=id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path


async def compare_framebuffer_png(
    transport: Transport, *, id: str, reference: Path, save_mismatch: Path | None = None
) -> bool:
    """Compare the current framebuffer PNG with a reference file.

    Performs a byte-for-byte comparison. If different and `save_mismatch` is
    provided, writes the current framebuffer PNG there.

    Returns True if identical, False otherwise.
    """
    if not reference.exists():
        raise WokwiError(f"Reference image does not exist: {reference}")
    current = await framebuffer_png_bytes(transport, id=id)
    ref_bytes = reference.read_bytes()
    if current == ref_bytes:
        return True
    if save_mismatch:
        save_mismatch.parent.mkdir(parents=True, exist_ok=True)
        save_mismatch.write_bytes(current)
    return False
