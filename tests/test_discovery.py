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
Test suite validating HTML Discovery & ZIP URL Extraction.
"""

import pytest
import responses

from coreason_etl_icd_10.config import DiagnosticConfigManifest
from coreason_etl_icd_10.discovery import EpistemicCmsDiscoveryTask


def test_extract_fiscal_year_success() -> None:
    """Validate extracting the fiscal year successfully from different formats."""
    url1 = "https://example.com/2024-icd-10-cm.zip"
    url2 = "https://example.com/icd10cm_codes_2025.zip"
    url3 = "https://example.com/folder2026/codes.zip"

    assert EpistemicCmsDiscoveryTask.extract_fiscal_year(url1) == 2024
    assert EpistemicCmsDiscoveryTask.extract_fiscal_year(url2) == 2025
    assert EpistemicCmsDiscoveryTask.extract_fiscal_year(url3) == 2026


def test_extract_fiscal_year_failure() -> None:
    """Validate extracting the fiscal year fails when no year exists."""
    url = "https://example.com/icd10cm_codes.zip"

    with pytest.raises(ValueError, match="Could not extract fiscal year"):
        EpistemicCmsDiscoveryTask.extract_fiscal_year(url)


@responses.activate
def test_discover_zip_url_from_html_success() -> None:
    """Validate discovering the ZIP URL from HTML scraping."""
    manifest = DiagnosticConfigManifest(
        cms_endpoint_base_url="https://www.cms.gov/medicare/coding-billing/icd-10-codes/2024-icd-10-cm",
        direct_zip_url_override=None,
    )

    html_content = b"""
    <html>
        <body>
            <a href="/files/document/2024-icd-10-cm-code-descriptions-zip.zip">Download 2024 Codes</a>
            <a href="/files/document/other-file.pdf">Other File</a>
        </body>
    </html>
    """

    responses.add(
        responses.GET,
        manifest.cms_endpoint_base_url,
        body=html_content,
        status=200,
    )

    discovered_url = EpistemicCmsDiscoveryTask.discover_zip_url(manifest)

    expected_url = "https://www.cms.gov/files/document/2024-icd-10-cm-code-descriptions-zip.zip"
    assert discovered_url == expected_url


@responses.activate
def test_discover_zip_url_from_html_failure() -> None:
    """Validate discovering the ZIP URL fails when no ZIP link exists."""
    manifest = DiagnosticConfigManifest(
        cms_endpoint_base_url="https://www.cms.gov/medicare/coding-billing/icd-10-codes/2024-icd-10-cm",
        direct_zip_url_override=None,
    )

    html_content = b"""
    <html>
        <body>
            <a href="/files/document/other-file.pdf">Other File</a>
        </body>
    </html>
    """

    responses.add(
        responses.GET,
        manifest.cms_endpoint_base_url,
        body=html_content,
        status=200,
    )

    with pytest.raises(ValueError, match=r"Could not locate a \.zip file link"):
        EpistemicCmsDiscoveryTask.discover_zip_url(manifest)


def test_discover_zip_url_override() -> None:
    """Validate discovering the ZIP URL respects the direct override."""
    manifest = DiagnosticConfigManifest(
        cms_endpoint_base_url="https://www.cms.gov/medicare/coding-billing/icd-10-codes/2024-icd-10-cm",
        direct_zip_url_override="https://example.com/direct/2025.zip",
    )

    # We do NOT add a responses mock here to verify it skips the network call
    discovered_url = EpistemicCmsDiscoveryTask.discover_zip_url(manifest)
    assert discovered_url == "https://example.com/direct/2025.zip"
