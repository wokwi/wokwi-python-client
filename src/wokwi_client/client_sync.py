# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import logging
import threading
import typing as t
from concurrent.futures import Future
from pathlib import Path

from wokwi_client import WokwiClient
from wokwi_client.serial import monitor_lines as monitor_serial_lines

if t.TYPE_CHECKING:
    pass


class WokwiClientSync:
    """Synchronous wrapper around the async WokwiClient."""

    token: str
    server: str | None
    _loop: asyncio.AbstractEventLoop | None
    _loop_thread: threading.Thread | None
    _client: WokwiClient | None
    _monitor_task: Future[t.Any] | None
    _connected: bool

    def __init__(self, token: str, server: str | None = None) -> None:
        self.token = token
        self.server = server
        self._loop = None
        self._loop_thread = None
        self._client = None
        self._monitor_task = None
        self._connected = False

    def _ensure_loop(self) -> None:
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
            self._loop_thread.start()

    def _run_async(self, coro: t.Coroutine[t.Any, t.Any, t.Any], timeout: float = 30) -> t.Any:
        self._ensure_loop()
        assert self._loop is not None
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    def connect(self) -> dict[str, t.Any]:
        if not self._connected:
            self._client = WokwiClient(self.token, self.server)
            result: dict[str, t.Any] = t.cast(
                dict[str, t.Any], self._run_async(self._client.connect())
            )
            self._connected = True
            return result
        return {}

    def disconnect(self) -> None:
        if self._connected and self._client:
            try:
                if self._monitor_task:
                    self._monitor_task.cancel()
                self._run_async(self._client.disconnect(), timeout=5)
            except Exception as e:
                logging.debug(f"Error during disconnect: {e}")
            finally:
                self._connected = False
                self._client = None
                if self._loop and self._loop_thread:
                    try:
                        self._loop.call_soon_threadsafe(self._loop.stop)
                        self._loop_thread.join(timeout=2)
                    except Exception as e:
                        logging.debug(f"Error stopping event loop: {e}")
                    finally:
                        self._loop = None
                        self._loop_thread = None

    def upload(self, name: str, content: bytes) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.upload(name, content))

    def upload_file(self, filename: str, local_path: Path | None = None) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.upload_file(filename, local_path))

    def download(self, name: str) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.download(name))

    def download_file(self, name: str, local_path: Path | None = None) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.download_file(name, local_path))

    def start_simulation(
        self,
        firmware: str,
        elf: str | None = None,
        pause: bool = False,
        chips: list[str] | None = None,
    ) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.start_simulation(firmware, elf, pause, chips or []))

    def pause_simulation(self) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.pause_simulation())

    def resume_simulation(self, pause_after: int | None = None) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.resume_simulation(pause_after))

    def wait_until_simulation_time(self, seconds: float) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.wait_until_simulation_time(seconds))

    def restart_simulation(self, pause: bool = False) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.restart_simulation(pause))

    def serial_monitor_cat(self) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.serial_monitor_cat())

    def write_serial(self, data: bytes | str | list[int]) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.serial_write(data))

    def read_pin(self, part: str, pin: str) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.read_pin(part, pin))

    def listen_pin(self, part: str, pin: str, listen: bool = True) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.listen_pin(part, pin, listen))

    def gpio_list(self) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.gpio_list())

    def monitor_serial(self, callback: t.Callable[[bytes], None]) -> None:
        if not self._connected:
            raise RuntimeError("Client not connected")

        async def _monitor() -> None:
            try:
                assert self._client is not None
                async for line in monitor_serial_lines(self._client._transport):
                    if not self._connected:
                        break
                    try:
                        callback(line)
                    except Exception as e:
                        logging.error(f"Error in serial monitor callback: {e}")
                        break
            except Exception as e:
                logging.error(f"Error in serial monitor: {e}")

        assert self._loop is not None
        self._monitor_task = asyncio.run_coroutine_threadsafe(_monitor(), self._loop)

    def set_control(self, part: str, control: str, value: int | bool | float) -> t.Any:
        if not self._connected:
            raise RuntimeError("Client not connected")
        assert self._client is not None
        return self._run_async(self._client.set_control(part, control, value))

    @property
    def version(self) -> str:
        if self._client:
            return self._client.version
        client = WokwiClient(self.token, self.server)
        return client.version

    @property
    def last_pause_nanos(self) -> int:
        if self._client:
            return self._client.last_pause_nanos
        return 0
