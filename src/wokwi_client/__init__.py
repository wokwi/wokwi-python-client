"""
Wokwi Python Client Library

Typed, asyncio-friendly Python SDK for the Wokwi Simulation API.

Provides the WokwiClient class for connecting to, controlling, and monitoring Wokwi simulations from Python.
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from .__version__ import get_version
from .client import WokwiClient
from .constants import GET_TOKEN_URL

__version__ = get_version()
__all__ = ["WokwiClient", "__version__", "GET_TOKEN_URL"]
