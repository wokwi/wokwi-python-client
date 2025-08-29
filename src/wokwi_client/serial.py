# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from collections.abc import AsyncGenerator
from typing import Union

from .event_queue import EventQueue
from .transport import Transport


async def monitor_lines(transport: Transport) -> AsyncGenerator[bytes, None]:
    """
    Monitor the serial output lines.
    """
    await transport.request("serial-monitor:listen", {})
    with EventQueue(transport, "serial-monitor:data") as queue:
        while True:
            event_msg = await queue.get()
            yield bytes(event_msg["payload"]["bytes"])


async def write_serial(transport: Transport, data: Union[bytes, str, list[int]]) -> None:
    """Write data to the serial monitor.

    Accepts bytes, str (encoded as utf-8), or an iterable of integer byte values.
    """
    if isinstance(data, str):
        payload = list(data.encode("utf-8"))
    elif isinstance(data, bytes):
        payload = list(data)
    else:
        payload = list(int(b) & 0xFF for b in data)
    await transport.request("serial-monitor:write", {"bytes": payload})
