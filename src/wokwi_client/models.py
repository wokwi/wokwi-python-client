# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from typing import Any, Optional

from pydantic import BaseModel, Field


class UploadParams(BaseModel):
    name: str
    binary: str  # base64


class SimulationParams(BaseModel):
    firmware: str
    elf: str
    pause: bool = False
    chips: list[str] = Field(default_factory=list)


class SDCardConfig(BaseModel):
    """
    Contents of a micro SD card in the diagram, for `start_simulation(sdcards=[...])`.

    Upload the files first (e.g. `upload("sdcard/hello.txt", data)`), then describe the
    card with either `prefix` (files whose names start with it are copied to the card,
    prefix stripped) or `image` (the name of an uploaded raw disk image).
    """

    part: Optional[str] = None
    """Diagram part id of the card; optional when the diagram has a single card."""
    prefix: Optional[str] = None
    """Uploaded files starting with this prefix are copied onto a freshly formatted card."""
    image: Optional[str] = None
    """Name of an uploaded raw disk image to serve as the card (byte for byte)."""
    size_bytes: Optional[int] = None
    """Card capacity in bytes (default 8 MB; the Wokwi CI server allows up to 64 MB)."""

    def to_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if self.part is not None:
            params["part"] = self.part
        if self.prefix is not None:
            params["prefix"] = self.prefix
        if self.image is not None:
            params["image"] = self.image
        if self.size_bytes is not None:
            params["sizeBytes"] = self.size_bytes
        return params


class SDCardFile(BaseModel):
    """A file read back from a simulated micro SD card."""

    name: str
    """Path on the card, `/`-separated, relative to the card root."""
    content: bytes
