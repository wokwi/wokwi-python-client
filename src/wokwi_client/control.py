"""Control command helpers for virtual parts.

Provides `set_control` to manipulate part controls (e.g. press a button).

Assumptions:
* Underlying websocket command name: "control:set".
* Parameter names expected by server: part, control, value.
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from typing import Union

from .protocol_types import ResponseMessage
from .transport import Transport


async def set_control(
    transport: Transport, *, part: str, control: str, value: Union[int, bool, float]
) -> ResponseMessage:
    """Set a control value on a part (e.g. simulate button press/release).

    Args:
        transport: Active Transport.
        part: Part identifier (e.g. "btn1").
        control: Control name (e.g. "pressed").
        value: Control value to set (float).
    """
    return await transport.request(
        "control:set", {"part": part, "control": control, "value": float(value)}
    )
