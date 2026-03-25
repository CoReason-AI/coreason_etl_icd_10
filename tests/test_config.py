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

from coreason_etl_icd_10.config import DiagnosticConfigManifest


def test_config_manifest_defaults() -> None:
    """Validate that the DiagnosticConfigManifest loads defaults correctly."""

    # Temporarily remove any existing env vars to isolate the test
    if "CMS_ENDPOINT_BASE_URL" in os.environ:
        del os.environ["CMS_ENDPOINT_BASE_URL"]
    if "DIRECT_ZIP_URL_OVERRIDE" in os.environ:
        del os.environ["DIRECT_ZIP_URL_OVERRIDE"]

    manifest = DiagnosticConfigManifest()

    assert manifest.cms_endpoint_base_url == "https://www.cms.gov/medicare/coding-billing/icd-10-codes/2024-icd-10-cm"
    assert manifest.direct_zip_url_override is None


def test_config_manifest_env_override() -> None:
    """Validate that environment variables properly override default configurations."""
    os.environ["CMS_ENDPOINT_BASE_URL"] = "https://example.com/mock-cms"
    os.environ["DIRECT_ZIP_URL_OVERRIDE"] = "https://example.com/mock-cms/file.zip"

    manifest = DiagnosticConfigManifest()

    assert manifest.cms_endpoint_base_url == "https://example.com/mock-cms"
    assert manifest.direct_zip_url_override == "https://example.com/mock-cms/file.zip"

    # Clean up
    del os.environ["CMS_ENDPOINT_BASE_URL"]
    del os.environ["DIRECT_ZIP_URL_OVERRIDE"]
