-- Copyright (c) 2026 CoReason, Inc.
-- Licensed under the Prosperity Public License 3.0

-- Unit test for icd10_decimal_injector macro

WITH test_data AS (
    SELECT 'A00' AS raw_code_string, 'A00' AS expected_formatted_code UNION ALL
    SELECT 'A000' AS raw_code_string, 'A00.0' AS expected_formatted_code UNION ALL
    SELECT 'E119' AS raw_code_string, 'E11.9' AS expected_formatted_code UNION ALL
    SELECT '  B10  ' AS raw_code_string, 'B10' AS expected_formatted_code UNION ALL
    SELECT '  B101  ' AS raw_code_string, 'B10.1' AS expected_formatted_code UNION ALL
    SELECT 'M123456' AS raw_code_string, 'M12.3456' AS expected_formatted_code
),

macro_application AS (
    SELECT
        raw_code_string,
        {{ icd10_decimal_injector('raw_code_string') }} AS actual_formatted_code,
        expected_formatted_code
    FROM test_data
)

SELECT *
FROM macro_application
WHERE actual_formatted_code != expected_formatted_code
