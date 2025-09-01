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

{% macro starrocks__create_view_as(relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}
  create or replace view {{ relation }} as {{ sql }};
{%- endmacro %}

{% macro starrocks__drop_view(relation) -%}
  drop view if exists {{ relation.render() }}
{%- endmacro %}

{% materialization view, adapter='starrocks' -%}
    {{ return(starrocks__create_or_replace_view()) }}
{%- endmaterialization %}

{% macro starrocks__create_or_replace_view() %}
    {%- set identifier = model['alias'] -%}

      {{ log('=== ' ~ database ~ '.' ~ model['schema'] ~ '.' ~ identifier) }}

    {%- set old_relation = adapter.get_relation(database=database, schema=schema, identifier=identifier) -%}
    {%- set exists_as_view = (old_relation is not none and old_relation.is_view) -%}

    {%- set target_relation = api.Relation.create(
        identifier=identifier, schema=schema, database=database,
        type='view') -%}
    {% set grant_config = config.get('grants') %}

    {{ run_hooks(pre_hooks) }}

    -- If there's a table with the same name and we weren't told to full refresh,
    -- that's an error. If we were told to full refresh, drop it. This behavior differs
    -- for Snowflake and BigQuery, so multiple dispatch is used.
    {%- if old_relation is not none and old_relation.is_table -%}
    {{ handle_existing_table(should_full_refresh(), old_relation) }}
    {%- endif -%}

    -- build model
    {% call statement('main', auto_begin=False) -%}
    {{ get_create_view_as_sql(target_relation, sql) }}
    {%- endcall %}

    {% set should_revoke = should_revoke(exists_as_view, full_refresh_mode=True) %}
    {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

    {{ run_hooks(post_hooks) }}

    {{ return({'relations': [target_relation]}) }}

{% endmacro %}