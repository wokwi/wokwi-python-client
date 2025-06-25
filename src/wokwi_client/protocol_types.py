# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from typing import Any, TypedDict, Union


class HelloMessage(TypedDict):
    type: str  # "hello"
    protocolVersion: int
    appName: str
    appVersion: str


class CommandMessage(TypedDict, total=False):
    type: str  # "command"
    command: str
    id: str
    params: dict[str, Any]


class ResponseMessage(TypedDict):
    type: str  # "response"
    command: str
    id: str
    result: dict[str, Any]
    error: bool


class ErrorResult(TypedDict):
    code: int
    message: str


class EventMessage(TypedDict):
    type: str  # "event"
    event: str
    payload: dict[str, Any]
    nanos: float
    paused: bool


IncomingMessage = Union[HelloMessage, ResponseMessage, EventMessage]
