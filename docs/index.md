# Wokwi Python Client Library

Typed, asyncio-friendly Python SDK for the **Wokwi Simulation API**.

## Features

- Connect to the Wokwi Simulator from Python
- Upload diagrams and firmware files
- Start, pause, resume, and restart simulations
- Monitor serial output asynchronously
- Fully type-annotated and easy to use with asyncio

## Installation

Requires Python ≥ 3.9

```bash
pip install wokwi-client
```

## Getting an API Token

Get your API token from [https://wokwi.com/dashboard/ci](https://wokwi.com/dashboard/ci).

## Quickstart Example

```python
import asyncio
import os
from wokwi_client import WokwiClient, GET_TOKEN_URL


async def main():
    token = os.getenv("WOKWI_CLI_TOKEN")
    if not token:
        raise SystemExit(
            f"Set WOKWI_CLI_TOKEN in your environment. You can get it from {GET_TOKEN_URL}."
        )

    client = WokwiClient(token)
    await client.connect()
    await client.upload_file("diagram.json")
    await client.upload_file("firmware.bin")
    await client.start_simulation(firmware="firmware.bin")
    serial_task = asyncio.create_task(
        client.serial_monitor_cat()
    )  # Stream serial output
    await client.wait_until_simulation_time(10)  # Run simulation for 10 seconds
    serial_task.cancel()
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
```

See the [examples/hello_esp32/main.py](https://github.com/wokwi/wokwi-python-client/blob/main/examples/hello_esp32/main.py) for a full example including serial monitoring, and [examples/micropython_esp32/main.py](https://github.com/wokwi/wokwi-python-client/blob/main/examples/micropython_esp32/main.py) for an example of running MicroPython on a simulated ESP32 board.

## API Reference

See the [API Reference](reference/wokwi_client.md) for full details.
