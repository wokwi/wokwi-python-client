# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from typing import Any, Optional

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
) -> ResponseMessage:
    params: dict[str, Any] = {"elf": elf, "pause": pause, "chips": chips}
    if isinstance(firmware, list):
        params["firmware"] = [{"offset": s.offset, "file": s.file} for s in firmware]
    elif firmware is not None:
        params["firmware"] = firmware
    if flash_size:
        params["flashSize"] = flash_size
    return await transport.request("sim:start", params)


async def pause(transport: Transport) -> ResponseMessage:
    return await transport.request("sim:pause", {})


async def resume(transport: Transport, pause_after: Optional[int] = None) -> ResponseMessage:
    return await transport.request("sim:resume", {"pauseAfter": pause_after})


async def restart(transport: Transport, pause: bool = False) -> ResponseMessage:
    return await transport.request("sim:restart", {"pause": pause})
