# Wokwi Python Client Library

Typed Python SDK for the **Wokwi Simulation API** with both async and synchronous interfaces.

## Features

- Connect to the Wokwi Simulator from Python
- Upload diagrams and firmware files
- Start, pause, resume, and restart simulations
- Monitor serial output asynchronously and write to them
- Control peripherals and read GPIO pins
- Fully type-annotated
- Two client interfaces: `WokwiClient` (async) and `WokwiClientSync` (sync)

## Installation

Requires Python ≥ 3.9

```bash
pip install wokwi-client
```

## Getting an API Token

Get your API token from [https://wokwi.com/dashboard/ci](https://wokwi.com/dashboard/ci).

## Quickstart Examples

### Async Client (WokwiClient)

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

For a complete example, see [examples/hello_esp32/main.py](https://github.com/wokwi/wokwi-python-client/blob/main/examples/hello_esp32/main.py).

### Sync Client (WokwiClientSync)

```python
import os
from wokwi_client import WokwiClientSync, GET_TOKEN_URL


def main():
    token = os.getenv("WOKWI_CLI_TOKEN")
    if not token:
        raise SystemExit(
            f"Set WOKWI_CLI_TOKEN in your environment. You can get it from {GET_TOKEN_URL}."
        )

    client = WokwiClientSync(token)
    client.connect()
    client.upload_file("diagram.json")
    client.upload_file("firmware.bin")
    client.start_simulation(firmware="firmware.bin")
    client.serial_monitor_cat()  # Stream serial output
    client.wait_until_simulation_time(10)  # Run simulation for 10 seconds
    client.disconnect()


if __name__ == "__main__":
    main()
```

For a complete example, see [examples/hello_esp32_sync/main.py](https://github.com/wokwi/wokwi-python-client/blob/main/examples/hello_esp32_sync/main.py).

### MicroPython Example

See [examples/micropython_esp32/main.py](https://github.com/wokwi/wokwi-python-client/blob/main/examples/micropython_esp32/main.py) for an example of running MicroPython on a simulated ESP32 board.

## API Reference

See the [API Reference](reference/wokwi_client.md) for full details.
