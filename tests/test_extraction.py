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
Test suite validating In-Memory ZIP Extraction and Fixed-Width Parsing.
"""

import io
import zipfile

import pytest
import responses

from coreason_etl_icd_10.extraction import EpistemicIcd10ExtractionTask


def test_parse_icd10_line_success() -> None:
    """Validate that the defensive slice parameters correctly parse a standard line."""
    # Based on CMS specs:
    # 1-7: Code, 8: Blank, 9: HIPAA, 10: Blank, 11-70: Short Desc, 71: Blank, 72+: Long Desc
    # 01234567890123456789012345678901234567890123456789012345678901234567890123456789
    # A000    1 Cholera due to Vibrio cholerae 01, biovar cholerae...
    # "A000   " + " " + "1" + " " + "Cholera due to Vibrio cholerae..."
    # Wait, the spec says:
    # Chars 1-7: ICD-10 Code (Left-justified) -> index 0:7
    # Char 8: Blank -> index 7
    # Char 9: HIPAA Valid Flag (0 or 1) -> index 8
    # Char 10: Blank -> index 9
    # Chars 11-70: Short Description -> index 10:70
    # Char 71: Blank -> index 70
    # Chars 72+: Long Description -> index 71:

    test_line = (
        "A000   "
        + " "
        + "1"
        + " "
        + "Cholera short description"
        + (" " * 35)
        + " "
        + "Cholera long description that goes on and on."
    )
    # Ensure length is correct:
    # A000   (7) + ' ' (1) + '1' (1) + ' ' (1) + Short Desc (60) + ' ' (1) = 71 chars before long desc
    assert len(test_line[:71]) == 71

    parsed = EpistemicIcd10ExtractionTask.parse_icd10_line(test_line)

    assert parsed["raw_code"] == "A000"
    assert parsed["hipaa_flag"] == "1"
    assert parsed["short_description"] == "Cholera short description"
    assert parsed["long_description"] == "Cholera long description that goes on and on."


def test_parse_icd10_line_too_short() -> None:
    """Validate that trying to parse a line that's too short raises a ValueError."""
    with pytest.raises(ValueError, match="Line is too short"):
        EpistemicIcd10ExtractionTask.parse_icd10_line("A000    1 Too Short")


@responses.activate
def test_extract_and_parse_success() -> None:
    """Validate downloading a ZIP in memory, finding the file, and parsing it correctly."""
    zip_url = "https://example.com/2024.zip"
    fiscal_year = 2024

    # Create an in-memory ZIP file with a valid txt payload
    txt_content = (
        "A000    1 Cholera short desc" + (" " * 42) + " Cholera long desc\n"
        "B99     0 Other short desc" + (" " * 44) + " Other long desc\n"
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # Include an empty line in the actual content to hit the coverage for the continue branch
        txt_content_with_empty = "\n\r\n" + txt_content + "\n"
        zf.writestr("icd10cm_codes_2024.txt", txt_content_with_empty)
        # Add a decoy file just to ensure it targets the correct one
        zf.writestr("decoy.pdf", "not text")

    responses.add(
        responses.GET,
        zip_url,
        body=zip_buffer.getvalue(),
        status=200,
        content_type="application/zip",
    )

    records = list(EpistemicIcd10ExtractionTask.extract_and_parse(zip_url, fiscal_year))

    assert len(records) == 2

    assert records[0]["fiscal_year"] == 2024
    assert records[0]["raw_data"]["raw_code"] == "A000"
    assert records[0]["raw_data"]["hipaa_flag"] == "1"
    assert records[0]["raw_data"]["short_description"] == "Cholera short desc"
    assert records[0]["raw_data"]["long_description"] == "Cholera long desc"

    assert records[1]["fiscal_year"] == 2024
    assert records[1]["raw_data"]["raw_code"] == "B99"
    assert records[1]["raw_data"]["hipaa_flag"] == "0"
    assert records[1]["raw_data"]["short_description"] == "Other short desc"
    assert records[1]["raw_data"]["long_description"] == "Other long desc"


@responses.activate
def test_extract_and_parse_file_not_found() -> None:
    """Validate that extraction fails when the ZIP doesn't contain the expected text file."""
    zip_url = "https://example.com/2024_bad.zip"

    # Create an in-memory ZIP with no text file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("decoy.pdf", "not text")

    responses.add(
        responses.GET,
        zip_url,
        body=zip_buffer.getvalue(),
        status=200,
        content_type="application/zip",
    )

    with pytest.raises(FileNotFoundError, match="Could not find a valid ICD-10 codes text file"):
        # The generator must be consumed to trigger the error
        list(EpistemicIcd10ExtractionTask.extract_and_parse(zip_url, 2024))
