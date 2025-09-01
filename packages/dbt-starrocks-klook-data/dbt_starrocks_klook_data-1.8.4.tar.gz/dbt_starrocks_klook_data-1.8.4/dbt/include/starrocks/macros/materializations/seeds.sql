/*
 * Copyright 2021-present StarRocks, Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https:*www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

{% macro starrocks__create_csv_table(model, agate_table) -%}
  {% set column_override = model['config'].get('column_types', {}) %}
  {% set quote_seed_column = model['config'].get('quote_columns', None) %}
  {% set engine = config.get('engine', 'OLAP') %}

  {% set sql %}
    create table {{ this.render() }} (
        {% for col_name in agate_table.column_names %}
            {%- set inferred_type = adapter.convert_type(agate_table, loop.index0) -%}
            {%- set type = column_override.get(col_name, inferred_type) -%}
            {%- set column_name = (col_name | string) -%}
            {{ adapter.quote_seed_column(column_name, quote_seed_column) }} {{ type }}
            {%- if not loop.last %},
        {% endif -%}
        {% endfor %}
    )
    {%- if engine == 'OLAP' -%}
      {{ starrocks__olap_table(False) }}
    {%- else -%}
      {{ starrocks__other_table() }}
    {%- endif -%}
  {% endset %}

  {% call statement('_', auto_begin=False) -%}
    {{ sql }}
  {%- endcall %}

  {{ return(sql) }}

{%- endmacro %}

{% macro starrocks__load_csv_rows(model, agate_table) %}

    {% set batch_size = get_batch_size() %}

    {% set cols_sql = get_seed_column_quoted_csv(model, agate_table.column_names) %}
    {% set bindings = [] %}

    {% set statements = [] %}

    {% for chunk in agate_table.rows | batch(batch_size) %}
    {% set bindings = [] %}

    {% for row in chunk %}
        {% do bindings.extend(row) %}
    {% endfor %}

    {% set sql %}
        insert into {{ this.render() }} ({{ cols_sql }}) values
        {% for row in chunk -%}
            ({%- for column in agate_table.column_names -%}
                {{ get_binding_char() }}
                {%- if not loop.last%},{%- endif %}
            {%- endfor -%})
            {%- if not loop.last%},{%- endif %}
        {%- endfor %}
    {% endset %}

    {% do adapter.add_query(sql, bindings=bindings, abridge_sql_log=True, auto_begin=False) %}

    {% if loop.index0 == 0 %}
    {% do statements.append(sql) %}
    {% endif %}
    {% endfor %}

    {# Return SQL so we can render it out into the compiled files #}
    {{ return(statements[0]) }}
{% endmacro %}

