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
Test suite validating the Epistemic policies for ICD-10 pipeline configuration.
"""

import os

from hypothesis import given
from hypothesis import strategies as st

from coreason_etl_icd_10.config import DiagnosticConfigManifest


def test_config_manifest_defaults() -> None:
    """Validate that the DiagnosticConfigManifest loads defaults correctly."""

    # Temporarily remove any existing env vars to isolate the test
    if "LOCAL_ZIP_PATH" in os.environ:
        del os.environ["LOCAL_ZIP_PATH"]

    manifest = DiagnosticConfigManifest()

    assert manifest.local_zip_path == "./data/icd10cm_codes_2024.zip"


def test_config_manifest_env_override() -> None:
    """Validate that environment variables properly override default configurations."""
    os.environ["LOCAL_ZIP_PATH"] = "/var/lib/data/mock-cms/file.zip"

    manifest = DiagnosticConfigManifest()

    assert manifest.local_zip_path == "/var/lib/data/mock-cms/file.zip"

    # Clean up
    del os.environ["LOCAL_ZIP_PATH"]


@given(
    st.text(min_size=1),
)
def test_config_manifest_property_based(local_path: str) -> None:
    """Validate Pydantic properties using hypothesis generated edge cases."""
    manifest = DiagnosticConfigManifest(
        local_zip_path=local_path,
    )
    assert manifest.local_zip_path == local_path
