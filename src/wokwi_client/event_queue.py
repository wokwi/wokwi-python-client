# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

"""
Queue-based event subscription helper for Transport.

Usage:
    with EventQueue(transport, "serial-monitor:data") as queue:
        # Use the queue to get events, calling get() or get_nowait()
        event = await queue.get()
        # do something with the event
        ...
"""

import asyncio

from .protocol_types import EventMessage
from .transport import Transport


class EventQueue:
    """A queue for events from a specific event type."""

    def __init__(self, transport: Transport, event_type: str) -> None:
        # Bind the queue to the current running loop (important for py3.9)
        self._loop = asyncio.get_running_loop()
        self._queue: asyncio.Queue[EventMessage] = asyncio.Queue()
        self._transport = transport
        self._event_type = event_type

        def listener(event: EventMessage) -> None:
            # Ensure we enqueue on the loop that owns the queue, even if
            # the listener is invoked from a different loop/thread.
            self._loop.call_soon_threadsafe(self._queue.put_nowait, event)

        self._listener = listener
        self._transport.add_event_listener(self._event_type, self._listener)

    def close(self) -> None:
        """Close the queue. This is useful when you want to stop listening for events."""
        self._transport.remove_event_listener(self._event_type, self._listener)

    async def get(self) -> EventMessage:
        """Get an event from the queue. Blocks until an event is available."""
        return await self._queue.get()

    def get_nowait(self) -> EventMessage:
        """Get an event from the queue. Raises QueueEmpty if no event is available."""
        return self._queue.get_nowait()

    def flush(self) -> None:
        """Flush the queue. This is useful when you want to wait for all events to be processed."""
        while not self._queue.empty():
            self._queue.get_nowait()

    def __enter__(self) -> "EventQueue":
        return self

    def __exit__(self, exc_type: type, exc_value: Exception, traceback: object) -> None:
        self.close()
