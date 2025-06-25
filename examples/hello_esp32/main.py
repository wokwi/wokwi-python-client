# SPDX-License-Identifier: MIT
# Copyright (C) 2025, CodeMagic LTD

import asyncio
import os
from pathlib import Path

import requests

from wokwi_client import GET_TOKEN_URL, WokwiClient

EXAMPLE_DIR = Path(__file__).parent
HELLO_WORLD_URL = "https://github.com/wokwi/esp-idf-hello-world/raw/refs/heads/main/bin"
FIRMWARE_FILES = {
    "hello_world.bin": f"{HELLO_WORLD_URL}/hello_world.bin",
    "hello_world.elf": f"{HELLO_WORLD_URL}/hello_world.elf",
}
SLEEP_TIME = int(os.getenv("WOKWI_SLEEP_TIME", "10"))


async def main() -> None:
    token = os.getenv("WOKWI_CLI_TOKEN")
    if not token:
        raise SystemExit(
            f"Set WOKWI_CLI_TOKEN in your environment. You can get it from {GET_TOKEN_URL}."
        )

    client = WokwiClient(token)
    print(f"Wokwi client library version: {client.version}")

    hello = await client.connect()
    print("Connected to Wokwi Simulator, server version:", hello["version"])

    for filename, url in FIRMWARE_FILES.items():
        if (EXAMPLE_DIR / filename).exists():
            continue
        print(f"Downloading {filename} from {url}")
        response = requests.get(url)
        response.raise_for_status()
        with open(EXAMPLE_DIR / filename, "wb") as f:
            f.write(response.content)

    # Upload the diagram and firmware files
    await client.upload_file("diagram.json", EXAMPLE_DIR / "diagram.json")
    await client.upload_file("hello_world.bin", EXAMPLE_DIR / "hello_world.bin")
    await client.upload_file("hello_world.elf", EXAMPLE_DIR / "hello_world.elf")

    # Start the simulation
    await client.start_simulation(
        firmware="hello_world.bin",
        elf="hello_world.elf",
    )

    # Stream serial output for a few seconds
    serial_task = asyncio.create_task(client.serial_monitor_cat())
    print(f"Simulation started, waiting for {SLEEP_TIME} seconds…")
    await client.wait_until_simulation_time(SLEEP_TIME)
    serial_task.cancel()

    # Disconnect from the simulator
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
