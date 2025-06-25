# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any, Optional

from .__version__ import get_version
from .constants import DEFAULT_WS_URL
from .file_ops import upload, upload_file
from .protocol_types import ResponseMessage
from .serial import monitor_lines
from .simulation import pause, restart, resume, start
from .transport import Transport


class WokwiClient:
    version: str

    def __init__(self, token: str, server: Optional[str] = None):
        self.version = get_version()
        self._transport = Transport(token, server or DEFAULT_WS_URL)

    async def connect(self) -> dict[str, Any]:
        return await self._transport.connect()

    async def disconnect(self) -> None:
        await self._transport.close()

    async def upload(self, name: str, content: bytes) -> ResponseMessage:
        return await upload(self._transport, name, content)

    async def upload_file(
        self, filename: str, local_path: Optional[Path] = None
    ) -> ResponseMessage:
        return await upload_file(self._transport, filename, local_path)

    async def start_simulation(self, **kwargs: Any) -> ResponseMessage:
        return await start(self._transport, **kwargs)

    async def pause_simulation(self) -> ResponseMessage:
        return await pause(self._transport)

    async def resume_simulation(self, pause_after: Optional[int] = None) -> ResponseMessage:
        return await resume(self._transport, pause_after)

    async def restart_simulation(self, pause: bool = False) -> ResponseMessage:
        return await restart(self._transport, pause)

    async def serial_monitor_cat(self) -> None:
        async for line in monitor_lines(self._transport):
            print(line.decode("utf-8"), end="", flush=True)
