# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import asyncio
import logging
import threading
import typing as t
from pathlib import Path

from wokwi_client import WokwiClient
from wokwi_client.serial import monitor_lines as monitor_serial_lines


class WokwiClientSync:
    """Synchronous wrapper around the async WokwiClient."""

    def __init__(self, token: str, server: t.Optional[str] = None):
        self.token = token
        self.server = server
        self._loop = None
        self._loop_thread = None
        self._client = None
        self._connected = False

    def _ensure_loop(self):
        """Ensure the async event loop is running."""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
            self._loop_thread.start()

    def _run_async(self, coro, timeout=30):
        """Run an async coroutine synchronously."""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    def connect(self):
        """Connect to Wokwi server."""
        if not self._connected:
            self._client = WokwiClient(self.token, self.server)
            result = self._run_async(self._client.connect())
            self._connected = True
            return result
        return {}

    def disconnect(self):
        """Disconnect from Wokwi server."""
        if self._connected and self._client:
            try:
                # Stop any ongoing monitor task
                if hasattr(self, '_monitor_task') and self._monitor_task:
                    self._monitor_task.cancel()

                # Disconnect the client
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

    def upload(self, name: str, content: bytes):
        """Upload a file to the simulator from bytes content."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.upload(name, content))

    def upload_file(self, filename: str, local_path: t.Optional[Path] = None):
        """Upload a file to the simulator."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.upload_file(filename, local_path))

    def start_simulation(self, firmware: str, elf: t.Optional[str] = None, pause: bool = False, chips: list[str] = []):
        """Start a simulation."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.start_simulation(firmware, elf, pause, chips))

    def pause_simulation(self):
        """Pause the running simulation."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.pause_simulation())

    def resume_simulation(self, pause_after: t.Optional[int] = None):
        """Resume the simulation, optionally pausing after a given number of nanoseconds."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.resume_simulation(pause_after))

    def wait_until_simulation_time(self, seconds: float):
        """Pause and resume the simulation until the given simulation time (in seconds) is reached."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.wait_until_simulation_time(seconds))

    def restart_simulation(self, pause: bool = False):
        """Restart the simulation, optionally starting paused."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.restart_simulation(pause))

    def serial_monitor_cat(self):
        """Print serial monitor output to stdout as it is received from the simulation."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.serial_monitor_cat())

    def write_serial(self, data: t.Union[bytes, str, list[int]]):
        """Write data to serial."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.serial_write(data))

    def read_pin(self, part: str, pin: str):
        """Read the current state of a pin."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.read_pin(part, pin))

    def listen_pin(self, part: str, pin: str, listen: bool = True):
        """Start or stop listening for changes on a pin."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.listen_pin(part, pin, listen))

    def monitor_serial(self, callback):
        """Start monitoring serial output with a callback."""
        if not self._connected:
            raise RuntimeError("Client not connected")

        async def _monitor():
            try:
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

        # Start monitoring in background
        self._monitor_task = asyncio.run_coroutine_threadsafe(_monitor(), self._loop)

    def set_control(self, part: str, control: str, value: t.Union[int, bool, float]):
        """Set control value for a part."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        return self._run_async(self._client.set_control(part, control, value))

    @property
    def version(self):
        """Get client version."""
        if self._client:
            return self._client.version
        # Return a default version if client not initialized yet
        client = WokwiClient(self.token, self.server)
        return client.version

    @property
    def last_pause_nanos(self):
        """Get the last pause time in nanoseconds."""
        if self._client:
            return self._client.last_pause_nanos
        return 0
