"""VCD (Value Change Dump) export helpers.

Provides utilities to read logic analyzer data from the simulation
via the `sim:read-vcd` command.

Exposed helpers:
* read_vcd       -> raw response with VCD data and metadata
* save_vcd       -> save VCD data to disk
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from .exceptions import WokwiError
from .protocol_types import ResponseMessage
from .transport import Transport

__all__ = [
    "VCDData",
    "read_vcd",
    "save_vcd",
]


class VCDData(TypedDict):
    """VCD data returned from the logic analyzer.

    Attributes:
        vcd: The VCD file content as a string.
        channel_count: Number of channels captured.
        sample_count: Number of samples captured.
    """

    vcd: str
    channel_count: int
    sample_count: int


async def read_vcd(transport: Transport) -> VCDData:
    """Read logic analyzer data as VCD (Value Change Dump).

    Returns the captured signals from the logic analyzer in VCD format,
    which can be viewed in tools like PulseView or GTKWave.

    Returns:
        VCD data containing the vcd string, channel count, and sample count.

    Raises:
        WokwiError: If no logic analyzer is present in the diagram or
            the response is malformed.
    """
    resp: ResponseMessage = await transport.request("sim:read-vcd", {})
    return _extract_vcd_data(resp)


def _extract_vcd_data(resp: ResponseMessage) -> VCDData:
    result = resp.get("result", {})
    vcd = result.get("vcd")
    channel_count = result.get("channelCount")
    sample_count = result.get("sampleCount")

    if not isinstance(vcd, str):
        raise WokwiError("Malformed sim:read-vcd response: missing 'vcd' string")
    if not isinstance(channel_count, int):
        raise WokwiError("Malformed sim:read-vcd response: missing 'channelCount' int")
    if not isinstance(sample_count, int):
        raise WokwiError("Malformed sim:read-vcd response: missing 'sampleCount' int")

    return VCDData(vcd=vcd, channel_count=channel_count, sample_count=sample_count)


async def save_vcd(transport: Transport, *, path: Path, overwrite: bool = True) -> VCDData:
    """Save logic analyzer VCD data to a file.

    Args:
        transport: Active transport.
        path: Destination file path.
        overwrite: Overwrite existing file (default True). If False and file
            exists, raises WokwiError.

    Returns:
        VCD data containing the vcd string, channel count, and sample count.

    Raises:
        WokwiError: If file exists and overwrite=False, or if no logic
            analyzer is present in the diagram.
    """
    if path.exists() and not overwrite:
        raise WokwiError(f"File already exists and overwrite=False: {path}")
    data = await read_vcd(transport)
    if data["sample_count"] > 0:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(data["vcd"])
    return data
