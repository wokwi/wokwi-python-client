"""Pin command helpers for the Wokwi Simulation API.

This module exposes helper coroutines for issuing pin-related commands:

* pin:read   - Read the current state of a pin.
* pin:listen - Start/stop listening for changes on a pin (emits pin:change
    events).
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from typing import TypedDict

from wokwi_client.protocol_types import ResponseMessage

from .transport import Transport


class PinReadMessage(TypedDict):
    pin: str
    direction: str
    value: bool
    pullUp: bool
    pullDown: bool


class PinListenEvent(TypedDict):
    part: str
    pin: str
    direction: str
    value: bool
    pullUp: bool
    pullDown: bool


async def pin_read(transport: Transport, *, part: str, pin: str) -> ResponseMessage:
    """Read the state of a pin.

    Args:
        transport: The active Transport instance.
        part: Part identifier (e.g. "uno").
        pin: Pin name (e.g. "A2", "13").
    """

    return await transport.request("pin:read", {"part": part, "pin": pin})


async def pin_listen(transport: Transport, *, part: str, pin: str, listen: bool = True) -> None:
    """Enable or disable listening for changes on a pin.

    When listening is enabled, "pin:change" events will be emitted with the
    pin state.

    Args:
        transport: The active Transport instance.
        part: Part identifier.
        pin: Pin name.
        listen: True to start listening, False to stop.
    """

    await transport.request("pin:listen", {"part": part, "pin": pin, "listen": listen})


async def gpio_list(transport: Transport) -> ResponseMessage:
    """List all GPIO pins and their current states.

    Args:
        transport: The active Transport instance.
    """

    return await transport.request("gpio:list", {})
