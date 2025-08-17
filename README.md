# Wokwi Python Client 🚀

Typed, asyncio-friendly Python SDK for the **Wokwi Simulation API**

[![PyPI version](https://img.shields.io/pypi/v/wokwi-client?logo=pypi)](https://pypi.org/project/wokwi-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/wokwi-client)](https://pypi.org/project/wokwi-client/)
[![CI](https://github.com/wokwi/wokwi-python-client/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/wokwi/wokwi-python-client/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/github/license/wokwi/wokwi-python-client)](LICENSE)

> **TL;DR:** Run and control your Wokwi simulations from Python with first-class type hints and zero boilerplate.

---

Wokwi is a platform for creating and running simulations of electronic circuits and embedded systems. It supports a wide range of hardware platforms, including ESP32 family, Arduino, Raspberry Pi, STM32 and more.In addition, it supports a [wide range of peripherals](https://docs.wokwi.com/getting-started/supported-hardware), including sensors, displays, motors, and debugging tools.

Wokwi Python Client is a Python SDK for the Wokwi Simulation API. It allows you to run and control your Wokwi simulations from Python in a typed, asyncio-friendly way. You can use it to automate your embedded testing and development workflows.

## Installation requirements

- Python ≥ 3.9
- An API token from [https://wokwi.com/dashboard/ci](https://wokwi.com/dashboard/ci).

Install the library with:
```bash
pip install wokwi-client
```

## Running the examples

The basic example is in the [examples/hello_esp32/main.py](examples/hello_esp32/main.py) file. It shows how to:

- Connect to the Wokwi Simulator
- Upload a diagram and firmware files
- Start a simulation
- Monitor serial output asynchronously

You can run the example with:

```bash
pip install -e .[dev]
python -m examples.hello_esp32.main
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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
