# Wokwi Python Client 🚀

Typed, asyncio-friendly Python SDK for the **Wokwi Simulation API**

[![PyPI version](https://img.shields.io/pypi/v/wokwi-client?logo=pypi)](https://pypi.org/project/wokwi-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/wokwi-client)](https://pypi.org/project/wokwi-client/)
[![CI](https://github.com/wokwi/wokwi-python-client/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/wokwi/wokwi-python-client/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/github/license/wokwi/wokwi-python-client)](LICENSE)

> **TL;DR:** Run and control your Wokwi simulations from Python with first-class type hints and zero boilerplate.

---

## Installation requirements

Python ≥ 3.9

An API token from [https://wokwi.com/dashboard/ci](https://wokwi.com/dashboard/ci).

## Running the examples

The basic example is in the [examples/hello_esp32/main.py](examples/hello_esp32/main.py) file. It shows how to:

- Connect to the Wokwi Simulator
- Upload a diagram and firmware files
- Start a simulation
- Monitor the serial output

You can run the example with:

```bash
pip install -e .[dev]
python -m examples.hello_esp32.main
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
