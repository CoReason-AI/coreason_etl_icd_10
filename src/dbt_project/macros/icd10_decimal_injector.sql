{% macro icd10_decimal_injector(raw_code_column) %}
    {#
        AGENT INSTRUCTION: This macro enforces the ICD-10 clinical decimal rule natively in SQL.
        If a code is longer than 3 characters, a decimal MUST be placed after the 3rd character.
    #}
    CASE
        WHEN length(trim({{ raw_code_column }})) <= 3 THEN trim({{ raw_code_column }})
        ELSE substring(trim({{ raw_code_column }}) from 1 for 3) || '.' || substring(trim({{ raw_code_column }}) from 4)
    END
{% endmacro %}
