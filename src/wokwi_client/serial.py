# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from collections.abc import AsyncGenerator

from .event_queue import EventQueue
from .transport import Transport


async def monitor_lines(transport: Transport) -> AsyncGenerator[bytes, None]:
    await transport.request("serial-monitor:listen", {})
    with EventQueue(transport, "serial-monitor:data") as queue:
        while True:
            event_msg = await queue.get()
            yield bytes(event_msg["payload"]["bytes"])
