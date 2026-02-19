import json
import logging
import os
from typing import Optional, TypedDict

logger = logging.getLogger(__name__)


class FirmwarePart(TypedDict):
    offset: int
    data: bytes


class IdfFirmwareResult(TypedDict):
    parts: list[FirmwarePart]
    flash_size: Optional[int]


def resolveIdfFirmware(flasher_args_path: str) -> IdfFirmwareResult:
    """
    Resolve ESP32 firmware from flasher_args.json file.
    Returns individual flash sections with their offsets, plus flash_size if available.

    Args:
        flasher_args_path: Path to the flasher_args.json file

    Returns:
        IdfFirmwareResult with individual parts and optional flash_size

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
    flasher_dir = os.path.dirname(flasher_args_path)

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

    flash_size = None
    flash_settings = flasher_args.get("flash_settings")
    if flash_settings and "flash_size" in flash_settings:
        raw = flash_settings["flash_size"]
        if isinstance(raw, str) and raw.endswith("MB"):
            flash_size = int(raw[:-2])
        else:
            logger.warning("Unexpected flash_size format in flasher_args.json: %r", raw)

    return {"parts": firmware_parts, "flash_size": flash_size}
