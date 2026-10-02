# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

DEFAULT_WS_URL = "wss://wokwi.com/api/ws/beta"
GET_TOKEN_URL = "https://wokwi.com/dashboard/ci"

MSG_TYPE_ERROR = "error"
MSG_TYPE_RESPONSE = "response"
MSG_TYPE_EVENT = "event"
MSG_TYPE_COMMAND = "command"
MSG_TYPE_HELLO = "hello"
PROTOCOL_VERSION = 1

# Largest WebSocket message accepted from the server (an SD card image export can be ~86 MB)
MAX_MESSAGE_SIZE = 512 * 1024 * 1024
