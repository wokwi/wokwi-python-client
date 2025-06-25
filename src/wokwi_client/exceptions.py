# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT


class WokwiError(Exception): ...


class ProtocolError(WokwiError): ...


class ServerError(WokwiError): ...
