# MicroPython on ESP32

This example shows how to run MicroPython on an ESP32 board. It creates a firmware image with a littlefs filesystem and injects a MicroPython script into it. The firmware image is uploaded to the Wokwi ESP32 simulator and the MicroPython script is executed. The script prints some information about the ESP32 chip and the filesystem.

## Running the example

Run the following command in the root directory of the project:

```bash
pip install -e .[dev]
python -m examples.micropython_esp32.main
```

## Program output

The program output is printed to the console. The output is similar to the following:

```
Wokwi client library version: 0.0.2
Connected to Wokwi Simulator, server version: 1.0.0-20250701-g79c3ac34
Simulation started, waiting for 3 seconds…
--------------------------------
Hello, MicroPython! I'm running on a Wokwi ESP32 simulator.
--------------------------------
CPU Frequency: 160000000
MAC Address: 24:0a:c4:00:01:10
Flash Size: 4096 kB
Total Heap: 166592 bytes
Free Heap: 163040 bytes
Filesystem:
  Root path : /
  Block size: 4096 bytes
  Free space: 2084864 bytes
--------------------------------
MicroPython v1.25.0 on 2025-04-15; Generic ESP32 module with ESP32
Type "help()" for more information.
>>>
```
