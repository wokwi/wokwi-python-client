# SPDX-FileCopyrightText: 2025-present CodeMagic LTD
#
# SPDX-License-Identifier: MIT
import click

from wokwi_client.__version__ import get_version


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=get_version(), prog_name="wokwi-client")
def wokwi_client() -> None:
    click.echo("Hello Virtual World!")
