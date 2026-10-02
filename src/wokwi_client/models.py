# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from typing import Optional

from pydantic import BaseModel, Field


class UploadParams(BaseModel):
    name: str
    binary: str  # base64


class TextUploadParams(BaseModel):
    name: str
    text: str


class SimulationParams(BaseModel):
    firmware: str
    elf: str
    pause: bool = False
    chips: list[str] = Field(default_factory=list)


class SDCardConfig(BaseModel):
    """
    A micro SD card in the diagram, for `start_simulation(sdcards=[...])`.

    Give either `prefix` (uploaded files under it are copied to a freshly formatted card) or
    `image` (an uploaded raw disk image). `upload_sdcard_folder()` builds one for you.
    """

    part: Optional[str] = None
    """Diagram part id; optional when the diagram has a single card."""
    prefix: Optional[str] = None
    """Copy uploaded files starting with this prefix onto the card (prefix stripped)."""
    image: Optional[str] = None
    """Name of an uploaded raw disk image to use as the card."""
    size_bytes: Optional[int] = Field(None, serialization_alias="sizeBytes")
    """Card capacity in bytes (default 8 MB, up to 64 MB on the Wokwi CI server)."""


class SDCardFile(BaseModel):
    """A file read back from a simulated micro SD card."""

    name: str
    """Path on the card, `/`-separated, relative to the card root."""
    content: bytes
