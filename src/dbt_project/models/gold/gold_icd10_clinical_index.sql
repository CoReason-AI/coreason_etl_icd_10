-- Copyright (c) 2026 CoReason, Inc.
-- Licensed under the Prosperity Public License 3.0

{{ config(materialized='view') }}

WITH ranked_codes AS (
    SELECT
        formatted_icd10_code,
        long_description,
        fiscal_year,
        ROW_NUMBER() OVER (
            PARTITION BY formatted_icd10_code
            ORDER BY fiscal_year DESC
        ) AS rn
    FROM {{ ref('icd10_ontology') }}
)

SELECT
    formatted_icd10_code,
    long_description
FROM ranked_codes
WHERE rn = 1
