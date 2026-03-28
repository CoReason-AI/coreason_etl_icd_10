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
Discovery module for locating the CMS ICD-10 ZIP payload locally.
"""

import re
from pathlib import Path

from coreason_etl_icd_10.config import DiagnosticConfigManifest
from coreason_etl_icd_10.utils.logger import logger


class EpistemicCmsDiscoveryTask:
    """
    EpistemicCmsDiscoveryTask to perform local path resolution and fiscal year extraction.

    AGENT INSTRUCTION: This class deterministically resolves the local path to the
    CMS ZIP file and extracts the applicable fiscal year from the filename.
    """

    @staticmethod
    def extract_fiscal_year(filepath: str) -> int:
        """
        Extracts the 4-digit fiscal year from the given file path.
        Raises ValueError if not found.
        """
        # Regex to find any 4-digit number starting with 20
        match = re.search(r"(20\d{2})", filepath)
        if not match:
            raise ValueError(f"Could not extract fiscal year from path: {filepath}")
        return int(match.group(1))

    @staticmethod
    def resolve_local_zip_path(manifest: DiagnosticConfigManifest) -> str:
        """
        Resolves the local ZIP file path from configuration.
        Raises FileNotFoundError if the file does not exist locally.
        """
        local_path = manifest.local_zip_path
        logger.info(f"Resolving local ZIP path: {local_path}")

        path_obj = Path(local_path)
        if not path_obj.exists() or not path_obj.is_file():
            raise FileNotFoundError(f"Configured local ZIP file does not exist: {local_path}")

        return str(path_obj.absolute())
