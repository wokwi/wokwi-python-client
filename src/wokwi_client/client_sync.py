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

    # Public attributes mirrored for convenience
    version: str
    last_pause_nanos: int  # this proxy resolves via __getattr__

    def __init__(self, token: str, server: str | None = None):
        # Create a fresh event loop + thread (daemon so it won't prevent process exit).
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop, args=(self._loop,), daemon=True, name="wokwi-sync-loop"
        )
        self._thread.start()

        # Underlying async client
        self._async_client = WokwiClient(token, server)

        # Mirror library version for quick access
        self.version = self._async_client.version

        # Track background tasks created via run_coroutine_threadsafe (serial monitors)
        self._bg_futures: set[Future[Any]] = set()

        # Idempotent disconnect guard
        self._closed = False

    @staticmethod
    def _run_loop(loop: asyncio.AbstractEventLoop) -> None:
        """Background thread loop runner."""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    # ----- Internal helpers -------------------------------------------------
    def _submit(self, coro: Coroutine[Any, Any, T]) -> Future[T]:
        """Submit a coroutine to the loop and return its concurrent.futures.Future."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def _call(self, coro: Coroutine[Any, Any, T]) -> T:
        """Submit a coroutine to the loop and block until it completes (or raises)."""
        return self._submit(coro).result()

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
        """Disconnect and stop the background loop.

        Order matters:
          1) Cancel and drain background serial-monitor futures.
          2) Disconnect the underlying transport.
          3) Stop the loop and join the thread.
        Safe to call multiple times.
        """
        if self._closed:
            return
        self._closed = True

        # (1) Cancel + drain monitors
        for fut in list(self._bg_futures):
            fut.cancel()
        for fut in list(self._bg_futures):
            with contextlib.suppress(FutureTimeoutError, Exception):
                # Give each monitor a short window to handle cancellation cleanly.
                fut.result(timeout=1.0)
            self._bg_futures.discard(fut)

        # (2) Disconnect transport
        with contextlib.suppress(Exception):
            self._call(self._async_client._transport.close())

        # (3) Stop loop / join thread
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread.is_alive():
            self._thread.join(timeout=5.0)

    # ----- Serial monitoring ------------------------------------------------
    def serial_monitor(self, callback: Callable[[bytes], Any]) -> None:
        """
        Start monitoring the serial output in the background and invoke `callback`
        for each line. Non-blocking. Runs until `disconnect()`.

        The callback may be sync or async. Exceptions raised by the callback are
        swallowed to keep the monitor alive (add your own logging as needed).
        """

        async def _runner() -> None:
            async for line in monitor_lines(self._async_client._transport):
                try:
                    maybe_awaitable = callback(line)
                    if inspect.isawaitable(maybe_awaitable):
                        await maybe_awaitable
                except Exception:
                    # Keep the monitor alive even if the callback throws.
                    pass

        fut = self._submit(_runner())
        self._add_bg_future(fut)

    def serial_monitor_cat(self, decode_utf8: bool = True, errors: str = "replace") -> None:
        """
        Print serial monitor output in the background (non-blocking). Runs until `disconnect()`.

        Args:
            decode_utf8: Whether to decode bytes as UTF-8 (default True).
            errors: UTF-8 decoding error strategy ('strict'|'ignore'|'replace').
        """

        async def _runner() -> None:
            async for line in monitor_lines(self._async_client._transport):
                try:
                    if decode_utf8:
                        try:
                            print(line.decode("utf-8", errors=errors), end="", flush=True)
                        except UnicodeDecodeError:
                            print(line, end="", flush=True)
                    else:
                        print(line, end="", flush=True)
                except Exception:
                    # Keep the monitor alive even if printing raises intermittently.
                    pass

        fut = self._submit(_runner())
        self._add_bg_future(fut)

    def stop_serial_monitors(self) -> None:
        """
        Cancel and drain all running serial monitors without disconnecting.

        Useful if you want to stop printing but keep the connection alive.
        """
        for fut in list(self._bg_futures):
            fut.cancel()
        for fut in list(self._bg_futures):
            with contextlib.suppress(FutureTimeoutError, Exception):
                fut.result(timeout=1.0)
            self._bg_futures.discard(fut)

    # ----- Dynamic method wrapping -----------------------------------------
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the underlying async client.

        If the attribute on `WokwiClient` is a coroutine function, return a
        sync wrapper that blocks until the coroutine completes.
        """
        # Explicit methods above (serial monitors) take precedence.
        attr = getattr(self._async_client, name)
        if callable(attr):
            func = getattr(WokwiClient, name, None)
            if func is not None and inspect.iscoroutinefunction(func):

                def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                    return self._call(attr(*args, **kwargs))

                sync_wrapper.__name__ = name
                sync_wrapper.__doc__ = func.__doc__
                return sync_wrapper
        return attr
