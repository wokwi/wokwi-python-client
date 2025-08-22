# Wokwi Python Client 🚀

Typed Python SDK for the **Wokwi Simulation API** with both async and synchronous interfaces

[![PyPI version](https://img.shields.io/pypi/v/wokwi-client?logo=pypi)](https://pypi.org/project/wokwi-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/wokwi-client)](https://pypi.org/project/wokwi-client/)
[![CI](https://github.com/wokwi/wokwi-python-client/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/wokwi/wokwi-python-client/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/github/license/wokwi/wokwi-python-client)](LICENSE)

> **TL;DR:** Run and control your Wokwi simulations from Python with first-class type hints, zero boilerplate, and both async and synchronous APIs.

---

Wokwi is a platform for creating and running simulations of electronic circuits and embedded systems. It supports a wide range of hardware platforms, including ESP32 family, Arduino, Raspberry Pi, STM32 and more.In addition, it supports a [wide range of peripherals](https://docs.wokwi.com/getting-started/supported-hardware), including sensors, displays, motors, and debugging tools.

Wokwi Python Client is a Python SDK for the Wokwi Simulation API. It provides two client interfaces:

- **`WokwiClient`**: Async client with full asyncio support for modern Python applications
- **`WokwiClientSync`**: Synchronous client that mirrors the async API for traditional blocking code

Both clients allow you to run and control your Wokwi simulations from Python in a typed, easy-to-use way. You can use them to automate your embedded testing and development workflows.

## Installation requirements

- Python ≥ 3.9
- An API token from [https://wokwi.com/dashboard/ci](https://wokwi.com/dashboard/ci).

Install the library with:
```bash
pip install wokwi-client
```

## Running the examples

### Async Example

The basic async example is in the [examples/hello_esp32/main.py](examples/hello_esp32/main.py) file. It shows how to:

- Connect to the Wokwi Simulator
- Upload a diagram and firmware files
- Start a simulation
- Monitor serial output asynchronously

You can run the async example with:

```bash
pip install -e .[dev]
python -m examples.hello_esp32.main
```

### Sync Example

The synchronous example is in the [examples/hello_esp32_sync/main.py](examples/hello_esp32_sync/main.py) file. It demonstrates the same functionality using the blocking `WokwiClientSync`:

```bash
pip install -e .[dev]
python -m examples.hello_esp32_sync.main
```

For more examples, see the [examples](examples) directory.

## Documentation

The API documentation is available at [https://wokwi.github.io/wokwi-python-client/](https://wokwi.github.io/wokwi-python-client/).

## Development

To run the tests, set the `WOKWI_CLI_TOKEN` environment variable (you can get a token from [https://wokwi.com/dashboard/ci](https://wokwi.com/dashboard/ci)) and run the following command:

```bash
hatch run dev:pytest
```

To run the linter, run the following command:

```bash
hatch run ruff format --check .
hatch run ruff check .
```

To run the type checker, run the following command:

```bash
hatch run mypy .
```

### Creating a new release

To create a new release, run the following commands:

```bash
git tag -m "v0.0.6" v0.0.6
git push --follow-tags
```

Replace `0.0.6` with the new version number.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
