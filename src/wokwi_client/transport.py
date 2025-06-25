# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import json
import os
import warnings
from typing import Any, Optional, cast

import websockets

from .__version__ import get_version
from .constants import (
    DEFAULT_WS_URL,
    MSG_TYPE_HELLO,
    MSG_TYPE_RESPONSE,
    PROTOCOL_VERSION,
)
from .exceptions import ProtocolError, ServerError, WokwiError
from .protocol_types import HelloMessage, IncomingMessage, ResponseMessage

TRANSPORT_DEFAULT_WS_URL = os.getenv("WOKWI_CLI_SERVER", DEFAULT_WS_URL)


class Transport:
    def __init__(self, token: str, url: str = TRANSPORT_DEFAULT_WS_URL):
        self._token = token
        self._url = url
        self._next_id = 1
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

    async def connect(self) -> dict[str, Any]:
        self._ws = await websockets.connect(
            self._url,
            extra_headers={
                "Authorization": f"Bearer {self._token}",
                "User-Agent": f"wokwi-client-py/{get_version()}",
            },
        )
        hello: IncomingMessage = await self._recv()
        if hello["type"] != MSG_TYPE_HELLO or hello.get("protocolVersion") != PROTOCOL_VERSION:
            raise ProtocolError(f"Unsupported protocol handshake: {hello}")
        hello_msg = cast(HelloMessage, hello)
        return {"version": hello_msg["appVersion"]}

    async def close(self) -> None:
        if self._ws:
            await self._ws.close()

    async def request(self, command: str, params: dict[str, Any]) -> ResponseMessage:
        msg_id = str(self._next_id)
        self._next_id += 1
        if self._ws is None:
            raise WokwiError("Not connected")
        await self._ws.send(
            json.dumps({"type": "command", "command": command, "params": params, "id": msg_id})
        )
        while True:
            msg: IncomingMessage = await self._recv()
            if msg["type"] == MSG_TYPE_RESPONSE and msg.get("id") == msg_id:
                resp_msg = cast(ResponseMessage, msg)
                if resp_msg.get("error"):
                    result = resp_msg["result"]
                    raise ServerError(result["message"])
                return resp_msg

    async def _recv(self) -> IncomingMessage:
        if self._ws is None:
            raise WokwiError("Not connected")
        raw_message = await self._ws.recv()
        while isinstance(raw_message, bytes):
            warnings.warn("Unexpected binary message received and skipped", RuntimeWarning)
            raw_message = await self._ws.recv()
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError as e:
            raise WokwiError(f"Failed to parse message: {raw_message}") from e
        if "type" not in message:
            raise WokwiError(f"Invalid message: {message}")
        if message["type"] == "error":
            raise WokwiError(f"Server error: {message['message']}")
        if message["type"] == "response" and message.get("error"):
            result = (
                message["result"]
                if "result" in message
                else {"code": -1, "message": "Unknown error"}
            )
            raise WokwiError(f"Server error {result['code']}: {result['message']}")
        return cast(IncomingMessage, message)

    async def recv(self) -> IncomingMessage:
        return await self._recv()
