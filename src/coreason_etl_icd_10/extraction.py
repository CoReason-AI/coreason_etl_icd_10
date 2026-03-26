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
In-memory extraction and fixed-width parsing module for CMS ICD-10 data.
"""

import io
import zipfile
from collections.abc import Generator
from typing import Any

from coreason_etl_icd_10.utils.http_client import EpistemicHttpClient
from coreason_etl_icd_10.utils.logger import logger


class EpistemicIcd10ExtractionTask:
    """
    EpistemicIcd10ExtractionTask to manage the payload retrieval and parsing into JSONB records.

    AGENT INSTRUCTION: This class must defensively parse the CMS fixed-width format and
    yield dictionaries specifically structured to prevent nested schema shredding by dlt.
    """

    @staticmethod
    def parse_icd10_line(line: str) -> dict[str, str]:
        """
        Parses a single line of the CMS ICD-10 fixed-width text file.
        Uses defensive slice parameters to protect the long description.
        """
        # Ensure the line is long enough to parse
        if len(line) < 72:
            raise ValueError(f"Line is too short to be a valid ICD-10 CMS fixed-width string: {line!r}")

        return {
            "raw_code": line[0:7].strip(),
            "hipaa_flag": line[8:9].strip(),
            "short_description": line[10:70].strip(),
            "long_description": line[71:].strip(),
        }

    @staticmethod
    def extract_and_parse(zip_url: str, fiscal_year: int) -> Generator[dict[str, Any]]:
        """
        Downloads the ZIP into memory, locates the '.txt' file with 'icd10cm_codes' in the name,
        and yields dict payloads for the Bronze table.
        """
        logger.info(f"Downloading ZIP payload from: {zip_url}")
        response = EpistemicHttpClient.get(zip_url)

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Locate the correct text file in the ZIP (case-insensitive check)
            target_filename = None
            for name in z.namelist():
                if "icd10cm_codes" in name.lower() and name.lower().endswith(".txt"):
                    target_filename = name
                    break

            if not target_filename:
                raise FileNotFoundError(f"Could not find a valid ICD-10 codes text file in the ZIP at {zip_url}")

            logger.info(f"Extracting and parsing text file: {target_filename}")

            with z.open(target_filename) as f:
                for line_bytes in f:
                    line = line_bytes.decode("utf-8").rstrip("\r\n").rstrip("\n")
                    if not line.strip():
                        continue

                    parsed_dict = EpistemicIcd10ExtractionTask.parse_icd10_line(line)
                    yield {"fiscal_year": fiscal_year, "raw_data": parsed_dict}
