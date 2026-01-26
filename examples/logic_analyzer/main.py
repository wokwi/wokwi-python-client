# SPDX-License-Identifier: MIT
# Copyright (C) 2026, CodeMagic LTD

"""
Example: Export logic analyzer data as VCD file.

This example demonstrates how to:
1. Connect to the Wokwi simulator
2. Run a simulation with a clock generator and logic analyzer
3. Export the captured signals as a VCD file

The VCD file can be viewed in tools like PulseView or GTKWave.
"""

import asyncio
import os
from pathlib import Path

from wokwi_client import GET_TOKEN_URL, WokwiClient

EXAMPLE_DIR = Path(__file__).parent
SLEEP_TIME = float(os.getenv("WOKWI_SLEEP_TIME", "1"))


async def main() -> None:
    token = os.getenv("WOKWI_CLI_TOKEN")
    if not token:
        raise SystemExit(
            f"Set WOKWI_CLI_TOKEN in your environment. You can get it from {GET_TOKEN_URL}."
        )

    server = os.getenv("WOKWI_CLI_SERVER")
    client = WokwiClient(token, server=server)
    print(f"Wokwi client library version: {client.version}")

    hello = await client.connect()
    print("Connected to Wokwi Simulator, server version:", hello["version"])

    # Upload the diagram and dummy firmware
    await client.upload_file("diagram.json", EXAMPLE_DIR / "diagram.json")
    await client.upload_file("dummy.hex", EXAMPLE_DIR / "dummy.hex")

    # Start the simulation
    await client.start_simulation(firmware="dummy.hex", pause=True)

    # Run the simulation for a short time to capture some clock cycles
    print(f"Running simulation for {SLEEP_TIME} seconds...")
    await client.wait_until_simulation_time(SLEEP_TIME)

    # Read the VCD data
    vcd_data = await client.read_vcd()
    print(f"Captured {vcd_data['sample_count']} samples on {vcd_data['channel_count']} channel(s)")

    # Save to file
    vcd_path = EXAMPLE_DIR / "output.vcd"
    await client.save_vcd(vcd_path)
    print(f"VCD data saved to: {vcd_path}")

    # Also print first few lines of the VCD for verification
    vcd_lines = vcd_data["vcd"].split("\n")[:15]
    print("\nVCD file preview:")
    for line in vcd_lines:
        print(f"  {line}")

    await client.disconnect()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
