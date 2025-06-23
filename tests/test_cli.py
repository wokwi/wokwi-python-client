# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT

import re

from click.testing import CliRunner

from wokwi_client.__version__ import get_version
from wokwi_client.cli import wokwi_client


def test_version_option() -> None:
    """`wokwi --version` prints the same __version__ string and exits with 0."""
    runner = CliRunner()
    result = runner.invoke(wokwi_client, ["--version"])

    assert result.exit_code == 0, result.output
    pattern = rf"wokwi.*{re.escape(get_version())}"
    assert re.search(pattern, result.output), result.output
