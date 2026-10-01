# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import base64
from typing import Any, Literal, Optional

from .models import SDCardConfig, SDCardFile
from .protocol_types import ResponseMessage
from .transport import Transport


async def start(  # noqa: PLR0913
    transport: Transport,
    *,
    firmware: Any = None,
    flash_size: Optional[int] = None,
    elf: Optional[str] = None,
    pause: bool = False,
    chips: list[str] = [],
    sdcards: Optional[list[SDCardConfig]] = None,
) -> ResponseMessage:
    params: dict[str, Any] = {"elf": elf, "pause": pause, "chips": chips}
    if isinstance(firmware, list):
        params["firmware"] = [{"offset": s.offset, "file": s.file} for s in firmware]
    elif firmware is not None:
        params["firmware"] = firmware
    if flash_size:
        params["flashSize"] = flash_size
    if sdcards:
        params["sdcards"] = [card.to_params() for card in sdcards]
    return await transport.request("sim:start", params)


async def export_sdcard_image(transport: Transport, part: Optional[str] = None) -> bytes:
    params: dict[str, Any] = {"format": "image"}
    if part is not None:
        params["part"] = part
    result = await transport.request("sdcard:export", params)
    return base64.b64decode(result["result"]["image"])


async def export_sdcard_files(transport: Transport, part: Optional[str] = None) -> list[SDCardFile]:
    params: dict[str, Any] = {"format": "files"}
    if part is not None:
        params["part"] = part
    result = await transport.request("sdcard:export", params)
    return [
        SDCardFile(name=entry["name"], content=base64.b64decode(entry["binary"]))
        for entry in result["result"]["files"]
    ]


SDCardExportFormat = Literal["image", "files"]


async def pause(transport: Transport) -> ResponseMessage:
    return await transport.request("sim:pause", {})


async def resume(transport: Transport, pause_after: Optional[int] = None) -> ResponseMessage:
    return await transport.request("sim:resume", {"pauseAfter": pause_after})


async def restart(transport: Transport, pause: bool = False) -> ResponseMessage:
    return await transport.request("sim:restart", {"pause": pause})
