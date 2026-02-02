# SPDX-License-Identifier: MIT
# Copyright (C) 2025, CodeMagic LTD

import asyncio
import os
from pathlib import Path

from examples.helper.github_download import download_github_dir
from wokwi_client import GET_TOKEN_URL, WokwiClient

EXAMPLE_DIR = Path(__file__).parent
USER = "espressif"
REPO = "pytest-embedded"
PATH = "tests/fixtures/hello_world_esp32/build"
REF = "7e66a07870d1cd97a454318892c6f6225def3144"

SLEEP_TIME = int(os.getenv("WOKWI_SLEEP_TIME", "10"))


async def main() -> None:
    token = os.getenv("WOKWI_CLI_TOKEN")
    if not token:
        raise SystemExit(
            f"Set WOKWI_CLI_TOKEN in your environment. You can get it from {GET_TOKEN_URL}."
        )

    # Automatically download build files from GitHub if missing
    build_dir = EXAMPLE_DIR / "build"
    download_github_dir(
        user=USER,
        repo=REPO,
        path=PATH,
        base_path=build_dir,
        ref=REF,
    )

    client = WokwiClient(token)
    print(f"Wokwi client library version: {client.version}")

    hello = await client.connect()
    print("Connected to Wokwi Simulator, server version:", hello["version"])

    # Upload the diagram and firmware files
    await client.upload_file("diagram.json", EXAMPLE_DIR / "diagram.json")
    filename = await client.upload_file(
        "flasher_args.json", EXAMPLE_DIR / "build" / "flasher_args.json"
    )

    # Start the simulation
    await client.start_simulation(
        firmware=filename,
    )

    # Stream serial output for a few seconds
    serial_task = asyncio.create_task(client.serial_monitor_cat())

    # Alternative lambda version
    # serial_task = client.serial_monitor(
    #     lambda line: print(line.decode("utf-8", errors="replace"), end="", flush=True)
    # )

    print(f"Simulation started, waiting for {SLEEP_TIME} seconds…")
    await client.wait_until_simulation_time(SLEEP_TIME)
    serial_task.cancel()

    # Disconnect from the simulator
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
