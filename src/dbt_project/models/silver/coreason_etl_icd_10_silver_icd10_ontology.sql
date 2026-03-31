-- Copyright (c) 2026 CoReason, Inc.
-- Licensed under the Prosperity Public License 3.0

{{ config(
    materialized='table',
    unique_key=['formatted_icd10_code', 'fiscal_year']
) }}

WITH source AS (
    SELECT
        fiscal_year,
        ingestion_ts,
        raw_data->>'raw_code' AS raw_code_string,
        raw_data->>'short_description' AS short_description,
        raw_data->>'long_description' AS long_description,
        raw_data->>'hipaa_flag' AS hipaa_flag
    FROM {{ source('bronze', 'coreason_etl_icd_10_bronze_icd10_cm_raw') }}
),

cleaned AS (
    SELECT
        fiscal_year,
        ingestion_ts,
        trim(raw_code_string) AS raw_code_string,
        trim(short_description) AS short_description,
        trim(long_description) AS long_description,
        CASE
            WHEN trim(hipaa_flag) = '1' THEN TRUE
            ELSE FALSE
        END AS is_billable
    FROM source
)

SELECT
    fiscal_year,
    ingestion_ts,
    raw_code_string,
    {{ icd10_decimal_injector('raw_code_string') }} AS formatted_icd10_code,
    uuid_generate_v5(uuid_ns_url(), {{ icd10_decimal_injector('raw_code_string') }}) AS coreason_id,
    short_description,
    long_description,
    is_billable
FROM cleaned
