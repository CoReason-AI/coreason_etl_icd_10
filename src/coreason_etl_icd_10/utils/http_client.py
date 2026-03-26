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
HTTP client utilities for epistemic ingestion pipelines.
"""

import requests

from coreason_etl_icd_10.utils.logger import logger


class EpistemicHttpClient:
    """
    EpistemicHttpClient to perform resilient HTTP requests.

    AGENT INSTRUCTION: This class deterministically manages HTTP headers and
    network calls to ensure anti-bot measures from external vendors are avoided.
    """

    @staticmethod
    def get(url: str) -> requests.Response:
        """
        Executes an HTTP GET request with standard headers to prevent WAF blocks.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        logger.info(f"Executing GET request to: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response
