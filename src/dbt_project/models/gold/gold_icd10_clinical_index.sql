-- Copyright (c) 2026 CoReason, Inc.
-- Licensed under the Prosperity Public License 3.0

{{ config(
    materialized='view'
) }}

WITH ranked_descriptions AS (
    SELECT
        formatted_icd10_code,
        long_description,
        fiscal_year,
        ingestion_ts,
        raw_code_string,
        short_description,
        is_billable,
        ROW_NUMBER() OVER (
            PARTITION BY formatted_icd10_code
            ORDER BY fiscal_year DESC
        ) as rn
    FROM {{ ref('icd10_ontology') }}
)

SELECT
    formatted_icd10_code,
    long_description,
    fiscal_year,
    ingestion_ts,
    raw_code_string,
    short_description,
    is_billable
FROM ranked_descriptions
WHERE rn = 1
