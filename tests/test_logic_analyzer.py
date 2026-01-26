# SPDX-FileCopyrightText: 2026 CodeMagic LTD
#
# SPDX-License-Identifier: MIT

from pathlib import Path

from .utils import run_example_module


def test_logic_analyzer_vcd_export() -> None:
    """Logic analyzer example should run and export a valid VCD file."""
    # Clean up any existing output file
    output_path = Path(__file__).parent.parent / "examples" / "logic_analyzer" / "output.vcd"
    if output_path.exists():
        output_path.unlink()

    result = run_example_module("examples.logic_analyzer.main", sleep_time="0.1")

    assert result.returncode == 0, f"Example failed with stderr: {result.stderr}"
    assert "Captured" in result.stdout
    assert "samples on" in result.stdout
    assert "VCD data saved to" in result.stdout

    # Verify the VCD file was created and has valid content
    assert output_path.exists(), "VCD file was not created"
    vcd_content = output_path.read_text()
    assert "$version" in vcd_content
    assert "$timescale" in vcd_content
    assert "CLK" in vcd_content
