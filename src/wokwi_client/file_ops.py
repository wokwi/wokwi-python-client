# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import base64
from pathlib import Path
from typing import Optional

from wokwi_client.idf import resolveIdfFirmware

from .models import UploadParams
from .protocol_types import ResponseMessage
from .transport import Transport


async def upload_file(
    transport: Transport, filename: str, local_path: Optional[Path] = None
) -> str:
    firmware_path = local_path or filename
    if str(firmware_path).endswith("flasher_args.json"):
        filename = "firmware.bin"
        content = resolveIdfFirmware(str(firmware_path))
    else:
        content = Path(firmware_path).read_bytes()
    await upload(transport, filename, content)
    return filename


async def upload(transport: Transport, name: str, content: bytes) -> ResponseMessage:
    params = UploadParams(name=name, binary=base64.b64encode(content).decode())
    return await transport.request("file:upload", params.model_dump())


async def download(transport: Transport, name: str) -> ResponseMessage:
    return await transport.request("file:download", {"name": name})
