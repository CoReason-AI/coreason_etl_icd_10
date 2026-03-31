-- Copyright (c) 2026 CoReason, Inc.
-- Licensed under the Prosperity Public License 3.0

{{ config(
    materialized='view'
) }}

SELECT
    coreason_id,
    fiscal_year,
    ingestion_ts,
    formatted_icd10_code,
    raw_code_string,
    short_description,
    long_description,
    is_billable
FROM {{ ref('coreason_etl_icd_10_silver_icd10_ontology') }}
WHERE is_billable = TRUE
