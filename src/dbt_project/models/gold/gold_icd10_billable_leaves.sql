-- Copyright (c) 2026 CoReason, Inc.
-- Licensed under the Prosperity Public License 3.0

{{ config(materialized='view') }}

SELECT
    formatted_icd10_code,
    long_description,
    fiscal_year
FROM {{ ref('icd10_ontology') }}
WHERE is_billable = TRUE
