# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import base64
from pathlib import Path
from typing import Optional

from .models import UploadParams
from .protocol_types import ResponseMessage
from .transport import Transport


async def upload_file(
    transport: Transport, filename: str, local_path: Optional[Path] = None
) -> ResponseMessage:
    path = Path(local_path or filename)
    content = path.read_bytes()
    return await upload(transport, filename, content)


async def upload(transport: Transport, name: str, content: bytes) -> ResponseMessage:
    params = UploadParams(name=name, binary=base64.b64encode(content).decode())
    return await transport.request("file:upload", params.model_dump())


async def download(transport: Transport, name: str) -> ResponseMessage:
    return await transport.request("file:download", {"name": name})


async def download_file(transport: Transport, name: str, local_path: Optional[Path] = None) -> None:
    if local_path is None:
        local_path = Path(name)

    result = await download(transport, name)
    with open(local_path, "wb") as f:
        f.write(base64.b64decode(result["result"]["binary"]))
