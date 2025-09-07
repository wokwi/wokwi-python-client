# Changelog

## 0.2.0 - 2025-09-07

- feat: add support for flasher_args.json upload (#13)

## 0.1.2 - 2025-09-03

- fix(client_sync): improve event loop initialization and background task management (#12)

## 0.1.1 - 2025-08-27

- fix: change PinReadMessage and PinListenEvent value type to bool (#11)
- fix(transport): handle errors in _background_recv (#10)

## 0.1.0 - 2025-08-22

- feat: add WokwiClientSync - a synchronous Wokwi client (#9)

## 0.0.9 - 2025-08-21

- feat: add gpio_list method to retrieve all GPIO pins in WokwiClient (#6)
- ci: disable fail-fast, only run tests if there's a CLI TOKEN available
- test: replace subprocess calls with run_example_module helper (#7)
- refactor: change upload methods to return None and update pin command helpers (#8)

## 0.0.8 - 2025-08-20

- feat: add `download()` and `download_file()` methods (#5)

## 0.0.7 - 2025-08-20

- feat: add `read_framebuffer_png_bytes()` and `save_framebuffer_png()` methods (#4)

## 0.0.6 - 2025-08-17

- feat: add `set_control()`, `read_pin()`, `listen_pin()`, `serial_write()` methods (#1)

## 0.0.5 - 2025-08-15

- feat: enhance serial monitor functionality with UTF-8 decoding options (#3)

## 0.0.4 - 2025-07-06

- feat: make `elf` parameter optional in `start_simulation()`

## 0.0.3 - 2025-07-01

- feat: add MicroPython + ESP32 example
- docs: explain about Wokwi and the library

## 0.0.2 - 2025-06-30

- chore: updated list of classifiers in `pyproject.toml`
- docs: fixed a broken badge in `README.md`

## 0.0.1 - 2025-06-29

Initial alpha release.
