# Changelog

## 0.5.1 - 2026-10-03

- fix: `wokwi_client.__version__` reported `0.0.0+local` in every release; it now reports the installed version

## 0.5.0 - 2026-10-02

- **Breaking:** drop Python 3.9 support (end of life 2025-10-31; current hatch/mypy no longer run on it). `requires-python` is now `>=3.10`. Python 3.14 added to CI and classifiers.
- feat: add `sdcards` parameter to `start_simulation()` (`SDCardConfig`) to preload the simulated micro SD card from uploaded files or a raw image
- feat: add `export_sdcard_image()` and `export_sdcard_files()` to read the micro SD card contents back
- feat: add `upload_sdcard_folder()` to upload a local directory tree as the card contents in one call
- feat: add `upload_text()`; `upload_file()` now uploads `.json` files as text, which the server requires for custom chip definitions (`<chip>.chip.json`) (#17, thanks @lucasssvaz)
- fix: `download()` now returns files that were uploaded as text
- fix: raise the WebSocket message size limit (was the `websockets` default of 1 MB), so large responses such as an SD card image no longer close the connection with code 1009

## 0.4.1 - 2026-10-02

- fix: `WokwiClient` and `WokwiClientSync` now honor the `WOKWI_CLI_SERVER` environment variable when no `server` argument is given (#18, thanks @lucasssvaz). Previously the public server was always used, so self-hosted CI servers (e.g. `wokwi/wokwi-ci-server-action`) were silently bypassed.
- fix: `WOKWI_CLI_SERVER` is now read when a `Transport`/client is created rather than when the module is imported, so setting it after `import wokwi_client` works as expected. The `Transport(url=...)` parameter is now optional. The undocumented `wokwi_client.transport.TRANSPORT_DEFAULT_WS_URL` constant was removed.
- test: add token-free unit tests for server URL resolution (explicit argument > `WOKWI_CLI_SERVER` > public server)

## 0.4.0 - 2026-02-19

- feat: add `upload_idf_firmware()` method for uploading ESP-IDF flash sections individually
- feat: add `flash_size` parameter to `start_simulation()`
- feat: add `touch_event()` method for touchscreen simulation

## 0.3.0 - 2026-01-26

- feat: add `read_vcd()` and `save_vcd()` methods to export logic analyzer data as VCD

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
