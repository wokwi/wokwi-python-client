# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any, Optional, Union

from .__version__ import get_version
from .constants import DEFAULT_WS_URL
from .control import set_control
from .event_queue import EventQueue
from .file_ops import upload, upload_file
from .pins import pin_listen, pin_read
from .protocol_types import EventMessage, ResponseMessage
from .serial import monitor_lines, write_serial
from .simulation import pause, restart, resume, start
from .transport import Transport


class WokwiClient:
    """
    Asynchronous client for the Wokwi Simulation API.

    This class provides methods to connect to the Wokwi simulator, upload files, control simulations,
    and monitor serial output. It is designed to be asyncio-friendly and easy to use in Python scripts
    and applications.
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
        self._pause_queue = EventQueue(self._transport, "sim:pause")

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
        """
        await self._transport.close()

    async def upload(self, name: str, content: bytes) -> ResponseMessage:
        """
        Upload a file to the simulator from bytes content.

        Args:
            name: The name to use for the uploaded file.
            content: The file content as bytes.

        Returns:
            The response message from the server.
        """
        return await upload(self._transport, name, content)

    async def upload_file(
        self, filename: str, local_path: Optional[Path] = None
    ) -> ResponseMessage:
        """
        Upload a local file to the simulator.

        Args:
            filename: The name to use for the uploaded file.
            local_path: Optional path to the local file. If not provided, uses filename as the path.

        Returns:
            The response message from the server.
        """
        return await upload_file(self._transport, filename, local_path)

    async def start_simulation(
        self,
        firmware: str,
        elf: Optional[str] = None,
        pause: bool = False,
        chips: list[str] = [],
    ) -> ResponseMessage:
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

        Returns:
            The response message from the server.
        """
        return await start(
            self._transport,
            firmware=firmware,
            elf=elf,
            pause=pause,
            chips=chips,
        )

    async def pause_simulation(self) -> ResponseMessage:
        """
        Pause the running simulation.

        Returns:
            The response message from the server.
        """
        return await pause(self._transport)

    async def resume_simulation(self, pause_after: Optional[int] = None) -> ResponseMessage:
        """
        Resume the simulation, optionally pausing after a given number of nanoseconds.

        Args:
            pause_after: Number of nanoseconds to run before pausing again (optional).

        Returns:
            The response message from the server.
        """
        return await resume(self._transport, pause_after)

    async def wait_until_simulation_time(self, seconds: float) -> None:
        """
        Pause and resume the simulation until the given simulation time (in seconds) is reached.

        Args:
            seconds: The simulation time to wait for, in seconds.
        """
        await pause(self._transport)
        remaining_nanos = seconds * 1e9 - self.last_pause_nanos
        if remaining_nanos > 0:
            self._pause_queue.flush()
            await resume(self._transport, int(remaining_nanos))
            await self._pause_queue.get()

    async def restart_simulation(self, pause: bool = False) -> ResponseMessage:
        """
        Restart the simulation, optionally starting paused.

        Args:
            pause: Whether to start the simulation paused (default: False).

        Returns:
            The response message from the server.
        """
        return await restart(self._transport, pause)

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

    async def read_pin(self, part: str, pin: str) -> ResponseMessage:
        """Read the current state of a pin.

        Args:
            part: The part id (e.g. "uno").
            pin: The pin name (e.g. "A2").
        """
        return await pin_read(self._transport, part=part, pin=pin)

    async def listen_pin(self, part: str, pin: str, listen: bool = True) -> ResponseMessage:
        """Start or stop listening for changes on a pin.

        When enabled, "pin:change" events will be delivered via the transport's
        event mechanism.

        Args:
            part: The part id.
            pin: The pin name.
            listen: True to start listening, False to stop.
        """
        return await pin_listen(self._transport, part=part, pin=pin, listen=listen)

    async def set_control(
        self, part: str, control: str, value: Union[int, bool, float]
    ) -> ResponseMessage:
        """Set a control value (e.g. simulate button press).

        Args:
            part: Part id (e.g. "btn1").
            control: Control name (e.g. "pressed").
            value: Control value to set (float).
        """
        return await set_control(self._transport, part=part, control=control, value=value)
