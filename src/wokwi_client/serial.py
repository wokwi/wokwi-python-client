# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from collections.abc import AsyncGenerator
from typing import cast

from .protocol_types import EventMessage
from .transport import Transport


async def monitor_lines(transport: Transport) -> AsyncGenerator[bytes, None]:
    await transport.request("serial-monitor:listen", {})
    while True:
        msg = await transport.recv()
        if msg["type"] == "event":
            event_msg = cast(EventMessage, msg)
            if event_msg["event"] == "serial-monitor:data":
                yield bytes(event_msg["payload"]["bytes"])
