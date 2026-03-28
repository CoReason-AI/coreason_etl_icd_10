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
Test suite validating Local Discovery & ZIP Path Extraction.
"""

from pathlib import Path

import pytest

from coreason_etl_icd_10.config import DiagnosticConfigManifest
from coreason_etl_icd_10.discovery import EpistemicCmsDiscoveryTask


def test_extract_fiscal_year_success() -> None:
    """Validate extracting the fiscal year successfully from different formats."""
    path1 = "/data/2024-icd-10-cm.zip"
    path2 = "./icd10cm_codes_2025.zip"
    path3 = "/folder2026/codes.zip"

    assert EpistemicCmsDiscoveryTask.extract_fiscal_year(path1) == 2024
    assert EpistemicCmsDiscoveryTask.extract_fiscal_year(path2) == 2025
    assert EpistemicCmsDiscoveryTask.extract_fiscal_year(path3) == 2026


def test_extract_fiscal_year_failure() -> None:
    """Validate extracting the fiscal year fails when no year exists."""
    path = "/data/icd10cm_codes.zip"

    with pytest.raises(ValueError, match="Could not extract fiscal year"):
        EpistemicCmsDiscoveryTask.extract_fiscal_year(path)


def test_resolve_local_zip_path_success(tmp_path: Path) -> None:
    """Validate resolving the local ZIP path successfully."""
    # Create a dummy zip file
    dummy_zip = tmp_path / "icd10cm_codes_2024.zip"
    dummy_zip.touch()

    manifest = DiagnosticConfigManifest(
        local_zip_path=str(dummy_zip),
    )

    resolved_path = EpistemicCmsDiscoveryTask.resolve_local_zip_path(manifest)

    assert resolved_path == str(dummy_zip.absolute())


def test_resolve_local_zip_path_failure(tmp_path: Path) -> None:
    """Validate resolving the local ZIP path fails when file does not exist."""
    missing_zip = tmp_path / "missing_file_2024.zip"

    manifest = DiagnosticConfigManifest(
        local_zip_path=str(missing_zip),
    )

    with pytest.raises(FileNotFoundError, match="Configured local ZIP file does not exist"):
        EpistemicCmsDiscoveryTask.resolve_local_zip_path(manifest)
