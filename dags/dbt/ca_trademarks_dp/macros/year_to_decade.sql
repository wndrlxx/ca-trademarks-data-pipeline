{% macro year_to_decade(year) %}
    CAST(FLOOR(year / 10) * 10 AS int64)
{% endmacro %}