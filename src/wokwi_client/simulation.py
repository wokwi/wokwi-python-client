# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from typing import Optional

from .protocol_types import ResponseMessage
from .transport import Transport


async def start(
    transport: Transport,
    *,
    firmware: str,
    elf: Optional[str] = None,
    pause: bool = False,
    chips: list[str] = [],
) -> ResponseMessage:
    return await transport.request(
        "sim:start", {"firmware": firmware, "elf": elf, "pause": pause, "chips": chips}
    )


async def pause(transport: Transport) -> ResponseMessage:
    return await transport.request("sim:pause", {})


async def resume(transport: Transport, pause_after: Optional[int] = None) -> ResponseMessage:
    return await transport.request("sim:resume", {"pauseAfter": pause_after})


async def restart(transport: Transport, pause: bool = False) -> ResponseMessage:
    return await transport.request("sim:restart", {"pause": pause})
