"""
Wokwi Python Client Library

Typed Python SDK for the Wokwi Simulation API with both async and synchronous interfaces.

Provides both WokwiClient (async) and WokwiClientSync (sync) classes for connecting to,
controlling, and monitoring Wokwi simulations from Python.
"""

# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from .__version__ import get_version
from .client import WokwiClient
from .client_sync import WokwiClientSync
from .constants import GET_TOKEN_URL

__version__ = get_version()
__all__ = ["WokwiClient", "WokwiClientSync", "__version__", "GET_TOKEN_URL"]
