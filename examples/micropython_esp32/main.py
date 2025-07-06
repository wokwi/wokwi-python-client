# SPDX-License-Identifier: MIT
# Copyright (C) 2025, CodeMagic LTD

import asyncio
import os
from pathlib import Path

import requests
from littlefs import LittleFS

from wokwi_client import GET_TOKEN_URL, WokwiClient

EXAMPLE_DIR = Path(__file__).parent
FIRMWARE_NAME = "ESP32_GENERIC-20250415-v1.25.0.bin"
FIRMWARE_FILE = EXAMPLE_DIR / FIRMWARE_NAME
FIRMWARE_URL = f"https://micropython.org/resources/firmware/{FIRMWARE_NAME}"
FIRMWARE_OFFSET = 0x1000
FLASH_SIZE = 0x400000
FS_OFFSET = 0x200000
FS_SIZE = 0x200000
SLEEP_TIME = int(os.getenv("WOKWI_SLEEP_TIME", "3"))

MICROPYTHON_CODE = """
# This is a MicroPython script that runs on the simulated ESP32 chip.
# It prints some information about the ESP32 chip and the filesystem.

import esp
import esp32
import gc
import machine
import os

print("--------------------------------")
print("Hello, MicroPython! I'm running on a Wokwi ESP32 simulator.")
print("--------------------------------")

# Chip information
print(f"CPU Frequency: {machine.freq()}")
mac_address = ':'.join(['{:02x}'.format(x) for x in machine.unique_id()])
print(f"MAC Address: {mac_address}")

# Memory information
print(f"Flash Size: {esp.flash_size() // 1024} kB")
print(f"Total Heap: {gc.mem_alloc() + gc.mem_free()} bytes")
print(f"Free Heap: {gc.mem_free()} bytes")

# Filesystem information
statvfs = os.statvfs("/")
block_size, free_blocks = statvfs[0], statvfs[3]
print("Filesystem:")
print(f"  Root path : /")
print(f"  Block size: {block_size} bytes")
print(f"  Free space: {block_size * free_blocks} bytes")
print("--------------------------------")
"""


async def main() -> None:
    token = os.getenv("WOKWI_CLI_TOKEN")
    if not token:
        raise SystemExit(
            f"Set WOKWI_CLI_TOKEN in your environment. You can get it from {GET_TOKEN_URL}."
        )

    if not FIRMWARE_FILE.exists():
        print(f"Downloading {FIRMWARE_NAME} from {FIRMWARE_URL}")
        response = requests.get(FIRMWARE_URL)
        response.raise_for_status()
        with open(FIRMWARE_FILE, "wb") as f:
            f.write(response.content)

    firmware_data = bytearray(FLASH_SIZE)
    with open(FIRMWARE_FILE, "rb") as f:
        firmware_data[FIRMWARE_OFFSET : FIRMWARE_OFFSET + f.tell()] = f.read()

    # Inject some micropython code into a littlefs filesystem inside the firmware image
    lfs = LittleFS(block_size=4096, block_count=512, prog_size=256)
    with lfs.open("main.py", "w") as lfs_file:
        lfs_file.write(MICROPYTHON_CODE)
    firmware_data[FS_OFFSET : FS_OFFSET + FS_SIZE] = lfs.context.buffer

    with open(EXAMPLE_DIR / "firmware.bin", "wb") as f:
        f.write(bytes(firmware_data))

    client = WokwiClient(token)
    print(f"Wokwi client library version: {client.version}")

    hello = await client.connect()
    print("Connected to Wokwi Simulator, server version:", hello["version"])

    # Upload the diagram and firmware files
    await client.upload_file("diagram.json", EXAMPLE_DIR / "diagram.json")
    await client.upload(FIRMWARE_NAME, bytes(firmware_data))

    # Start the simulation
    await client.start_simulation(firmware=FIRMWARE_NAME)

    # Stream serial output for a few seconds
    serial_task = asyncio.create_task(client.serial_monitor_cat())
    print(f"Simulation started, waiting for {SLEEP_TIME} seconds…")
    await client.wait_until_simulation_time(SLEEP_TIME)
    serial_task.cancel()

    # Disconnect from the simulator
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
