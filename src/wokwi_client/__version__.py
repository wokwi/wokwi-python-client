# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("wokwi-client")
except PackageNotFoundError:  # source tree that was never installed
    __version__ = "0.0.0+local"


def get_version() -> str:
    return __version__
