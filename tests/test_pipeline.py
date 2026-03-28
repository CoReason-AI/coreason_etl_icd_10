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
Test suite validating the DLT Resource Pipeline Assembly.
"""

from unittest.mock import patch

import pytest

from coreason_etl_icd_10.config import DiagnosticConfigManifest
from coreason_etl_icd_10.pipeline import fetch_icd10_cm_raw


def test_dlt_pipeline_success() -> None:
    """Validate that the DLT resource generates records correctly."""

    mock_manifest = DiagnosticConfigManifest(local_zip_path="/data/2024.zip")

    mock_records = [
        {"fiscal_year": 2024, "raw_code": "A000", "raw_data": {"raw_code": "A000"}},
        {"fiscal_year": 2024, "raw_code": "B99", "raw_data": {"raw_code": "B99"}},
    ]

    with patch("coreason_etl_icd_10.pipeline.EpistemicCmsDiscoveryTask.resolve_local_zip_path") as mock_resolve:
        mock_resolve.return_value = "/data/2024.zip"

        with patch("coreason_etl_icd_10.pipeline.EpistemicCmsDiscoveryTask.extract_fiscal_year") as mock_extract_yr:
            mock_extract_yr.return_value = 2024

            with patch(
                "coreason_etl_icd_10.pipeline.EpistemicIcd10ExtractionTask.extract_and_parse"
            ) as mock_extract_parse:
                mock_extract_parse.return_value = (record for record in mock_records)

                # Fetch records from the DLT resource
                results = list(fetch_icd10_cm_raw(mock_manifest))

                assert len(results) == 2
                assert results[0]["fiscal_year"] == 2024
                assert results[0]["raw_code"] == "A000"
                assert results[0]["raw_data"]["raw_code"] == "A000"

                mock_resolve.assert_called_once_with(mock_manifest)
                mock_extract_yr.assert_called_once_with("/data/2024.zip")
                mock_extract_parse.assert_called_once_with("/data/2024.zip", 2024)


def test_dlt_pipeline_error_handling() -> None:
    """Validate that pipeline failures are re-raised correctly."""

    with patch("coreason_etl_icd_10.pipeline.EpistemicCmsDiscoveryTask.resolve_local_zip_path") as mock_resolve:
        mock_resolve.side_effect = ValueError("File not found")

        # DLT intercepts exceptions generated inside the pipeline generator
        # and wraps them in PipelineStepFailed or similar. Instead of matching exact type,
        # we check it's raised correctly.
        with pytest.raises(Exception, match="File not found"):
            list(fetch_icd10_cm_raw())
