"""Touch event helpers for parts with touchscreens.

Provides `touch_event` to simulate touch interactions (press, move, release)
on parts with capacitive or resistive touchscreens.

Assumptions:
* Underlying websocket command name: "touch:event".
* Parameter names expected by server: part, x, y, event, releaseAfter.
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from typing import Any, Optional

from .protocol_types import ResponseMessage
from .transport import Transport


async def touch_event(  # noqa: PLR0913
    transport: Transport,
    *,
    part: str,
    x: float,
    y: float,
    event: str,
    release_after: Optional[int] = None,
) -> ResponseMessage:
    """Send a touch event to a part.

    Args:
        transport: Active Transport.
        part: Part identifier (e.g. "lcd1").
        x: X coordinate (touch controller coordinates).
        y: Y coordinate (touch controller coordinates).
        event: Touch event type: "press", "release", or "move".
        release_after: For "press" events, automatically release after
            this many nanoseconds (optional).
    """
    params: dict[str, Any] = {"part": part, "x": x, "y": y, "event": event}
    if release_after is not None:
        params["releaseAfter"] = release_after
    return await transport.request("touch:event", params)
