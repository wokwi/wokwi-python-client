import json
import os
from typing import TypedDict

MAX_FIRMWARE_SIZE = 4 * 1024 * 1024  # 4MB


class FirmwarePart(TypedDict):
    offset: int
    data: bytes


def resolveIdfFirmware(flasher_args_path: str) -> bytes:
    """
    Resolve ESP32 firmware from flasher_args.json file.
    Implemented based on the logic from the wokwi-cli.
    - https://github.com/wokwi/wokwi-cli/blob/1726692465f458420f71bc4dbd100aeedf2e37bb/src/uploadFirmware.ts

    More about flasher_args.json:
    - https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32/api-guides/build-system.html

    Args:
        flasher_args_path: Path to the flasher_args.json file

    Returns:
        Combined firmware binary data as bytes

    Raises:
        ValueError: If flasher_args.json is invalid or files are missing
        FileNotFoundError: If required firmware files are not found
    """
    try:
        with open(flasher_args_path) as f:
            flasher_args = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Failed to read flasher_args.json: {e}")

    if "flash_files" not in flasher_args:
        raise ValueError("flash_files is not defined in flasher_args.json")

    firmware_parts: list[FirmwarePart] = []
    firmware_size = 0
    flasher_dir = os.path.dirname(flasher_args_path)

    # Process each flash file entry
    for offset_str, file_path in flasher_args["flash_files"].items():
        try:
            offset = int(offset_str, 16)
        except ValueError:
            raise ValueError(f"Invalid offset in flasher_args.json flash_files: {offset_str}")

        full_file_path = os.path.join(flasher_dir, file_path)

        try:
            with open(full_file_path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Firmware file not found: {full_file_path}")

        firmware_parts.append({"offset": offset, "data": data})
        firmware_size = max(firmware_size, offset + len(data))

    if firmware_size > MAX_FIRMWARE_SIZE:
        raise ValueError(
            f"Firmware size ({firmware_size} bytes) exceeds the maximum supported size ({MAX_FIRMWARE_SIZE} bytes)"
        )

    # Create combined firmware binary
    firmware_data = bytearray(firmware_size)

    # Fill with 0xFF (typical flash erased state)
    for i in range(firmware_size):
        firmware_data[i] = 0xFF

    # Write each firmware part to the correct offset
    for part in firmware_parts:
        offset = part["offset"]
        data = part["data"]
        firmware_data[offset : offset + len(data)] = data

    return bytes(firmware_data)
