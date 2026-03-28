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
Configuration policies for the ICD-10 ingestion pipeline.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DiagnosticConfigManifest(BaseSettings):
    """
    EpistemicIngestionPolicy to manage the boundaries and location of the CMS ICD-10 payload.

    AGENT INSTRUCTION: This class deterministically manages the configurations for the
    in-memory extraction process and local ingestion pathways, protecting the Knowledge Graph
    from drift.
    """

    local_zip_path: str = Field(
        default="./data/icd10cm_codes_2024.zip",
        description="The absolute or relative local path pointing to the CMS ICD-10 ZIP payload.",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
