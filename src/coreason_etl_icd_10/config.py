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
    in-memory extraction process and HTTP ingestion pathways, protecting the Knowledge Graph
    from drift.
    """

    cms_endpoint_base_url: str = Field(
        default="https://www.cms.gov/medicare/coding-billing/icd-10-codes/2024-icd-10-cm",
        description="The primary HTTP destination containing the HTML page with the CMS ZIP asset link.",
    )
    direct_zip_url_override: str | None = Field(
        default=None,
        description=(
            "Optional fallback URL for the ZIP payload, bypassing the HTML "
            "discovery step if anti-bot measures are encountered."
        ),
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
