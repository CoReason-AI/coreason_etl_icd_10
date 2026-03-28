{% macro icd10_decimal_injector(raw_code_column) %}
    case
        when length(trim({{ raw_code_column }})) <= 3 then trim({{ raw_code_column }})
        else substring(trim({{ raw_code_column }}) from 1 for 3) || '.' || substring(trim({{ raw_code_column }}) from 4)
    end
{% endmacro %}
