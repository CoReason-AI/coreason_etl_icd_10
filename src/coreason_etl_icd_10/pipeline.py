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
DLT pipeline assembly for the ICD-10 CMS ingestion.
"""

from collections.abc import Generator
from typing import Any

import dlt

from coreason_etl_icd_10.config import DiagnosticConfigManifest
from coreason_etl_icd_10.discovery import EpistemicCmsDiscoveryTask
from coreason_etl_icd_10.extraction import EpistemicIcd10ExtractionTask
from coreason_etl_icd_10.utils.logger import logger


@dlt.resource(
    name="icd10_cm_raw",
    write_disposition="merge",
    max_table_nesting=0,
)
def fetch_icd10_cm_raw(manifest: DiagnosticConfigManifest | None = None) -> Generator[dict[str, Any]]:
    """
    DLT Resource mapping the entire pipeline from HTML discovery to JSONB payload yielding.

    AGENT INSTRUCTION: This generator yields nested dicts where `max_table_nesting=0`
    forces dlt to store `raw_data` natively as a JSONB object in PostgreSQL, allowing
    the DBT layer to safely parse it down the line.
    """
    if manifest is None:
        manifest = DiagnosticConfigManifest()

    logger.info("Initializing ICD-10 pipeline execution.")

    try:
        zip_url = EpistemicCmsDiscoveryTask.discover_zip_url(manifest)
        fiscal_year = EpistemicCmsDiscoveryTask.extract_fiscal_year(zip_url)

        logger.info(f"Resolved ingestion target: {zip_url} (Fiscal Year: {fiscal_year})")

        yield from EpistemicIcd10ExtractionTask.extract_and_parse(zip_url, fiscal_year)
        logger.info("Pipeline execution completed successfully.")

    except Exception as e:
        logger.exception("Pipeline encountered an epistemic failure.")
        raise e
