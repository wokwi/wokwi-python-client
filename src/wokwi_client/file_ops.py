# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import base64
from pathlib import Path
from typing import Optional

from wokwi_client.idf import resolveIdfFirmware

from .models import TextUploadParams, UploadParams
from .protocol_types import ResponseMessage
from .transport import Transport


class FlashSection:
    """A flash section with its offset and remote file name."""

    def __init__(self, offset: int, file: str):
        self.offset = offset
        self.file = file


class IdfFirmwareUploadResult:
    """Result of uploading ESP-IDF firmware sections."""

    def __init__(self, firmware: list[FlashSection], flash_size: Optional[int] = None):
        self.firmware = firmware
        self.flash_size = flash_size


async def upload_file(
    transport: Transport, filename: str, local_path: Optional[Path] = None
) -> str:
    path = Path(local_path or filename)
    # The server needs JSON (diagram, custom chips) as text, same as the Wokwi CLI
    if Path(filename).suffix == ".json":
        await upload_text(transport, filename, path.read_text(encoding="utf-8-sig"))
    else:
        await upload(transport, filename, path.read_bytes())
    return filename


async def upload_idf_firmware(
    transport: Transport, flasher_args_path: "str | Path"
) -> IdfFirmwareUploadResult:
    result = resolveIdfFirmware(str(flasher_args_path))
    sections: list[FlashSection] = []
    for part in result["parts"]:
        remote_name = f"flash-{part['offset']:x}.bin"
        await upload(transport, remote_name, part["data"])
        sections.append(FlashSection(offset=part["offset"], file=remote_name))
    return IdfFirmwareUploadResult(firmware=sections, flash_size=result["flash_size"])


async def upload(transport: Transport, name: str, content: bytes) -> ResponseMessage:
    params = UploadParams(name=name, binary=base64.b64encode(content).decode())
    return await transport.request("file:upload", params.model_dump())


async def upload_text(transport: Transport, name: str, text: str) -> ResponseMessage:
    params = TextUploadParams(name=name, text=text)
    return await transport.request("file:upload", params.model_dump())


async def download(transport: Transport, name: str) -> ResponseMessage:
    return await transport.request("file:download", {"name": name})
