# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_icd_10

"""
Test suite validating complex and edge case scenarios for Local ZIP Extraction and Fixed-Width Parsing.
"""

import zipfile
from pathlib import Path

from coreason_etl_icd_10.extraction import EpistemicIcd10ExtractionTask


def test_parse_icd10_line_exact_boundary() -> None:
    """Validate that a line with exactly 72 characters parses without raising an error."""
    # A line exactly 72 characters long has 1 character of long description.
    test_line = "A" * 7 + " " + "1" + " " + "S" * 60 + " " + "L"
    assert len(test_line) == 72

    parsed = EpistemicIcd10ExtractionTask.parse_icd10_line(test_line)

    assert parsed["raw_code"] == "A" * 7
    assert parsed["hipaa_flag"] == "1"
    assert parsed["short_description"] == "S" * 60
    assert parsed["long_description"] == "L"


def test_parse_icd10_line_massive_long_description() -> None:
    """Validate parsing a line with an exceptionally long description."""
    massive_desc = "L" * 10000
    test_line = "A" * 7 + " " + "0" + " " + "S" * 60 + " " + massive_desc

    parsed = EpistemicIcd10ExtractionTask.parse_icd10_line(test_line)

    assert parsed["raw_code"] == "A" * 7
    assert parsed["hipaa_flag"] == "0"
    assert parsed["short_description"] == "S" * 60
    assert parsed["long_description"] == massive_desc


def test_parse_icd10_line_unusual_characters() -> None:
    """Validate parsing handles unicode/special characters in descriptions correctly."""
    short_desc = "Cholera—also known as: 💀"
    # Pad short desc to 60 characters with spaces
    padded_short = short_desc.ljust(60, " ")

    long_desc = "Cölera is a severe infection. (See also: \u2022 Vibrio)"

    test_line = "A000   " + " " + "1" + " " + padded_short + " " + long_desc

    parsed = EpistemicIcd10ExtractionTask.parse_icd10_line(test_line)

    # Note: extraction.py currently strips the fields. The existing tests in test_extraction.py
    # assert that the fields are stripped, e.g. code is "A000" not "A000   ", short_desc is short_desc without padding.
    # Therefore, the parsed value for short_description will be stripped of trailing whitespace.
    assert parsed["short_description"] == short_desc
    assert parsed["long_description"] == long_desc


def test_extract_and_parse_complex_zip(tmp_path: Path) -> None:
    """Validate extraction behaves correctly with deep directories and different CRLF formats inside the ZIP."""
    zip_path = tmp_path / "complex_2025.zip"
    fiscal_year = 2025

    # File content with Windows CRLF, Unix LF, extra blank lines, and padding spaces.
    content = (
        "A000    1 Short desc 1" + (" " * 48) + " Long desc 1\r\n"
        "\n\r\n"
        "A001    0 Short desc 2" + (" " * 48) + " Long desc 2\n"
        "A009    1 Short desc 3" + (" " * 48) + " Long desc 3   \r\n"
    )

    with zipfile.ZipFile(zip_path, "w") as zf:
        # Place the correct file inside a nested directory
        zf.writestr("nested/path/to/icd10cm_codes_2025.txt", content)
        # Place an invalid file with similar name
        zf.writestr("icd10cm_codes_wrong.csv", "invalid content")

    records = list(EpistemicIcd10ExtractionTask.extract_and_parse(str(zip_path), fiscal_year))

    assert len(records) == 3
    # Note: extraction.py strips the fields. So raw_code will be "A000", not "A000   ".
    assert records[0]["raw_data"]["raw_code"] == "A000"
    assert records[0]["raw_data"]["long_description"] == "Long desc 1"

    assert records[1]["raw_data"]["raw_code"] == "A001"
    assert records[1]["raw_data"]["long_description"] == "Long desc 2"

    assert records[2]["raw_data"]["raw_code"] == "A009"
    assert records[2]["raw_data"]["long_description"] == "Long desc 3"
