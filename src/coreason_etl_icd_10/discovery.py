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
Discovery module for locating the CMS ICD-10 ZIP payload.
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from coreason_etl_icd_10.config import DiagnosticConfigManifest
from coreason_etl_icd_10.utils.http_client import EpistemicHttpClient
from coreason_etl_icd_10.utils.logger import logger


class EpistemicCmsDiscoveryTask:
    """
    EpistemicCmsDiscoveryTask to perform HTML scraping and URL extraction.

    AGENT INSTRUCTION: This class deterministically locates the CMS ZIP file URL
    and extracts the applicable fiscal year from the URL or filename.
    """

    @staticmethod
    def extract_fiscal_year(url: str) -> int:
        """
        Extracts the 4-digit fiscal year from the given URL or filename.
        Raises ValueError if not found.
        """
        # Regex to find any 4-digit number starting with 20
        match = re.search(r"(20\d{2})", url)
        if not match:
            raise ValueError(f"Could not extract fiscal year from URL: {url}")
        return int(match.group(1))

    @staticmethod
    def discover_zip_url(manifest: DiagnosticConfigManifest) -> str:
        """
        Discovers the ZIP file URL either via fallback override or HTML scraping.
        Raises ValueError if the ZIP link cannot be found in the HTML.
        """
        if manifest.direct_zip_url_override:
            logger.info("Using direct ZIP URL override from configuration.")
            return manifest.direct_zip_url_override

        logger.info(f"Discovering ZIP URL from CMS endpoint: {manifest.cms_endpoint_base_url}")
        response = EpistemicHttpClient.get(manifest.cms_endpoint_base_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Look for any link that ends in .zip
        for a_tag in soup.find_all("a", href=True):
            href = str(a_tag["href"])
            if href.lower().endswith(".zip"):
                # Handle relative URLs
                full_url = urljoin(manifest.cms_endpoint_base_url, href)
                logger.info(f"Discovered ZIP URL: {full_url}")
                return full_url

        raise ValueError("Could not locate a .zip file link on the CMS endpoint page.")
