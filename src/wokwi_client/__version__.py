# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from importlib.metadata import PackageNotFoundError, version

try:  # works for normal + editable installs
    __version__: str = version(__name__.replace("_", "-"))
except PackageNotFoundError:  # running from a raw source tree
    try:
        # if you use hatch-vcs, this tiny module is auto-generated at build time
        from ._version import version as __version__  # type: ignore
    except ModuleNotFoundError:
        __version__ = "0.0.0+local"


def get_version() -> str:
    return __version__
