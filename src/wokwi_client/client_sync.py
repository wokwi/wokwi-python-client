"""
Synchronous Wokwi Client Library

This module exposes a blocking (sync) interface that mirrors the async
`WokwiClient` API by running an asyncio loop in a dedicated thread and
delegating all coroutine calls to that loop.
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import contextlib
import inspect
import threading
from collections.abc import Coroutine
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Any, Callable, TypeVar

from .client import WokwiClient
from .serial import monitor_lines

T = TypeVar("T")


class WokwiClientSync:
    """
    Synchronous client for the Wokwi Simulation API.

    Design:
      • A private asyncio loop runs on a dedicated background thread.
      • Public methods mirror the async API by submitting the underlying
        coroutine calls onto that loop and waiting for results (blocking).
      • Long-lived streamers (serial monitors) are scheduled on the loop and
        tracked, so we can cancel & drain them on `disconnect()`.
    """

    def __init__(self, token: str, server: str | None = None):
        # Create a new event loop for the background thread
        self._loop = asyncio.new_event_loop()
        # Event to signal that the event loop is running
        self._loop_started_event = threading.Event()
        # Start background thread running the event loop
        self._thread = threading.Thread(
            target=self._run_loop, args=(self._loop,), daemon=True, name="wokwi-sync-loop"
        )
        self._thread.start()
        # **Wait until loop is fully started before proceeding** (prevents race conditions)
        if not self._loop_started_event.wait(timeout=8.0):  # timeout to avoid deadlock
            raise RuntimeError("WokwiClientSync event loop failed to start")
        # Initialize underlying async client on the running loop
        self._async_client = WokwiClient(token, server)
        # Track background monitor tasks (futures) for cancellation on exit
        self._bg_futures: set[Future[Any]] = set()
        # Flag to avoid double-closing
        self._closed = False

    def _run_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Target function for the background thread: runs the asyncio event loop."""
        asyncio.set_event_loop(loop)
        # Signal that the loop is now running and ready to accept tasks
        loop.call_soon(self._loop_started_event.set)
        loop.run_forever()

    # ----- Internal helpers -------------------------------------------------
    def _submit(self, coro: Coroutine[Any, Any, T]) -> Future[T]:
        """Submit a coroutine to the loop and return its concurrent.futures.Future."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def _call(self, coro: Coroutine[Any, Any, T]) -> T:
        """Submit a coroutine to the background loop and wait for result."""
        if self._closed:
            raise RuntimeError("Cannot call methods on a closed WokwiClientSync")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()  # Block until the coroutine completes or raises

    def _add_bg_future(self, fut: Future[Any]) -> None:
        """Track a background future so we can cancel & drain on shutdown."""
        self._bg_futures.add(fut)

    # ----- Context manager sugar -------------------------------------------
    def __enter__(self) -> WokwiClientSync:
        self.connect()
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: Any) -> None:
        self.disconnect()

    # ----- Lifecycle --------------------------------------------------------
    def connect(self) -> dict[str, Any]:
        """Connect to the simulator (blocking) and return server info."""
        return self._call(self._async_client.connect())

    def disconnect(self) -> None:
        if self._closed:
            return

        # (1) Cancel + drain monitors
        for fut in list(self._bg_futures):
            fut.cancel()
        for fut in list(self._bg_futures):
            with contextlib.suppress(FutureTimeoutError, Exception):
                fut.result(timeout=1.0)
            self._bg_futures.discard(fut)

        # (2) Disconnect transport
        with contextlib.suppress(Exception):
            fut = asyncio.run_coroutine_threadsafe(self._async_client.disconnect(), self._loop)
            fut.result(timeout=2.0)

        # (3) Stop loop / join thread
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread.is_alive():
            self._thread.join(timeout=5.0)

        # (4) Close loop
        with contextlib.suppress(Exception):
            self._loop.close()

        # (5) Mark closed at the very end
        self._closed = True

    # ----- Serial monitoring ------------------------------------------------
    def serial_monitor(self, callback: Callable[[bytes], Any]) -> None:
        """
        Start monitoring the serial output in the background and invoke `callback`
        for each line. Non-blocking. Runs until `disconnect()`.

        The callback may be sync or async. Exceptions raised by the callback are
        swallowed to keep the monitor alive (add your own logging as needed).
        """

        async def _runner() -> None:
            try:
                # **Prepare to receive serial events before enabling monitor**
                # (monitor_lines will subscribe to serial events internally)
                async for line in monitor_lines(self._async_client._transport):
                    try:
                        result = callback(line)  # invoke callback with the raw bytes line
                        if inspect.isawaitable(result):
                            await result  # await if callback is async
                    except Exception:
                        # Swallow exceptions from callback to keep monitor alive
                        pass
            finally:
                # Remove this task’s future from the set when done
                self._bg_futures.discard(task_future)

        # Schedule the serial monitor runner on the event loop:
        task_future = asyncio.run_coroutine_threadsafe(_runner(), self._loop)
        self._bg_futures.add(task_future)
        # (No return value; monitoring happens in background)

    def serial_monitor_cat(self, decode_utf8: bool = True, errors: str = "replace") -> None:
        """
        Print serial monitor output in the background (non-blocking). Runs until `disconnect()`.

        Args:
            decode_utf8: Whether to decode bytes as UTF-8 (default True).
            errors: UTF-8 decoding error strategy ('strict'|'ignore'|'replace').
        """

        async def _runner() -> None:
            try:
                # **Subscribe to serial events before reading output**
                async for line in monitor_lines(self._async_client._transport):
                    try:
                        if decode_utf8:
                            # Decode bytes to string (handle errors per parameter)
                            text = line.decode("utf-8", errors=errors)
                            print(text, end="", flush=True)
                        else:
                            # Print raw bytes
                            print(line, end="", flush=True)
                    except Exception:
                        # Swallow print errors to keep stream alive
                        pass
            finally:
                self._bg_futures.discard(task_future)

        task_future = asyncio.run_coroutine_threadsafe(_runner(), self._loop)
        self._bg_futures.add(task_future)
        # (No return; printing continues in background)

    def stop_serial_monitors(self) -> None:
        """Stop all active serial monitor background tasks."""
        for fut in list(self._bg_futures):
            fut.cancel()
        self._bg_futures.clear()

    # ----- Dynamic method wrapping -----------------------------------------
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the underlying async client.

        If the attribute on `WokwiClient` is a coroutine function, return a
        sync wrapper that blocks until the coroutine completes.
        """
        # Explicit methods (like serial_monitor functions above) take precedence over __getattr__
        attr = getattr(self._async_client, name)
        if callable(attr):
            # Get the function object from WokwiClient class (unbound) to check if coroutine
            func = getattr(WokwiClient, name, None)
            if func is not None and inspect.iscoroutinefunction(func):
                # Wrap coroutine method to run in background loop
                def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                    return self._call(attr(*args, **kwargs))

                sync_wrapper.__name__ = name
                sync_wrapper.__doc__ = getattr(func, "__doc__", "")
                return sync_wrapper
        return attr
