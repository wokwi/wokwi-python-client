# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import asyncio
import base64
import inspect
from pathlib import Path
from typing import Any, Callable, Optional, Union, cast

from .__version__ import get_version
from .constants import DEFAULT_WS_URL
from .control import set_control
from .event_queue import EventQueue
from .exceptions import ProtocolError
from .file_ops import download, upload, upload_file
from .framebuffer import (
    read_framebuffer_png_bytes,
    save_framebuffer_png,
)
from .pins import PinReadMessage, gpio_list, pin_listen, pin_read
from .protocol_types import EventMessage
from .serial import monitor_lines, write_serial
from .simulation import pause, restart, resume, start
from .transport import Transport


class WokwiClient:
    """
    Asynchronous client for the Wokwi Simulation API.

    This class provides methods to connect to the Wokwi simulator, upload files, control simulations,
    and monitor serial output. It is designed to be asyncio-friendly and easy to use in Python scripts
    and applications. For a synchronous interface, see WokwiClientSync.
    """

    version: str
    last_pause_nanos: int

    def __init__(self, token: str, server: Optional[str] = None):
        """
        Initialize the WokwiClient.

        Args:
            token: API token for authentication (get from https://wokwi.com/dashboard/ci).
            server: Optional custom server URL. Defaults to the public Wokwi server.
        """
        self.version = get_version()
        self._transport = Transport(token, server or DEFAULT_WS_URL)
        self.last_pause_nanos = 0
        self._transport.add_event_listener("sim:pause", self._on_pause)
        # Lazily create in an active event loop (important for py3.9 and sync client)
        self._pause_queue: Optional[EventQueue] = None
        self._serial_monitor_tasks: set[asyncio.Task[None]] = set()

    async def connect(self) -> dict[str, Any]:
        """
        Connect to the Wokwi simulator server.

        Returns:
            A dictionary with server information (e.g., version).
        """
        return await self._transport.connect()

    async def disconnect(self) -> None:
        """
        Disconnect from the Wokwi simulator server.

        This also stops all active serial monitors.
        """
        self.stop_serial_monitors()
        await self._transport.close()

    async def upload(self, name: str, content: bytes) -> None:
        """
        Upload a file to the simulator from bytes content.

        Args:
            name: The name to use for the uploaded file.
            content: The file content as bytes.
        """
        await upload(self._transport, name, content)

    async def upload_file(self, filename: str, local_path: Optional[Path] = None) -> str:
        """
        Upload a local file to the simulator.
        If you specify the local_path to the file `flasher_args.json` (IDF flash information),
        the contents of the file will be processed and the correct firmware file will be
        uploaded instead, returning the firmware filename.

        Args:
            filename: The name to use for the uploaded file.
            local_path: Optional path to the local file. If not provided, uses filename as the path.
        Returns:
            The filename of the uploaded file (useful for idf when uploading flasher_args.json).
        """
        return await upload_file(self._transport, filename, local_path)

    async def download(self, name: str) -> bytes:
        """
        Download a file from the simulator.

        Args:
            name: The name of the file to download.

        Returns:
            The downloaded file content as bytes.
        """
        result = await download(self._transport, name)
        return base64.b64decode(result["result"]["binary"])

    async def download_file(self, name: str, local_path: Optional[Path] = None) -> None:
        """
        Download a file from the simulator and save it to a local path.

        Args:
            name: The name of the file to download.
            local_path: The local path to save the downloaded file. If not provided, uses the name as the path.
        """
        if local_path is None:
            local_path = Path(name)

        result = await self.download(name)
        with open(local_path, "wb") as f:
            f.write(result)

    async def start_simulation(
        self,
        firmware: str,
        elf: Optional[str] = None,
        pause: bool = False,
        chips: list[str] = [],
    ) -> None:
        """
        Start a new simulation with the given parameters.

        The firmware and ELF files must be uploaded to the simulator first using the
        `upload()` or `upload_file()` methods.
        The firmware file is required for the simulation to run.
        The ELF file is optional and can speed up the simulation in some cases.

        The optional `chips` parameter can be used to load custom chips into the simulation.
        For each custom chip, you need to upload two files:
        - A JSON file with the chip definition, called `<chip_name>.chip.json`.
        - A binary file with the chip firmware, called `<chip_name>.chip.bin`.

        For example, to load the `inverter` chip, you need to upload the `inverter.chip.json`
        and `inverter.chip.bin` files. Then you can pass `["inverter"]` to the `chips` parameter,
        and reference it in your diagram.json file by adding a part with the type `chip-inverter`.

        Args:
            firmware: The firmware binary filename.
            elf: The ELF file filename (optional).
            pause: Whether to start the simulation paused (default: False).
            chips: List of custom chips to load into the simulation (default: empty list).
        """
        await start(
            self._transport,
            firmware=firmware,
            elf=elf,
            pause=pause,
            chips=chips,
        )

    async def pause_simulation(self) -> None:
        """
        Pause the running simulation.
        """
        await pause(self._transport)

    async def resume_simulation(self, pause_after: Optional[int] = None) -> None:
        """
        Resume the simulation, optionally pausing after a given number of nanoseconds.

        Args:
            pause_after: Number of nanoseconds to run before pausing again (optional).
        """
        await resume(self._transport, pause_after)

    async def wait_until_simulation_time(self, seconds: float) -> None:
        """
        Pause and resume the simulation until the given simulation time (in seconds) is reached.

        Args:
            seconds: The simulation time to wait for, in seconds.
        """
        await pause(self._transport)
        remaining_nanos = seconds * 1e9 - self.last_pause_nanos
        if remaining_nanos > 0:
            if self._pause_queue is None:
                self._pause_queue = EventQueue(self._transport, "sim:pause")
            self._pause_queue.flush()
            await resume(self._transport, int(remaining_nanos))
            await self._pause_queue.get()

    async def restart_simulation(self, pause: bool = False) -> None:
        """
        Restart the simulation, optionally starting paused.

        Args:
            pause: Whether to start the simulation paused (default: False).
        """
        await restart(self._transport, pause)

    def serial_monitor(self, callback: Callable[[bytes], Any]) -> asyncio.Task[None]:
        """
        Start monitoring the serial output in the background and invoke `callback` for each line.

        This method **does not block**: it creates and returns an asyncio.Task that runs until the
        transport is closed or the task is cancelled. The callback may be synchronous or async.

        Example:
            task = client.serial_monitor(lambda line: print(line.decode(), end=""))
            ... do other async work ...
            task.cancel()
        """

        async def _runner() -> None:
            try:
                async for line in monitor_lines(self._transport):
                    try:
                        result = callback(line)
                        if inspect.isawaitable(result):
                            await result
                    except Exception:
                        # Swallow callback exceptions to keep the monitor alive.
                        # Users can add their own error handling inside the callback.
                        pass
            finally:
                # Clean up task from the set when it completes
                self._serial_monitor_tasks.discard(task)

        task = asyncio.create_task(_runner(), name="wokwi-serial-monitor")
        self._serial_monitor_tasks.add(task)
        return task

    def stop_serial_monitors(self) -> None:
        """
        Stop all active serial monitor tasks.

        This method cancels all tasks created by the serial_monitor method.
        After calling this method, all active serial monitors will stop receiving data.
        """
        for task in self._serial_monitor_tasks.copy():
            task.cancel()
        self._serial_monitor_tasks.clear()

    async def serial_monitor_cat(self, decode_utf8: bool = True, errors: str = "replace") -> None:
        """
        Print serial monitor output to stdout as it is received from the simulation.

        Args:
            decode_utf8: Whether to decode bytes as UTF-8. If False, prints raw bytes (default: True).
            errors: How to handle UTF-8 decoding errors. Options: 'strict', 'ignore', 'replace' (default: 'replace').
        """
        async for line in monitor_lines(self._transport):
            if decode_utf8:
                try:
                    output = line.decode("utf-8", errors=errors)
                    print(output, end="", flush=True)
                except UnicodeDecodeError:
                    # Fallback to raw bytes if decoding fails completely
                    print(line, end="", flush=True)
            else:
                print(line, end="", flush=True)

    async def serial_write(self, data: Union[bytes, str, list[int]]) -> None:
        """Write data to the simulation serial monitor interface."""
        await write_serial(self._transport, data)

    def _on_pause(self, event: EventMessage) -> None:
        self.last_pause_nanos = int(event["nanos"])

    async def read_pin(self, part: str, pin: str) -> PinReadMessage:
        """Read the current state of a pin.

        Args:
            part: The part id (e.g. "uno").
            pin: The pin name (e.g. "A2").
        """
        pin_data = await pin_read(self._transport, part=part, pin=pin)
        return cast(PinReadMessage, pin_data["result"])

    async def listen_pin(self, part: str, pin: str, listen: bool = True) -> None:
        """Start or stop listening for changes on a pin.

        When enabled, "pin:change" events will be delivered via the transport's
        event mechanism.

        Args:
            part: The part id.
            pin: The pin name.
            listen: True to start listening, False to stop.
        """
        await pin_listen(self._transport, part=part, pin=pin, listen=listen)

    async def gpio_list(self) -> list[str]:
        """Get a list of all GPIO pins available in the simulation.

        Returns:
            list[str]: Example: ["esp32:GPIO0", "esp32:GPIO1", ...]
        """
        resp = await gpio_list(self._transport)
        pins_val: Any = resp.get("result", {}).get("pins")
        if not isinstance(pins_val, list) or not all(isinstance(p, str) for p in pins_val):
            raise ProtocolError("Malformed gpio:list response: expected result.pins: list[str]")
        return cast(list[str], pins_val)

    async def set_control(self, part: str, control: str, value: Union[int, bool, float]) -> None:
        """Set a control value (e.g. simulate button press).

        Args:
            part: Part id (e.g. "btn1").
            control: Control name (e.g. "pressed").
            value: Control value to set (float).
        """
        await set_control(self._transport, part=part, control=control, value=value)

    async def read_framebuffer_png_bytes(self, id: str) -> bytes:
        """Return the current framebuffer as PNG bytes."""
        return await read_framebuffer_png_bytes(self._transport, id=id)

    async def save_framebuffer_png(self, id: str, path: Path, overwrite: bool = True) -> Path:
        """Save the current framebuffer as a PNG file."""
        return await save_framebuffer_png(self._transport, id=id, path=path, overwrite=overwrite)
