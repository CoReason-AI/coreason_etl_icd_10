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

import zipfile
import csv
import io
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any
from coreason_etl_icd_10.utils.logger import logger

class EpistemicIcd10ExtractionTask:
    """
    EpistemicIcd10ExtractionTask modified to parse OMOP CONCEPT.csv payloads.
    """

    @staticmethod
    def extract_and_parse(local_zip_path: str, fiscal_year: int) -> Generator[dict[str, Any], None, None]:
        logger.info(f"Extracting OMOP payload from: {local_zip_path}")
        ingestion_ts = datetime.now(UTC)

        with zipfile.ZipFile(local_zip_path, "r") as z:
            # Target the OMOP CONCEPT file
            if "CONCEPT.csv" not in z.namelist():
                raise FileNotFoundError("Could not find CONCEPT.csv in the OMOP ZIP file.")

            logger.info("Extracting and parsing CONCEPT.csv")

            with z.open("CONCEPT.csv") as f:
                # OMOP files are typically tab-separated (\t). If yours is comma-separated, change delimiter to ','
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'), delimiter='\t')
                
                for row in reader:
                    # Filter only for ICD-10 concepts if necessary
                    if row.get("vocabulary_id", "").startswith("ICD10"):
                        yield {
                            "fiscal_year": fiscal_year,
                            "raw_code": row.get("concept_code", ""),
                            "ingestion_ts": ingestion_ts,
                            "raw_data": {
                                "raw_code": row.get("concept_code", ""),
                                "short_description": row.get("concept_name", "")[:60], # Map OMOP concept_name
                                "long_description": row.get("concept_name", ""),
                                "hipaa_flag": "1" if row.get("standard_concept") == "S" else "0"
                            },
                        }
