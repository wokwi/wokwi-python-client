# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import asyncio
import contextlib
import json
import os
import warnings
from typing import Any, Callable, Optional, cast

import websockets

from .__version__ import get_version
from .constants import (
    DEFAULT_WS_URL,
    MSG_TYPE_EVENT,
    MSG_TYPE_HELLO,
    MSG_TYPE_RESPONSE,
    PROTOCOL_VERSION,
)
from .exceptions import ProtocolError, ServerError, WokwiError
from .protocol_types import EventMessage, HelloMessage, IncomingMessage, ResponseMessage

TRANSPORT_DEFAULT_WS_URL = os.getenv("WOKWI_CLI_SERVER", DEFAULT_WS_URL)


class Transport:
    def __init__(self, token: str, url: str = TRANSPORT_DEFAULT_WS_URL):
        self._token = token
        self._url = url
        self._next_id = 1
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._event_listeners: dict[str, list[Callable[[EventMessage], Any]]] = {}
        self._response_futures: dict[str, asyncio.Future[ResponseMessage]] = {}
        self._recv_task: Optional[asyncio.Task[None]] = None
        self._closed = False

    async def connect(self, throw_error: bool = True) -> dict[str, Any]:
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
        self._closed = False
        # Start background message processor after successful hello.
        self._recv_task = asyncio.create_task(self._background_recv(throw_error))
        return {"version": hello_msg["appVersion"]}

    async def close(self) -> None:
        self._closed = True
        if self._recv_task:
            self._recv_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._recv_task
        if self._ws:
            await self._ws.close()

    def add_event_listener(self, event_type: str, listener: Callable[[EventMessage], Any]) -> None:
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(listener)

    def remove_event_listener(
        self, event_type: str, listener: Callable[[EventMessage], Any]
    ) -> None:
        if event_type in self._event_listeners:
            self._event_listeners[event_type] = [
                registered_listener
                for registered_listener in self._event_listeners[event_type]
                if registered_listener != listener
            ]
            if not self._event_listeners[event_type]:
                del self._event_listeners[event_type]

    async def _dispatch_event(self, event_msg: EventMessage) -> None:
        listeners = self._event_listeners.get(event_msg["event"], [])
        for listener in listeners:
            result = listener(event_msg)
            if hasattr(result, "__await__"):
                await result

    async def request(self, command: str, params: dict[str, Any]) -> ResponseMessage:
        if self._ws is None:
            raise WokwiError("Not connected")
        msg_id = str(self._next_id)
        self._next_id += 1

        loop = asyncio.get_running_loop()
        future: asyncio.Future[ResponseMessage] = loop.create_future()
        self._response_futures[msg_id] = future

        await self._ws.send(
            json.dumps({"type": "command", "command": command, "params": params, "id": msg_id})
        )
        try:
            resp_msg_resp = await future
            if resp_msg_resp.get("error"):
                result = resp_msg_resp.get("result", {})
                raise ServerError(result.get("message", "Unknown server error"))
            return resp_msg_resp
        finally:
            # Remove future mapping if still present (be defensive)
            self._response_futures.pop(msg_id, None)

    async def _background_recv(self, throw_error: bool = True) -> None:  # noqa: PLR0912
        try:
            while not self._closed and self._ws is not None:
                msg: IncomingMessage = await self._recv()
                if msg["type"] == MSG_TYPE_EVENT:
                    await self._dispatch_event(cast(EventMessage, msg))
                elif msg["type"] == MSG_TYPE_RESPONSE:
                    resp_msg_resp = cast(ResponseMessage, msg)
                    resp_id = str(resp_msg_resp.get("id"))
                    future = self._response_futures.get(resp_id)
                    if future is None or future.done():
                        continue
                    future.set_result(resp_msg_resp)
        except asyncio.CancelledError:
            # Expected during shutdown via close()
            raise
        except websockets.ConnectionClosed as e:
            # Mark closed and fail pending futures to avoid hangs.
            self._closed = True
            for fut in list(self._response_futures.values()):
                if not fut.done():
                    fut.set_exception(e)
            with contextlib.suppress(Exception):
                if self._ws:
                    await self._ws.close()
            if throw_error:
                raise
        except Exception as e:
            warnings.warn(f"Background recv error: {e}", RuntimeWarning)
            if throw_error:
                self._closed = True
                for fut in list(self._response_futures.values()):
                    if not fut.done():
                        fut.set_exception(e)
                with contextlib.suppress(Exception):
                    if self._ws:
                        await self._ws.close()
                raise
        finally:
            # If we’re exiting the loop and marked closed, ensure no future hangs.
            if self._closed:
                for fut in list(self._response_futures.values()):
                    if not fut.done():
                        fut.set_exception(RuntimeError("Transport receive loop exited"))

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
            result = message.get("result", {"code": -1, "message": "Unknown error"})
            raise WokwiError(f"Server error {result['code']}: {result['message']}")
        return cast(IncomingMessage, message)
